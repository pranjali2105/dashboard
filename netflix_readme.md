# **📊 Netflix Content Strategy Dashboard**

This is a comprehensive, multi-tab Executive Dashboard built using **Plotly Dash** to analyze content performance, identify market gaps, and inform strategic decisions for a streaming service (simulated using Netflix data).

It is designed to be fully responsive (desktop/tablet) and includes features like real-time filtering, theme toggles, and data export capabilities.

## **📁 Project Structure**

The project uses the modern Dash Pages architecture for multi-page routing.

/Dashboard/  
    ├── app.py                      \# Main Dash Application file  
    ├── netflix.csv                 \# Primary Data Source  
    ├── prepare\_talent\_data.py      \# Script to preprocess Talent/Genre data  
    ├── assets/                     \# Custom CSS and JavaScript for styling  
    │     └── custom.css  
    │     └── theme\_changer.js  
    ├── requirements.txt            \# List of required Python packages  
    ├── pages/                      \# Contains the layout and callbacks for each tab  
    │   ├── tab1\_overview.py        \# Executive Overview (KPIs)  
    │   ├── tab2\_explorer.py        \# Content Explorer (AgGrid)  
    │   ├── tab3\_trends.py          \# Trend Intelligence  
    │   ├── tab4\_geo.py             \# Geographic Insights  
    │   ├── tab5\_genres.py          \# Genre Intelligence  
    │   ├── tab6\_talent.py          \# Creator & Talent Hub  
    │   └── tab7\_recommendations.py \# (Placeholder for final recommendations)

## **🚀 Setup and Run Instructions**

### **Step 1: Install Dependencies**

1. Navigate to the project root directory (Dashboard/).  
2. Install all required Python packages using pip:  
   pip install \-r requirements.txt

### **Step 2: Prepare the Data**

Some tabs (like **Creator & Talent Hub** and **Genre Intelligence**) require pre-calculated data saved in optimized .parquet files.

1. Run the preparation script **once**:  
   python prepare\_talent\_data.py

   *This script reads netflix.csv and generates the talent\_portfolio.parquet, talent\_edges.parquet, and genre\_edges.parquet files.*

### **Step 3: Run the Dashboard**

1. Run the main application file:  
   python app.py

2. Open your web browser and navigate to the link provided in the terminal (e.g., http://127.0.0.1:8050/).

## **✨ Key Dashboard Features**

| Tab | Key Feature | Functionality |
| :---- | :---- | :---- |
| **Executive Overview** | KPIs & Summary Charts | Displays total titles, growth rate, and top-level diversity metrics. |
| **Content Explorer** | Interactive Data Grid | Allows instant **search, filter, sort, and export (CSV/Excel)** across the entire library via dash-ag-grid. |
| **Trend Intelligence** | Growth Projections | Plots content additions over time, including seasonal trends and projected growth based on historical data. |
| **Geographic Insights** | Interactive Choropleth Map | Visualizes content saturation and opportunity scores by country, with region-level drill-downs. |
| **Genre Intelligence** | Co-occurrence Matrix | Uses a heatmap to visualize which genres are most (or least) commonly paired, aiding in **competitive gap analysis**. |
| **Creator & Talent Hub** | Network Visualization | Displays actor/director collaboration networks and rising stars identified by growth algorithms. |

