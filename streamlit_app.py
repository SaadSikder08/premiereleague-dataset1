import streamlit as st
import pandas as pd
import os
import glob
import altair as alt
import re

# Streamlit page settings
st.set_page_config(page_title="Premier League Table", page_icon="⚽")
st.title("⚽ Premier League Table (2017-2025)")
st.write("This app visualizes the Premier League table from 2010 to 2025. Yes its made by me")

# Function to load and combine all CSV files
@st.cache_data
def load_data():
    data_folder = "data/"  # Folder where all CSVs are stored
    all_files = glob.glob(os.path.join(data_folder, "premier_league_*.csv"))  # Find all CSVs
    
    all_data = []
    
    for file in all_files:
        df = pd.read_csv(file)

        # Extract year from filename safely
        match = re.search(r'(\d{4})', file)
        year = int(match.group(1)) if match else 0  

        # Rename columns and keep only necessary ones
        df = df.rename(columns={"Unnamed: 1": "team", "Unnamed: 17": "points"})
        df = df[["team", "points"]]

        # Clean team names (remove anything in parentheses like "Everton (-8)")
        df["team"] = df["team"].str.replace(r"\s*\(.*?\)", "", regex=True)

        # Convert points to numeric
        df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)

        df["year"] = year
        all_data.append(df)

    if all_data:
        df_combined = pd.concat(all_data, ignore_index=True)
        df_combined["year"] = df_combined["year"].astype(int)  # Ensure year is integer
        return df_combined
    else:
        return pd.DataFrame(columns=["year", "team", "points"])

# Load all the data when the app starts
df = load_data()

# Year selection
years = st.slider("Select Years", 2017, 2025, (2017, 2025))

# Filter data based on selected year range
df_filtered = df[(df["year"] >= years[0]) & (df["year"] <= years[1])]

# Team selection
distinct_teams = df_filtered["team"].unique()
teams = st.multiselect("Select Teams", distinct_teams, default=distinct_teams)

df_filtered = df_filtered[df_filtered["team"].isin(teams)]

# Aggregate total points per team in the selected range
df_agg = df_filtered.groupby("team", as_index=False)["points"].sum()

# Display filtered data
st.dataframe(df_filtered, use_container_width=True)

# Show as a bar chart
if not df_agg.empty:
    chart = (
        alt.Chart(df_agg)
        .mark_bar()
        .encode(
            x=alt.X("team:N", title="Team", sort="-y"),  # Sort by points descending
            y=alt.Y("points:Q", title="Total Points"),
            color=alt.Color("team:N", legend=None),
            tooltip=["team", "points"]
        )
        .properties(height=400)
    )

    # Add text labels to bars
    text = chart.mark_text(
        align="center",
        baseline="bottom",
        dy=-5  # Position labels above bars
    ).encode(text="points:Q")

    st.altair_chart(chart + text, use_container_width=True)
else:
    st.warning("No data available for the selected filters. Please check if data for the selected years exists.")
