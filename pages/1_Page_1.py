
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Median Household Income Trends",
    page_icon="📈",
    layout="wide"
)

# --------------------------------------------------
# 2. SIDEBAR NAVIGATION
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

st.sidebar.divider()

st.sidebar.subheader("Dataset Information")
st.sidebar.write("**Source:** DOSM")
st.sidebar.write("**Location:** Selangor")
st.sidebar.write("**Period:** 2022–2024")
st.sidebar.write("**Variable:** Median Household Income")


# --------------------------------------------------
# 3. DATA LOADING
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

    # Focus on the selected study period
    result = result[
        result["year"].between(2022, 2024)
    ].copy()

    return result


# --------------------------------------------------
# 4. SECTION AND DESCRIPTION
# --------------------------------------------------
st.title("Page 1: Median Household Income Trends")

st.subheader("Section 1: Household Income Analysis")

st.write("""
This section examines the changes in median household income
across parliamentary constituencies in Selangor between 2022
and 2024. The analysis uses household income data obtained
from the Department of Statistics Malaysia (DOSM).
""")

st.subheader("Description")

st.write("""
Median household income represents the middle value of
household income when all households are arranged from
lowest to highest. This visualization uses interactive
charts to explore income trends, compare constituencies,
and identify differences in household income over the
selected period.
""")

# --------------------------------------------------
# 5. OBJECTIVE STATEMENT
# --------------------------------------------------
st.subheader("Visualization Objective")

st.markdown("""
**To examine changes in median household income across
parliamentary constituencies in Selangor from 2022 to 2024.**
""")

st.divider()


# --------------------------------------------------
# 6. MAIN VISUALIZATION
# --------------------------------------------------
try:

    df_selangor = get_selangor_data()

    if df_selangor.empty:
        st.warning(
            "No Selangor data is available for 2022–2024."
        )
        st.stop()

    # --------------------------------------------------
    # CONSTITUENCY FILTER
    # --------------------------------------------------
    st.subheader("Explore the Data")

    constituencies = sorted(
        df_selangor["parlimen"].dropna().unique()
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

    df_filtered = df_selangor[
        df_selangor["parlimen"].isin(
            selected_constituencies
        )
    ].copy()

    # --------------------------------------------------
    # PREPARE YEARLY DATA
    # --------------------------------------------------
    yearly_income = (
        df_filtered.groupby("year")["income_median"]
        .median()
        .reset_index()
        .sort_values("year")
    )

    if yearly_income.empty:
        st.warning("No income data is available.")
        st.stop()

    first_year = int(yearly_income["year"].min())
    latest_year = int(yearly_income["year"].max())

    first_income = yearly_income.iloc[0]["income_median"]
    latest_income = yearly_income.iloc[-1]["income_median"]

    income_change = latest_income - first_income

    percentage_change = (
        (income_change / first_income) * 100
        if first_income != 0
        else 0
    )

    # --------------------------------------------------
    # 7. SUMMARY BOX
    # --------------------------------------------------
    st.subheader("Summary of Key Findings")

    if income_change > 0:
        trend_description = (
            "Median household income increased "
            "during the selected period."
        )
    elif income_change < 0:
        trend_description = (
            "Median household income decreased "
            "during the selected period."
        )
    else:
        trend_description = (
            "Median household income remained unchanged "
            "during the selected period."
        )

    st.markdown(
        f"""
        <div style="
            background-color: #E8F4FD;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #2171B5;
            color: #172B4D;
        ">
            <h4 style="color: #174A75;">
                Key Income Findings
            </h4>
            <p>
                The median household income changed from
                <b>RM {first_income:,.2f}</b> in
                <b>{first_year}</b> to
                <b>RM {latest_income:,.2f}</b> in
                <b>{latest_year}</b>.
            </p>
            <p>
                This represents a change of
                <b>RM {income_change:,.2f}</b>
                (<b>{percentage_change:+.2f}%</b>).
            </p>
            <p>
                <b>Overall finding:</b> {trend_description}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # KPI metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Starting Year",
        first_year
    )

    col2.metric(
        "Latest Year",
        latest_year
    )

    col3.metric(
        "Latest Median Income",
        f"RM {latest_income:,.0f}"
    )

    col4.metric(
        "Income Change",
        f"RM {income_change:,.0f}",
        f"{percentage_change:+.2f}%"
    )

    st.divider()

    # --------------------------------------------------
    # VISUALIZATION 1: LINE CHART
    # --------------------------------------------------
    st.subheader(
        "Visualization 1: Yearly Median Household Income"
    )

    st.write("""
    This line chart illustrates changes in median household
    income across the selected constituencies over time.
    Each point represents the median of the constituency-level
    median household income values for that year.
    """)

    chart_data = yearly_income.copy()

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

    fig1 = px.line(
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

    fig1.update_traces(
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

    fig1.update_layout(
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
        fig1,
        use_container_width=True
    )

    st.caption(
        "Hover over each point to view income values and changes."
    )

    # Interpretation
    st.markdown("**Interpretation:**")

    st.write(
        f"The chart shows that median household income "
        f"{'increased' if income_change > 0 else 'decreased' if income_change < 0 else 'remained unchanged'} "
        f"from RM {first_income:,.2f} in {first_year} "
        f"to RM {latest_income:,.2f} in {latest_year}. "
        f"The overall change was {percentage_change:+.2f}%."
    )

    st.divider()

    # --------------------------------------------------
    # VISUALIZATION 2: HORIZONTAL BAR CHART
    # --------------------------------------------------
    st.subheader(
        "Visualization 2: Median Income by Constituency"
    )

    st.write("""
    This horizontal bar chart compares median household
    income across the selected parliamentary constituencies
    for the latest available year. It helps identify
    differences in income levels between constituencies.
    """)

    latest_data = df_filtered[
        df_filtered["year"] == latest_year
    ].copy()

    constituency_income = (
        latest_data.groupby("parlimen")["income_median"]
        .median()
        .reset_index()
        .sort_values("income_median", ascending=True)
    )

    fig2 = px.bar(
        constituency_income,
        x="income_median",
        y="parlimen",
        orientation="h",
        text="income_median",
        labels={
            "income_median": "Median Household Income (RM)",
            "parlimen": "Parliamentary Constituency"
        }
    )

    fig2.update_traces(
        marker_color="#2171B5",
        texttemplate="RM %{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Median Income: RM %{x:,.2f}"
            "<extra></extra>"
        )
    )

    fig2.update_layout(
        template="plotly_white",
        title={
            "text": f"Median Household Income by Constituency ({latest_year})",
            "x": 0.5,
            "xanchor": "center"
        },
        height=max(
            550,
            constituency_income["parlimen"].nunique() * 35
        ),
        margin=dict(l=150, r=100, t=80, b=60),
        xaxis_title="Median Household Income (RM)",
        yaxis_title="Parliamentary Constituency"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.markdown("**Interpretation:**")

    highest_row = constituency_income.loc[
        constituency_income["income_median"].idxmax()
    ]

    lowest_row = constituency_income.loc[
        constituency_income["income_median"].idxmin()
    ]

    st.write(
        f"In {latest_year}, **{highest_row['parlimen']}** "
        f"recorded the highest median household income "
        f"at RM {highest_row['income_median']:,.2f}, while "
        f"**{lowest_row['parlimen']}** recorded the lowest "
        f"at RM {lowest_row['income_median']:,.2f}. "
        f"This highlights the differences in median household "
        f"income between parliamentary constituencies."
    )

    st.divider()

    # --------------------------------------------------
    # VISUALIZATION 3: HEATMAP
    # --------------------------------------------------
    st.subheader(
        "Visualization 3: Income Distribution Heatmap"
    )

    st.write("""
    This heatmap displays median household income across
    parliamentary constituencies and years. Different
    colour intensities represent different income levels,
    allowing users to identify patterns and changes
    across constituencies over time.
    """)

    heatmap_data = (
        df_filtered.pivot_table(
            index="parlimen",
            columns="year",
            values="income_median",
            aggfunc="median"
        )
    )

    # Sort constituencies by the latest available year
    if latest_year in heatmap_data.columns:
        heatmap_data = heatmap_data.sort_values(
            by=latest_year,
            ascending=False
        )

    fig3 = px.imshow(
        heatmap_data,
        labels={
            "x": "Year",
            "y": "Parliamentary Constituency",
            "color": "Median Income (RM)"
        },
        color_continuous_scale="Blues",
        aspect="auto",
        text_auto=".0f"
    )

    fig3.update_layout(
        template="plotly_white",
        title={
            "text": "Median Household Income by Year and Constituency",
            "x": 0.5,
            "xanchor": "center"
        },
        height=max(
            600,
            len(heatmap_data) * 30
        ),
        xaxis_title="Year",
        yaxis_title="Parliamentary Constituency"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.markdown("**Interpretation:**")

    st.write("""
    The heatmap uses colour intensity to represent differences
    in median household income. Darker shades indicate
    relatively higher income values, while lighter shades
    indicate relatively lower income values. Comparing
    colours across years helps users identify changes in
    income patterns and differences between constituencies.
    """)

    st.divider()

    # --------------------------------------------------
    # 8. YEARLY INCOME SUMMARY TABLE
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

    # --------------------------------------------------
    # 9. DATASET PREVIEW
    # --------------------------------------------------
    st.subheader("Dataset Preview")

    st.write("""
    The table below displays the median household income
    records for the selected parliamentary constituencies.
    """)

    preview_data = df_filtered[
        ["year", "parlimen", "income_median"]
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
    # 10. DATA SOURCE
    # --------------------------------------------------
    st.divider()

    st.caption(
        "Source: Department of Statistics Malaysia (DOSM). "
        "Population and Household Income datasets, 2020–2024. "
        "Analysis period: 2022–2024."
    )

except Exception as e:

    st.error(
        f"An error occurred while loading the data: {e}"
    )

    st.info(
        "Please check the dataset URLs, column names, "
        "and requirements.txt file."
    )
