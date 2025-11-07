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
    color="danger",  # <-- ADD THIS LINE
)



# 3. Define the main App Layout

app.layout = dbc.Container(

[

navbar,

dash.page_container

],

fluid=True,

)



# 4. Run the App

if __name__ == '__main__':

# Make sure this 'if' block is here!
  app.run(debug=True, port=8052)