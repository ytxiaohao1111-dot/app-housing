"""BANA409 Data App Lab — California Housing Data (1990).

Put app-housing.py and housing.csv in the same folder, then run:
    streamlit run app-housing.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="California Housing Data (1990)", layout="wide")

# Change the name below to your own name before taking the submission screenshot.
AUTHOR_NAME = "Your Name"
DATA_DIR = Path(__file__).resolve().parent


@st.cache_data
def load_housing_data() -> pd.DataFrame:
    """Load housing.csv from the same directory as this Python script."""
    csv_path = DATA_DIR / "housing.csv"
    if not csv_path.is_file():
        st.error("Cannot find housing.csv next to app-housing.py.")
        st.stop()
    data = pd.read_csv(csv_path)

    required = {
        "longitude", "latitude", "median_house_value",
        "median_income", "ocean_proximity",
    }
    missing = required.difference(data.columns)
    if missing:
        st.error(f"Missing required columns: {', '.join(sorted(missing))}")
        st.stop()
    return data


housing = load_housing_data()

st.title(f"California Housing Data (1990) by {AUTHOR_NAME}")

# Main-page price slider, matching the assignment example.
minimum_price = st.slider(
    "Minimal Median House Value",
    min_value=0,
    max_value=int(housing["median_house_value"].max()),
    value=200000,
    step=1000,
)

# Filters in the sidebar.
st.sidebar.header("Housing Filters")
location_options = sorted(housing["ocean_proximity"].dropna().unique().tolist())
selected_locations = st.sidebar.multiselect(
    "Choose the location type",
    options=location_options,
    default=location_options,
)

income_level = st.sidebar.radio(
    "Choose income level",
    options=["Low", "Medium", "High"],
    index=0,
)

# Apply all three filters to the same dataframe.
filtered = housing[
    (housing["median_house_value"] >= minimum_price)
    & (housing["ocean_proximity"].isin(selected_locations))
].copy()

if income_level == "Low":
    filtered = filtered[filtered["median_income"] <= 2.5]
elif income_level == "Medium":
    filtered = filtered[
        (filtered["median_income"] > 2.5)
        & (filtered["median_income"] < 4.5)
    ]
else:  # High
    filtered = filtered[filtered["median_income"] >= 4.5]

st.subheader("See more filters in the sidebar:")
st.caption(f"Showing {len(filtered):,} of {len(housing):,} housing records")

# Show geographical locations. Streamlit recognizes longitude/latitude columns.
if filtered.empty:
    st.warning("No housing records match these filters. Try adjusting your choices.")
else:
    st.map(filtered[["latitude", "longitude"]].dropna())

# Histogram below the map; the assignment requires exactly 30 bins.
st.subheader("Distribution of Median House Value")
if not filtered.empty:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.hist(filtered["median_house_value"].dropna(), bins=30, edgecolor="white")
    ax.set_xlabel("Median House Value ($)")
    ax.set_ylabel("Number of Housing Records")
    ax.set_title("Median House Value Histogram")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("The histogram will appear when matching housing records are available.")
