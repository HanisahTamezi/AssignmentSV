
import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Median Household Income",
    page_icon="📊",
    layout="wide"
)

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

    df_pop = df_pop[df_pop["date"].dt.year.between(2020, 2024)]
    df_inc = df_inc[df_inc["date"].dt.year.between(2020, 2024)]
    df_pov = df_pov[df_pov["date"].dt.year.between(2020, 2024)]

    df_pop = df_pop[
        (df_pop["sex"] == "both")
        & (df_pop["age"] == "overall")
        & (df_pop["ethnicity"] == "overall")
    ]

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


def get_selangor_data():
    data = load_data()
    result = data[data["state"] == "Selangor"].copy()
    result["date"] = pd.to_datetime(result["date"])
    return result


# Page title
st.header("Median Household Income in Selangor", divider="gray")

st.markdown("""
This visualization compares median household income across parliamentary
constituencies in Selangor for the latest available year (2020–2024).
""")

try:
    df_selangor = get_selangor_data()

    if df_selangor.empty:
        st.warning("No Selangor data available.")
    else:
        # Get latest year
        latest_year = int(df_selangor["date"].dt.year.max())

        df_latest = df_selangor[
            df_selangor["date"].dt.year == latest_year
        ].copy()

        # Sort income
        df_latest = df_latest.sort_values(
            "income_median",
            ascending=True
        )

        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Latest Data Year",
            latest_year,
            border=True
        )

        col2.metric(
            "Number of Constituencies",
            df_latest["parlimen"].nunique(),
            border=True
        )

        col3.metric(
            "Highest Median Income",
            f"RM {df_latest['income_median'].max():,.0f}",
            border=True
        )

        col4.metric(
            "Lowest Median Income",
            f"RM {df_latest['income_median'].min():,.0f}",
            border=True
        )

        st.divider()

        # Interactive filters
        st.subheader("Explore Household Income")

        selected_constituencies = st.multiselect(
            "Select Parliamentary Constituencies",
            options=sorted(df_latest["parlimen"].unique()),
            default=sorted(df_latest["parlimen"].unique())
        )

        df_chart = df_latest[
            df_latest["parlimen"].isin(selected_constituencies)
        ].copy()

        # Median Household Income Chart
        st.subheader("Median Household Income by Constituency")

        fig = px.bar(
            df_chart,
            x="income_median",
            y="parlimen",
            orientation="h",
            color="income_median",
            color_continuous_scale="Viridis",
            text="income_median",
            title=f"Median Household Income Across Selangor ({latest_year})",
            labels={
                "income_median": "Median Household Income (RM)",
                "parlimen": "Parliamentary Constituency"
            },
            hover_data={
                "income_median": ":,.0f",
                "income_mean": ":,.0f",
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
            height=max(500, len(df_chart) * 35),
            coloraxis_showscale=False,
            showlegend=False,
            margin=dict(l=150, r=100, t=80, b=60),
            xaxis_title="Median Household Income (RM)",
            yaxis_title="Parliamentary Constituency",
            title_x=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Dataset Preview
        st.subheader("Dataset Preview")

        st.dataframe(
            df_latest[
                ["parlimen", "income_median", "income_mean", "poverty_absolute"]
            ].sort_values("income_median", ascending=False),
            use_container_width=True
        )

        # Source
        st.caption(
            f"Source: Department of Statistics Malaysia (DOSM). "
            f"Latest available year: {latest_year}."
        )

except Exception as e:
    st.error(
        "Unable to display this visualization. "
        "Please check the dataset and column names."
    )
    st.exception(e)
