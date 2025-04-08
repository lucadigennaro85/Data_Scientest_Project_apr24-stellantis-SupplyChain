import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('eTL (Transform & Load)/trustpilot_reviews_combined.csv')
df_unique = df.drop_duplicates(subset='Company')

max_reviews = df_unique['Number of Reviews'].max()
max_trustscore = df_unique['Trustscore'].max()
max_5stars = df_unique['5 stars reviews percentage'].max()
max_4stars = df_unique['4 stars reviews percentage'].max()
max_3stars = df_unique['3 stars reviews percentage'].max()
max_2stars = df_unique['2 stars reviews percentage'].max()
max_1star = df_unique['1 star reviews percentage'].max()
max_stars = max_5stars + max_4stars + max_3stars + max_2stars + max_1star
max_vader = df_unique['VADER Sentiment Score'].max()
max_textblob = df_unique['TextBlob Sentiment Score'].max()
max_bert = df_unique['BERT Sentiment Score'].max()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Trustpilot dashboard"),
    
    dcc.Graph(id='bar-chart-reviews'),
    dcc.Graph(id='bar-chart-trustscore'),
    dcc.Graph(id='scatter-plot-trustscore-reviews'),
    dcc.Graph(id='bar-chart-stars'),
    dcc.Graph(id='bar-chart-sentiment')
])

@app.callback(
    Output('bar-chart-reviews', 'figure'),
    Output('bar-chart-trustscore', 'figure'),
    Output('scatter-plot-trustscore-reviews', 'figure'),
    Output('bar-chart-stars', 'figure'),
    Output('bar-chart-sentiment', 'figure'),
    Input('bar-chart-reviews', 'id')
)
def update_graphs(_):
    fig1 = px.bar(df_unique.sort_values(by='Number of Reviews', ascending=False), x='Company', y='Number of Reviews', title='Number of reviews per Company')
    fig1.update_layout(yaxis=dict(range=[0, max_reviews]))

    fig2 = px.bar(df_unique.sort_values(by='Trustscore', ascending=False), y='Trustscore', x='Company', title='Trustscore')
    fig2.update_layout(yaxis=dict(range=[0, max_trustscore]))

    fig3 = px.scatter(df_unique, x='Number of Reviews', y='Trustscore', color='Company', title='Trustscore and Number of reviews')

    fig4 = go.Figure(data=[
        go.Bar(name='5 Stars', x=df_unique['Company'], y=df_unique['5 stars reviews percentage']),
        go.Bar(name='4 Stars', x=df_unique['Company'], y=df_unique['4 stars reviews percentage']),
        go.Bar(name='3 Stars', x=df_unique['Company'], y=df_unique['3 stars reviews percentage']),
        go.Bar(name='2 Stars', x=df_unique['Company'], y=df_unique['2 stars reviews percentage']),
        go.Bar(name='1 Star', x=df_unique['Company'], y=df_unique['1 star reviews percentage'])
    ])
    fig4.update_layout(barmode='stack', title='Stars distribution per Company', yaxis=dict(range=[0, max_stars]))

    fig5 = px.bar(df_unique, x='Company', y=['VADER Sentiment Score', 'TextBlob Sentiment Score', 'BERT Sentiment Score'], title='Sentiment analysis scores per Company')    
    fig5.update_layout(yaxis=dict(range=[-1, max(max_vader, max_textblob, max_bert)]))

    return fig1, fig2, fig3, fig4, fig5

if __name__ == '__main__':
    app.run(debug=False)