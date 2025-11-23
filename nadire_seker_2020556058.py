import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


@st.cache_data
def load_data():
    base_dir = os.path.dirname(__file__)
    candidate_paths = [
        os.path.join(base_dir, "data", "Mental_Health_Lifestyle_CLEAN.csv"),
        os.path.join(base_dir, "data", "mental_health_lifestyle_clean.csv"),
        r"/mnt/data/Mental_Health_Lifestyle_CLEAN.csv",
        r"/mnt/data/Mental_Health_Lifestyle_CLEAN (1).csv",
    ]

    for p in candidate_paths:
        if p and os.path.exists(p):
            df = pd.read_csv(p)
            return df

    raise FileNotFoundError(
        "Dataset not found. Please place 'Mental_Health_Lifestyle_CLEAN.csv' into a 'data' folder "
        "inside the project, or update the candidate_paths in load_data()."
    )


def chart_scatter_matrix_sleep_exercise_stress(df_local: pd.DataFrame):
    st.subheader("7️⃣ Sleep, Exercise & Happiness (Scatter Matrix)")

    if df_local.empty:
        st.warning("No data available for selected filters.")
        return

    numeric_cols = [
        c for c in
        ["Sleep Hours", "Screen Time per Day (Hours)", "Happiness Score"]
        if c in df_local.columns
    ]

    if len(numeric_cols) < 2:
        st.info("Not enough numeric columns for scatter matrix.")
        return

    selected_dims = st.multiselect(
        "Select variables for scatter matrix (min 2)",
        numeric_cols,
        default=numeric_cols,
        key="m3_scatter_dims"
    )

    if len(selected_dims) < 2:
        st.info("Please select at least two variables.")
        return

    color_map = {"Low": "#1f77b4", "Moderate": "#2ca02c", "High": "#d62728"}

    fig = px.scatter_matrix(
        df_local, 
        dimensions=selected_dims,
        color="Stress Level" if "Stress Level" in df_local.columns else None,
        opacity=0.65,  
        hover_data=["Age", "Country", "Gender"]
        if {"Age", "Country", "Gender"}.issubset(df_local.columns)
        else None,
        color_discrete_map=color_map if "Stress Level" in df_local.columns else None,
    )

    fig.update_traces(marker=dict(size=2.8))

    fig.update_layout(
        legend=dict(
            title=dict(
            side="top",    
            font=dict(size=20, color="white")), 
            font=dict(size=18),    
            itemsizing="constant",
            orientation="v",
            x=1.05,                  
            y=1.0
        ),
        height=750,
        font=dict(size=14),
        margin=dict(l=60, r=120, t=50, b=50)  
    )

    st.plotly_chart(fig, use_container_width=True)


def chart_heatmap_social_media_mood(df: pd.DataFrame):
    st.subheader("📱 Social Media Usage vs Mood (Heatmap)")
    st.write("Average happiness score by screen-time range and exercise level. Use the slider to change bin count.")

    if df.empty:
        st.warning("No data available for selected filters.")
        return

    screen_col = "Screen Time per Day (Hours)"
    if screen_col not in df.columns:
        st.info("Screen time column not found in dataset.")
        return

    bin_count = st.slider("Number of screen-time bins", min_value=3, max_value=10, value=5, key="heatmap_bins")

    minv = float(df[screen_col].min())
    maxv = float(df[screen_col].max())
    bins = np.linspace(minv, maxv, bin_count + 1)
    labels = [f"{round(bins[i],1)}–{round(bins[i+1],1)}" for i in range(len(bins)-1)]

    df_local = df.copy()
    df_local["ScreenBin"] = pd.cut(df_local[screen_col], bins=bins, labels=labels, include_lowest=True)

    if "Exercise Level" not in df_local.columns:
        st.info("Exercise Level column not found in dataset.")
        return

    pivot = df_local.pivot_table(
        index="Exercise Level",
        columns="ScreenBin",
        values="Happiness Score" if "Happiness Score" in df_local.columns else df_local.columns[0],
        aggfunc="mean"
    ).reindex(index=["Low", "Moderate", "High"])  

    fig = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(color="Avg Happiness Score"),
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        font=dict(size=13),
        xaxis_title="Screen Time per Day (binned, hours)",
        yaxis_title="Exercise Level",
        coloraxis_colorbar=dict(title="Happiness", thickness=14, title_side="top"),
        margin=dict(l=60, r=30, t=50, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)



def chart_violin_wellbeing_activity(df: pd.DataFrame):
    st.subheader("💛 Overall Wellbeing vs Physical Activity (Violin Plot)")
    st.write("Distribution of happiness score by exercise level and gender. Use the dropdown to focus on a single gender.")

    if df.empty:
        st.warning("No data available for selected filters.")
        return

    if "Happiness Score" not in df.columns or "Exercise Level" not in df.columns:
        st.info("Required columns for violin plot not found (Happiness Score, Exercise Level).")
        return

    gender_options = ["All"]
    if "Gender" in df.columns:
        gender_options += sorted(df["Gender"].dropna().unique().tolist())

    selected_gender = st.selectbox("Gender filter for this chart", gender_options, key="violin_gender")

    df_plot = df.copy()
    if selected_gender != "All":
        df_plot = df_plot[df_plot["Gender"] == selected_gender]

    if df_plot.empty:
        st.warning("No rows after applying gender filter.")
        return

    color_map = {"Male": "#1f77b4", "Female": "#d62728", "Other": "#9467bd"}

    fig = px.violin(
        df_plot,
        x="Exercise Level",
        y="Happiness Score",
        color="Gender" if selected_gender == "All" and "Gender" in df_plot.columns else None,
        box=True,
        points="all",
        color_discrete_map=color_map if "Gender" in df_plot.columns else None,
        hover_data=["Age", "Country", "Stress Level"] if set(["Age", "Country", "Stress Level"]).issubset(df_plot.columns) else None
    )

    fig.update_layout(
        font=dict(size=13),
        xaxis_title="Exercise Level",
        yaxis_title="Happiness Score (Overall Wellbeing)",
        margin=dict(l=60, r=30, t=50, b=50),
        legend=dict(title="Gender", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)



def main():
    st.set_page_config(page_title="Mental Health & Lifestyle Dashboard", layout="wide")
    st.title("Mental Health & Lifestyle Dashboard")

    try:
        df = load_data()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    st.sidebar.header("Filters")

    if "Gender" in df.columns:
        gender_options = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
        selected_gender = st.sidebar.selectbox("Gender", gender_options, index=0)
    else:
        selected_gender = "All"

    if "Country" in df.columns:
        country_options = ["All"] + sorted(df["Country"].dropna().unique().tolist())
        selected_country = st.sidebar.selectbox("Country", country_options, index=0)
    else:
        selected_country = "All"

    screen_col = "Screen Time per Day (Hours)"
    if screen_col in df.columns:
        min_screen = float(df[screen_col].min())
        max_screen = float(df[screen_col].max())
        screen_range = st.sidebar.slider(
            "Screen Time per Day (Hours)",
            min_value=round(min_screen, 1),
            max_value=round(max_screen, 1),
            value=(round(min_screen, 1), round(max_screen, 1))
        )
    else:
        screen_range = (0.0, 999.0)


    df_filtered = df.copy()
    if selected_gender != "All" and "Gender" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Gender"] == selected_gender]
    if selected_country != "All" and "Country" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["Country"] == selected_country]
    if screen_col in df_filtered.columns:
        df_filtered = df_filtered[(df_filtered[screen_col] >= screen_range[0]) & (df_filtered[screen_col] <= screen_range[1])]


    with st.expander("Show sample of filtered data"):
        st.dataframe(df_filtered.head())

    st.markdown("---")
    chart_scatter_matrix_sleep_exercise_stress(df_filtered)

    st.markdown("---")
    chart_heatmap_social_media_mood(df_filtered)

    st.markdown("---")
    chart_violin_wellbeing_activity(df_filtered)

    st.markdown("---")
    st.write("**Notes:** Colors chosen for clear contrast (Low=blue, Moderate=green, High=red). Use filters on the left to explore subsets.")


if __name__ == "__main__":
    main()
