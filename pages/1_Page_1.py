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
    result["year"] = result["date"].dt.year

    return result


# --------------------------------------------------
# MAIN PAGE
# --------------------------------------------------
st.title("Median Household Income Trends in Selangor")

st.write(
    "This page examines changes in median household income "
    "across parliamentary constituencies in Selangor "
    "from 2022 to 2024."
)

st.markdown(
    "**Visualization Objective:** To examine the changes "
    "in median household income across parliamentary "
    "constituencies in Selangor from 2022 to 2024."
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

    # --------------------------------------------------
    # CONSTITUENCY FILTER
    # --------------------------------------------------
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
    # KPI METRICS
    # --------------------------------------------------
    yearly_income = (
        df_filtered.groupby("year")["income_median"]
        .median()
        .reset_index()
        .sort_values("year")
    )

    if yearly_income.empty:
        st.warning("No income data is available for the selection.")
        st.stop()

    first_year = int(yearly_income["year"].min())
    latest_year = int(yearly_income["year"].max())

    first_income = yearly_income.iloc[0]["income_median"]
    latest_income = yearly_income.iloc[-1]["income_median"]

    income_change = latest_income - first_income

    if first_income != 0:
        percentage_change = (
            income_change / first_income
        ) * 100
    else:
        percentage_change = 0

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
        f"RM {latest_income:,.2f}"
    )

    col4.metric(
        "Income Change",
        f"RM {income_change:,.2f}",
        f"{percentage_change:+.2f}%"
    )

    st.divider()

    # --------------------------------------------------
    # LINE CHART WITH DETAILED DATA POINTS
    # --------------------------------------------------
    st.subheader(
        "Median Household Income Changes (2022–2024)"
    )

    st.write(
        "The line chart illustrates yearly changes in median "
        "household income. Each dot represents the median "
        "of the selected constituencies for that year."
    )

    chart_data = (
        df_filtered.groupby("year")["income_median"]
        .median()
        .reset_index()
        .sort_values("year")
    )

    # Calculate yearly income changes
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

    # Create line chart
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

    # Customize line and dots
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
            "text": "Yearly Median Household Income (2022-2024)",
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
        "Hover over each dot to view the median income, "
        "income change, and percentage change."
    )

    st.divider()

    # --------------------------------------------------
    # YEARLY INCOME DATA TABLE
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
        "The table below displays the selected Selangor "
        "parliamentary constituency records."
    )

    preview_columns = [
        "year",
        "parlimen",
        "income_median"
    ]

    preview_data = df_filtered[preview_columns].copy()

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
        "Household Income and Basic Amenities Survey data, 2020–2024."
    )

except Exception as e:

    st.error(
        f"An error occurred while loading the data: {e}"
    )

    st.info(
        "Please check the dataset URLs, column names, "
        "and requirements.txt file."
    )
