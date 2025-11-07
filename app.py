import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# 1. Initialize the Dash App
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.CYBORG,
        # This loads the AgGrid dark theme
        "https://cdn.jsdelivr.net/npm/ag-grid-community@31.1.1/styles/ag-theme-alpine-dark.css"
    ]
)

# --- CRITICAL CHANGE 1: Define the Flask Server Object ---
# Gunicorn needs access to the underlying Flask server object.
# We assign the Dash app's server to a variable named 'server'.
server = app.server 
# --------------------------------------------------------

navbar = dbc.NavbarSimple(
    dbc.Nav(
        [
            dbc.NavLink(page['name'], href=page['relative_path'], active="exact")
            for page in dash.page_registry.values()
        ],
        pills=True,
    ),
    brand="Strategic Dashboard",
    dark=True,
    color="danger", 
)

# 3. Define the main App Layout
app.layout = dbc.Container(
    [
        navbar,
        dash.page_container
    ],
    fluid=True,
)

# 4. Run the App (Modified for Production)
if __name__ == '__main__':
    # When running locally, use this command:
    app.run(debug=True, port=8052)
    
# NOTE: The production server (Gunicorn on Render) ignores the 'if __name__ == "__main__":' 
# block and instead looks directly for the 'server' object defined above.
