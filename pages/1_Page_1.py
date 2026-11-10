import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Median Household Income Trends",
    page_icon="📈",
    layout="wide"
)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("📊 Selangor Dashboard")
    st.caption("Socioeconomic Data Analysis")

    st.divider()

    st.subheader("Navigation")

    st.page_link(
        "sv_assignment.py",
        label="Home",
        icon="🏠"
    )

    st.page_link(
        "pages/1_Page_1.py",
        label="Median Household Income Trends",
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


# ==========================================
# GET SELANGOR DATA
# ==========================================

def get_selangor_data():

    data = load_data()

    result = data[
        data["state"] == "Selangor"
    ].copy()

    result["date"] = pd.to_datetime(result["date"])

    result["year"] = result["date"].dt.year

    return result


# ==========================================
# PAGE TITLE
# ==========================================

st.header(
    "Median Household Income Trends in Selangor",
    divider="gray"
)

st.markdown("""
This visualization examines changes in median household income
across parliamentary constituencies in Selangor from 2020 to 2024.

The line chart illustrates the overall trend in median household
income over the five-year period.
""")


# ==========================================
# MAIN VISUALIZATION
# ==========================================

try:

    df_selangor = get_selangor_data()

    if df_selangor.empty:

        st.warning("No Selangor data available.")

    else:

        # ==================================
        # CALCULATE YEARLY MEDIAN INCOME
        # ==================================

        # Calculate the median of constituency-level
        # median household incomes for each year.

        yearly_income = (
            df_selangor
            .groupby("year")["income_median"]
            .median()
            .reset_index()
        )

        yearly_income = yearly_income.sort_values("year")

        # ==================================
        # KPI METRICS
        # ==================================

        first_year = int(yearly_income["year"].min())
        latest_year = int(yearly_income["year"].max())

        first_income = yearly_income.loc[
            yearly_income["year"] == first_year,
            "income_median"
        ].iloc[0]

        latest_income = yearly_income.loc[
            yearly_income["year"] == latest_year,
            "income_median"
        ].iloc[0]

        income_change = latest_income - first_income

        percentage_change = (
            (income_change / first_income) * 100
            if first_income != 0 else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Starting Year",
            first_year,
            border=True
        )

        col2.metric(
            "Latest Year",
            latest_year,
            border=True
        )

        col3.metric(
            "Median Household Income",
            f"RM {latest_income:,.0f}",
            border=True
        )

        col4.metric(
            "Income Change",
            f"{percentage_change:+.2f}%",
            delta=f"RM {income_change:+,.0f}",
            border=True
        )

        st.divider()


        # ==================================
        # INTERACTIVE FILTER
        # ==================================

        st.subheader("Explore Income Trends")

        selected_constituencies = st.multiselect(
            "Select Parliamentary Constituencies",
            options=sorted(
                df_selangor["parlimen"].unique()
            ),
            default=sorted(
                df_selangor["parlimen"].unique()
            )
        )

        df_filtered = df_selangor[
            df_selangor["parlimen"].isin(
                selected_constituencies
            )
        ].copy()


        # ==================================
        # LINE CHART
        # ==================================

        st.subheader(
            "Median Household Income Trends (2020–2024)"
        )

        if df_filtered.empty:

            st.warning(
                "Please select at least one constituency "
                "to display the chart."
            )

        else:

            # Calculate yearly median income
            # based on selected constituencies.

            chart_data = (
                df_filtered
                .groupby("year")["income_median"]
                .median()
                .reset_index()
            )

            chart_data = chart_data.sort_values("year")

            fig = px.line(
                chart_data,
                x="year",
                y="income_median",
                markers=True,
                text="income_median",
                title="Median Household Income in Selangor (2020–2024)",
                labels={
                    "year": "Year",
                    "income_median": "Median Household Income (RM)"
                }
            )

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=9),
                texttemplate="RM %{y:,.0f}",
                textposition="top center",
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Median Household Income: RM %{y:,.2f}"
                    "<extra></extra>"
                )
            )

            fig.update_layout(
                template="plotly_white",
                height=500,
                xaxis=dict(
                    tickmode="linear",
                    dtick=1,
                    title="Year"
                ),
                yaxis_title="Median Household Income (RM)",
                title_x=0.5,
                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.divider()


        # ==================================
        # YEARLY DATASET PREVIEW
        # ==================================

        st.subheader("Yearly Median Household Income")

        st.write("""
        The table below presents the median of constituency-level
        median household incomes for each year.
        """)

        display_data = yearly_income.copy()

        display_data["income_median"] = (
            display_data["income_median"]
            .apply(lambda x: f"RM {x:,.2f}")
        )

        display_data.columns = [
            "Year",
            "Median Household Income"
        ]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


        # ==================================
        # SOURCE
        # ==================================

        st.caption(
            "Source: Department of Statistics Malaysia (DOSM). "
            "Household Income by Parliamentary Constituency, 2020–2024."
        )


except Exception as e:

    st.error(
        "Unable to display this visualization. "
        "Please check the dataset and column names."
    )

    st.exception(e)
