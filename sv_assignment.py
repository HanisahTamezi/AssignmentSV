
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Selangor Socioeconomic Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:

    st.title("📊 Selangor Dashboard")
    st.caption("Socioeconomic Data Analysis")

    st.divider()

    st.subheader("Navigation")

    # Home page
    st.page_link(
        "sv_assignment.py",
        label="Home",
        icon="🏠"
    )

    # Visualization pages
    st.page_link(
        "pages/1_Page_1.py",
        label="Median Household Income",
        icon="📈"
    )

    st.page_link(
        "pages/2_Page_2.py",
        label="Income and Absolute Poverty",
        icon="🔍"
    )

    st.page_link(
        "pages/3_Page_3.py",
        label="Mean Household Income",
        icon="📊"
    )

    st.divider()

    st.subheader("Dataset Information")

    st.write("**Source:** DOSM")
    st.write("**Location:** Selangor")
    st.write("**Period:** 2020–2024")

    st.divider()

    st.caption("Scientific Visualization Assignment")


# ==========================================
# DASHBOARD TITLE
# ==========================================

st.header(
    "Selangor Socioeconomic Dashboard",
    divider="gray"
)

st.markdown("""
This dashboard explores household income, population and absolute poverty
across parliamentary constituencies in Selangor using DOSM data from 2020 to 2024.
""")


# ==========================================
# LOAD DATASETS
# ==========================================

@st.cache_data
def load_data():

    pop_url = "https://storage.dosm.gov.my/population/population_parlimen.parquet"

    income_url = "https://storage.dosm.gov.my/hies/hh_income_parlimen.parquet"

    poverty_url = "https://storage.dosm.gov.my/hies/hh_poverty_parlimen.parquet"

    # Read datasets
    df_pop = pd.read_parquet(pop_url)
    df_inc = pd.read_parquet(income_url)
    df_pov = pd.read_parquet(poverty_url)

    # Convert date columns
    for frame in (df_pop, df_inc, df_pov):
        frame["date"] = pd.to_datetime(frame["date"])

    # Filter years 2020–2024
    df_pop = df_pop[
        df_pop["date"].dt.year.between(2020, 2024)
    ]

    df_inc = df_inc[
        df_inc["date"].dt.year.between(2020, 2024)
    ]

    df_pov = df_pov[
        df_pov["date"].dt.year.between(2020, 2024)
    ]

    # Filter overall population
    df_pop = df_pop[
        (df_pop["sex"] == "both") &
        (df_pop["age"] == "overall") &
        (df_pop["ethnicity"] == "overall")
    ]

    # Merge population and income datasets
    merged = pd.merge(
        df_pop,
        df_inc,
        on=["date", "state", "parlimen"],
        how="inner"
    )

    # Merge with poverty dataset
    merged = pd.merge(
        merged,
        df_pov,
        on=["date", "state", "parlimen"],
        how="inner"
    )

    return merged


# ==========================================
# MAIN DASHBOARD
# ==========================================

try:

    # Load all datasets
    data = load_data()

    # Filter Selangor
    selangor = data[
        data["state"] == "Selangor"
    ].copy()

    if selangor.empty:

        st.warning("No Selangor records found.")

    else:

        # ==================================
        # KPI METRICS
        # ==================================

        latest_year = int(
            selangor["date"].dt.year.max()
        )

        latest_data = selangor[
            selangor["date"].dt.year == latest_year
        ].copy()

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
            value=f"{latest_data['population'].sum():,.0f}",
            border=True
        )

        col4.metric(
            label="Total Records",
            value=f"{len(selangor):,}",
            border=True
        )

        st.divider()


        # ==================================
        # DATASET PREVIEW
        # ==================================

        st.subheader("Dataset Preview")

        st.write(
            "The table below displays the first 10 records "
            "of the combined Selangor socioeconomic dataset."
        )

        st.dataframe(
            selangor.head(10),
            use_container_width=True,
            hide_index=True
        )

        st.divider()


        # ==================================
        # POPULATION VISUALIZATION
        # ==================================

        st.subheader(
            "Population Distribution by Constituency"
        )

        st.write(
            f"Population distribution across parliamentary "
            f"constituencies in Selangor for {latest_year}."
        )

        # Sort population in descending order
        population_data = latest_data.sort_values(
            by="population",
            ascending=False
        )

        fig = px.bar(
            population_data,
            x="parlimen",
            y="population",
            title=f"Population by Parliamentary Constituency ({latest_year})",
            color="population",
            color_continuous_scale="Blues",
            labels={
                "parlimen": "Parliamentary Constituency",
                "population": "Population"
            },
            hover_data={
                "parlimen": True,
                "population": ":,.0f"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            template="plotly_white",
            xaxis_title="Parliamentary Constituency",
            yaxis_title="Total Population"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()


        # ==================================
        # ABOUT THE DATASET
        # ==================================

        st.subheader("About the Dataset")

        st.markdown("""
        The dashboard combines three datasets from the
        **Department of Statistics Malaysia (DOSM)**:

        1. **Population by Parliamentary Constituency**
           - Provides population information for each constituency.

        2. **Household Income by Parliamentary Constituency**
           - Provides household income statistics, including mean and median income.

        3. **Household Poverty by Parliamentary Constituency**
           - Provides information on absolute poverty across constituencies.
        """)

        st.info(
            "Use the sidebar navigation to explore the three "
            "visualization pages."
        )

        st.caption(
            "Data Source: Department of Statistics Malaysia (DOSM) | 2020–2024"
        )


# ==========================================
# ERROR HANDLING
# ==========================================

except Exception as e:

    st.error(
        "The data could not be loaded. "
        "Please check your internet connection and dataset availability."
    )

    st.exception(e)
