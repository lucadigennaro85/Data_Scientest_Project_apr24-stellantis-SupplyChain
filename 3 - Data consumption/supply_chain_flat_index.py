from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline  # for bert sentiment analysis
import csv
import json
import hashlib
from collections import defaultdict
from elasticsearch import Elasticsearch, helpers
import statistics
import pandas as pd
import sys

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()
sentiment_analyzer_bert = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

def generate_review_id(company, review_text):
    """Generates a unique review_id from Company + Review Comment."""
    return hashlib.md5((company + review_text).encode('utf-8')).hexdigest()

def compute_vader_sentiment(text):
    if not text or text.strip() == "":
        return 0  # Neutral as default for empty text
    score = vader_analyzer.polarity_scores(text)["compound"]
    return 1 if score >= 0.05 else -1 if score <= -0.05 else 0

def compute_textblob_sentiment(text):
    if not text or text.strip() == "":
        return 0  # Neutral as default for empty text
    score = TextBlob(text).sentiment.polarity
    return 1 if score > 0.1 else -1 if score < -0.1 else 0

def compute_bert_sentiment_batch(texts):
    # USED the cardiffnlp/twitter-roberta-base-sentiment BERT model which is optimized for Twitter (very strong in social NLP)
    # It is 2nd heaviest in in computing resources usage and 2nd highest in accurracy - used mostly in NLP for social media
    if not texts:
        return []

    # Truncate long reviews to 512 tokens (approx. ~400 words)
    truncated_texts = [text[:512] if text.strip() else " " for text in texts]  # Ensures no empty text
    results = sentiment_analyzer_bert(truncated_texts, batch_size=64)

    # Handle potential empty results gracefully
    return [
        1 if r and r["label"] == "LABEL_2"
        else -1 if r and r["label"] == "LABEL_0"
        else 0
        for r in results
    ]

# Process Reviews with review_id generation
def process_reviews(input_file, output_file, sentiment_method, sentiment_label):

    with open(input_file, newline='', encoding='utf-8') as csvfile:
        rows = list(csv.DictReader(csvfile))

    # Sort rows to ensure consistent order for identical review_id generation (case-insensitive sorting)
    rows = sorted(rows, key=lambda x: (x.get("Company", "").lower(), x.get("Review Comment", "").lower()))

    # Step 1- Clean and cast necessary fields
    for row in rows:
        # Clean "Number of Reviews"
        num_reviews_str = row.get("Number of Reviews", "").replace(",", "").strip()
        try:
            row["Number of Reviews"] = int(num_reviews_str) if num_reviews_str else 0
        except ValueError:
            row["Number of Reviews"] = 0

        # Clean "Trustscore"
        trustscore_str = str(row.get("Trustscore", "")).strip()
        try:
            row["Trustscore"] = float(trustscore_str) if trustscore_str else 0.0
        except ValueError:
            row["Trustscore"] = 0.0

        # Clean review percentages (5 to 1 stars)
        for star_key in [
            "5 stars reviews percentage",
            "4 stars reviews percentage",
            "3 stars reviews percentage",
            "2 stars reviews percentage",
            "1 star reviews percentage"
        ]:
            val = row.get(star_key, "").replace("<", "").replace("%", "").strip()
            try:
                row[star_key] = float(val) if val else 0.0
            except ValueError:
                row[star_key] = 0.0

        # Clean "Review Stars"
        review_stars_str = str(row.get("Review Stars", "")).strip()
        try:
            row["Review Stars"] = int(review_stars_str) if review_stars_str else 0
        except ValueError:
            row["Review Stars"] = 0

    # Step 2: Initialize counters
    blank_review_counter = 0
    duplicate_counter_map = defaultdict(int)  # Tracks counts for duplicate rows

    # Step 3: Assign unique review_id and calculate review length
    seen_reviews = defaultdict(int)  # Tracks duplicate detection logic
    for row in rows:
        company = row.get("Company", "").strip()
        review_text = row.get("Review Comment", "").strip()

        # Calculate Review Length (word count)
        row["Review Length"] = len(review_text.split()) if review_text else 0  

        if review_text:  # Non-blank reviews
            review_key = f"{company}_{review_text}"
            seen_reviews[review_key] += 1

            if seen_reviews[review_key] > 1:
                # For duplicates, add a counter to differentiate
                duplicate_counter_map[review_key] += 1
                row["review_id"] = hashlib.md5((review_key + f"_dup_{duplicate_counter_map[review_key]}").encode('utf-8')).hexdigest()
            else:
                # First occurrence — no counter needed
                row["review_id"] = hashlib.md5(review_key.encode('utf-8')).hexdigest()

        else:  # Blank reviews — use counter for uniqueness
            blank_review_counter += 1
            row["review_id"] = hashlib.md5((company + f"_blank_{blank_review_counter}").encode('utf-8')).hexdigest()

    # Step 4: Calculate Sentiments
    batch_size = 64
    for i in range(0, len(rows), batch_size):
        batch_texts = [row["Review Comment"] for row in rows[i:i + batch_size]]

        if sentiment_method == compute_vader_sentiment or sentiment_method == compute_textblob_sentiment:
            sentiments = [sentiment_method(text) for text in batch_texts]  # Handle VADER & TextBlob
        else:
            sentiments = sentiment_method(batch_texts)  # Handle BERT (batch processing)

        for row, sentiment in zip(rows[i:i + batch_size], sentiments):
            row[sentiment_label] = sentiment

    # Step 5: Calculate and round company sentiment scores
    company_sentiments = defaultdict(list)
    for row in rows:
        company_sentiments[row["Company"]].append(row[sentiment_label])

    for row in rows:
        row[f"Company {sentiment_label}"] = round(
            sum(company_sentiments[row["Company"]]) / len(company_sentiments[row["Company"]]), 5
        )

    # Step 6: Calculate Combined_Score for every row (even duplicate rows) for each company
    for row in rows:  # Iterate through every row in the original list
        try:
            # Clean inputs
            trustscore_str = str(row.get("Trustscore", "")).strip().replace("\ufeff", "")
            reviews_str = str(row.get("Number of Reviews", "")).strip().replace(",", "").replace("\ufeff", "")

            # Convert to appropriate types
            trustscore = float(trustscore_str) if trustscore_str else 0.0
            num_reviews = int(reviews_str) if reviews_str else 0

            # Business rule: if both are 0, Combined_Score = 0
            if trustscore == 0 and num_reviews == 0:
                row["Combined_Score"] = 0.0
            else:
                # Combined Score=(R×N)/(N+C) 
                # This is a Bayesian-like shrinkage toward 0.
                # If N is low (few reviews), the formula pulls the Combined Score down toward 0.
                # If N is large (many reviews), the Combined Score is closer to the raw Trustscore (R).
                # Where:
                #       R is the Trustscore column (FLOAT) - the average rating (0-5).
                #       N is the “Number of Reviews” (num_reviews) column (INTEGER)
                #       C is a constant that controls how much weight is given to the number of reviews. It is calculated once in the __main__ section below 
                row["Combined_Score"] = round(trustscore * num_reviews / (num_reviews + C), 5)

        except (ValueError, TypeError) as e:
            print(f"Error parsing row for company {row.get('Company')}: {e}")
            row["Combined_Score"] = None   

    # Step 7: Write output file
    fieldnames = list(rows[0].keys())
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Sentiment analysis completed using {sentiment_method.__name__}. Output saved to {output_file}")

# Consolidate Sentiment CSVs into One
def merge_sentiment_csvs():

    # Load the three sentiment files
    vader_df = pd.read_csv("trustpilot_reviews_with_sentiment_vader.csv")
    textblob_df = pd.read_csv("trustpilot_reviews_with_sentiment_textblob.csv")
    bert_df = pd.read_csv("trustpilot_reviews_with_sentiment_bert.csv")

    # Ensure no duplicate review_id entries
    vader_df.drop_duplicates(subset='review_id', inplace=True)
    textblob_df.drop_duplicates(subset='review_id', inplace=True)
    bert_df.drop_duplicates(subset='review_id', inplace=True)

    # Merge dataframes on 'review_id' using INNER JOIN for exact matches only
    merged_df = vader_df.merge(
        textblob_df[['review_id', 'TextBlob Sentiment Score', 'Company TextBlob Sentiment Score']], 
        on='review_id', 
        how='inner'
    ).merge(
        bert_df[['review_id', 'BERT Sentiment Score', 'Company BERT Sentiment Score']], 
        on='review_id', 
        how='inner'
    )

    # Retain "Review Length" and "Combined_Score" from one of the original files (VADER)
    merged_df["Review Length"] = vader_df["Review Length"]
    merged_df["Combined_Score"] = vader_df["Combined_Score"]  # ✅ Added this line
    
    # ✅ Reorder columns before saving
    desired_column_order = [
        "Company", "Domain", "Number of Reviews", "Trustscore", "Combined_Score",
        "5 stars reviews percentage", "4 stars reviews percentage",
        "3 stars reviews percentage", "2 stars reviews percentage", "1 star reviews percentage",
        "Company VADER Sentiment Score", "Company TextBlob Sentiment Score", "Company BERT Sentiment Score",
        "review_id", "Review Stars", "Review Comment", "Review Length", "Company Response",
        "VADER Sentiment Score", "TextBlob Sentiment Score", "BERT Sentiment Score"
    ]

    # Only include columns that exist in the current merged_df (robust fallback)
    reordered_columns = [col for col in desired_column_order if col in merged_df.columns]
    merged_df = merged_df[reordered_columns]

    # Save final merged file
    merged_df.to_csv("trustpilot_reviews_combined.csv", index=False)

    print("✅ Merged CSV created successfully: trustpilot_reviews_combined.csv")

# Elasticsearch Flat Index Setup
def setup_flat_index():
    mapping = {
        "mappings": {
            "properties": {
                "Company": {"type": "keyword"},
                "Domain": {"type": "keyword"},
                "Number of Reviews": {"type": "integer"},
                "Trustscore": {"type": "float"},
                "Combined_score": {"type": "float"},
                "5 stars reviews percentage": {"type": "float"},
                "4 stars reviews percentage": {"type": "float"},
                "3 stars reviews percentage": {"type": "float"},
                "2 stars reviews percentage": {"type": "float"},
                "1 star reviews percentage": {"type": "float"},
                "Company VADER Sentiment Score": {"type": "float"},
                "Company TextBlob Sentiment Score": {"type": "float"},
                "Company BERT Sentiment Score": {"type": "float"},
                "review_id": {"type": "keyword"},
                "Review Stars": {"type": "integer"},
                "Review Comment": {"type": "text"},
                "Review Length": {"type": "integer"},
                "Company Response": {"type": "text"},
                "VADER Sentiment Score": {"type": "keyword"},
                "TextBlob Sentiment Score": {"type": "keyword"},
                "BERT Sentiment Score": {"type": "keyword"},
#               "Reviewer Username": {"type": "keyword"},
#               "Review date": {"type": "date"}
            }
        }
    }

    if not es.indices.exists(index="trustpilot_reviews_combined_flat"):
        es.indices.create(index="trustpilot_reviews_combined_flat", body=mapping)
        print("✅ Flat structure mapping created successfully.")
    else:
        print("ℹ️ Index already exists — skipped creation.")


# import to elastic
def import_to_elastic_flat(file_name):
    with open(file_name, encoding='utf-8') as f:
        reader = csv.DictReader(f)

        def process_row(row):
            # Convert missing or empty fields to None (avoid indexing issues)
            for key in row:
                if row[key] == "":
                    row[key] = None

            # Function to clean and convert percentage values safely
            def clean_percentage(value):
                if value is None:
                    return None
                value = value.strip('%')  # Remove % sign
                if value == "<1":  
                    return 1.0  # Convert "<1%" to 1.0
                try:
                    return float(value)
                except ValueError:
                    return None  # Handle any unexpected errors

            # Ensure proper data types and handle missing numeric values safely
            return {
                "_index": "trustpilot_reviews_combined_flat",
                "_source": {
                    "review_id": row["review_id"],
                    "Company": row["Company"],
                    "Domain": row.get("Domain", None),
                    "Number of Reviews": int(row["Number of Reviews"]) if row["Number of Reviews"] and row["Number of Reviews"].isdigit() else None,
                    "Trustscore": float(row["Trustscore"]) if row["Trustscore"] else None,
                    "Combined_Score": float(row["Combined_Score"]) if row["Combined_Score"] else None,
                    "5 stars reviews percentage": clean_percentage(row["5 stars reviews percentage"]),
                    "4 stars reviews percentage": clean_percentage(row["4 stars reviews percentage"]),
                    "3 stars reviews percentage": clean_percentage(row["3 stars reviews percentage"]),
                    "2 stars reviews percentage": clean_percentage(row["2 stars reviews percentage"]),
                    "1 star reviews percentage": clean_percentage(row["1 star reviews percentage"]),
                    "Company VADER Sentiment Score": float(row["Company VADER Sentiment Score"]) if row["Company VADER Sentiment Score"] else None,
                    "Company TextBlob Sentiment Score": float(row["Company TextBlob Sentiment Score"]) if row["Company TextBlob Sentiment Score"] else None,
                    "Company BERT Sentiment Score": float(row["Company BERT Sentiment Score"]) if row["Company BERT Sentiment Score"] else None,
                    "Review Stars": int(float(row["Review Stars"].strip())) if row.get("Review Stars") and row["Review Stars"].strip().replace(".", "", 1).isdigit() else None,
                    "Review Comment": row["Review Comment"],
                    "Company Response": row.get("Company Response", None),
                    "VADER Sentiment Score": row["VADER Sentiment Score"],
                    "TextBlob Sentiment Score": row["TextBlob Sentiment Score"],
                    "BERT Sentiment Score": row["BERT Sentiment Score"],
                    "Review Length": int(row["Review Length"]) if row["Review Length"] and row["Review Length"].isdigit() else None
                }
            }

        # Process rows and insert into Elasticsearch in bulk
        success, errors = helpers.bulk(es, (process_row(row) for row in reader), chunk_size=500, raise_on_error=False)

        # Handle potential errors
        if errors:
            with open("failed_docs_flat.json", "w", encoding="utf-8") as f:
                json.dump(errors, f, indent=4)
            print("⚠️ Some records failed to import. Check failed_docs_flat.json for details.")

    print("✅ Flat data import completed successfully.")

# Example usage
# I added this condition to ensure that I have flexibility to run the whole .py code including
# the file generation or run only elastic connection and update separately importing the 2 elastic
# update methods (setup_flat_index() & import_to_elastic_flat("trustpilot_reviews_combined.csv")) 
if __name__ == "__main__":

    input_file = "trustpilot_reviews.csv"

    # This will hold one (num_reviews, trustscore) pair per company
    company_data = {}

    with open(input_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row["Company"].strip()

            # Clean up and try to parse "Number of Reviews"
            num_reviews_raw = row["Number of Reviews"].replace(",", "").strip()
            try:
                num_reviews = int(num_reviews_raw)
            except (ValueError, TypeError):
                continue  # skip invalid rows

            # Trustscore is optional here, but we can keep it for Combined_Score later
            trustscore_raw = row.get("Trustscore", "").strip()
            try:
                trustscore = float(trustscore_raw) if trustscore_raw else None
            except ValueError:
                trustscore = None  # keep as None if not parsable

            if company not in company_data:
                company_data[company] = {
                    "Number of Reviews": num_reviews,
                    "Trustscore": trustscore
                }

    # The value of C should be chosen based on your dataset using either a median or mean calculation, C is used in above process_reviews method
    # at step 6 where a Bayesian-like formnula with shrinkage towars 0 (trustscore * num_reviews / (num_reviews + C)) is used to calculate the combined_score.
    # This is used to avoid a skewed trustscore for companies with smaller num_reviews by taking into account also the number of reviews 
    # Recommendation for C Calculation:
    #     Median is preferred over mean because the mean would be skewed by the outlier (1500 reviews).
    #     The median provides a better central value for typical companies.
    # Companies with a high number of reviews are mostly rated by their actual score.
    # Companies with a low number of reviews are adjusted towards the average rating across all companies.
    # Extract just the review counts to calculate C
    review_counts = [data["Number of Reviews"] for data in company_data.values()]
    C = statistics.median(review_counts)

    # print(f"📌 Calculated C Value (Median of Reviews): {C}")  # Temporary debug output

    process_reviews("trustpilot_reviews.csv", "trustpilot_reviews_with_sentiment_vader.csv", compute_vader_sentiment, "VADER Sentiment Score")
    process_reviews("trustpilot_reviews.csv", "trustpilot_reviews_with_sentiment_textblob.csv", compute_textblob_sentiment, "TextBlob Sentiment Score")
    process_reviews("trustpilot_reviews.csv", "trustpilot_reviews_with_sentiment_bert.csv", compute_bert_sentiment_batch, "BERT Sentiment Score")
    
    merge_sentiment_csvs()

# Initialize Elasticsearch connection
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="./ca/ca.crt",
    basic_auth=("elastic", "datascientest")
)

# Check if Elasticsearch is reachable; if not exit program gracefully

if not es.ping():
    print("❌ ERROR: Cannot connect to Elasticsearch. Is the Docker container running?")
    sys.exit(1)  # Stop execution immediately

print("✅ Successfully connected to Elasticsearch!")

# Uncomment when ready to import
# setup_flat_index()
# import_to_elastic_flat("trustpilot_reviews_combined.csv")
