
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Mean Household Income Comparison",
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

    for frame in (df_pop, df_inc, df_pov):
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
    result["year"] = result["date"].dt.year.astype(str)

    return result


# --------------------------------------------------
# SECTION AND PAGE DESCRIPTION
# --------------------------------------------------
st.title("Mean Household Income Comparison in Selangor")

st.markdown(
    "### Section 2.3: Mean Household Income Comparison (2022–2024)"
)

st.markdown("**Description**")

st.write(
    "This visualization uses a grouped horizontal bar chart "
    "to compare mean household income across parliamentary "
    "constituencies in Selangor between 2022 and 2024. "
    "Different colours represent the two comparison years, "
    "allowing users to identify differences in mean household "
    "income between constituencies and observe changes over time."
)

st.markdown("**Objective Statement**")

st.info(
    "To compare mean household income across parliamentary "
    "constituencies in Selangor between 2022 and 2024 and "
    "identify the differences in income levels over the period."
)

st.divider()


# --------------------------------------------------
# MAIN VISUALIZATION
# --------------------------------------------------
try:

    df_selangor = get_selangor_data()

    # Filter 2022 and 2024
    df_selangor = df_selangor[
        df_selangor["year"].isin(["2022", "2024"])
    ].copy()

    if df_selangor.empty:

        st.warning(
            "No records were found for 2022 and 2024."
        )
        st.stop()

    # --------------------------------------------------
    # INTERACTIVE FILTERS
    # --------------------------------------------------
    st.subheader("Explore Income Comparison")

    selected_years = st.multiselect(
        "Select Years",
        options=["2022", "2024"],
        default=["2022", "2024"]
    )

    constituencies = sorted(
        df_selangor["parlimen"].dropna().unique()
    )

    selected_constituencies = st.multiselect(
        "Select Parliamentary Constituencies",
        options=constituencies,
        default=constituencies
    )

    if not selected_years or not selected_constituencies:

        st.warning(
            "Please select at least one year and constituency."
        )
        st.stop()

    df_chart = df_selangor[
        (df_selangor["year"].isin(selected_years))
        & (
            df_selangor["parlimen"].isin(
                selected_constituencies
            )
        )
    ].copy()

    if df_chart.empty:

        st.warning(
            "No data is available for the selected filters."
        )
        st.stop()

    # --------------------------------------------------
    # CALCULATE YEARLY AVERAGES
    # --------------------------------------------------
    df_2022 = df_chart[
        df_chart["year"] == "2022"
    ]

    df_2024 = df_chart[
        df_chart["year"] == "2024"
    ]

    avg_2022 = df_2022["income_mean"].mean()
    avg_2024 = df_2024["income_mean"].mean()

    if (
        pd.notna(avg_2022)
        and pd.notna(avg_2024)
        and avg_2022 != 0
    ):

        income_change = avg_2024 - avg_2022

        percentage_change = (
            income_change / avg_2022
        ) * 100

    else:

        income_change = None
        percentage_change = None

    # --------------------------------------------------
    # CALCULATE CONSTITUENCY-LEVEL CHANGES
    # --------------------------------------------------
    comparison = df_chart.pivot_table(
        index="parlimen",
        columns="year",
        values="income_mean",
        aggfunc="mean"
    ).reset_index()

    # Ensure both year columns exist
    for year in ["2022", "2024"]:

        if year not in comparison.columns:
            comparison[year] = pd.NA

    comparison["income_change"] = (
        comparison["2024"] - comparison["2022"]
    )

    comparison["percentage_change"] = (
        comparison["income_change"]
        / comparison["2022"].replace(0, pd.NA)
    ) * 100

    valid_comparison = comparison.dropna(
        subset=["2022", "2024", "income_change"]
    )

    # --------------------------------------------------
    # SUMMARY BOX
    # --------------------------------------------------
    st.subheader("Summary Box")

    st.write(
        "The following indicators summarise the mean household "
        "income across the selected constituencies."
    )

    with st.container(border=True):

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Comparison Period",
            "2022–2024"
        )

        col2.metric(
            "Constituencies",
            df_chart["parlimen"].nunique()
        )

        col3.metric(
            "Average Income (2022)",
            (
                f"RM {avg_2022:,.0f}"
                if pd.notna(avg_2022)
                else "N/A"
            )
        )

        col4.metric(
            "Average Income (2024)",
            (
                f"RM {avg_2024:,.0f}"
                if pd.notna(avg_2024)
                else "N/A"
            ),
            delta=(
                f"{percentage_change:+.2f}%"
                if percentage_change is not None
                else None
            )
        )

        st.divider()

        if percentage_change is not None:

            if percentage_change > 0:

                st.success(
                    f"The average mean household income increased "
                    f"by RM {income_change:,.2f} "
                    f"({percentage_change:.2f}%) between 2022 and 2024."
                )

            elif percentage_change < 0:

                st.warning(
                    f"The average mean household income decreased "
                    f"by RM {abs(income_change):,.2f} "
                    f"({abs(percentage_change):.2f}%) between "
                    f"2022 and 2024."
                )

            else:

                st.info(
                    "The average mean household income remained "
                    "unchanged between 2022 and 2024."
                )

        else:

            st.info(
                "The average income change cannot be calculated "
                "because data for both years is required."
            )

    st.divider()

    # --------------------------------------------------
    # GROUPED HORIZONTAL BAR CHART
    # --------------------------------------------------
    st.subheader("Mean Household Income by Constituency")

    st.write(
        "The grouped horizontal bar chart compares the mean "
        "household income of each selected constituency. "
        "The light blue bars represent 2022, while the dark "
        "blue bars represent 2024."
    )

    # Sort constituencies according to 2024 income
    sort_order = (
        df_selangor[
            df_selangor["year"] == "2024"
        ]
        .sort_values(
            "income_mean",
            ascending=False
        )["parlimen"]
        .tolist()
    )

    if not df_chart.empty:

        fig = px.bar(
            df_chart,
            x="income_mean",
            y="parlimen",
            color="year",
            barmode="group",
            orientation="h",
            text="income_mean",
            category_orders={
                "parlimen": sort_order,
                "year": ["2022", "2024"]
            },
            color_discrete_map={
                "2022": "#9ECAE1",
                "2024": "#2171B5"
            },
            labels={
                "income_mean": "Mean Household Income (RM)",
                "parlimen": "Parliamentary Constituency",
                "year": "Year"
            },
            hover_data={
                "income_mean": ":,.0f",
                "income_median": ":,.0f",
                "poverty_absolute": ":.2f"
            }
        )

        fig.update_traces(
            texttemplate="RM %{x:,.0f}",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            template="plotly_white",
            title={
                "text": "Mean Household Income: 2022 vs 2024",
                "x": 0.5,
                "xanchor": "center"
            },
            height=max(
                600,
                df_chart["parlimen"].nunique() * 45
            ),
            bargap=0.25,
            margin=dict(
                l=150,
                r=120,
                t=100,
                b=60
            ),
            xaxis_title="Mean Household Income (RM)",
            yaxis_title="Parliamentary Constituency",
            legend_title="Year",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="lightgrey",
                tickformat=",.0f"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.caption(
        "Hover over the bars to view the mean household income "
        "and other available constituency information."
    )

    st.divider()

    # --------------------------------------------------
    # INTERPRETATION / DISCUSSION
    # --------------------------------------------------
    st.subheader("Interpretation / Discussion")

    st.markdown("**Observed Patterns and Trends**")

    if (
        pd.notna(avg_2022)
        and pd.notna(avg_2024)
    ):

        if avg_2024 > avg_2022:

            st.write(
                f"The chart shows an overall increase in average "
                f"mean household income from RM {avg_2022:,.2f} "
                f"in 2022 to RM {avg_2024:,.2f} in 2024. "
                f"This represents an increase of "
                f"{percentage_change:.2f}% across the selected "
                f"constituencies."
            )

        elif avg_2024 < avg_2022:

            st.write(
                f"The chart shows an overall decrease in average "
                f"mean household income from RM {avg_2022:,.2f} "
                f"in 2022 to RM {avg_2024:,.2f} in 2024. "
                f"This represents a decrease of "
                f"{abs(percentage_change):.2f}% across the selected "
                f"constituencies."
            )

        else:

            st.write(
                "The average mean household income remained "
                "unchanged between 2022 and 2024."
            )

    else:

        st.write(
            "A comparison of the overall average income cannot "
            "be made because data from both years is required."
        )

    st.markdown("**Key Findings**")

    if not valid_comparison.empty:

        highest_increase = valid_comparison.loc[
            valid_comparison["income_change"].idxmax()
        ]

        highest_decrease = valid_comparison.loc[
            valid_comparison["income_change"].idxmin()
        ]

        st.write(
            f"- The largest increase in mean household income "
            f"was recorded in {highest_increase['parlimen']}, "
            f"with an increase of RM "
            f"{highest_increase['income_change']:,.2f}."
        )

        st.write(
            f"- The smallest change or largest decrease was "
            f"recorded in {highest_decrease['parlimen']}, "
            f"with a change of RM "
            f"{highest_decrease['income_change']:,.2f}."
        )

        highest_2024 = valid_comparison.loc[
            valid_comparison["2024"].idxmax()
        ]

        st.write(
            f"- {highest_2024['parlimen']} recorded the highest "
            f"mean household income in 2024 among the "
            f"constituencies with data for both years, at "
            f"RM {highest_2024['2024']:,.2f}."
        )

    else:

        st.write(
            "Constituency-level changes cannot be calculated "
            "because matching records for both 2022 and 2024 "
            "are required."
        )

    st.markdown("**Anomalies and Differences**")

    st.write(
        "The differences in bar lengths indicate that mean "
        "household income is not distributed equally across "
        "all parliamentary constituencies. Some constituencies "
        "may record considerably higher income levels, while "
        "others may show smaller increases or decreases between "
        "the two years. These variations highlight differences "
        "in household income conditions across Selangor."
    )

    st.markdown("**Scientific Meaning and Relevance**")

    st.write(
        "Mean household income represents the average household "
        "income within a constituency. Comparing this indicator "
        "between 2022 and 2024 helps identify changes in average "
        "income levels and differences in socioeconomic "
        "conditions across geographical areas."
    )

    st.write(
        "An increase in mean household income may indicate "
        "improved average income conditions. However, the mean "
        "can be influenced by households with particularly high "
        "incomes and does not necessarily mean that every "
        "household experienced an income increase. Other factors, "
        "such as employment opportunities, economic conditions "
        "and cost of living, may also influence household income."
    )

    st.write(
        "This visualization fulfils the objective of comparing "
        "mean household income across parliamentary constituencies "
        "in Selangor between 2022 and 2024."
    )

    st.divider()

    # --------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------
    st.subheader("Dataset Preview")

    st.write(
        "The table below displays mean and median household "
        "income, together with absolute poverty rates, for "
        "the selected constituencies in 2022 and 2024."
    )

    preview_data = df_chart[
        [
            "year",
            "parlimen",
            "income_mean",
            "income_median",
            "poverty_absolute"
        ]
    ].sort_values(
        ["parlimen", "year"]
    )

    preview_data.columns = [
        "Year",
        "Parliamentary Constituency",
        "Mean Household Income (RM)",
        "Median Household Income (RM)",
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
        "Population, Household Income and Household Poverty datasets. "
        "Comparison years: 2022 and 2024."
    )

except Exception as e:

    st.error(
        "Unable to display this visualization. "
        "Please check the dataset and column names."
    )

    st.exception(e)
