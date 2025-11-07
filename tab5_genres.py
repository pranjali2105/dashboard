# Save this in /pages/tab5_genres.py

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='Genre Intelligence', path='/genre-intelligence')

# --- 1. Load Pre-processed Data ---
try:
    df_edges = pd.read_parquet('genre_edges.parquet')
    df_raw = pd.read_csv("netflix.csv")
except FileNotFoundError:
    layout = html.Div([
        html.H1("Error: Data files not found.", className="text-danger"),
        html.P("Please run 'prepare_talent_data.py' to generate .parquet files and ensure 'netflix.csv' is present.")
    ])
    raise FileNotFoundError("Missing data files. Run prep script.")

# --- 2. Create the Co-occurrence Matrix (Feature 2) ---
# We use a pivot table to create the matrix for the heatmap
# We need to add the reverse relationships (source, target) -> (target, source)
df_edges_reverse = df_edges.rename(columns={'source': 'target', 'target': 'source'})
df_edges_full = pd.concat([df_edges, df_edges_reverse])

# Pivot to create the matrix
matrix_df = pd.pivot_table(df_edges_full, values='weight', index='source', columns='target', fill_value=0)

# Create the heatmap figure
fig_heatmap = px.imshow(
    matrix_df,
    title="Genre Co-occurrence Matrix",
    color_continuous_scale='Reds' # Use a red color scale
)
# 
fig_heatmap.update_layout(
    template="plotly_dark",
    font_color="white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)
fig_heatmap.update_xaxes(side="bottom")


# --- 3. Prepare Data for Trend Analysis (Feature 3) ---
df_raw['date_added'] = pd.to_datetime(df_raw['date_added'], errors='coerce')
df_raw['year_added'] = df_raw['date_added'].dt.year
df_raw = df_raw.dropna(subset=['listed_in', 'year_added'])

# Explode the 'listed_in' column
df_genre_trend = df_raw.assign(genre=df_raw['listed_in'].str.split(', ')).explode('genre')
df_genre_trend['genre'] = df_genre_trend['genre'].str.strip()

# Get a list of all unique genres for the filter
ALL_GENRES = sorted(df_genre_trend['genre'].unique())


# --- 4. Define Page Layout ---
layout = dbc.Container([
    html.H1("Genre & Category Intelligence", className="mt-4 netflix-glow"),

    # Row 1: Filters (Feature 1)
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H5("Genre Explorer", className="card-title"),
                    dcc.Dropdown(
                        id='genre-filter-dropdown',
                        options=[{'label': g, 'value': g} for g in ALL_GENRES],
                        value='Dramas', # Set a default
                        placeholder="Select a genre..."
                    )
                ]),
                color="dark"
            )
        ], width=12)
    ], className="mt-4"),
    
    # Row 2: Charts & Analysis
    dbc.Row([
        # Column 1: Trend & Gaps
        dbc.Col([
            # Feature 3: Trend Analysis
            dbc.Card(
                dcc.Graph(id='genre-trend-graph'),
                color="dark",
                body=True,
                className="mb-4"
            ),
            
            # Features 4 & 5: Opportunity / Gap Analysis
            dbc.Card(
                [
                    dbc.CardHeader(html.H4("Competitive Gap Analysis")),
                    dbc.CardBody(id="gap-analysis-card")
                ],
                color="dark",
                inverse=True
            )
        ], width=4),

        # Column 2: Co-occurrence Matrix
        dbc.Col([
            dbc.Card(
                dcc.Graph(id='co-occurrence-heatmap', figure=fig_heatmap, style={'height': '700px'}),
                color="dark",
                body=True
            )
        ], width=8)
    ], className="mt-4 mb-4")
], fluid=True)


# --- 5. Define Callback ---

@dash.callback(
    Output('genre-trend-graph', 'figure'),
    Output('gap-analysis-card', 'children'),
    Input('genre-filter-dropdown', 'value')
)
def update_genre_analysis(selected_genre):
    if not selected_genre:
        return px.line(title="Select a genre"), "Select a genre to see gap analysis."

    # --- 1. Update Trend Graph ---
    df_filtered = df_genre_trend[df_genre_trend['genre'] == selected_genre]
    df_trend = df_filtered.groupby('year_added').size().reset_index(name='count')
    
    fig_trend = px.line(
        df_trend,
        x='year_added',
        y='count',
        title=f"Trend for '{selected_genre}'",
        markers=True,
        color_discrete_sequence=['#E50914'] # Netflix Red
    )
    fig_trend.update_layout(
        template="plotly_dark",
        font_color="white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # --- 2. Update Gap Analysis ---
    try:
        # Find genres that co-occur *least* with the selected one
        co_occurrences = matrix_df.loc[selected_genre].sort_values()
        
        # Filter out self and any with > 0 occurrences
        gaps = co_occurrences[co_occurrences == 0].index.tolist()
        
        # Get the top 5 "most related" genres
        most_related = co_occurrences[co_occurrences > 0].sort_values(ascending=False).head(5).index.tolist()
        
        gap_analysis_content = [
            html.Strong(f"Most Paired With '{selected_genre}':"),
            html.P(", ".join(most_related)),
            html.Hr(),
            html.Strong(f"Untapped Pairings (Gaps) for '{selected_genre}':"),
            html.P(", ".join(gaps[:20]) + "...") # Show the first 20 gaps
        ]
    
    except KeyError:
        # Handle case where genre isn't in the matrix (e.g., only in 1 movie)
        gap_analysis_content = html.P("Not enough co-occurrence data to analyze gaps for this genre.")
    
    return fig_trend, gap_analysis_content