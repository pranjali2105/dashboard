# Save this in the /pages/ folder as tab6_talent.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash_ag_grid as dag  # Import dash_ag_grid

dash.register_page(__name__, name='Creator & Talent Hub', path='/talent-hub')

# --- 1. Load Pre-processed Data ---
# These files were created by prepare_talent_data.py
try:
    df_portfolio = pd.read_parquet('talent_portfolio.parquet')
    df_edges = pd.read_parquet('talent_edges.parquet')
    df_rising_stars = pd.read_parquet('rising_stars.parquet')
except FileNotFoundError:
    layout = html.Div([
        html.H1("Error: Data files not found."),
        html.P("Please run 'prepare_talent_data.py' first to generate the required .parquet files.")
    ])
    # Stop here if files are missing
    raise FileNotFoundError("Missing .parquet files. Run 'prepare_talent_data.py'.")


# --- 2. Create Master Lists for Controls ---
TALENT_LIST = sorted(df_portfolio['name'].unique())


# --- 3. Define Page Layout ---
layout = dbc.Container([
    # FIX: Added 'className="text-light"'
    html.H1("🎬 Creator & Talent Hub", className="netflix-glow"),
    
    dbc.Tabs([
        # --- TAB 1: TALENT EXPLORER (Features 1-4) ---
        dbc.Tab(label='Talent Explorer', children=[
            dbc.Row([
                # -- Left Column: Controls & Portfolio --
                dbc.Col([
                    # FIX: Added 'className="text-light"'
                    html.H4("Talent Search", className="text-light"),
                    dcc.Dropdown(
                        id='talent-search-dropdown',
                        options=[{'label': name, 'value': name} for name in TALENT_LIST],
                        placeholder="Search for an Actor or Director...",
                    ),
                    
                    # FIX: Added 'className="mt-4 text-light"'
                    html.H4("Portfolio Analysis", className="mt-4 text-light"),
                    # FIX: Added 'color="dark"'
                    dbc.Card(id='portfolio-stats-card', body=True, className="mb-3", color="dark"),
                    
                    # FIX: Added 'className="ag-theme-alpine-dark"'
                    dag.AgGrid(
                        id='portfolio-table-grid',
                        className="ag-theme-alpine-dark", 
                        style={"height": "300px"},
                        columnDefs=[
                            {"field": "title", "sortable": True, "filter": True},
                            {"field": "role", "sortable": True, "filter": "agSetColumnFilter"},
                            {"field": "release_year", "sortable": True},
                        ],
                        defaultColDef={"resizable": True},
                        dashGridOptions={"domLayout": "autoHeight"},
                    ),
                    
                    # FIX: Added 'className="mt-4 text-light"'
                    html.H4("Portfolio Diversity", className="mt-4 text-light"),
                    dcc.Graph(id='diversity-pie-chart')

                ], width=5),
                
                # -- Right Column: Network Vis --
                dbc.Col([
                    # FIX: Added 'className="text-light"'
                    html.H4("Collaboration Network", className="text-light"),
                    dbc.Alert("Shows this person and their direct collaborators.", color="info"),
                    cyto.Cytoscape(
                        id='collaboration-network-graph',
                        layout={'name': 'cose'},
                        style={'width': '100%', 'height': '700px'},
                        stylesheet=[
                            # Make node text white and larger
                            {'selector': 'node', 'style': {'label': 'data(label)', 'font-size': '10px', 'color': 'white'}},
                            {'selector': 'edge', 'style': {'line-color': '#ccc', 'width': 'data(weight)'}},
                            # This uses the red from your previous code
                            {'selector': '.center-node', 'style': {'background-color': "#d20f0f", 'color': 'white'}},
                        ]
                    )
                ], width=7)
            ])
        ]),
        # --- TAB 2: RISING STARS (Feature 5) ---
        dbc.Tab(label='Rising Stars', children=[
            # FIX: Added 'className="mt-3 text-light"'
            html.H4("Rising Stars Identification", className="mt-3 text-light"),
            dbc.Alert("Talent with the highest positive growth in new titles over the past 5 years.", color="info"),
            
            # FIX: Added 'className="ag-theme-alpine-dark"'
            dag.AgGrid(
                id='rising-stars-grid',
                className="ag-theme-alpine-dark",
                rowData=df_rising_stars.to_dict('records'),
                columnDefs=[
                    {"field": "name", "sortable": True, "filter": True},
                    {"field": "growth_slope", "headerName": "Growth Trend Score", "sortable": True, "valueFormatter": {"function": "d3.format('.2f')(params.value)"}},
                    {"field": "total_recent_titles", "headerName": "Total Recent Titles", "sortable": True},
                ],
                defaultColDef={"sortable": True, "resizable": True},
                style={"height": "600px", "width": "100%"},
            )
        ])
    ])
], fluid=True)

# --- 4. Define Callbacks ---
@dash.callback(
    Output('portfolio-stats-card', 'children'),
    Output('portfolio-table-grid', 'rowData'),
    Output('diversity-pie-chart', 'figure'),
    Output('collaboration-network-graph', 'elements'),
    Input('talent-search-dropdown', 'value')
)
def update_talent_page(selected_name):
    if not selected_name:
        # FIX: Added template="plotly_dark" to the default empty fig
        fig_pie = px.pie(title="Select a name")
        fig_pie.update_layout(template="plotly_dark", title_font_color="white")
        return ["Select a name", [], fig_pie, []]

    # --- 1. Filter for Portfolio (Features 3 & 4) ---
    df_person_portfolio = df_portfolio[df_portfolio['name'] == selected_name]
    
    # --- 2. Build Portfolio Stats Card (Feature 3) ---
    total_titles = df_person_portfolio['show_id'].nunique()
    first_year = df_person_portfolio['release_year'].min()
    last_year = df_person_portfolio['release_year'].max()
    roles = ", ".join(df_person_portfolio['role'].unique())
    
    stats_card = [
        html.H5(selected_name, className="card-title"),
        html.P(f"Roles: {roles}", className="card-text"),
        html.P(f"Total Titles: {total_titles}", className="card-text"),
        html.P(f"Active: {first_year} - {last_year}", className="card-text"),
    ]
    
    # --- 3. Build Portfolio Table (Feature 3) ---
    portfolio_table_data = df_person_portfolio[['title', 'role', 'release_year']].drop_duplicates().to_dict('records')

    # --- 4. Build Diversity Pie Chart (Feature 4) ---
    df_country_count = df_person_portfolio.groupby('country').size().reset_index(name='count')
    fig_pie = px.pie(
        df_country_count,
        names='country',
        values='count',
        title="Portfolio by Country of Production"
    )
    # FIX: Added template="plotly_dark" and 'font_color'
    fig_pie.update_layout(
        showlegend=False, 
        margin=dict(t=30, l=10, r=10, b=10),
        template="plotly_dark",
        font_color="white" # Ensures all text in the plot is white
    )

    # --- 5. Build Network Graph (Feature 2) ---
    df_person_edges = df_edges[
        (df_edges['source'] == selected_name) | (df_edges['target'] == selected_name)
    ]
    collaborators = set(df_person_edges['source']).union(set(df_person_edges['target']))
    collaborators.discard(selected_name)
    
    elements = []
    elements.append({'data': {'id': selected_name, 'label': selected_name}, 'classes': 'center-node'})
    for name in collaborators:
        elements.append({'data': {'id': name, 'label': name}})
    for _, row in df_person_edges.iterrows():
        elements.append({
            'data': {
                'source': row['source'],
                'target': row['target'],
                'weight': row['weight'] / 5 
            }
        })

    return stats_card, portfolio_table_data, fig_pie, elements
