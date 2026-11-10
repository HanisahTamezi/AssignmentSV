
import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Selangor Socioeconomic Dashboard",
    page_icon="📊",
    layout="wide"
)

# Dashboard title
st.header("Selangor Socioeconomic Dashboard", divider="gray")

st.markdown("""
This dashboard explores household income, population and absolute poverty
across parliamentary constituencies in Selangor using DOSM data from 2020 to 2024.
""")

# Load datasets
@st.cache_data
def load_data():
    pop_url = "https://storage.dosm.gov.my/population/population_parlimen.parquet"
    income_url = "https://storage.dosm.gov.my/hies/hh_income_parlimen.parquet"
    poverty_url = "https://storage.dosm.gov.my/hies/hh_poverty_parlimen.parquet"

    df_pop = pd.read_parquet(pop_url)
    df_inc = pd.read_parquet(income_url)
    df_pov = pd.read_parquet(poverty_url)

    for frame in (df_pop, df_inc, df_pov):
        frame["date"] = pd.to_datetime(frame["date"])

    # Filter years 2020–2024
    df_pop = df_pop[df_pop["date"].dt.year.between(2020, 2024)]
    df_inc = df_inc[df_inc["date"].dt.year.between(2020, 2024)]
    df_pov = df_pov[df_pov["date"].dt.year.between(2020, 2024)]

    # Filter overall population
    df_pop = df_pop[
        (df_pop["sex"] == "both") &
        (df_pop["age"] == "overall") &
        (df_pop["ethnicity"] == "overall")
    ]

    # Merge datasets
    merged = pd.merge(
        df_pop, df_inc,
        on=["date", "state", "parlimen"],
        how="inner"
    )

    merged = pd.merge(
        merged, df_pov,
        on=["date", "state", "parlimen"],
        how="inner"
    )

    return merged


# Main dashboard
try:
    data = load_data()

    # Filter Selangor
    selangor = data[data["state"] == "Selangor"].copy()

    if selangor.empty:
        st.warning("No Selangor records found.")
    else:
        # KPI Metrics
        latest_year = int(selangor["date"].dt.year.max())

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            label="Latest Data Year",
            value=latest_year,
            border=True
        )

        col2.metric(
            label="Parliamentary Constituencies",
            value=selangor["parlimen"].nunique(),
            border=True
        )

        col3.metric(
            label="Total Population",
            value=f"{selangor[selangor['date'].dt.year == latest_year]['population'].sum():,.0f}",
            border=True
        )

        col4.metric(
            label="Total Records",
            value=f"{len(selangor):,}",
            border=True
        )

        st.divider()

        # Dataset Preview
        st.subheader("Dataset Preview")

        st.dataframe(
            selangor.head(10),
            use_container_width=True
        )

        # Visualization: Population by Constituency
        st.subheader("Population Distribution by Constituency")

        latest_data = selangor[
            selangor["date"].dt.year == latest_year
        ]

        fig = px.bar(
            latest_data,
            x="parlimen",
            y="population",
            title=f"Population by Parliamentary Constituency ({latest_year})",
            color="population",
            color_continuous_scale="Blues",
            labels={
                "parlimen": "Parliamentary Constituency",
                "population": "Population"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Dataset Information
        st.subheader("About the Dataset")

        st.write("""
        The dashboard combines three datasets from the Department of Statistics
        Malaysia (DOSM):

        - Population by Parliamentary Constituency
        - Household Income by Parliamentary Constituency
        - Household Poverty by Parliamentary Constituency

        The analysis focuses on Selangor from 2020 to 2024.
        """)

        st.info(
            "Navigate to Page 1, Page 2 or Page 3 using the sidebar "
            "to explore the detailed visualizations."
        )

except Exception as e:
    st.error("The data could not be loaded. Please check your internet connection.")
    st.exception(e)
