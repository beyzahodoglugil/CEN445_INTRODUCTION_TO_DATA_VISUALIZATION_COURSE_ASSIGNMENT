import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- Veri Yükleme --------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Mental_Health_Lifestyle_CLEAN.csv")

df = load_data()

st.title("🧠 Mental Health and Lifestyle Dashboard")

# -------------------- Age Group Column --------------------
df["Age_Group"] = pd.cut(
    df["Age"],
    bins=[0, 20, 30, 40, 50, 60, 100],
    labels=["0-20", "21-30", "31-40", "41-50", "51-60", "60+"]
)

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.title("Filters")

gender_filter = st.sidebar.multiselect(
    "Select Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

age_group_filter = st.sidebar.selectbox(
    "Select Age Group:",
    options=df["Age_Group"].dropna().unique()
)

diet_filter = st.sidebar.multiselect(
    "Select Diet Type:",
    options=df["Diet Type"].unique(),
    default=df["Diet Type"].unique()
)

mh_filter = st.sidebar.multiselect(
    "Select Mental Health Condition:",
    options=df["Mental Health Condition"].unique(),
    default=df["Mental Health Condition"].unique()
)

age_min, age_max = st.sidebar.slider(
    "Select Age Range:",
    min_value=int(df["Age"].min()),
    max_value=int(df["Age"].max()),
    value=(18, 40)
)


# SCATTER PLOT

st.subheader("1️⃣ Sleep Hours and Stress Level")

# Stress Level → numeric mapping
size_map = {"Low": 10, "Moderate": 20, "High": 30}
df["Stress_Num"] = df["Stress Level"].map(size_map)

scatter_df = df[
    (df["Gender"].isin(gender_filter)) &
    (df["Age_Group"] == age_group_filter)
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


#TREEMAP
# ============================================================
# 2️⃣ ADVANCED GRAPH — TREEMAP
# ============================================================

st.subheader("2️⃣ Diet Type and Mental Health Condition")

treemap_df = df[
    (df["Diet Type"].isin(diet_filter)) &
    (df["Mental Health Condition"].isin(mh_filter))
].copy()

# Clean missing values
treemap_df = treemap_df.dropna(subset=["Diet Type", "Mental Health Condition"])

# Count per (Diet Type, Mental Health Condition)
treemap_grouped = treemap_df.groupby(
    ["Diet Type", "Mental Health Condition"]
).size().reset_index(name="Count")

if not treemap_grouped.empty:
    fig_treemap = px.treemap(
        treemap_grouped,
        path=["Diet Type", "Mental Health Condition"],  # hierarchical
        values="Count",                                 # size of rectangles
        color="Count",                                  # COLOR BASED ON VALUE
        color_continuous_scale="Blues",                 # Darker = more common
        hover_data={"Count": True}
    )

    fig_treemap.update_layout(margin=dict(t=30, l=0, r=0, b=0))

    st.plotly_chart(fig_treemap, use_container_width=True)
else:
    st.warning("No data available for the selected diet/mental health filters.")




#BOX PLOT

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
