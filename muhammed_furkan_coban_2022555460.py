import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Streamlit config (must be the first Streamlit command)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DataVis Dashboard",
    layout="wide"
)

# ---------------------------------------------------------
# 1. Data loading
# ---------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    # Keep the string "None" as is, do not convert to NA
    df = pd.read_csv(path, keep_default_na=False)
    return df


df = load_data("Mental_Health_Lifestyle_CLEAN.csv")

st.title("Work, Activity and Country-Based Analysis")

# ---------------------------------------------------------
# 2. Helper: Stress level encoding
# ---------------------------------------------------------
# Numeric coding for stress level, mainly for color mapping
STRESS_CODE_MAP = {"Low": 0.0, "Moderate": 0.5, "High": 1.0}
df["Stress_Level_Code"] = df["Stress Level"].map(STRESS_CODE_MAP)

# Numeric axis for stress level in parallel coordinates (0=Low, 1=Moderate, 2=High)
STRESS_AXIS_MAP = {"Low": 0, "Moderate": 1, "High": 2}

# Custom color scale: Low = blue, Moderate = orange, High = green
STRESS_COLORSCALE = [
    [0.00, "#1f77b4"],  # Low
    [0.32, "#1f77b4"],

    [0.34, "#ff7f0e"],  # Moderate
    [0.66, "#ff7f0e"],

    [0.68, "#2ca02c"],  # High
    [1.00, "#2ca02c"],
]

# ---------------------------------------------------------
# Tab selection (pseudo-tabs using radio)
# ---------------------------------------------------------
tab_choice = st.radio(
    "Select chart:",
    (
        "4️⃣ Average Happiness by Country (Bar Chart)",
        "5️⃣ Mental Health by Country & Activity (Sunburst)",
        "6️⃣ Work / Screen Time vs Stress & Happiness (Parallel Coordinates)",
    ),
    horizontal=True,
    key="tab_choice_radio"
)

# ---------------------------------------------------------
# TAB 1 (now Chart 4): Bar Chart (Average Happiness per Country)
# ---------------------------------------------------------
if tab_choice.startswith("4️⃣"):
    st.subheader("4️⃣ Average Happiness Score by Country")

    st.markdown(
        "This chart shows the average **happiness score** for each country."
    )

    mean_happy = (
        df.groupby("Country", as_index=False)["Happiness Score"]
        .mean()
        .rename(columns={"Happiness Score": "Mean Happiness"})
    )

    if mean_happy.empty:
        st.warning("No data available to compute average happiness per country.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            max_for_slider = max(1, min(30, len(mean_happy)))
            top_n = st.slider(
                "Number of countries to show (Top-N)",
                min_value=1,
                max_value=max_for_slider,
                value=min(10, max_for_slider),
                key="bar_top_n"
            )
        with col_b:
            order = st.selectbox(
                "Sorting order",
                options=["Happiest → least happy", "Least happy → happiest"],
                key="bar_order"
            )

        ascending = (order == "Least happy → happiest")
        mean_happy_sorted = mean_happy.sort_values(
            "Mean Happiness",
            ascending=ascending
        ).head(top_n)

        fig_bar = px.bar(
            mean_happy_sorted,
            x="Country",
            y="Mean Happiness",
            color="Mean Happiness",
            labels={
                "Country": "Country",
                "Mean Happiness": "Average Happiness Score"
            },
            hover_data=["Mean Happiness"]
        )
        fig_bar.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )


# ---------------------------------------------------------
# TAB 2 (Chart 5): Sunburst Plot (Country > Exercise > Mental Health)
# ---------------------------------------------------------
elif tab_choice.startswith("5️⃣"):
    st.subheader("5️⃣ Mental Health Distribution by Country and Physical Activity")

    st.markdown(
        "This chart shows the hierarchy **Country → Exercise Level → Mental Health Condition**. "
        "Each ring represents a level, and the area of each slice represents the number of people."
    )

    all_countries = sorted(df["Country"].dropna().unique())
    selected_countries = st.multiselect(
        "Countries (leave empty to include all)",
        options=all_countries,
        key="sb_countries"
    )

    sb_df = df.copy()
    if selected_countries:
        sb_df = sb_df[sb_df["Country"].isin(selected_countries)]

    grouped = (
        sb_df
        .groupby(["Country", "Exercise Level", "Mental Health Condition"])
        .size()
        .reset_index(name="Count")
    )

    if grouped.empty:
        st.warning("No data available for the selected country/filter combination.")
    else:
        fig_sun = px.sunburst(
            grouped,
            path=["Country", "Exercise Level", "Mental Health Condition"],
            values="Count",
            color="Exercise Level",
            labels={
                "Country": "Country",
                "Exercise Level": "Exercise Level",
                "Mental Health Condition": "Mental Health Condition",
                "Count": "Number of People"
            }
        )
        fig_sun.update_traces(hovertemplate="<b>%{label}</b><br>Count: %{value}")
        st.plotly_chart(fig_sun, use_container_width=True)

# ---------------------------------------------------------
# TAB 3 (6. Grafik): Parallel Coordinates Plot (No Colors)
# ---------------------------------------------------------
elif tab_choice.startswith("6️⃣"):
    st.subheader("6️⃣ Work / Screen Time vs Stress and Happiness (Parallel Coordinates)")

    st.markdown(
        "This chart displays **weekly work hours**, **daily screen time**, "
        "**happiness score**, and **stress level** together using parallel axes. "
        "Stress level is represented as a separate axis instead of color."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        stress_options = sorted(df["Stress Level"].dropna().unique())
        selected_stress = st.multiselect(
            "Stress levels",
            options=stress_options,
            default=stress_options,
            key="pc_stress_levels"
        )

    with col2:
        min_work = int(df["Work Hours per Week"].min())
        max_work = int(df["Work Hours per Week"].max())
        work_range = st.slider(
            "Weekly work hours",
            min_value=min_work,
            max_value=max_work,
            value=(min_work, max_work),
            key="pc_work_range"
        )

    with col3:
        min_screen = float(df["Screen Time per Day (Hours)"].min())
        max_screen = float(df["Screen Time per Day (Hours)"].max())
        screen_range = st.slider(
            "Daily screen time (hours)",
            min_value=min_screen,
            max_value=max_screen,
            value=(min_screen, max_screen),
            key="pc_screen_range"
        )

    # -------- FILTERED DATA --------
    pc_df = df[
        df["Stress Level"].isin(selected_stress)
        & df["Work Hours per Week"].between(work_range[0], work_range[1])
        & df["Screen Time per Day (Hours)"].between(screen_range[0], screen_range[1])
    ][[
        "Work Hours per Week",
        "Screen Time per Day (Hours)",
        "Happiness Score",
        "Stress Level",
    ]].dropna()

    # Numeric axis for stress (0=Low, 1=Moderate, 2=High)
    STRESS_AXIS_MAP = {"Low": 0, "Moderate": 1, "High": 2}
    pc_df["Stress_Axis"] = pc_df["Stress Level"].map(STRESS_AXIS_MAP)

    # Shuffle rows to reduce overlay bias
    pc_df = pc_df.sample(frac=1, random_state=42).reset_index(drop=True)

    if pc_df.empty:
        st.warning("No data left after filtering. Please widen the ranges or select more stress levels.")
    else:
        # RENKSİZ PARALLEL COORDINATES → Tek renk: gri
        fig_pc = px.parallel_coordinates(
            pc_df,
            dimensions=[
                "Work Hours per Week",
                "Screen Time per Day (Hours)",
                "Happiness Score",
                "Stress_Axis",
            ],
            color=None,  # <-- RENK YOK
            labels={
                "Work Hours per Week": "Weekly Work Hours",
                "Screen Time per Day (Hours)": "Daily Screen Time (hours)",
                "Happiness Score": "Happiness Score",
                "Stress_Axis": "Stress Level"
            }
        )

        # Stress Axis → Replace ticks 0/1/2 with labels
        dim_list = fig_pc.data[0]["dimensions"]
        for dim in dim_list:
            if dim["label"] == "Stress Level":
                dim["tickvals"] = [0, 1, 2]
                dim["ticktext"] = ["Low", "Moderate", "High"]
                break

        # Gray line color for all lines
        fig_pc.update_traces(line=dict(color="#00AA00"))

        fig_pc.update_layout(
            margin=dict(l=60, r=40, t=60, b=40),
            font=dict(size=12)
        )

        st.plotly_chart(fig_pc, use_container_width=True)

