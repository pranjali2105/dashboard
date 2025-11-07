# Save this file as /pages/tab4_geo.py

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import country_converter as coco
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='Geographic Insights', path='/geographic-insights')

# --- 1. Data Preparation ---

try:
    df_raw = pd.read_csv("netflix.csv")

    try:
        df_capitals = pd.read_csv("country-capital-lat-long-population.csv")
    except FileNotFoundError:
        print("WARNING: 'country-capital-lat-long-population.csv' not found. Production Hub map will be empty.")
        df_capitals = pd.DataFrame(columns=['Country', 'Latitude', 'Longitude'])

except FileNotFoundError:
    layout = html.Div([
        html.H1("Error: netflix.csv not found", className="text-danger"),
        html.P("Please make sure 'netflix.csv' is in your main project folder.")
    ])
    raise FileNotFoundError("netflix.csv not found. Cannot build page.")

# --- Process Netflix Data ---
df_clean = df_raw.dropna(subset=['country'])
df_clean['country'] = df_clean['country'].str.strip()
df_exploded = df_clean.assign(country=df_clean['country'].str.split(', ')).explode('country')
df_exploded['country'] = df_exploded['country'].str.strip()

df_agg = df_exploded.groupby('country').size().reset_index(name='title_count')

cc = coco.CountryConverter()
df_agg['iso_alpha'] = cc.convert(df_agg['country'], to='ISO3', not_found=None)
df_agg['continent'] = cc.convert(df_agg['country'], to='continent', not_found=None)

df_agg['mock_population'] = (df_agg['title_count'] * 10000) + abs(df_agg['country'].apply(hash) % 5000)
df_agg['opportunity_score'] = df_agg['mock_population'] / (df_agg['title_count'] + 1)
df_agg = df_agg.dropna(subset=['iso_alpha', 'continent'])

# --- Merge with Capitals ---
df_capitals.rename(columns={"Country": "country", "Latitude": "lat", "Longitude": "lon"}, inplace=True)
df_hubs = pd.merge(df_agg, df_capitals[['country', 'lat', 'lon']], on='country', how='left')
df_hubs = df_hubs.dropna(subset=['lat', 'lon'])

# --- 2. Layout ---
layout = dbc.Container([
    html.H1("🌍 Geographic Insights", className="mt-4 netflix-glow"),

    dbc.Row([
        # --- Left Column: Map + Controls ---
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Map Metric", className="card-title"),
                    dcc.RadioItems(
                        id='map-metric-selector',
                        options=[
                            {'label': ' Total Titles', 'value': 'title_count'},
                            {'label': ' Market Opportunity', 'value': 'opportunity_score'},
                        ],
                        value='title_count',
                        labelStyle={'display': 'block', 'margin-top': '5px'},
                        inputStyle={'margin-right': '5px'}
                    )
                ])
            ], color="dark", className="mb-3"),

            # Fixed-height World Map (scroll fix)
            dcc.Graph(
                id='world-map',
                config={'displayModeBar': False, 'scrollZoom': False},
                style={'height': '70vh', 'minHeight': '500px'}  # 👈 FIXED HEIGHT
            )
        ], width=8),

        # --- Right Column: Tabs ---
        dbc.Col([
            dbc.Tabs([
                # --- Country Comparison ---
                dbc.Tab(label='Country Comparison', children=[
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id='country-comparator-dropdown',
                                options=[{'label': c, 'value': c} for c in sorted(df_agg['country'].unique())],
                                multi=True,
                                placeholder="Select countries to compare..."
                            ),
                        )
                    ], className="mt-4"),
                    dcc.Graph(
                        id='country-comparison-graph',
                        config={'scrollZoom': False},
                        style={'height': '400px'}  # Consistent height
                    )
                ]),

                # --- Regional Deep Dive ---
                dbc.Tab(label='Regional Deep Dive', children=[
                    dbc.Alert("Click a country on the map to see its regional deep dive.", color="info", className="mt-4"),
                    dcc.Graph(
                        id='regional-deep-dive-graph',
                        config={'scrollZoom': False},
                        style={'height': '400px'}
                    )
                ]),

                # --- Production Hubs ---
                dbc.Tab(label='Production Hubs', children=[
                    dcc.Graph(
                        id='production-hub-map',
                        config={'scrollZoom': False},
                        style={'height': '70vh', 'minHeight': '500px'}  # 👈 FIXED HEIGHT TOO
                    )
                ]),
            ])
        ], width=4)
    ], className="mt-4")
], fluid=True)


# --- 3. Styling Helpers ---
def style_bar_chart(fig, title_text):
    fig.update_layout(
        template="plotly_dark",
        font_color="white",
        title_text=title_text,
        margin={"r":10,"t":40,"l":10,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.3)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.3)'),
    )
    return fig

def style_figure_layout(fig, title_text):
    fig.update_layout(
        template="plotly_dark",
        font_color="white",
        title_text=title_text,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar={'len': 0.75, 'yanchor': 'middle', 'y': 0.5}
    )
    return fig

def style_map_geos(fig, map_type="choropleth"):
    if map_type == "scatter":
        fig.update_geos(
            bgcolor="rgba(0,0,0,0)",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.3)",
            showland=True,
            landcolor="rgb(40,40,40)"
        )
    else:
        fig.update_geos(
            bgcolor="rgba(0,0,0,0)",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.3)"
        )
    return fig


# --- 4. Callbacks ---
@dash.callback(
    Output('world-map', 'figure'),
    Input('map-metric-selector', 'value')
)
def update_world_map(selected_metric):
    title = f"Global Distribution of {'Total Titles' if selected_metric == 'title_count' else 'Market Opportunity'}"
    fig = px.choropleth(
        df_agg,
        locations="iso_alpha",
        color=selected_metric,
        hover_name="country",
        hover_data={"iso_alpha": False, "title_count": True, "opportunity_score": ":.2f"},
        color_continuous_scale=px.colors.sequential.Plasma,
        projection="natural earth"
    )
    fig = style_map_geos(fig, map_type="choropleth")
    return style_figure_layout(fig, title)


@dash.callback(
    Output('country-comparison-graph', 'figure'),
    Input('country-comparator-dropdown', 'value')
)
def update_comparison_chart(selected_countries):
    title = "Select countries to compare"
    if not selected_countries:
        fig = px.bar()
        return style_bar_chart(fig, title)

    df_filtered = df_agg[df_agg['country'].isin(selected_countries)]
    fig = px.bar(df_filtered, x='country', y='title_count', color='country')
    return style_bar_chart(fig, 'Comparison of Total Titles')


@dash.callback(
    Output('regional-deep-dive-graph', 'figure'),
    Input('world-map', 'clickData')
)
def update_regional_deep_dive(click_data):
    if click_data is None:
        df_continent = df_agg.groupby('continent')['title_count'].sum().reset_index()
        fig = px.bar(df_continent, x='continent', y='title_count', color='continent')
        return style_bar_chart(fig, 'Titles by Continent (Click a country to see its region)')

    clicked_country_name = click_data['points'][0]['hovertext']
    try:
        clicked_continent = df_agg[df_agg['country'] == clicked_country_name]['continent'].values[0]
    except IndexError:
        return style_bar_chart(px.bar(), 'Click a country to see its regional deep dive')

    df_regional = df_agg[df_agg['continent'] == clicked_continent]
    fig = px.bar(df_regional, x='country', y='title_count', color='country')
    return style_bar_chart(fig, f'Deep Dive: Titles in {clicked_continent}')


@dash.callback(
    Output('production-hub-map', 'figure'),
    Input('map-metric-selector', 'value')
)
def update_hub_map(selected_metric):
    if df_hubs.empty:
        fig = px.bar()
        return style_bar_chart(fig, "Production Hub data not available.")

    fig = px.scatter_geo(
        df_hubs,
        lat='lat',
        lon='lon',
        size=selected_metric,
        color='continent',
        hover_name='country',
        hover_data={'lat': False, 'lon': False, 'title_count': True, 'opportunity_score': ':.2f'},
        projection="natural earth"
    )

    title = f"Top Production Hubs by {'Total Titles' if selected_metric == 'title_count' else 'Market Opportunity'}"
    fig = style_map_geos(fig, map_type="scatter")
    return style_figure_layout(fig, title)
