from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess

app = FastAPI()

@app.on_event("startup")
def start_dash():
    subprocess.Popen(["python", "graph.py"])

def fig_to_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def load_data():
    df = pd.read_csv('trustpilot_reviews_combined.csv')
    df_unique = df.drop_duplicates(subset='Company')
    return df_unique

def generate_figures(df):
    max_vals = {
        'reviews': df['Number of Reviews'].max(),
        'trustscore': df['Trustscore'].max(),
        'combined': df['Combined_Score'].max(),
        'stars': df[[col for col in df.columns if 'stars reviews percentage' in col]].sum(axis=1).max(),
        'vader': df['VADER Sentiment Score'].max(),
        'textblob': df['TextBlob Sentiment Score'].max(),
        'bert': df['BERT Sentiment Score'].max()
    }

    fig1 = px.bar(df, x='Company', y='Number of Reviews', title='Number of reviews per Company')
    fig1.update_layout(yaxis=dict(range=[0, max_vals['reviews']]))

    fig2 = px.bar(df, x='Company', y='Trustscore', title='Trustscore')
    fig2.update_layout(yaxis=dict(range=[0, max_vals['trustscore']]))

    fig3 = px.bar(df, x='Company', y='Combined_Score', title='Combined Score')
    fig3.update_layout(yaxis=dict(range=[0, max_vals['combined']]))

    fig4 = px.scatter(df, x='Number of Reviews', y='Trustscore', color='Company', title='Trustscore and Number of reviews')

    fig5 = go.Figure(data=[
        go.Bar(name=stars, x=df['Company'], y=df[stars])
        for stars in ['5 stars reviews percentage', '4 stars reviews percentage',
                      '3 stars reviews percentage', '2 stars reviews percentage',
                      '1 star reviews percentage']
    ])
    fig5.update_layout(barmode='stack', title='Stars distribution per Company', yaxis=dict(range=[0, max_vals['stars']]))

    fig6 = px.bar(df, x='Company',
                  y=['VADER Sentiment Score', 'TextBlob Sentiment Score', 'BERT Sentiment Score'],
                  title='Sentiment analysis scores per Company', barmode='group')
    fig6.update_layout(yaxis=dict(range=[-1, max(max_vals['vader'], max_vals['textblob'], max_vals['bert'])]))

    return [fig1, fig2, fig3, fig4, fig5, fig6]

def render_html(title, figs):
    sections = "".join(
        f"<h2>{fig.layout.title.text}</h2>{fig_to_html(fig)}" for fig in figs
    )
    return f"""
    <html>
        <head><title>{title}</title></head>
        <body>
            <h1>{title}</h1>
            {sections}
        </body>
    </html>
    """

@app.get("/company/{company_name}", response_class=HTMLResponse)
def get_company_graphs(company_name: str):
    df = load_data()
    df['normalized_company'] = df['Company'].str.lower().str.strip()
    normalized_name = company_name.lower().strip()
    matching = df[df['normalized_company'].str.contains(normalized_name)]

    if matching.empty:
        available = df['Company'].sort_values().to_list()
        return HTMLResponse(content=f"<html><body><h1>Company not found</h1><p>Available companies: {', '.join(available)}</p></body></html>")

    figs = generate_figures(matching)
    return HTMLResponse(content=render_html(f"Graphs for {company_name}", figs))

@app.get("/companies", response_class=HTMLResponse)
def get_all_company_graphs():
    df = load_data()
    figs = generate_figures(df)
    return HTMLResponse(content=render_html("Graphs for All Companies", figs))
