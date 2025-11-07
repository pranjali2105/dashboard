import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
# --- MODIFICATION 1: 'dash_cytoscape' import removed ---
# import dash_cytoscape as cyto 
import dash_ag_grid as dag  # Import dash_ag_grid

dash.register_page(__name__, name='Creator & Talent Hub', path='/talent-hub')

# --- 1. Load Pre-processed Data ---
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
    html.H1("🎬 Creator & Talent Hub", className="netflix-glow"),
    
    dbc.Tabs([
        # --- TAB 1: TALENT EXPLORER (Features 1-4) ---
        dbc.Tab(label='Talent Explorer', children=[
            dbc.Row([
                # -- Left Column: Controls & Portfolio --
                dbc.Col([
                    html.H4("Talent Search", className="text-light"),
                    dcc.Dropdown(
                        id='talent-search-dropdown',
                        options=[{'label': name, 'value': name} for name in TALENT_LIST],
                        placeholder="Search for an Actor or Director...",
                    ),
                    
                    html.H4("Portfolio Analysis", className="mt-4 text-light"),
                    dbc.Card(id='portfolio-stats-card', body=True, className="mb-3", color="dark"),
                    
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
                    
                    html.H4("Portfolio Diversity", className="mt-4 text-light"),
                    dcc.Graph(id='diversity-pie-chart')

                ], width=5),
                
                # -- Right Column: Network Vis --
                dbc.Col([
                    html.H4("Collaboration Network", className="text-light"),
                    dbc.Alert("Shows this person and their direct collaborators.", color="info"),
                    
                    # --- MODIFICATION 2: Cytoscape component removed and replaced ---
                    # The 'cyto.Cytoscape' component was removed to avoid the error.
                    dbc.Alert(
                        "Network graph feature is temporarily disabled due to hosting resource limitations.",
                        color="warning",
                        className="mt-3"
                    )
                    # --- End of MODIFICATION 2 ---

                ], width=7)
            ])
        ]),
        # --- TAB 2: RISING STARS (Feature 5) ---
        dbc.Tab(label='Rising Stars', children=[
            html.H4("Rising Stars Identification", className="mt-3 text-light"),
            dbc.Alert("Talent with the highest positive growth in new titles over the past 5 years.", color="info"),
            
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
    # --- MODIFICATION 3: The Output for the network graph has been removed ---
    # Output('collaboration-network-graph', 'elements'), 
    Input('talent-search-dropdown', 'value')
)
def update_talent_page(selected_name):
    if not selected_name:
        fig_pie = px.pie(title="Select a name")
        fig_pie.update_layout(template="plotly_dark", title_font_color="white")
        # --- MODIFICATION 4: Removed the 4th item from the default return list ---
        return ["Select a name", [], fig_pie]

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
    fig_pie.update_layout(
        showlegend=False, 
        margin=dict(t=30, l=10, r=10, b=10),
        template="plotly_dark",
        font_color="white"
    )

    # --- MODIFICATION 5: The entire network graph logic block has been deleted ---
    # (The block that started with "# --- 5. Build Network Graph (Feature 2) ---")
    # --- End of MODIFICATION 5 ---

    # --- MODIFICATION 6: Removed 'elements' from the final return statement ---
    return stats_card, portfolio_table_data, fig_pie
