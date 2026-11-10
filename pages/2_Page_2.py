import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Income and Absolute Poverty",
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
st.header("Income and Absolute Poverty in Selangor", divider="gray")

st.markdown("""
This visualization examines the relationship between median household
income and absolute poverty rates across parliamentary constituencies
in Selangor for the latest available year.
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

        # KPI Metrics
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

        # Interactive filter
        st.subheader("Explore the Relationship")

        selected_constituencies = st.multiselect(
            "Select Parliamentary Constituencies",
            options=sorted(df_latest["parlimen"].unique()),
            default=sorted(df_latest["parlimen"].unique())
        )

        df_chart = df_latest[
            df_latest["parlimen"].isin(selected_constituencies)
        ].copy()

        # Scatter Plot
        st.subheader("Median Income vs Absolute Poverty")

        if len(df_chart) >= 2:
            fig = px.scatter(
                df_chart,
                x="income_median",
                y="poverty_absolute",
                hover_name="parlimen",
                hover_data={
                    "income_median": ":,.0f",
                    "income_mean": ":,.0f",
                    "poverty_absolute": ":.2f"
                },
                trendline="ols",
                trendline_color_override="#E74C3C",
                title=f"Relationship Between Median Household Income and Absolute Poverty ({latest_year})",
                labels={
                    "income_median": "Median Household Income (RM)",
                    "poverty_absolute": "Absolute Poverty Rate (%)"
                }
            )

        else:
            fig = px.scatter(
                df_chart,
                x="income_median",
                y="poverty_absolute",
                hover_name="parlimen",
                title="Median Income vs Absolute Poverty",
                labels={
                    "income_median": "Median Household Income (RM)",
                    "poverty_absolute": "Absolute Poverty Rate (%)"
                }
            )

        fig.update_traces(
            marker=dict(
                size=12,
                opacity=0.8,
                line=dict(width=1, color="black")
            ),
            selector=dict(mode="markers")
        )

        fig.update_layout(
            template="plotly_grey",
            title_x=0.5,
            height=650,
            showlegend=False,
            hoverlabel=dict(
                bgcolor="grey",
                font_size=12
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="lightgrey"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="lightgrey"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info("""
        **How to interpret the chart:**

        - Each point represents one parliamentary constituency.
        - The X-axis represents median household income.
        - The Y-axis represents the absolute poverty rate.
        - The red trendline shows the overall relationship between the two variables.
        """)

        st.divider()

        # Dataset Preview
        st.subheader("Dataset Preview")

        st.dataframe(
            df_latest[
                ["parlimen", "income_median", "income_mean", "poverty_absolute"]
            ].sort_values("poverty_absolute", ascending=False),
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
