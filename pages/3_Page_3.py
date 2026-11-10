import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Mean Household Income Comparison",
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
st.header("Mean Household Income Comparison in Selangor", divider="gray")

st.markdown("""
This visualization compares mean household income across parliamentary
constituencies in Selangor between 2022 and 2024.
""")

try:
    df_selangor = get_selangor_data()

    # Filter 2022 and 2024
    df_selangor["year"] = df_selangor["date"].dt.year.astype(str)

    df_selangor = df_selangor[
        df_selangor["year"].isin(["2022", "2024"])
    ].copy()

    if df_selangor.empty:
        st.warning("No records were found for 2022 and 2024.")

    else:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)

        df_2022 = df_selangor[df_selangor["year"] == "2022"]
        df_2024 = df_selangor[df_selangor["year"] == "2024"]

        avg_2022 = df_2022["income_mean"].mean()
        avg_2024 = df_2024["income_mean"].mean()

        percentage_change = (
            ((avg_2024 - avg_2022) / avg_2022) * 100
            if pd.notna(avg_2022) and avg_2022 != 0
            else None
        )

        col1.metric(
            "Comparison Period",
            "2022–2024",
            border=True
        )

        col2.metric(
            "Constituencies",
            df_selangor["parlimen"].nunique(),
            border=True
        )

        col3.metric(
            "Average Income (2022)",
            f"RM {avg_2022:,.0f}" if pd.notna(avg_2022) else "N/A",
            border=True
        )

        col4.metric(
            "Average Income (2024)",
            f"RM {avg_2024:,.0f}" if pd.notna(avg_2024) else "N/A",
            delta=f"{percentage_change:+.2f}%" if percentage_change is not None else None,
            border=True
        )

        st.divider()

        # Interactive filter
        st.subheader("Explore Income Comparison")

        selected_years = st.multiselect(
            "Select Years",
            options=["2022", "2024"],
            default=["2022", "2024"]
        )

        selected_constituencies = st.multiselect(
            "Select Parliamentary Constituencies",
            options=sorted(df_selangor["parlimen"].unique()),
            default=sorted(df_selangor["parlimen"].unique())
        )

        df_chart = df_selangor[
            (df_selangor["year"].isin(selected_years))
            & (df_selangor["parlimen"].isin(selected_constituencies))
        ].copy()

        # Sort based on 2024 income
        sort_order = (
            df_selangor[df_selangor["year"] == "2024"]
            .sort_values("income_mean", ascending=False)["parlimen"]
            .tolist()
        )

        # Grouped horizontal bar chart
        st.subheader("Mean Household Income by Constituency")

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
                title="Mean Household Income: 2022 vs 2024",
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
                title_x=0.5,
                height=max(600, df_chart["parlimen"].nunique() * 45),
                bargap=0.25,
                margin=dict(l=150, r=120, t=100, b=60),
                xaxis_title="Mean Household Income (RM)",
                yaxis_title="Parliamentary Constituency",
                legend_title="Year",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="lightgrey"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Please select at least one year and constituency.")

        st.divider()

        # Dataset Preview
        st.subheader("Dataset Preview")

        st.dataframe(
            df_selangor[
                ["year", "parlimen", "income_mean",
                 "income_median", "poverty_absolute"]
            ].sort_values(
                ["parlimen", "year"]
            ),
            use_container_width=True
        )

        # Source
        st.caption(
            "Source: Department of Statistics Malaysia (DOSM)."
        )

except Exception as e:
    st.error(
        "Unable to display this visualization. "
        "Please check the dataset and column names."
    )
    st.exception(e)
