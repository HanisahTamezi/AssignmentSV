
# ==========================================
# LINE CHART WITH DETAILED DOTS
# ==========================================

st.subheader(
    "Median Household Income Trends (2020–2024)"
)

if df_filtered.empty:

    st.warning(
        "Please select at least one constituency "
        "to display the chart."
    )

else:

    # Calculate yearly median household income
    chart_data = (
        df_filtered
        .groupby("year")["income_median"]
        .median()
        .reset_index()
        .sort_values("year")
    )

    # Calculate annual income changes
    chart_data["income_change"] = (
        chart_data["income_median"].diff()
    )

    chart_data["percentage_change"] = (
        chart_data["income_median"].pct_change() * 100
    )

    # Format first year's change
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
        title="Median Household Income in Selangor (2020–2024)",
        labels={
            "year": "Year",
            "income_median": "Median Household Income (RM)"
        },
        custom_data=[
            "income_change",
            "percentage_change"
        ]
    )

    # Customize dots and connecting line
    fig.update_traces(
        mode="lines+markers+text",

        line=dict(
            width=3
        ),

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

        textfont=dict(
            size=12
        ),

        hovertemplate=(
            "<b>Year: %{x}</b><br>"
            "Median Household Income: RM %{y:,.2f}<br>"
            "Income Change: RM %{customdata[0]:+,.2f}<br>"
            "Percentage Change: %{customdata[1]:+.2f}%"
            "<extra></extra>"
        )
    )

    # Customize chart layout
    fig.update_layout(
        template="plotly_white",
        height=550,

        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=1
        ),

        yaxis=dict(
            title="Median Household Income (RM)",
            tickprefix="RM ",
            tickformat=",.0f"
        ),

        title_x=0.5,

        hovermode="closest",

        showlegend=False,

        margin=dict(
            l=80,
            r=50,
            t=100,
            b=70
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "Each dot represents the median of constituency-level "
        "median household incomes for the selected constituencies "
        "in that year. Hover over each dot for more details."
    )
