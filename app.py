import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="CEN445 - Mental Health & Lifestyle Dashboard",
    layout="wide"
)

st.title("CEN445 - Mental Health & Lifestyle Dashboard")


@st.cache_data
def load_data() -> pd.DataFrame:
    base_dir = os.path.dirname(__file__)
    candidate_paths = [
        os.path.join(base_dir, "data", "Mental_Health_Lifestyle_CLEAN.csv"),
        os.path.join(base_dir, "Mental_Health_Lifestyle_CLEAN.csv"),
        r"/mnt/data/Mental_Health_Lifestyle_CLEAN.csv",
        r"/mnt/data/Mental_Health_Lifestyle_CLEAN (1).csv",
    ]

    for p in candidate_paths:
        if p and os.path.exists(p):
            df_ = pd.read_csv(p, keep_default_na=False)
            return df_

    raise FileNotFoundError(
        "Dataset not found. Please place 'Mental_Health_Lifestyle_CLEAN.csv' either "
        "in the project root or in a 'data' folder."
    )


try:
    df = load_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()



if "Stress Level" in df.columns:
    STRESS_CODE_MAP = {"Low": 0.0, "Moderate": 0.5, "High": 1.0}
    df["Stress_Level_Code"] = df["Stress Level"].map(STRESS_CODE_MAP)

if "Age" in df.columns and "Age_Group" not in df.columns:
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[0, 20, 30, 40, 50, 60, 100],
        labels=["0-20", "21-30", "31-40", "41-50", "51-60", "60+"]
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



def chart_heatmap_social_media_mood(df_local: pd.DataFrame):
    st.subheader("8️⃣ Social Media Usage vs Happiness (Heatmap)")

    if df_local.empty:
        st.warning("No data available for selected filters.")
        return

    screen_col = "Screen Time per Day (Hours)"
    if screen_col not in df_local.columns:
        st.info("Screen time column not found in dataset.")
        return

    bin_count = st.slider(
        "Number of screen-time bins",
        min_value=3,
        max_value=10,
        value=5,
        key="m3_heatmap_bins"
    )

    minv = float(df_local[screen_col].min())
    maxv = float(df_local[screen_col].max())
    bins = np.linspace(minv, maxv, bin_count + 1)
    labels = [f"{round(bins[i], 1)}–{round(bins[i + 1], 1)}"
              for i in range(len(bins) - 1)]

    df_bin = df_local.copy()
    df_bin["ScreenBin"] = pd.cut(
        df_bin[screen_col], bins=bins, labels=labels, include_lowest=True
    )

    if "Exercise Level" not in df_bin.columns:
        st.info("Exercise Level column not found in dataset.")
        return

    pivot = df_bin.pivot_table(
        index="Exercise Level",
        columns="ScreenBin",
        values="Happiness Score"
        if "Happiness Score" in df_bin.columns
        else df_bin.columns[0],
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


def chart_violin_wellbeing_activity(df_local: pd.DataFrame):
    st.subheader("9️⃣ Overall Wellbeing vs Physical Activity (Violin Plot)")

    if df_local.empty:
        st.warning("No data available for selected filters.")
        return

    if "Happiness Score" not in df_local.columns or "Exercise Level" not in df_local.columns:
        st.info("Required columns for violin plot not found (Happiness Score, Exercise Level).")
        return

    gender_options = ["All"]
    if "Gender" in df_local.columns:
        gender_options += sorted(df_local["Gender"].dropna().unique().tolist())

    selected_gender = st.selectbox(
        "Gender filter for this chart",
        gender_options,
        key="m3_violin_gender"
    )

    df_plot = df_local.copy()
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
        color=("Gender"
               if selected_gender == "All" and "Gender" in df_plot.columns
               else None),
        box=True,
        points="all",
        color_discrete_map=color_map if "Gender" in df_plot.columns else None,
        hover_data=["Age", "Country", "Stress Level"]
        if set(["Age", "Country", "Stress Level"]).issubset(df_plot.columns)
        else None
    )

    fig.update_layout(
        font=dict(size=13),
        xaxis_title="Exercise Level",
        yaxis_title="Happiness Score (Overall Wellbeing)",
        margin=dict(l=60, r=30, t=50, b=50),
        legend=dict(
            title="Gender",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


member = st.radio(
    "Select member:",
    (
        "👤 Member 1 : Naciye Beyza Hodoğlugil - Sleep, Diet & MH",
        "👤 Member 2 : Muhammed Furkan Çoban - Work & Country",
        "👤 Member 3 : Nadire Şeker - Lifestyle & Wellbeing",
    ),
    horizontal=True,
    key="member_selector"
)



if member.startswith("👤 Member 1"):
    st.header("Naciye Beyza Hodoğlugil - Sleep, Diet & Mental Health")

    m2_choice = st.radio(
        "Select graphic:",
        (
            "1️⃣ Sleep Hours and Stress Level (Scatter)",
            "2️⃣ Diet Type and Mental Health Condition (Treemap)",
            "3️⃣ Sleep Hours by Gender (Box Plot)",
        ),
        horizontal=True,
        key="m2_chart_choice"
    )

    if m2_choice.startswith("1️⃣"):
        st.markdown("### Filters for Scatter")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            gender_filter = st.multiselect(
                "Select Gender:",
                options=df["Gender"].unique(),
                default=list(df["Gender"].unique()),
                key="m2_scatter_gender"
            )
        with col_f2:
            age_group_filter = st.selectbox(
                "Select Age Group:",
                options=df["Age_Group"].dropna().unique(),
                key="m2_scatter_age_group"
            )

        sleep_min, sleep_max = st.slider(
            "Select Sleep Hours Range:",
            min_value=float(df["Sleep Hours"].min()),
            max_value=float(df["Sleep Hours"].max()),
            value=(float(df["Sleep Hours"].min()), float(df["Sleep Hours"].max())),
            step=0.5,
            key="m2_scatter_sleep_range"
        )

        st.subheader("1️⃣ Sleep Hours and Stress Level")

        size_map = {"Low": 10, "Moderate": 20, "High": 30}
        df["Stress_Num"] = df["Stress Level"].map(size_map)

        scatter_df = df[
            (df["Gender"].isin(gender_filter)) &
            (df["Age_Group"] == age_group_filter) &
            (df["Sleep Hours"].between(sleep_min, sleep_max))
        ]

        if not scatter_df.empty:
            fig_scatter = px.scatter(
                scatter_df,
                x="Sleep Hours",
                y="Age",
                color="Gender",
                size="Stress_Num",
                hover_data=["Age", "Sleep Hours", "Stress Level"],
                opacity=0.85,
                size_max=12,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_scatter.update_traces(
                marker=dict(line=dict(width=1, color="white"))
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")

    elif m2_choice.startswith("2️⃣"):
        st.markdown("### Filters for Treemap")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            diet_filter = st.multiselect(
                "Select Diet Type:",
                options=df["Diet Type"].unique(),
                default=list(df["Diet Type"].unique()),
                key="m2_tree_diet"
            )
        with col_f2:
            mh_filter = st.multiselect(
                "Select Mental Health Condition:",
                options=df["Mental Health Condition"].unique(),
                default=list(df["Mental Health Condition"].unique()),
                key="m2_tree_mh"
            )

        st.subheader("2️⃣ Diet Type and Mental Health Condition")

        treemap_df = df[
            (df["Diet Type"].isin(diet_filter)) &
            (df["Mental Health Condition"].isin(mh_filter))
        ].copy()

        treemap_df = treemap_df.dropna(
            subset=["Diet Type", "Mental Health Condition"]
        )

        treemap_grouped = treemap_df.groupby(
            ["Diet Type", "Mental Health Condition"]
        ).size().reset_index(name="Count")

        if not treemap_grouped.empty:
            fig_treemap = px.treemap(
                treemap_grouped,
                path=["Diet Type", "Mental Health Condition"],
                values="Count",
                color="Count",
                color_continuous_scale="Blues",
                hover_data={"Count": True}
            )
            fig_treemap.update_layout(margin=dict(t=30, l=0, r=0, b=0))
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.warning("No data available for the selected diet/mental health filters.")

    elif m2_choice.startswith("3️⃣"):
        st.markdown("### Filters for Box Plot")

        age_min, age_max = st.slider(
            "Select Age Range:",
            min_value=int(df["Age"].min()),
            max_value=int(df["Age"].max()),
            value=(18, 40),
            key="m2_box_age_range"
        )

        st.subheader("3️⃣ Sleep Hours by Gender")

        box_df = df[
            (df["Age"] >= age_min) &
            (df["Age"] <= age_max)
        ]

        if not box_df.empty:
            fig_box = px.box(
                box_df,
                x="Gender",
                y="Sleep Hours",
                color="Gender",
                points="all",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_box.update_traces(marker=dict(opacity=0.7))
            fig_box.update_layout(
                xaxis_title="Gender",
                yaxis_title="Sleep Hours"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("No data available in this age range.")



elif member.startswith("👤 Member 2"):
    st.header("Muhammed Furkan Çoban - Work, Activity and Country-Based Analysis")

    m1_choice = st.radio(
        "Select graphic:",
        (
            "4️⃣ Average Happiness by Country (Bar Chart)",
            "5️⃣ Mental Health by Country & Activity (Sunburst)",
            "6️⃣ Work / Screen Time vs Stress & Happiness (Parallel Coordinates)",
        ),
        horizontal=True,
        key="m1_tab_choice_radio"
    )

    if m1_choice.startswith("4️⃣"):
        st.subheader("4️⃣ Average Happiness Score by Country")
        st.markdown("Average **happiness score** for each country.")

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
                    key="m1_bar_top_n"
                )
            with col_b:
                order = st.selectbox(
                    "Sorting order",
                    options=["Happiest → least happy", "Least happy → happiest"],
                    key="m1_bar_order"
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

            st.plotly_chart(fig_bar, use_container_width=True)

    elif m1_choice.startswith("5️⃣"):
        st.subheader("5️⃣ Mental Health Distribution by Country and Physical Activity")
        st.markdown("Hierarchy: **Country → Exercise Level → Mental Health Condition**.")

        all_countries = sorted(df["Country"].dropna().unique())
        selected_countries = st.multiselect(
            "Countries (leave empty to include all)",
            options=all_countries,
            key="m1_sb_countries"
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

    elif m1_choice.startswith("6️⃣"):
        st.subheader("6️⃣ Work / Screen Time vs Stress and Happiness (Parallel Coordinates)")
        st.markdown(
            "Weekly work hours, daily screen time, happiness score and stress level "
            "together using parallel axes."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            stress_options = sorted(df["Stress Level"].dropna().unique())
            selected_stress = st.multiselect(
                "Stress levels",
                options=stress_options,
                default=stress_options,
                key="m1_pc_stress_levels"
            )

        with col2:
            min_work = int(df["Work Hours per Week"].min())
            max_work = int(df["Work Hours per Week"].max())
            work_range = st.slider(
                "Weekly work hours",
                min_value=min_work,
                max_value=max_work,
                value=(min_work, max_work),
                key="m1_pc_work_range"
            )

        with col3:
            min_screen = float(df["Screen Time per Day (Hours)"].min())
            max_screen = float(df["Screen Time per Day (Hours)"].max())
            screen_range = st.slider(
                "Daily screen time (hours)",
                min_value=min_screen,
                max_value=max_screen,
                value=(min_screen, max_screen),
                key="m1_pc_screen_range"
            )

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

        stress_axis_map = {"Low": 0, "Moderate": 1, "High": 2}
        pc_df["Stress_Axis"] = pc_df["Stress Level"].map(stress_axis_map)

        pc_df = pc_df.sample(frac=1, random_state=42).reset_index(drop=True)

        if pc_df.empty:
            st.warning(
                "No data left after filtering. Please widen the ranges or select more stress levels."
            )
        else:
            fig_pc = px.parallel_coordinates(
                pc_df,
                dimensions=[
                    "Work Hours per Week",
                    "Screen Time per Day (Hours)",
                    "Happiness Score",
                    "Stress_Axis",
                ],
                color=None,
                labels={
                    "Work Hours per Week": "Weekly Work Hours",
                    "Screen Time per Day (Hours)": "Daily Screen Time (hours)",
                    "Happiness Score": "Happiness Score",
                    "Stress_Axis": "Stress Level"
                }
            )

            dim_list = fig_pc.data[0]["dimensions"]
            for dim in dim_list:
                if dim["label"] == "Stress Level":
                    dim["tickvals"] = [0, 1, 2]
                    dim["ticktext"] = ["Low", "Moderate", "High"]
                    break

            fig_pc.update_traces(line=dict(color="#00AA00"))
            fig_pc.update_layout(
                margin=dict(l=60, r=40, t=60, b=40),
                font=dict(size=12)
            )
            st.plotly_chart(fig_pc, use_container_width=True)



elif member.startswith("👤 Member 3"):
    st.header("Nadire Şeker - Multivariate Analysis of Lifestyle Habits and Wellbeing")
    
    m3_choice = st.radio(
        "Select graphic:",
        (
            "7️⃣ Sleep, Exercise & Happiness (Scatter Matrix)",
            "8️⃣ Social Media vs Happiness (Heatmap)",
            "9️⃣ Wellbeing vs Physical Activity (Violin Plot)",
        ),
        horizontal=True,
        key="m3_chart_choice"
    )

    st.markdown("### Filters")

    col_f1, col_f2, col_f3 = st.columns(3)

    if "Gender" in df.columns:
        gender_options_m3 = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
        with col_f1:
            selected_gender_m3 = st.selectbox(
                "Gender",
                gender_options_m3,
                index=0,
                key="m3_gender"
            )
    else:
        selected_gender_m3 = "All"

    if "Country" in df.columns:
        country_options_m3 = ["All"] + sorted(df["Country"].dropna().unique().tolist())
        with col_f2:
            selected_country_m3 = st.selectbox(
                "Country",
                country_options_m3,
                index=0,
                key="m3_country"
            )
    else:
        selected_country_m3 = "All"

    screen_col = "Screen Time per Day (Hours)"
    if screen_col in df.columns:
        min_screen_m3 = float(df[screen_col].min())
        max_screen_m3 = float(df[screen_col].max())
        with col_f3:
            screen_range_m3 = st.slider(
                "Screen Time per Day (Hours)",
                min_value=round(min_screen_m3, 1),
                max_value=round(max_screen_m3, 1),
                value=(round(min_screen_m3, 1), round(max_screen_m3, 1)),
                key="m3_screen"
            )
    else:
        screen_range_m3 = (0.0, 999.0)

    df_filtered_m3 = df.copy()
    if selected_gender_m3 != "All" and "Gender" in df_filtered_m3.columns:
        df_filtered_m3 = df_filtered_m3[df_filtered_m3["Gender"] == selected_gender_m3]
    if selected_country_m3 != "All" and "Country" in df_filtered_m3.columns:
        df_filtered_m3 = df_filtered_m3[df_filtered_m3["Country"] == selected_country_m3]
    if screen_col in df_filtered_m3.columns:
        df_filtered_m3 = df_filtered_m3[
            (df_filtered_m3[screen_col] >= screen_range_m3[0]) &
            (df_filtered_m3[screen_col] <= screen_range_m3[1])
        ]

    if m3_choice.startswith("7️⃣"):
        chart_scatter_matrix_sleep_exercise_stress(df_filtered_m3)
    elif m3_choice.startswith("8️⃣"):
        chart_heatmap_social_media_mood(df_filtered_m3)
    elif m3_choice.startswith("9️⃣"):
        chart_violin_wellbeing_activity(df_filtered_m3)
