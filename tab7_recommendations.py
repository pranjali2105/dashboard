# Save this as /pages/tab5_recommendations.py

import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='Strategic Recommendations', path='/recommendations')

# --- Custom Netflix-style color palette ---
NETFLIX_RED = "#E50914"
NETFLIX_BLACK = "#141414"
NETFLIX_DARK_GRAY = "#1F1F1F"
TEXT_GRAY = "#B3B3B3"

# --- Layout ---
layout = dbc.Container([
    # --- PAGE HEADER ---
    html.Div([
        html.H1("Strategic Recommendations", style={
            "color": NETFLIX_RED,
            "fontWeight": "bold",
            "fontSize": "2.5rem",
            "textTransform": "uppercase",
            "letterSpacing": "1px",
            "textShadow": "0px 0px 10px rgba(229,9,20,0.6)",
        }),
        html.P(
            "A data-driven strategy blueprint inspired by Netflix’s global content expansion.",
            style={"color": TEXT_GRAY, "fontSize": "1.1rem"}
        ),
        html.Hr(style={"borderTop": f"2px solid {NETFLIX_RED}", "opacity": "0.7"})
    ], className="mt-4 mb-4"),

    dbc.Row([
        # --- LEFT COLUMN: MAIN RECOMMENDATIONS ---
        dbc.Col([
            # --- ACTIONABLE INSIGHTS CARD ---
            dbc.Card([
                dbc.CardHeader(html.H4("Actionable Insights Summary", style={"color": NETFLIX_RED})),
                dbc.CardBody([
                    html.P("Key insights driving Netflix’s strategic roadmap:", style={"color": TEXT_GRAY}),
                    html.Ul([
                        html.Li("🌎 Global content diversification is accelerating — US saturation but strong international growth."),
                        html.Li("🎬 'International TV Shows' dominate releases, highlighting global audience demand."),
                        html.Li("👨‍👩‍👧 Family and Kids genres remain underrepresented, especially across Asia."),
                    ], style={"color": "white"})
                ])
            ], style={
                "backgroundColor": NETFLIX_DARK_GRAY,
                "border": f"1px solid {NETFLIX_RED}",
                "boxShadow": "0 0 12px rgba(229,9,20,0.2)",
                "borderRadius": "15px"
            }, className="mb-4"),

            # --- PRIORITY RECOMMENDATIONS CARD ---
            dbc.Card([
                dbc.CardHeader(html.H4("Priority Recommendations", style={"color": NETFLIX_RED})),
                dbc.CardBody([
                    html.Ol([
                        html.Li("🎥 Invest in **co-productions** across India, South Korea, and Brazil to capitalize on emerging hubs."),
                        html.Li("🚀 Greenlight **3 new flagship Sci-Fi & Fantasy series** to strengthen competitive advantage."),
                        html.Li("🎯 Launch **regional marketing campaigns** in Europe focusing on 'Drama' and 'Thriller' genres."),
                    ], style={"color": "white", "lineHeight": "1.7"})
                ])
            ], style={
                "backgroundColor": NETFLIX_DARK_GRAY,
                "border": f"1px solid {NETFLIX_RED}",
                "boxShadow": "0 0 12px rgba(229,9,20,0.2)",
                "borderRadius": "15px"
            }, className="mb-4"),

            # --- ROADMAP CARD ---
            dbc.Card([
                dbc.CardHeader(html.H4("Next Steps Roadmap", style={"color": NETFLIX_RED})),
                dbc.CardBody([
                    html.H5("Quarter 1 (Next 3 Months):", style={"color": TEXT_GRAY}),
                    html.Ul([
                        html.Li("🎬 Finalize budget for South Korean co-productions."),
                        html.Li("🧠 Begin A/B testing for European drama campaigns."),
                    ], style={"color": "white"}),

                    html.H5("Quarter 2 (3–6 Months):", style={"color": TEXT_GRAY, "marginTop": "1rem"}),
                    html.Ul([
                        html.Li("🌍 Launch European campaign for 'The Crown'-style dramas."),
                        html.Li("📊 Review Q1 content acquisition and engagement KPIs."),
                    ], style={"color": "white"}),

                    html.H5("Quarter 3 (6–9 Months):", style={"color": TEXT_GRAY, "marginTop": "1rem"}),
                    html.Ul([
                        html.Li("👨‍👩‍👧 Greenlight two new 'Kids & Family' titles for the Asian market."),
                    ], style={"color": "white"}),
                ])
            ], style={
                "backgroundColor": NETFLIX_DARK_GRAY,
                "border": f"1px solid {NETFLIX_RED}",
                "boxShadow": "0 0 12px rgba(229,9,20,0.2)",
                "borderRadius": "15px"
            }, className="mb-4"),
        ], width=8),

        # --- RIGHT COLUMN: OPPORTUNITIES & RISKS ---
        dbc.Col([
            # --- INVESTMENT OPPORTUNITIES ---
            dbc.Card([
                dbc.CardHeader(html.H4("Investment Opportunities", style={"color": NETFLIX_RED})),
                dbc.CardBody([
                    html.P("Promising areas for strategic investment:", style={"color": TEXT_GRAY}),
                    html.Ul([
                        html.Li("🌍 Emerging markets like Nigeria and Egypt."),
                        html.Li("🎞️ Underserved genres: 'Anime' and 'Documentaries'."),
                        html.Li("⭐ Top-tier creative partnerships (directors, actors)."),
                    ], style={"color": "white"})
                ])
            ], style={
                "backgroundColor": NETFLIX_DARK_GRAY,
                "border": f"1px solid {NETFLIX_RED}",
                "boxShadow": "0 0 12px rgba(229,9,20,0.2)",
                "borderRadius": "15px"
            }, className="mb-4"),

            # --- RISK AREAS ---
            dbc.Card([
                dbc.CardHeader(html.H4("Risk Areas Identification", style={"color": NETFLIX_RED})),
                dbc.CardBody([
                    html.P("Monitor these potential strategic risks:", style={"color": TEXT_GRAY}),
                    html.Ul([
                        html.Li("📉 Oversaturation in the US/UK markets."),
                        html.Li("💸 Rising production costs in high-output hubs."),
                        html.Li("🎭 Talent attrition to competitor platforms."),
                    ], style={"color": "white"})
                ])
            ], style={
                "backgroundColor": NETFLIX_DARK_GRAY,
                "border": f"1px solid {NETFLIX_RED}",
                "boxShadow": "0 0 12px rgba(229,9,20,0.2)",
                "borderRadius": "15px"
            }, className="mb-4"),
        ], width=4)
    ])
], fluid=True, style={
    "backgroundColor": NETFLIX_BLACK,
    "minHeight": "100vh",
    "paddingBottom": "30px"
})
