import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Selangor Socioeconomic Dashboard",
    page_icon="📊",
    layout="wide"
)

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

    # Keep the 2020–2024 period used in the original notebook.
    df_pop = df_pop[df_pop["date"].dt.year.between(2020, 2024)]
    df_inc = df_inc[df_inc["date"].dt.year.between(2020, 2024)]
    df_pov = df_pov[df_pov["date"].dt.year.between(2020, 2024)]

    # Retain the overall population category used in the original analysis.
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

st.title("Selangor Socioeconomic Dashboard")
st.markdown(
    """
    This dashboard explores household income and absolute poverty across
    parliamentary constituencies in Selangor using DOSM data from 2020 to 2024.

    Use the navigation menu on the left to explore the three visualization pages.
    """
)

try:
    data = load_data()
    selangor = data[data["state"] == "Selangor"].copy()

    if selangor.empty:
        st.warning("No Selangor records were found in the selected dataset.")
    else:
        latest_year = int(selangor["date"].dt.year.max())
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest data year", latest_year)
        c2.metric("Parliamentary constituencies", selangor["parlimen"].nunique())
        c3.metric("Records (2020–2024)", f"{len(selangor):,}")

        st.subheader("About the dataset")
        st.write(
            "The analysis combines DOSM parliamentary-level population, "
            "household income and poverty datasets. The analysis focuses on "
            "Selangor and uses the 2020–2024 period."
        )
        st.info(
            "Choose **Page 1**, **Page 2**, or **Page 3** from the sidebar "
            "to view the detailed charts."
        )
except Exception as e:
    st.error("The data could not be loaded. Check your internet connection and the dataset URLs.")
    st.exception(e)
