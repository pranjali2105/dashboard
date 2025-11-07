# Save this in /pages/tab1_overview.py

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# This makes it the home page
dash.register_page(__name__, name='Executive Overview', path='/')

# --- 1. Load Data & Calculate KPIs ---
try:
    df = pd.read_csv("netflix.csv")
except FileNotFoundError:
    layout = html.Div([
        html.H1("Error: netflix.csv not found", className="text-danger"),
        html.P("Please make sure 'netflix.csv' is in your main 'Dashboard' folder.")
    ])
    raise FileNotFoundError("netflix.csv not found.")

# --- KPI Calculations ---
total_titles = len(df)

# IMPORTANT: Drop rows where date_added is blank
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df = df.dropna(subset=['date_added']) # This cleans data for all charts

df['year_added'] = df['date_added'].dt.year
most_recent_year = df['year_added'].max()
titles_last_2_years = len(df[df['year_added'] >= (most_recent_year - 1)])

movie_count = len(df[df['type'] == 'Movie'])
tv_show_count = len(df[df['type'] == 'TV Show'])

# --- 2. Create Figures for Charts ---

# Helper function to style all figures
def style_figure_dark(fig):
    fig.update_layout(
        template="plotly_dark",
        font_color="white",
        paper_bgcolor="rgba(0,0,0,0)", # Transparent background
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text='' # Clean up legend title
    )
    return fig

# --- Chart 1: Titles Added Over Time (Bar Chart) ---
df_titles_by_year = df.groupby('year_added').size().reset_index(name='count').tail(10)
fig_titles_over_time = px.bar(
    df_titles_by_year,
    x='year_added',
    y='count',
    title="Titles Added in the Last 10 Years",
    color_discrete_sequence=['#E50914'] # Makes bar red
)
fig_titles_over_time = style_figure_dark(fig_titles_over_time)


# --- Chart 2: Geographic Diversity Chart ---
df_clean = df.dropna(subset=['country'])
df_clean['country'] = df_clean['country'].str.strip()
df_exploded = df_clean.assign(country=df_clean['country'].str.split(', ')).explode('country')
df_exploded['country'] = df_exploded['country'].str.strip()
top_10_countries = df_exploded['country'].value_counts().head(10).reset_index()
top_10_countries.columns = ['country', 'count']
fig_geo_diversity = px.bar(
    top_10_countries,
    y='country',
    x='count',
    title="Geographic Diversity (Top 10 Countries)",
    orientation='h',
    color_discrete_sequence=['#E50914'] # Makes bar red
)
fig_geo_diversity.update_layout(yaxis={'categoryorder':'total ascending'})
fig_geo_diversity = style_figure_dark(fig_geo_diversity)


# --- Chart 3: Rating Pie Chart ---
df_rating = df.dropna(subset=['rating'])
rating_counts = df_rating['rating'].value_counts()
top_5_ratings = rating_counts.head(5).index
df_rating['rating_grouped'] = df_rating['rating'].apply(lambda x: x if x in top_5_ratings else 'Other')
fig_rating_pie = px.pie(
    df_rating,
    names='rating_grouped',
    title="Content Breakdown by Rating",
    color_discrete_sequence=px.colors.sequential.Reds_r # Hues of red
)
fig_rating_pie = style_figure_dark(fig_rating_pie)

# --- Chart 4: Seasonal Trend Line Plot ---
df['month_num'] = df['date_added'].dt.month
df['month_abbr'] = df['date_added'].dt.strftime('%b')
df_seasonal = df.groupby(['month_num', 'month_abbr', 'type']).size().reset_index(name='count')
df_seasonal = df_seasonal.sort_values('month_num')
fig_seasonal_trend = px.line(
    df_seasonal,
    x='month_abbr',
    y='count',
    color='type',
    title="Seasonal Addition Trends",
    markers=True,
    # --- THIS IS THE FIX ---
    color_discrete_map={
        'Movie': '#F08080',  # Light Red
        'TV Show': '#E50914' # Proper Netflix Red
    }
)
fig_seasonal_trend = style_figure_dark(fig_seasonal_trend)


# --- 3. Helper Function to create KPI Card ---
def create_kpi_card(title, value, color):
    return dbc.Card(
        [
            html.H3(title, className="card-title"),
            html.H2(f"{value:,}", className="card-text"),
        ],
        body=True,
        color=color,
        inverse=True,
        className="mb-4"
    )

# --- 4. Define Page Layout (Updated) ---
layout = dbc.Container([
    html.H1("📁 Executive Overview", className="mt-4 netflix-glow"),

    # Row 1: KPI Cards
    dbc.Row([
        dbc.Col(create_kpi_card("Total Titles", total_titles, "dark"), md=3),
        dbc.Col(create_kpi_card("Added (Last 2 Yrs)", titles_last_2_years, "dark"), md=3),
        dbc.Col(create_kpi_card("Total Movies", movie_count, "dark"), md=3),
        dbc.Col(create_kpi_card("Total TV Shows", tv_show_count, "dark"), md=3),
    ], className="mt-4"),

    # Row 2: Summary Charts
    dbc.Row([
        dbc.Col(dcc.Graph(id="titles-over-time", figure=fig_titles_over_time), width=6),
        dbc.Col(dcc.Graph(id="geo-diversity-chart", figure=fig_geo_diversity), width=6),
    ], className="mt-4"),
    
    # Row 3: Pie and Line Charts
    dbc.Row([
        dbc.Col(dcc.Graph(id="rating-pie-chart", figure=fig_rating_pie), width=6),
        dbc.Col(dcc.Graph(id="seasonal-trend-chart", figure=fig_seasonal_trend), width=6),
    ], className="mt-4"),

    # Row 4: Key Findings
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                    html.H4("Key Findings & Recommendations", className="card-title"),
                    dcc.Markdown(
"""
* **Insight 1:** The number of titles added per year has peaked and is now declining.
* **Insight 2:** The library is heavily concentrated in a few key countries, primarily the United States.
* **Insight 3:** The majority of content is targeted at mature audiences (e.g., TV-MA, R).
* **Insight 4:** There is a clear seasonal spike in content additions, peaking in January and July.
* **Recommendation:** Focus on acquiring high-quality TV Shows in emerging markets, particularly during off-peak months.
"""
                    )
                ],
                body=True,
                color="dark",
                inverse=True,
                className="mt-4"
            )
        )
    ], className="mb-4")
], fluid=True)