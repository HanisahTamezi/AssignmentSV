import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Income and Absolute Poverty",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
st.sidebar.title("Navigation")

st.sidebar.page_link(
    "sv_assignment.py",
    label="Home",
    icon="🏠"
)

st.sidebar.page_link(
    "pages/1_Page_1.py",
    label="Page 1: Income Trends",
    icon="📈"
)

st.sidebar.page_link(
    "pages/2_Page_2.py",
    label="Page 2: Income and Poverty",
    icon="📊"
)

st.sidebar.page_link(
    "pages/3_Page_3.py",
    label="Page 3: Income Comparison",
    icon="📉"
)

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data():

    pop_url = (
        "https://storage.dosm.gov.my/population/"
        "population_parlimen.parquet"
    )

    income_url = (
        "https://storage.dosm.gov.my/hies/"
        "hh_income_parlimen.parquet"
    )

    poverty_url = (
        "https://storage.dosm.gov.my/hies/"
        "hh_poverty_parlimen.parquet"
    )

    df_pop = pd.read_parquet(pop_url)
    df_inc = pd.read_parquet(income_url)
    df_pov = pd.read_parquet(poverty_url)

    for frame in [df_pop, df_inc, df_pov]:
        frame["date"] = pd.to_datetime(frame["date"])

    # Filter data from 2020 to 2024
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

    # Merge datasets
    merged = pd.merge(
        df_pop,
        df_inc,
        on=["date", "state", "parlimen"],
        how="inner"
    )

    merged = pd.merge(
        merged,
        df_pov,
        on=["date", "state", "parlimen"],
        how="inner"
    )

    return merged


def get_selangor_data():

    data = load_data()

    result = data[
        data["state"] == "Selangor"
    ].copy()

    result["date"] = pd.to_datetime(result["date"])

    return result


# --------------------------------------------------
# PAGE TITLE AND DESCRIPTION
# --------------------------------------------------
st.title("Income and Absolute Poverty in Selangor")

st.write(
    "This visualization examines the relationship between "
    "median household income and absolute poverty rates "
    "across parliamentary constituencies in Selangor "
    "for the latest available year."
)

st.markdown(
    "**Visualization Objective:** To examine the relationship "
    "between median household income and absolute poverty "
    "rates across parliamentary constituencies in Selangor."
)

st.divider()

# --------------------------------------------------
# MAIN VISUALIZATION
# --------------------------------------------------
try:

    df_selangor = get_selangor_data()

    if df_selangor.empty:

        st.warning("No Selangor data available.")

    else:

        # Get latest available year
        latest_year = int(
            df_selangor["date"].dt.year.max()
        )

        df_latest = df_selangor[
            df_selangor["date"].dt.year == latest_year
        ].copy()

        # --------------------------------------------------
        # KPI METRICS
        # --------------------------------------------------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Latest Data Year",
            latest_year,
            border=True
        )

        col2.metric(
            "Constituencies",
            df_latest["parlimen"].nunique(),
            border=True
        )

        col3.metric(
            "Average Median Income",
            f"RM {df_latest['income_median'].mean():,.0f}",
            border=True
        )

        col4.metric(
            "Average Poverty Rate",
            f"{df_latest['poverty_absolute'].mean():.2f}%",
            border=True
        )

        st.divider()

        # --------------------------------------------------
        # INTERACTIVE FILTER
        # --------------------------------------------------
        st.subheader("Explore the Relationship")

        constituencies = sorted(
            df_latest["parlimen"].dropna().unique()
        )

        selected_constituencies = st.multiselect(
            "Select Parliamentary Constituencies",
            options=constituencies,
            default=constituencies
        )

        if not selected_constituencies:

            st.warning(
                "Please select at least one constituency."
            )

        else:

            df_chart = df_latest[
                df_latest["parlimen"].isin(
                    selected_constituencies
                )
            ].copy()

            # --------------------------------------------------
            # SCATTER PLOT
            # --------------------------------------------------
            st.subheader(
                "Median Income vs Absolute Poverty"
            )

            st.write(
                "Each point represents a parliamentary "
                "constituency. Explore the relationship between "
                "household income and poverty by hovering "
                "over the data points."
            )

            if len(df_chart) >= 2:

                fig = px.scatter(
                    df_chart,
                    x="income_median",
                    y="poverty_absolute",
                    hover_name="parlimen",
                    hover_data={
                        "income_median": ":,.2f",
                        "income_mean": ":,.2f",
                        "poverty_absolute": ":.2f"
                    },
                    trendline="ols",
                    trendline_color_override="#E74C3C",
                    title=(
                        "Relationship Between Median Household "
                        f"Income and Absolute Poverty ({latest_year})"
                    ),
                    labels={
                        "income_median":
                            "Median Household Income (RM)",
                        "poverty_absolute":
                            "Absolute Poverty Rate (%)"
                    }
                )

            else:

                fig = px.scatter(
                    df_chart,
                    x="income_median",
                    y="poverty_absolute",
                    hover_name="parlimen",
                    hover_data={
                        "income_median": ":,.2f",
                        "income_mean": ":,.2f",
                        "poverty_absolute": ":.2f"
                    },
                    title=(
                        "Median Income vs Absolute Poverty"
                    ),
                    labels={
                        "income_median":
                            "Median Household Income (RM)",
                        "poverty_absolute":
                            "Absolute Poverty Rate (%)"
                    }
                )

            # Customize scatter plot markers
            fig.update_traces(
                marker=dict(
                    size=13,
                    opacity=0.8,
                    line=dict(
                        width=1,
                        color="black"
                    )
                ),
                selector=dict(mode="markers")
            )

            # Customize chart layout
            fig.update_layout(
                template="plotly_white",
                title_x=0.5,
                height=650,
                showlegend=False,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12
                ),
                xaxis=dict(
                    title="Median Household Income (RM)",
                    showgrid=True,
                    gridcolor="lightgrey",
                    tickformat=",.0f"
                ),
                yaxis=dict(
                    title="Absolute Poverty Rate (%)",
                    showgrid=True,
                    gridcolor="lightgrey"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # --------------------------------------------------
            # CHART INTERPRETATION
            # --------------------------------------------------
            st.info(
                """
                **How to Interpret the Chart**

                - Each dot represents one parliamentary constituency.
                - The X-axis represents median household income (RM).
                - The Y-axis represents the absolute poverty rate (%).
                - The red trendline shows the overall linear relationship
                  between median household income and absolute poverty.
                - A downward trend suggests that constituencies with
                  higher median income tend to have lower poverty rates.
                """
            )

            st.divider()

            # --------------------------------------------------
            # DATASET PREVIEW
            # --------------------------------------------------
            st.subheader("Dataset Preview")

            st.write(
                "The table shows household income and absolute "
                "poverty rates for each selected constituency."
            )

            preview_data = df_chart[
                [
                    "parlimen",
                    "income_median",
                    "income_mean",
                    "poverty_absolute"
                ]
            ].sort_values(
                "poverty_absolute",
                ascending=False
            )

            preview_data.columns = [
                "Parliamentary Constituency",
                "Median Household Income (RM)",
                "Mean Household Income (RM)",
                "Absolute Poverty Rate (%)"
            ]

            st.dataframe(
                preview_data,
                use_container_width=True,
                hide_index=True
            )

        # --------------------------------------------------
        # DATA SOURCE
        # --------------------------------------------------
        st.divider()

        st.caption(
            "Source: Department of Statistics Malaysia (DOSM). "
            f"Latest available year: {latest_year}."
        )

except Exception as e:

    st.error(
        "Unable to display this visualization. "
        "Please check the dataset and column names."
    )

    st.exception(e)
