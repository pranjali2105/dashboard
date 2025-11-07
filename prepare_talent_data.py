# Save this as prepare_talent_data.py

import pandas as pd
import numpy as np
from itertools import combinations

print("Starting talent data preparation...")

# --- 1. Load Data ---
try:
    # This path points to your Desktop
    df = pd.read_csv("netflix.csv")
except FileNotFoundError:
    print("Error: /Users/pranjalimane/Desktop/netflix.csv not found.")
    exit()

# --- 2. Build Portfolio & Master Talent List (Features 1, 3, 4) ---
def explode_talent(df_in, column_name, role):
    """Helper function to explode a talent column (cast or director)"""
    df_role = df_in[['show_id', 'title', 'release_year', 'country', column_name]].copy()
    df_role = df_role.dropna(subset=[column_name])
    df_role = df_role.assign(**{column_name: df_role[column_name].str.split(', ')}).explode(column_name)
    df_role['name'] = df_role[column_name].str.strip()
    df_role['role'] = role
    
    # Clean up country data for portfolio diversity
    df_role = df_role.dropna(subset=['country'])
    df_role = df_role.assign(country=df_role['country'].str.split(', ')).explode('country')
    df_role['country'] = df_role['country'].str.strip()
    
    return df_role[['show_id', 'title', 'release_year', 'country', 'name', 'role']]

print("Step 1/3: Processing portfolios...")
df_cast = explode_talent(df, 'cast', 'Actor')
df_director = explode_talent(df, 'director', 'Director')
df_portfolio = pd.concat([df_cast, df_director]).drop_duplicates()

# Save for Features 1, 3, 4
df_portfolio.to_parquet('talent_portfolio.parquet', index=False)
print("  -> talent_portfolio.parquet saved.")

# --- 3. Build Collaboration Edges (Feature 2) ---
print("Step 2/3: Building collaboration network... (this may take a minute)")
shows = df_portfolio.groupby('show_id')['name'].apply(list)
edges = []
for talent_list in shows:
    for pair in combinations(sorted(talent_list), 2):
        edges.append({'source': pair[0], 'target': pair[1]})
df_edges = pd.DataFrame(edges)
df_edges_agg = df_edges.groupby(['source', 'target']).size().reset_index(name='weight')

# Save for Feature 2
df_edges_agg.to_parquet('talent_edges.parquet', index=False)
print(f"  -> talent_edges.parquet saved with {len(df_edges_agg)} unique relationships.")

# --- 4. Identify Rising Stars (Feature 5) ---
print("Step 3/3: Identifying rising stars...")
df_yearly_count = df_portfolio.groupby(['name', 'release_year']).size().reset_index(name='titles_count')

RECENT_YEAR = df['release_year'].max() - 5 
df_recent = df_yearly_count[df_yearly_count['release_year'] >= RECENT_YEAR]

def get_growth_slope(group):
    if len(group) < 2: return 0
    y = group['titles_count'].values
    x = group['release_year'].values
    slope, _ = np.polyfit(x, y, 1)
    return slope

df_growth = df_recent.groupby('name').apply(get_growth_slope).reset_index(name='growth_slope')
df_total = df_recent.groupby('name')['titles_count'].sum().reset_index(name='total_recent_titles')
df_rising = pd.merge(df_growth, df_total, on='name')
df_rising = df_rising[(df_rising['growth_slope'] > 0) & (df_rising['total_recent_titles'] >= 2)]
df_rising = df_rising.sort_values(by=['growth_slope', 'total_recent_titles'], ascending=False)

# Save for Feature 5
df_rising.head(100).to_parquet('rising_stars.parquet', index=False)
print("  -> rising_stars.parquet saved.")
print("--- Preparation Complete! ---")
# --- 5. Build Genre Co-occurrence (for Tab 5) ---
print("Step 4/4: Building genre co-occurrence matrix...")

# Reload the raw dataframe
df_genre = pd.read_csv("netflix.csv")
df_genre = df_genre.dropna(subset=['listed_in'])

# Explode the 'listed_in' column
df_genre = df_genre.assign(genre=df_genre['listed_in'].str.split(', ')).explode('genre')
df_genre['genre'] = df_genre['genre'].str.strip()

# Group by show to get a list of genres for each show
show_genres = df_genre.groupby('show_id')['genre'].apply(list)

genre_edges = []
# Iterate over each show's list of genres
for genre_list in show_genres:
    # Create all unique pairs (edges) for this show
    for pair in combinations(sorted(genre_list), 2):
        genre_edges.append({'source': pair[0], 'target': pair[1]})

df_genre_edges = pd.DataFrame(genre_edges)

# Aggregate edges to get a 'weight'
df_genre_edges_agg = df_genre_edges.groupby(['source', 'target']).size().reset_index(name='weight')

# Save for Feature 2
df_genre_edges_agg.to_parquet('genre_edges.parquet', index=False)
print(f"  -> genre_edges.parquet saved with {len(df_genre_edges_agg)} relationships.")
print("--- All Data Preparation Complete! ---")