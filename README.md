Hello friends.



I uploaded in GitHub in the eTL (Transform & Load) folder:

the Transformed and enriched trustpilot_reviews_combined.csv file that is used to Load into Elastic. The Load is already completed.
The 2 versions of the python code for 2 type of data structure / Indices (how the document database Elasticsearch calls them):

suply_chain_flat_index.py: for flat index where every row represents a document knowing that there is 1-to-many relationship between Companies and reviews, consequently having multiple rows which are loaded into Elastic as a flat document structure
suply_chain_nested_index.py: for nested index where each company is a document that has subdocuments (reviews) nested underneath it
a set of example kibana queries (KIBANA QUERIES.docx) that you may run in the kibana dashboard - let me know when you want to play a little with the queries and I will have the env. up
