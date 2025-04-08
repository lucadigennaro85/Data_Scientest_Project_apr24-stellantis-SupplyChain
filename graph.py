import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv('eTL (Transform & Load)/trustpilot_reviews_combined.csv')
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Trustpilot dashboard"),
    
    dcc.Graph(id='bar-chart-reviews'),
    dcc.Graph(id='pie-chart-trustscore'),
    dcc.Graph(id='scatter-plot-trustscore-reviews'),
    dcc.Graph(id='bar-chart-5stars'),
    dcc.Graph(id='bar-chart-sentiment')
])

@app.callback(
    Output('bar-chart-reviews', 'figure'),
    Output('pie-chart-trustscore', 'figure'),
    Output('scatter-plot-trustscore-reviews', 'figure'),
    Output('bar-chart-5stars', 'figure'),
    Output('bar-chart-sentiment', 'figure'),
    Input('bar-chart-reviews', 'id')
)
def update_graphs(_):
    fig1 = px.bar(df, x='Company', y='Number of Reviews', title='Number of reviews per Company')
    fig2 = px.bar(df, y='Trustscore', x='Company', title='Trustscore')
    fig3 = px.scatter(df, x='Number of Reviews', y='Trustscore', color='Company', title='Trustscore and Number of reviews')
    fig4 = px.bar(df, x='Company', y='5 stars reviews percentage', title='5 stars reviews percentage')
    fig5 = px.bar(df, x='Company', y=['VADER Sentiment Score', 'TextBlob Sentiment Score', 'BERT Sentiment Score'], title='Sentiment analysis scores per Company')    
    return fig1, fig2, fig3, fig4, fig5

if __name__ == '__main__':
    app.run(debug=True)