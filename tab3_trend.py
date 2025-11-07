# Save this in /pages/tab3_trends.py

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np

dash.register_page(__name__, name='Trend Intelligence', path='/trend-intelligence')

# --- 1. Load and Prepare Data ---
try:
    df = pd.read_csv("netflix.csv")
except FileNotFoundError:
    layout = html.Div([
        html.H1("Error: netflix.csv not found", className="text-danger"),
        html.P("Please make sure 'netflix.csv' is in your main 'Dashboard' folder.")
    ])
    raise FileNotFoundError("netflix.csv not found.")

# --- Prep for Time-Series & Seasonal ---
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df = df.dropna(subset=['date_added'])
df['year_added'] = df['date_added'].dt.year
df['month_num'] = df['date_added'].dt.month
df['month_abbr'] = df['date_added'].dt.strftime('%b')

# Prep data for main time-series chart (Feature 1)
df_yearly_counts = df.groupby(['year_added', 'type']).size().reset_index(name='count')

# Prep data for seasonal chart (Feature 3)
df_seasonal = df.groupby(['month_num', 'month_abbr', 'type']).size().reset_index(name='count')
df_seasonal = df_seasonal.sort_values('month_num')

# --- NEW: Milestones Data (Feature 5) ---
milestones_data = [
    {'date': '2016-01-01', 'event': 'Global Expansion', 'description': 'Netflix launched in 130 new countries, reaching 190 countries globally.'},
    {'date': '2017-01-01', 'event': 'First Emmy Win for Original Content', 'description': 'House of Cards won its first major Emmy, signifying industry recognition.'},
    {'date': '2018-01-01', 'event': 'Content Spend Exceeds $12 Billion', 'description': 'Massive investment in original movies and series to attract subscribers.'},
    {'date': '2020-01-01', 'event': 'Pandemic Boost & Subscriber Surge', 'description': 'Record subscriber growth due to global lockdowns.'},
    {'date': '2022-01-01', 'event': 'First Subscriber Decline', 'description': 'Netflix reported its first subscriber loss in over a decade, signaling market saturation.'},
]

df_milestones = pd.DataFrame(milestones_data)
df_milestones['date'] = pd.to_datetime(df_milestones['date'])


# --- 2. Helper Function for Styling ---
def style_figure_dark(fig):
    fig.update_layout(
        template="plotly_dark",
        font_color="white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text=''
    )
    return fig

# --- NEW: Create Milestones Timeline Figure ---
# We'll use a simple scatter plot with custom markers to simulate a timeline
fig_milestones = go.Figure()

# Add a horizontal line to represent the timeline axis
fig_milestones.add_trace(go.Scatter(
    x=[df_milestones['date'].min(), df_milestones['date'].max()],
    y=[0, 0], # All points on the same y-axis level
    mode='lines',
    line=dict(color='grey', width=2),
    showlegend=False
))

# Add markers for each milestone
for i, row in df_milestones.iterrows():
    fig_milestones.add_trace(go.Scatter(
        x=[row['date']],
        y=[0], # All markers on the same horizontal line
        mode='markers+text',
        marker=dict(symbol='diamond-open', size=12, color='#E50914', line=dict(width=2, color='#E50914')),
        name=row['event'],
        text=f"<b>{row['date'].year}</b><br>{row['event']}",
        textposition="top center", # Position text above the marker
        hovertemplate=f"<b>%{{x|%Y-%m-%d}}</b><br>{row['event']}<br>{row['description']}<extra></extra>"
    ))

fig_milestones.update_layout(
    title="Historical Milestones",
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False, # Hide y-axis labels as it's just a timeline
        title=""
    ),
    xaxis=dict(
        showgrid=False,
        tickformat="%Y",
        range=[df_milestones['date'].min() - pd.Timedelta(days=180), df_milestones['date'].max() + pd.Timedelta(days=180)]
    ),
    height=250, # Make it compact
    margin=dict(l=20, r=20, t=50, b=20),
    template="plotly_dark",
    font_color="white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False # Legend not needed for this style
)


# --- 3. Define Page Layout ---
layout = dbc.Container([
    html.H1("🧠 Trend Intelligence", className="mt-4 netflix-glow"),

    # Row 1: Main Interactive Chart & Controls
    dbc.Row([
        # Column 1: The Controls
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H5("Comparison Tools (Feature 2)", className="card-title"),
                    dcc.Checklist(
                        id='trend-comparison-checklist',
                        options=[
                            {'label': ' Movies', 'value': 'Movie'},
                            {'label': ' TV Shows', 'value': 'TV Show'},
                        ],
                        value=['Movie', 'TV Show'], # Default to showing both
                        labelStyle={'display': 'block', 'margin-top': '5px'},
                        inputStyle={'margin-right': '5px'}
                    ),
                    html.Hr(),
                    html.H5("Analysis Tools", className="card-title"),
                    dbc.Switch(
                        id='projection-switch',
                        label="Show Growth Projection (Feature 4)",
                        value=False,
                    ),
                ]),
                color="dark"
            )
        ], width=3),

        # Column 2: The Main Chart
        dbc.Col([
            dbc.Card(
                # Feature 1: Interactive time-series chart
                dcc.Graph(id='main-trend-chart'),
                color="dark",
                body=True
            )
        ], width=9)
    ], className="mt-4"),

    # Row 2: Seasonal Analysis
    dbc.Row([
        dbc.Col([
            dbc.Card(
                # Feature 3: Seasonal pattern analysis
                dcc.Graph(
                    id='seasonal-trend-chart',
                    figure=style_figure_dark(px.line(
                        df_seasonal,
                        x='month_abbr',
                        y='count',
                        color='type',
                        title="Seasonal Addition Trends",
                        markers=True,
                        color_discrete_map={
                            'Movie': '#F08080',
                            'TV Show': '#E50914'
                        }
                    ))
                ),
                color="dark",
                body=True
            )
        ], width=12)
    ], className="mt-4"),
    
    # NEW ROW 3: Historical Milestones Timeline
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dcc.Graph(id='milestones-timeline', figure=fig_milestones),
                color="dark",
                body=True
            )
        ], width=12)
    ], className="mt-4 mb-4") # Add bottom margin to the last row
], fluid=True)


# --- 4. Define Callback for Main Chart ---
@dash.callback(
    Output('main-trend-chart', 'figure'),
    Input('trend-comparison-checklist', 'value'),
    Input('projection-switch', 'value')
)
def update_main_trend_chart(selected_types, show_projection):
    
    # Filter data based on checklist
    df_filtered = df_yearly_counts[df_yearly_counts['type'].isin(selected_types)].copy() # Use .copy() to avoid SettingWithCopyWarning

    # --- NEW: Create a list of frames for animation ---
    frames = []
    
    # Get overall max values for consistent axis ranges
    min_year = df_yearly_counts['year_added'].min()
    max_year = df_yearly_counts['year_added'].max()
    max_count = df_yearly_counts['count'].max()

    # Create the initial static figure (the "original graph")
    fig = go.Figure(
        layout=go.Layout(
            title="Content Added Per Year",
            xaxis=dict(range=[min_year, max_year]),
            yaxis=dict(range=[0, max_count * 1.1]),
            updatemenus=[dict(type="buttons",
                              buttons=[dict(label="Play",
                                            method="animate",
                                            args=[None, {"frame": {"duration": 500, "redraw": True},
                                                          "fromcurrent": True, "transition": {"duration": 300, "easing": "linear"}}])])]
        )
    )

    # Add the full static lines (the "original graph") for the selected types
    for item_type in selected_types:
        df_type = df_filtered[df_filtered['type'] == item_type]
        color = '#F08080' if item_type == 'Movie' else '#E50914'
        fig.add_trace(go.Scatter(
            x=df_type['year_added'],
            y=df_type['count'],
            mode='lines+markers',
            name=f'{item_type} (Full)',
            line=dict(color=color, width=1, dash='dot'), # Make static line slightly thinner and dotted
            showlegend=True,
            legendgroup=item_type # Group legends
        ))
    
    # Generate frames for the animated "drawing" effect
    for year in sorted(df_filtered['year_added'].unique()):
        frame_data = []
        for item_type in selected_types:
            df_slice = df_filtered[(df_filtered['type'] == item_type) & (df_filtered['year_added'] <= year)]
            color = '#F08080' if item_type == 'Movie' else '#E50914'
            
            # This trace will be animated
            frame_data.append(go.Scatter(
                x=df_slice['year_added'],
                y=df_slice['count'],
                mode='lines+markers',
                name=f'{item_type} (Animated)',
                line=dict(color=color, width=3), # Make animated line thicker
                marker=dict(size=8, color=color),
                showlegend=False, # Don't show legend for animated parts, it gets redundant
                legendgroup=item_type
            ))
        
        frames.append(go.Frame(data=frame_data, name=str(year)))

    fig.frames = frames

    # Add Growth Projection (Feature 4) - this will be static above the animated lines
    if show_projection:
        df_total_trend = df_yearly_counts.groupby('year_added')['count'].sum().reset_index()
        df_recent_trend = df_total_trend[df_total_trend['year_added'] >= 2015]
        
        x = df_recent_trend['year_added']
        y = df_recent_trend['count']
        
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)

        fig.add_trace(go.Scatter(
            x=x, 
            y=p(x),
            mode='lines',
            name='Growth Projection',
            line=dict(dash='dash', color='yellow', width=2),
            showlegend=True # Show legend for projection
        ))

    # Style the final figure
    fig = style_figure_dark(fig)
    return fig