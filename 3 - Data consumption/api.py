from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess

app = FastAPI()

@app.on_event("startup")
def start_dash():
    subprocess.Popen(["python", "3 - Data consumption/graph.py"])

def fig_to_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

@app.get("/company/{company_name}", response_class=HTMLResponse)
def get_company_graphs(company_name: str):
    df = pd.read_csv('3 - Data consumption/trustpilot_reviews_combined.csv')
    df_unique = df.drop_duplicates(subset='Company')
    
    # Normalize company names for case-insensitive and space-insensitive matching
    df_unique['normalized_company'] = df_unique['Company'].str.lower().str.strip()
    normalized_company_name = company_name.lower().strip()
    
    # Find matching companies
    matching_companies = df_unique[df_unique['normalized_company'].str.contains(normalized_company_name)]
    
    if matching_companies.empty:
        available_companies = df_unique['Company'].sort_values().to_list()
        return HTMLResponse(content=f"<html><body><h1>Company not found</h1><p>Available companies: {', '.join(available_companies)}</p></body></html>")
    
    max_reviews = df_unique['Number of Reviews'].max()
    max_trustscore = df_unique['Trustscore'].max()
    max_combinedscore = df_unique['Combined_Score'].max()
    max_5stars = df_unique['5 stars reviews percentage'].max()
    max_4stars = df_unique['4 stars reviews percentage'].max()
    max_3stars = df_unique['3 stars reviews percentage'].max()
    max_2stars = df_unique['2 stars reviews percentage'].max()
    max_1star = df_unique['1 star reviews percentage'].max()
    max_stars = max_5stars + max_4stars + max_3stars + max_2stars + max_1star
    max_vader = df_unique['VADER Sentiment Score'].max()
    max_textblob = df_unique['TextBlob Sentiment Score'].max()
    max_bert = df_unique['BERT Sentiment Score'].max()

    fig1 = px.bar(matching_companies, x='Company', y='Number of Reviews', title='Number of reviews per Company')
    fig1.update_layout(yaxis=dict(range=[0, max_reviews]))

    fig2 = px.bar(matching_companies, y='Trustscore', x='Company', title='Trustscore')
    fig2.update_layout(yaxis=dict(range=[0, max_trustscore]))

    fig3 = px.bar(matching_companies, y='Combined_Score', x='Company', title='Combined Score')
    fig3.update_layout(yaxis=dict(range=[0, max_combinedscore]))

    fig4 = px.scatter(matching_companies, x='Number of Reviews', y='Trustscore', color='Company', title='Trustscore and Number of reviews')

    fig5 = go.Figure(data=[
        go.Bar(name='5 Stars', x=matching_companies['Company'], y=matching_companies['5 stars reviews percentage']),
        go.Bar(name='4 Stars', x=matching_companies['Company'], y=matching_companies['4 stars reviews percentage']),
        go.Bar(name='3 Stars', x=matching_companies['Company'], y=matching_companies['3 stars reviews percentage']),
        go.Bar(name='2 Stars', x=matching_companies['Company'], y=matching_companies['2 stars reviews percentage']),
        go.Bar(name='1 Star', x=matching_companies['Company'], y=matching_companies['1 star reviews percentage'])
    ])
    fig5.update_layout(barmode='stack', title='Stars distribution per Company', yaxis=dict(range=[0, max_stars]))

    fig6 = px.bar(df_unique, x='Company', y=['VADER Sentiment Score', 'TextBlob Sentiment Score', 'BERT Sentiment Score'], title='Sentiment analysis scores per Company', barmode='group')    
    fig6.update_layout(yaxis=dict(range=[-1, max(max_vader, max_textblob, max_bert)]))

    html_content = f"""
    <html>
        <head><title>Graphs for {company_name}</title></head>
        <body>
            <h1>Graphs for {company_name}</h1>
            <h2>Number of Reviews</h2>
            {fig_to_html(fig1)}
            <h2>Trustscore</h2>
            {fig_to_html(fig2)}
            <h2>Combined Score</h2>
            {fig_to_html(fig3)}
            <h2>Trustscore and Number of Reviews</h2>
            {fig_to_html(fig4)}
            <h2>Stars Distribution</h2>
            {fig_to_html(fig5)}
            <h2>Sentiment Analysis Scores</h2>
            {fig_to_html(fig6)}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

