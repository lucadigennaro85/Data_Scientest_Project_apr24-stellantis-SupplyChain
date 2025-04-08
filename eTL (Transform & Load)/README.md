Hello friends.



I uploaded in GitHub in the eTL (Transform & Load) folder:

1. the Transformed and enriched trustpilot_reviews_combined.csv file that is used to Load into Elastic. The Load is already completed.
3. The 2 versions of the python code for 2 type of data structure / Indices (how the document database Elasticsearch calls them):
   a) suply_chain_flat_index.py: for flat index where every row represents a document knowing that there is 1-to-many relationship between Companies and reviews, consequently having multiple rows which are loaded into Elastic as a flat document structure
   b) suply_chain_nested_index.py: for nested index where each company is a document that has subdocuments (reviews) nested underneath it
4.	a set of example kibana queries (KIBANA QUERIES.docx) that you may run in the kibana dashboard - let me know when you want to play a little with the queries and I will have the env. up
5.	access kibana dashboard at: http://<IP_address>:5601
6.	Login using the id and password from lesson 1: user id: elastic, password: datascientest
7.	Click “Explore on my own”
8.	Go to the hamburger menu (3 lines) upper left and scroll down and choose Dev Tools
9.	Dismiss the “Welcome to Console”
10.	Now you are in the env: delete the default query in the Console: click in the console CTRL A and then <Delete or Backspace>
11.	copy / paste from the KIBANA QUERIES.docx queries into the kibana dashboard and then use the right upper corner arrow (right side of the query panel) to run the query
12.	README.md file - with this info.
