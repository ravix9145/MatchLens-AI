import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Soccer 2026 Match Predictor",
    page_icon="⚽",
    layout="centered"
)

@st.cache_resource
def load_artifacts():
   BASE_DIR = Path(__file__).resolve().parent

   model_path = BASE_DIR / "models" / "match_predictor.pkl"
   data_path = BASE_DIR / "models" / "team_data.pkl"

   model = joblib.load(model_path)
   team_data = joblib.load(data_path)

   return model, team_data["team_stats"], team_data["feature_cols"]

# Load artifacts
model, team_stats, feature_cols = load_artifacts()

# Title and caption
st.title("⚽ Soccer 2026 Match Predictor")
st.caption("Predictions based on historical international football results")

# Sort team names
team_names = sorted(team_stats.keys())

# Team selection
col1, col2 = st.columns(2)
with col1:
    default_a = team_names.index("Brazil") if "Brazil" in team_names else 0
    team_a = st.selectbox("Team A", team_names, index=default_a)
with col2:
    default_b = team_names.index("Argentina") if "Argentina" in team_names else 1
    team_b = st.selectbox("Team B", team_names, index=default_b)

# Match settings
is_neutral = st.checkbox("Neutral venue", value=True)
is_major_tournament = st.checkbox("Major tournament (e.g. World Cup)", value=True)

# Predict button
if st.button("Predict", type="primary", use_container_width=True):
    if team_a == team_b:
        st.error("Please pick two different teams.")
    else:
        # Get team statistics
        stats_a = team_stats[team_a]
        stats_b = team_stats[team_b]

        # Build feature row
        feature_row = pd.DataFrame([{
            "team_a_winrate": stats_a["winrate"],
            "team_b_winrate": stats_b["winrate"],
            "team_a_goal_avg": stats_a["goal_avg"],
            "team_b_goal_avg": stats_b["goal_avg"],
            "team_a_recent_form": stats_a["recent_form"],
            "team_b_recent_form": stats_b["recent_form"],
            "is_neutral": int(is_neutral),
            "is_major_tournament": int(is_major_tournament)
        }])

        # Reindex to match feature_cols order
        feature_row = feature_row[feature_cols]

        # Get prediction probabilities
        proba = model.predict_proba(feature_row)
        team_a_prob = proba[0][0]
        draw_prob = proba[0][1]
        team_b_prob = proba[0][2]

        # Display metrics
        st.subheader("Prediction Results")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{team_a} wins", f"{team_a_prob * 100:.1f}%")
        with col2:
            st.metric("Draw", f"{draw_prob * 100:.1f}%")
        with col3:
            st.metric(f"{team_b} wins", f"{team_b_prob * 100:.1f}%")

        # Display progress bars
        st.progress(team_a_prob, text=f"{team_a} win probability")
        st.progress(draw_prob, text="Draw probability")
        st.progress(team_b_prob, text=f"{team_b} win probability")

        # Display team statistics table
        st.subheader("Team Statistics")
        stats_table = pd.DataFrame({
            "Team": [team_a, team_b],
            "Win Rate": [f"{stats_a['winrate']:.3f}", f"{stats_b['winrate']:.3f}"],
            "Avg Goals Scored": [f"{stats_a['goal_avg']:.2f}", f"{stats_b['goal_avg']:.2f}"],
            "Recent Form (Last 10)": [f"{stats_a['recent_form']:.3f}", f"{stats_b['recent_form']:.3f}"],
            "Matches Played": [stats_a["matches_played"], stats_b["matches_played"]]
        })
        st.table(stats_table)
