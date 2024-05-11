"""
dashboard.py
"""

# Third-party imports
import streamlit as st
import pandas as pd
import plotly.express as px

# Local imports
from utils import load_resale_data
from config import LIST_OF_HDB_TOWNS, LIST_OF_FLAT_TYPES


# Set page title
st.title("Resale Dashboard")



# Sidebar to allow user to select towns, flat types, and y-axis
with st.sidebar:
    selected_towns = st.multiselect("Select a town",
                                    LIST_OF_HDB_TOWNS,
                                    default="ANG MO KIO",
                                    max_selections=5)
    selected_flat_types = st.multiselect("Select a flat type",
                                         LIST_OF_FLAT_TYPES,
                                         default="5 ROOM",
                                         max_selections=2)
    selected_y_axis = st.selectbox("Select y-axis",
                                   ["resale_price", "price_per_sqm"])

# Set section title
st.subheader("Resale Prices Over Time")
selected_trend = st.checkbox("Show trendline", value=True)


# Create an empty DataFrame
df = pd.DataFrame()

# Load data for each town and flat type combination
with st.spinner("Loading data..."):
    for town in selected_towns:
        for flat_type in selected_flat_types:
            temp_df = load_resale_data(town=town, flat_type=flat_type)
            if not temp_df.empty:
                temp_df['town'] = town
                temp_df['flat_type'] = flat_type
                df = pd.concat([df, temp_df], ignore_index=True)

# Error handling: Display a warning if no data is found
if df.empty:
    st.warning("No data found.")
    st.stop()

# Convert price to float
df["resale_price"] = df["resale_price"].astype(float)

# Calculate price per sqm if selected
if selected_y_axis == "price_per_sqm":
    df["floor_area_sqm"] = df["floor_area_sqm"].astype(float)
    df["resale_price"] = df["resale_price"] / df["floor_area_sqm"]

# Group data by month and calculate mean price
df_grouped = df.groupby(["month", "town", "flat_type"])[["resale_price"]].mean().reset_index()
df_grouped["resale_price"] = df_grouped["resale_price"].round(-2)

# Calculate the xlim for the line chart
min_price = df_grouped["resale_price"].min() * 0.95
max_price = df_grouped["resale_price"].max() * 1.05

# Convert month to datetime
df_grouped["month"] = pd.to_datetime(df_grouped["month"])

# Create a line chart using Plotly Express
if selected_trend:
    fig = px.scatter(df_grouped,
                    x="month",
                    y="resale_price",
                    color='town',
                    opacity=0.3,
                    symbol='flat_type',
                    trendline="lowess",  # Using LOESS for smoothing
                    trendline_options={"frac": 0.3},
                    title="Resale Prices Over Time",
                    labels={
                        "resale_price": "Avg Resale Price",
                        "month": "Month"
                    })
    
else:
    fig = px.line(df_grouped,
                    x="month",
                    y="resale_price",
                    color='town',
                    line_dash='flat_type',
                    title="Resale Prices Over Time",
                    labels={
                        "resale_price": "Avg Resale Price",
                        "month": "Month"
                    })
                 
# Update layout to add legends below the chart
fig.update_layout(
    legend_title_text='Town & Flat Type',
    legend={
        "orientation":"h",
        "yanchor":"bottom",
        "y":-0.3,
        "xanchor":"right",
        "x":1
    },
    height=600
)

# Update x-axis range
margin = pd.Timedelta(days=180)
fig.update_xaxes(range=[df_grouped["month"].min() - margin,
                        df_grouped["month"].max() + margin])

# Update y-axis range
fig.update_yaxes(range=[min_price, max_price])

# Display the chart
st.plotly_chart(fig)

# New section
st.divider()
st.subheader("Compound Annual Growth Rate (CAGR)")

# Display CAGR for each town and flat type combination
for town in selected_towns:
    for flat_type in selected_flat_types:
        df_filtered = df_grouped[(df_grouped["town"] == town) & (df_grouped["flat_type"] == flat_type)]
        cagr = (df_filtered["resale_price"].iloc[-1] / df_filtered["resale_price"].iloc[0]) ** (12 / len(df_filtered)) - 1
        st.metric(label=f"{town} {flat_type}",
                  value=f"{cagr:.2%}",
                  delta_color="inverse")
        

# New section
st.divider()
st.subheader("Map of Singapore")

# Coordinates for a central point in Singapore
latitude = 1.3521
longitude = 103.8198

# Creating a map using Plotly Express
fig = px.scatter_mapbox(
    lat=[latitude], 
    lon=[longitude], 
    zoom=10, 
    height=300,
    center={"lat": latitude, "lon": longitude}
)

fig.update_layout(mapbox_style="open-street-map", 
                  height=600)

# Display the map in the Streamlit app
st.plotly_chart(fig)
