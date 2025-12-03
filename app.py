import streamlit as st
import pandas as pd
import numpy as np

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Factory Frenzy Leaderboard",
    page_icon="🏭",
    layout="wide"
)

# ---------- CUSTOM CSS FOR VIBE ----------
st.markdown(
    """
    <style>
    /* Remove default padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #1e1b4b, #0f766e 40%, #f97316 90%);
        color: #f9fafb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Title styling */
    .leaderboard-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #fefce8;
        text-shadow: 0 0 20px rgba(0,0,0,0.7);
        letter-spacing: 0.03em;
    }
    .leaderboard-subtitle {
        font-size: 1rem;
        color: #e5e7eb;
        opacity: 0.9;
    }

    /* Card style */
    .rank-card {
        background: rgba(15,23,42,0.86);
        border-radius: 1.3rem;
        padding: 1.3rem 1.5rem;
        box-shadow: 0 18px 45px rgba(15,23,42,0.7);
        border: 1px solid rgba(148,163,184,0.3);
    }
    .rank-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }
    .rank-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f9fafb;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .rank-score {
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.4rem;
        color: #22c55e;
    }
    .rank-meta {
        font-size: 0.85rem;
        color: #d1d5db;
        margin-top: 0.2rem;
    }

    /* Dataframe tweaks */
    .dataframe td, .dataframe th {
        color: #0f172a !important;
    }

    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- DATA LOADING HELPERS ----------

REQUIRED_COLUMNS = [
    "Team",
    "Reputation",
    "Orders",
    "Accuracy_%",
    "Budget_Left",
    "Badges",
]

def preprocess_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Validate columns, sort, and add Rank."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(
            f"Missing columns in Excel file: {', '.join(missing)}. "
            f"Expected columns: {', '.join(REQUIRED_COLUMNS)}"
        )
        st.stop()

    df = df.copy()
    # Ensure numeric types where needed
    for col in ["Reputation", "Orders", "Accuracy_%", "Budget_Left"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(by="Reputation", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df

@st.cache_data
def load_scores_from_default_file(path: str = "scores.xlsx") -> pd.DataFrame:
    df = pd.read_excel(path)
    return preprocess_scores(df)

# ---------- SIDEBAR: DATA SOURCE + CONTROLS ----------
with st.sidebar:
    st.title("⚙️ Controls")

    st.markdown("#### 📂 Data source")
    uploaded_file = st.file_uploader(
        "Upload latest scores.xlsx",
        type=["xlsx"],
        help="Leave empty to use the default scores.xlsx from the repo.",
    )

    # Decide which dataframe to use
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df = preprocess_scores(df)
        using_uploaded = True
    else:
        try:
            df = load_scores_from_default_file()
            using_uploaded = False
        except Exception as e:
            st.error(
                "Could not load `scores.xlsx`. "
                "Make sure it exists in the same folder as app.py and has the right columns."
            )
            st.exception(e)
            st.stop()

    st.markdown("---")
    st.markdown("#### 🧮 View options")

    sort_option = st.selectbox(
        "Sort by",
        ["Reputation", "Orders", "Accuracy_%", "Budget_Left"],
        index=0,
    )
    ascending = st.toggle("Ascending order", value=False)
    num_teams = len(df)

if num_teams == 0:
    st.error("No teams found in the data. Please check your scores.xlsx file.")
    st.stop()

# If there are fewer than 3 teams, start from 1
min_n = 1 if num_teams < 3 else 3
default_n = num_teams

show_top_n = st.slider(
    "Show top N teams",
    min_n,
    num_teams,
    value=default_n,
)

    st.markdown("---")
    if st.button("🔄 Refresh data"):
        # Clears cache so default Excel reloads if edited
        st.cache_data.clear()
        st.experimental_rerun()

    st.caption(
        "Tip: update `scores.xlsx` (or upload a new file) and hit refresh to see latest standings."
    )

# ---------- APPLY SORTING & LIMIT ----------
df_sorted = df.sort_values(by=sort_option, ascending=ascending).head(show_top_n).reset_index(drop=True)
df_sorted["Rank"] = df_sorted.index + 1

# ---------- HEADER ----------
st.markdown(
    """
    <div class="leaderboard-title">
        🏭 Chaos Factory Leaderboard
    </div>
    <div class="leaderboard-subtitle">
        Real-time bragging rights for the most efficient (and least chaotic) factory teams.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")

# ---------- TOP 3 SPOTLIGHT ----------
st.subheader("👑 Top Teams")

top3 = df_sorted.head(3)
crowns = ["🥇", "🥈", "🥉"]
accent_emojis = ["🔥", "⚡", "💥"]

# handle case where fewer than 3 teams
cols = st.columns(3)
for i in range(len(top3)):
    row = top3.iloc[i]
    col = cols[i]
    with col:
        st.markdown(
            f"""
            <div class="rank-card">
                <div class="rank-title">Rank {row['Rank']}</div>
                <div class="rank-name">{crowns[i]} {row['Team']} {accent_emojis[i]}</div>
                <div class="rank-score">
                    {row['Reputation']}
                    <span style="font-size:0.9rem; margin-left:0.2rem; font-weight:500;">
                        Reputation
                    </span>
                </div>
                <div class="rank-meta">
                    Orders: <b>{int(row['Orders']) if not pd.isna(row['Orders']) else '-'}</b> · 
                    Accuracy: <b>{row['Accuracy_%']}%</b> · 
                    Budget left: <b>₹{int(row['Budget_Left']) if not pd.isna(row['Budget_Left']) else '-'}</b><br/>
                    Badges: {row['Badges']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("")

# ---------- FULL LEADERBOARD TABLE ----------
st.subheader("📊 Full Leaderboard")

display_cols = ["Rank", "Team", "Reputation", "Orders", "Accuracy_%", "Budget_Left", "Badges"]
table_df = df_sorted[display_cols].copy()
table_df = table_df.set_index("Rank")

st.dataframe(
    table_df,
    use_container_width=True,
)

# ---------- CHARTS ----------
st.markdown("")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 📈 Reputation distribution")
    rep_series = df_sorted.set_index("Team")["Reputation"]
    st.bar_chart(rep_series)

with col_chart2:
    st.markdown("#### 🎯 Accuracy distribution")
    acc_series = df_sorted.set_index("Team")["Accuracy_%"]
    st.bar_chart(acc_series)

