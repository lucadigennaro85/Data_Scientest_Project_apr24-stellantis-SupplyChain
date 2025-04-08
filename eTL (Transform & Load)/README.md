Hello friends.



I uploaded in GitHub in the eTL (Transform & Load) folder:

1. the Transformed and enriched trustpilot_reviews_combined.csv file that is used to Load into Elastic. The Load is already completed.
3. The 2 versions of the python code for 2 type of data structure / Indices (how the document database Elasticsearch calls them):
   a) suply_chain_flat_index.py: for flat index where every row represents a document knowing that there is 1-to-many relationship between Companies and reviews, consequently having multiple rows which are loaded
   into Elastic as a flat document structure
   b) suply_chain_nested_index.py: for nested index where each company is a document that has subdocuments (reviews) nested underneath it
4.	a set of example kibana queries (KIBANA QUERIES.docx) that you may run in the kibana dashboard - let me know when you want to play a little with the queries and I will have the env. up
a.	access kibana dashboard at: http://<IP_address>:5601
b.	Login using the id and password from lesson 1: user id: elastic, password: datascientest
c.	Click “Explore on my own”
d.	Go to the hamburger menu (3 lines) upper left and scroll down and choose Dev Tools
e.	Dismiss the “Welcome to Console”
f.	Now you are in the env: delete the default query in the Console: click in the console CTRL A and then <Delete or Backspace>
g.	copy / paste from the KIBANA QUERIES.docx queries into the kibana dashboard and then use the right upper corner arrow (right side of the query panel) to run the query
8. a README.md file - with this info.
