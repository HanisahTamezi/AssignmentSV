
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
        (df_pop["sex"] == "both")
        & (df_pop["age"] == "overall")
        & (df_pop["ethnicity"] == "overall")
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
# SECTION AND PAGE DESCRIPTION
# --------------------------------------------------
st.title("Income and Absolute Poverty in Selangor")

st.markdown(
    "### Section 2.2: Relationship Between Income and Poverty"
)

st.markdown("**Description**")

st.write(
    "This visualization uses a scatter plot to examine "
    "the relationship between median household income "
    "and absolute poverty rates across parliamentary "
    "constituencies in Selangor in 2024. Each point "
    "represents one parliamentary constituency, while "
    "the trendline illustrates the overall relationship "
    "between the two variables."
)

st.markdown("**Objective Statement**")

st.info(
    "To investigate the relationship between median "
    "household income and absolute poverty rates across "
    "parliamentary constituencies in Selangor in 2024."
)

st.divider()


# --------------------------------------------------
# MAIN VISUALIZATION
# --------------------------------------------------
try:

    df_selangor = get_selangor_data()

    if df_selangor.empty:
        st.warning("No Selangor data available.")
        st.stop()

    # --------------------------------------------------
    # FILTER DATA FOR 2024
    # --------------------------------------------------
    selected_year = 2024

    df_latest = df_selangor[
        df_selangor["date"].dt.year == selected_year
    ].copy()

    if df_latest.empty:
        st.warning(
            "No Selangor data available for 2024."
        )
        st.stop()

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
        st.stop()

    df_chart = df_latest[
        df_latest["parlimen"].isin(
            selected_constituencies
        )
    ].copy()

    # Remove missing values from variables used in analysis
    df_chart = df_chart.dropna(
        subset=[
            "income_median",
            "poverty_absolute"
        ]
    )

    if df_chart.empty:
        st.warning(
            "No valid income and poverty records are available."
        )
        st.stop()

    # --------------------------------------------------
    # CALCULATE SUMMARY STATISTICS
    # --------------------------------------------------
    avg_income = df_chart["income_median"].mean()

    avg_poverty = df_chart["poverty_absolute"].mean()

    constituency_count = df_chart["parlimen"].nunique()

    correlation = df_chart[
        ["income_median", "poverty_absolute"]
    ].corr().iloc[0, 1]

    highest_poverty = df_chart.loc[
        df_chart["poverty_absolute"].idxmax()
    ]

    lowest_poverty = df_chart.loc[
        df_chart["poverty_absolute"].idxmin()
    ]

    # --------------------------------------------------
    # SUMMARY BOX
    # --------------------------------------------------
    st.subheader("Summary Box")

    st.write(
        "The following indicators provide an overview "
        "of household income and absolute poverty "
        "across the selected constituencies."
    )

    with st.container(border=True):

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Data Year",
            selected_year
        )

        col2.metric(
            "Constituencies",
            constituency_count
        )

        col3.metric(
            "Average Median Income",
            f"RM {avg_income:,.0f}"
        )

        col4.metric(
            "Average Poverty Rate",
            f"{avg_poverty:.2f}%"
        )

        st.divider()

        if pd.notna(correlation):

            st.metric(
                "Pearson Correlation",
                f"{correlation:.3f}"
            )

            if correlation < 0:
                st.info(
                    "The selected data shows a negative "
                    "relationship between median household "
                    "income and absolute poverty."
                )

            elif correlation > 0:
                st.info(
                    "The selected data shows a positive "
                    "relationship between median household "
                    "income and absolute poverty."
                )

            else:
                st.info(
                    "The selected data shows no linear "
                    "correlation between the two variables."
                )

        else:
            st.info(
                "Correlation cannot be calculated because "
                "the selected values do not have sufficient variation."
            )

    st.divider()

    # --------------------------------------------------
    # SCATTER PLOT
    # --------------------------------------------------
    st.subheader(
        "Median Household Income vs Absolute Poverty"
    )

    st.write(
        "Each point represents a parliamentary constituency. "
        "The horizontal axis shows median household income, "
        "while the vertical axis shows the absolute poverty rate. "
        "Hover over the points to explore individual values."
    )

    # Create trendline when there are enough valid observations
    # and more than one distinct income value.
    if (
        len(df_chart) >= 2
        and df_chart["income_median"].nunique() > 1
    ):

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

    # Chart layout
    fig.update_layout(
        template="plotly_white",
        title={
            "text": (
                "Relationship Between Median Household Income "
                "and Absolute Poverty in 2024"
            ),
            "x": 0.5,
            "xanchor": "center"
        },
        height=650,
        showlegend=False,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_color="black"
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

    st.caption(
        "The red line represents the linear trendline. "
        "Hover over each point to view constituency details."
    )

    st.divider()

    # --------------------------------------------------
    # INTERPRETATION / DISCUSSION
    # --------------------------------------------------
    st.subheader("Interpretation / Discussion")

    st.markdown("**Observed Patterns and Relationships**")

    if pd.notna(correlation):

        if correlation < 0:
            relationship = "negative"

        elif correlation > 0:
            relationship = "positive"

        else:
            relationship = "no linear"

        correlation_strength = abs(correlation)

        if correlation_strength < 0.30:
            strength = "weak"

        elif correlation_strength < 0.70:
            strength = "moderate"

        else:
            strength = "strong"

        st.write(
            f"The scatter plot and Pearson correlation "
            f"coefficient indicate a {strength} {relationship} "
            f"linear relationship between median household "
            f"income and absolute poverty rates. The correlation "
            f"value is {correlation:.3f}."
        )

        if correlation < 0:
            st.write(
                "The downward direction of the relationship "
                "suggests that constituencies with higher "
                "median household income generally tend to "
                "have lower absolute poverty rates."
            )

        elif correlation > 0:
            st.write(
                "The upward direction of the relationship "
                "suggests that constituencies with higher "
                "median household income also tend to have "
                "higher absolute poverty rates in the selected data."
            )

        else:
            st.write(
                "The correlation indicates no linear association "
                "between the two variables in the selected data."
            )

    else:

        st.write(
            "A linear relationship could not be established "
            "because there is insufficient variation in the "
            "selected data."
        )

    st.markdown("**Key Findings**")

    st.write(
        f"- The highest absolute poverty rate was recorded "
        f"in {highest_poverty['parlimen']}, at "
        f"{highest_poverty['poverty_absolute']:.2f}%."
    )

    st.write(
        f"- The lowest absolute poverty rate was recorded "
        f"in {lowest_poverty['parlimen']}, at "
        f"{lowest_poverty['poverty_absolute']:.2f}%."
    )

    st.write(
        f"- The average median household income across "
        f"the selected constituencies was RM {avg_income:,.2f}."
    )

    st.write(
        f"- The average absolute poverty rate across "
        f"the selected constituencies was {avg_poverty:.2f}%."
    )

    st.markdown("**Anomalies and Data Patterns**")

    st.write(
        "Some data points may appear further away from the "
        "trendline. These points represent constituencies "
        "where the observed poverty rate differs from the "
        "general linear pattern. Such variations suggest "
        "that median household income alone may not explain "
        "all differences in poverty rates."
    )

    st.markdown("**Scientific Meaning and Relevance**")

    st.write(
        "Median household income represents the middle value "
        "of household income, while the absolute poverty rate "
        "indicates the proportion of households or population "
        "classified as living in absolute poverty according "
        "to the DOSM measure. Examining both variables helps "
        "identify socioeconomic patterns across constituencies."
    )

    st.write(
        "However, correlation does not establish causation. "
        "Other factors, such as employment opportunities, "
        "household size, education and cost of living, may "
        "also influence poverty conditions."
    )

    st.write(
        "This visualization fulfils the objective of "
        "investigating the relationship between median "
        "household income and absolute poverty rates "
        "across parliamentary constituencies in Selangor in 2024."
    )

    st.divider()

    # --------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------
    st.subheader("Dataset Preview")

    st.write(
        "The table below displays household income and "
        "absolute poverty information for each selected "
        "parliamentary constituency in 2024."
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
    ).copy()

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
        "Population, Household Income and Household Poverty "
        "datasets. Visualization year: 2024."
    )

except Exception as e:

    st.error(
        "Unable to display this visualization. "
        "Please check the dataset and column names."
    )

    st.exception(e)
