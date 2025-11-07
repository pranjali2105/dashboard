# Save this in /pages/tab2_explorer.py

import dash
from dash import dcc, html, Input, Output, State, ALL
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

dash.register_page(__name__, name='Content Explorer', path='/content-explorer')

# --- 1. Load Data ---
try:
    df = pd.read_csv("netflix.csv")
    df = df.fillna("N/A")
except FileNotFoundError:
    layout = html.Div([
        html.H1("Error: netflix.csv not found", className="text-danger"),
        html.P("Please make sure 'netflix.csv' is in your main 'Dashboard' folder.")
    ])
    raise FileNotFoundError("netflix.csv not found.")

# --- 2. Define Grid Columns ---
columnDefs = [
    {"field": "title", "filter": "agTextColumnFilter", "checkboxSelection": True, "headerCheckboxSelection": True},
    {"field": "type", "filter": "agSetColumnFilter"},
    {"field": "release_year", "filter": "agNumberColumnFilter"},
    {"field": "rating", "filter": "agSetColumnFilter"},
]

# --- 3. Define Page Layout ---
layout = dbc.Container([
    html.H1("🔎  Content Explorer", className="mt-4 netflix-glow"),
    
    # NEW: Add a 'dcc.Store' to hold the currently selected title
    # This is an invisible component that acts as our app's "memory"
    dcc.Store(id='selected-title-store', data=None),

    dbc.Row([
        # --- Left Column: The Grid ---
        dbc.Col([
            dbc.Alert(
                [
                    html.I(className="bi bi-info-circle-fill me-2"),
                    "Search, sort, right-click to export, and select a title to see details."
                ], 
                color="info",
                className="d-flex align-items-center"
            ),
            dag.AgGrid(
                id='content-browser-grid',
                rowData=df.to_dict('records'),
                columnDefs=columnDefs,
                className="ag-theme-alpine-dark",
                defaultColDef={
                    "sortable": True, "filter": True, "resizable": True, "floatingFilter": True,
                },
                dashGridOptions={
                    "pagination": True, "paginationPageSize": 20, "rowSelection": "multiple",
                },
                style={"height": "600px"}
            )
        ], width=8),

        # --- Right Column: The Quick Facts Card ---
        dbc.Col([
            dbc.Card(
                [
                    dbc.CardHeader(html.H4("Quick Facts")),
                    dbc.CardBody(
                        id="quick-facts-card", # This card's content is now driven by the 'dcc.Store'
                        children=[
                            html.P("Select a title from the grid to see details.", className="text-muted")
                        ]
                    )
                ],
                color="dark",
                inverse=True,
                className="sticky-top"
            )
        ], width=4)
    ], className="mt-4")
], fluid=True)


# --- 4. Define Callbacks ---

# Callback 1: Update the Store when a GRID ROW is selected
@dash.callback(
    Output('selected-title-store', 'data'),
    Input('content-browser-grid', 'selectedRows'),
    prevent_initial_call=True # Don't fire when app loads
)
def update_store_from_grid(selected_rows):
    if not selected_rows:
        return dash.no_update # If deselected, do nothing
    
    # Get the title from the selected row and put it in the store
    title = selected_rows[0]['title']
    return title


# Callback 2: Update the Store when a DYNAMIC BUTTON is clicked
@dash.callback(
    Output('selected-title-store', 'data', allow_duplicate=True), # 'allow_duplicate' is key
    Input({'type': 'similar-movie-button', 'title': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_store_from_button(n_clicks):
    # Find out which button was *actually* clicked
    triggered_id_dict = dash.ctx.triggered_id
    
    if not triggered_id_dict:
        return dash.no_update
        
    # The ID is a dictionary like {'type': '...', 'title': 'The Movie'}
    # We just want the title
    title = triggered_id_dict['title']
    return title


# Callback 3: Update the CARD whenever the STORE is updated
# This is the *only* callback that builds the card
@dash.callback(
    Output('quick-facts-card', 'children'),
    Input('selected-title-store', 'data') # Listens only to the store
)
def update_quick_facts_from_store(selected_title):
    # If store is empty, show default message
    if not selected_title:
        return html.P("Select a title from the grid to see details.", className="text-muted")

    # Find the movie's data in the main dataframe
    data_rows = df[df['title'] == selected_title]
    if data_rows.empty:
        return html.P("Error: Title not found.", className="text-danger")
        
    data = data_rows.iloc[0] # Get the first row
    
    # --- Find Similar Titles ---
    selected_rating = data['rating']
    
    same_rating_df = df[
        (df['rating'] == selected_rating) & 
        (df['title'] != selected_title)
    ]
    
    similar_titles_df = same_rating_df.sample(min(3, len(same_rating_df)))
    
    # --- Create CLICKABLE similar titles ---
    similar_titles_components = []
    if not similar_titles_df.empty:
        similar_titles_components.append(html.Hr())
        similar_titles_components.append(html.Strong(f"More with rating '{selected_rating}':"))
        
        # Create a ListGroup of clickable Buttons
        title_list = [
            # NEW
            dbc.ListGroupItem(
                dbc.Button(
                    title,
                    id={'type': 'similar-movie-button', 'title': title},
                    # We removed color="link" and added 'similar-movie-link'
                    className="p-0 text-start similar-movie-link" 
                ),
                className="border-0"
            ) 
            for title in similar_titles_df['title']
        ]
        similar_titles_components.append(dbc.ListGroup(title_list, flush=True, className="mt-2"))
    
    # --- Build the Card Body ---
    card_body = [
        html.H5(data['title'], className="card-title"),
        html.P(f"Type: {data['type']} ({data['release_year']})", className="card-subtitle mb-2"),
        html.Hr(),
        html.Strong("Rating: "),
        html.Span(data['rating']),
        html.Br(),
        html.Strong("Director: "),
        html.Span(data['director']),
        html.Hr(),
        html.Strong("Cast:"),
        html.P(data['cast'], style={'font-size': '0.9em'}),
        html.Hr(),
        html.Strong("Description:"),
        html.P(data['description'], style={'font-size': '0.9em'}),
    ]
    
    card_body.extend(similar_titles_components)
    
    return card_body