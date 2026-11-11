
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Median Household Income Trends",
    page_icon="📈",
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
    result["year"] = result["date"].dt.year

    return result


# --------------------------------------------------
# SECTION AND PAGE DESCRIPTION
# --------------------------------------------------
st.title("Median Household Income Trends in Selangor")

st.markdown("### Section 2.1: Median Household Income Trends")

st.markdown("**Description**")

st.write(
    "This visualization presents the changes in median "
    "household income across parliamentary constituencies "
    "in Selangor between 2022 and 2024. A line chart is used "
    "to display yearly income patterns and highlight changes "
    "in household income over the selected period."
)

st.markdown("**Objective Statement**")

st.info(
    "To examine changes in median household income across "
    "parliamentary constituencies in Selangor from 2022 to 2024."
)

st.divider()

# --------------------------------------------------
# DISPLAY DATA AND VISUALIZATION
# --------------------------------------------------
try:

    df_selangor = get_selangor_data()

    if df_selangor.empty:
        st.warning("No Selangor data is available.")
        st.stop()

    # Filter visualization period: 2022–2024
    df_selangor = df_selangor[
        df_selangor["year"].between(2022, 2024)
    ].copy()

    if df_selangor.empty:
        st.warning(
            "No income records were found for 2022–2024."
        )
        st.stop()

    # --------------------------------------------------
    # CONSTITUENCY FILTER
    # --------------------------------------------------
    st.subheader("Explore the Visualization")

    constituencies = sorted(
        df_selangor["parlimen"].dropna().unique()
    )

    selected_constituencies = st.multiselect(
        "Select Parliamentary Constituencies",
        options=constituencies,
        default=constituencies
    )

    if not selected_constituencies:
        st.warning("Please select at least one constituency.")
        st.stop()

    df_filtered = df_selangor[
        df_selangor["parlimen"].isin(
            selected_constituencies
        )
    ].copy()

    # --------------------------------------------------
    # YEARLY MEDIAN INCOME CALCULATION
    # --------------------------------------------------
    chart_data = (
        df_filtered.groupby("year")["income_median"]
        .median()
        .reset_index()
        .sort_values("year")
    )

    if chart_data.empty:
        st.warning("No income data is available.")
        st.stop()

    # Calculate income changes
    chart_data["income_change"] = (
        chart_data["income_median"].diff()
    )

    chart_data["percentage_change"] = (
        chart_data["income_median"].pct_change() * 100
    )

    chart_data["income_change"] = (
        chart_data["income_change"].fillna(0)
    )

    chart_data["percentage_change"] = (
        chart_data["percentage_change"].fillna(0)
    )

    # Get starting and latest values
    first_year = int(chart_data.iloc[0]["year"])
    latest_year = int(chart_data.iloc[-1]["year"])

    first_income = chart_data.iloc[0]["income_median"]
    latest_income = chart_data.iloc[-1]["income_median"]

    income_change = latest_income - first_income

    percentage_change = (
        (income_change / first_income) * 100
        if first_income != 0
        else 0
    )

    # --------------------------------------------------
    # SUMMARY BOX
    # --------------------------------------------------
    st.subheader("Summary Box")

    st.write(
        "The following indicators provide a quick overview "
        "of median household income changes during the "
        "selected period."
    )

    with st.container(border=True):

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Starting Income",
            f"RM {first_income:,.0f}",
            help=f"Median income in {first_year}"
        )

        col2.metric(
            "Latest Income",
            f"RM {latest_income:,.0f}",
            help=f"Median income in {latest_year}"
        )

        col3.metric(
            "Total Income Change",
            f"RM {income_change:,.0f}",
            delta=f"{percentage_change:+.2f}%"
        )

        col4.metric(
            "Selected Constituencies",
            len(selected_constituencies)
        )

        if income_change > 0:
            st.success(
                f"Median household income increased by "
                f"RM {income_change:,.0f} "
                f"({percentage_change:.2f}%) between "
                f"{first_year} and {latest_year}."
            )

        elif income_change < 0:
            st.warning(
                f"Median household income decreased by "
                f"RM {abs(income_change):,.0f} "
                f"({abs(percentage_change):.2f}%) between "
                f"{first_year} and {latest_year}."
            )

        else:
            st.info(
                "Median household income remained unchanged "
                "between the selected years."
            )

    st.divider()

    # --------------------------------------------------
    # LINE CHART
    # --------------------------------------------------
    st.subheader("Median Household Income Trends")

    st.write(
        "The line chart illustrates yearly changes in median "
        "household income. Each point represents the median "
        "of the selected constituencies for that year."
    )

    fig = px.line(
        chart_data,
        x="year",
        y="income_median",
        markers=True,
        text="income_median",
        custom_data=[
            "income_change",
            "percentage_change"
        ],
        labels={
            "year": "Year",
            "income_median": "Median Household Income (RM)"
        }
    )

    fig.update_traces(
        mode="lines+markers+text",
        line=dict(width=3),
        marker=dict(
            size=14,
            symbol="circle",
            line=dict(
                width=2,
                color="white"
            )
        ),
        texttemplate="RM %{y:,.0f}",
        textposition="top center",
        hovertemplate=(
            "<b>Year: %{x}</b><br>"
            "Median Income: RM %{y:,.2f}<br>"
            "Income Change: RM %{customdata[0]:,.2f}<br>"
            "Percentage Change: %{customdata[1]:.2f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=550,
        title={
            "text": "Yearly Median Household Income (2022–2024)",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=1
        ),
        yaxis=dict(
            title="Median Household Income (RM)",
            tickformat=",.0f"
        ),
        hovermode="closest"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "Hover over each point to view median income, "
        "income change and percentage change."
    )

    st.divider()

    # --------------------------------------------------
    # INTERPRETATION / DISCUSSION
    # --------------------------------------------------
    st.subheader("Interpretation / Discussion")

    st.markdown("**Observed Patterns and Trends**")

    if income_change > 0:

        st.write(
            f"The line chart shows an overall upward trend "
            f"in median household income from {first_year} "
            f"to {latest_year}. The median income increased "
            f"from RM {first_income:,.0f} to "
            f"RM {latest_income:,.0f}, representing an "
            f"increase of RM {income_change:,.0f} "
            f"({percentage_change:.2f}%)."
        )

    elif income_change < 0:

        st.write(
            f"The line chart shows an overall downward trend "
            f"in median household income from {first_year} "
            f"to {latest_year}. The median income decreased "
            f"from RM {first_income:,.0f} to "
            f"RM {latest_income:,.0f}, representing a "
            f"decrease of RM {abs(income_change):,.0f} "
            f"({abs(percentage_change):.2f}%)."
        )

    else:

        st.write(
            "The chart shows that median household income "
            "remained at the same level between the first "
            "and latest available years."
        )

    # Highest and lowest yearly values
    highest_row = chart_data.loc[
        chart_data["income_median"].idxmax()
    ]

    lowest_row = chart_data.loc[
        chart_data["income_median"].idxmin()
    ]

    st.markdown("**Key Findings**")

    st.write(
        f"- The highest median household income was recorded "
        f"in {int(highest_row['year'])}, at "
        f"RM {highest_row['income_median']:,.0f}."
    )

    st.write(
        f"- The lowest median household income was recorded "
        f"in {int(lowest_row['year'])}, at "
        f"RM {lowest_row['income_median']:,.0f}."
    )

    st.write(
        "- The line chart allows users to identify changes "
        "in income levels and compare the overall trend "
        "across the selected years."
    )

    st.markdown("**Scientific Meaning and Relevance**")

    st.write(
        "Median household income is an indicator of the "
        "income level of households. An increase in the "
        "median may suggest an improvement in the income "
        "position of households represented in the selected "
        "constituencies. However, this does not necessarily "
        "mean that every household experienced an income "
        "increase, as the median represents the middle "
        "value of the income distribution."
    )

    st.write(
        "This visualization supports the objective of "
        "examining changes in median household income "
        "across parliamentary constituencies in Selangor "
        "from 2022 to 2024."
    )

    st.divider()

    # --------------------------------------------------
    # YEARLY INCOME SUMMARY TABLE
    # --------------------------------------------------
    st.subheader("Yearly Income Summary")

    display_data = chart_data.copy()

    display_data["income_median"] = (
        display_data["income_median"].map(
            lambda x: f"RM {x:,.2f}"
        )
    )

    display_data["income_change"] = (
        display_data["income_change"].map(
            lambda x: f"RM {x:,.2f}"
        )
    )

    display_data["percentage_change"] = (
        display_data["percentage_change"].map(
            lambda x: f"{x:.2f}%"
        )
    )

    display_data.columns = [
        "Year",
        "Median Household Income",
        "Income Change",
        "Percentage Change"
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------
    st.subheader("Dataset Preview")

    st.write(
        "The table below displays the selected parliamentary "
        "constituency records used in this visualization."
    )

    preview_columns = [
        "year",
        "parlimen",
        "income_median"
    ]

    preview_data = df_filtered[
        preview_columns
    ].copy()

    preview_data = preview_data.sort_values(
        ["year", "parlimen"]
    )

    preview_data.columns = [
        "Year",
        "Parliamentary Constituency",
        "Median Household Income (RM)"
    ]

    st.dataframe(
        preview_data,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------
    st.caption(
        "Source: Department of Statistics Malaysia (DOSM). "
        "Population and Household Income datasets, 2020–2024. "
        "Visualization period: 2022–2024."
    )

except Exception as e:

    st.error(
        f"An error occurred while loading the data: {e}"
    )

    st.info(
        "Please check the dataset URLs, column names, "
        "and requirements.txt file."
    )
