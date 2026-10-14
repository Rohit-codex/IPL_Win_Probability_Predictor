from __future__ import annotations

import base64
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st


TEAMS = [
    "Sunrisers Hyderabad",
    "Mumbai Indians",
    "Royal Challengers Bangalore",
    "Kolkata Knight Riders",
    "Kings XI Punjab",
    "Chennai Super Kings",
    "Rajasthan Royals",
    "Delhi Capitals",
]

CITIES = [
    "Hyderabad",
    "Bangalore",
    "Mumbai",
    "Indore",
    "Kolkata",
    "Delhi",
    "Chandigarh",
    "Jaipur",
    "Chennai",
    "Cape Town",
    "Port Elizabeth",
    "Durban",
    "Centurion",
    "East London",
    "Johannesburg",
    "Kimberley",
    "Bloemfontein",
    "Ahmedabad",
    "Cuttack",
    "Nagpur",
    "Dharamsala",
    "Visakhapatnam",
    "Pune",
    "Raipur",
    "Ranchi",
    "Abu Dhabi",
    "Sharjah",
    "Mohali",
    "Bengaluru",
]

PROJECT_DIRECTORY = Path(__file__).parent
MODEL_PATH = PROJECT_DIRECTORY / "pipe.pkl"
BACKGROUND_PATH = PROJECT_DIRECTORY / "assets" / "stadium-night.png"


@st.cache_data
def get_background_css_value(image_path: str) -> str:
    """Return a self-contained CSS background so the app works offline."""
    path = Path(image_path)
    if not path.is_file():
        return "linear-gradient(135deg, #05070d 0%, #210811 48%, #09050a 100%)"

    encoded_image = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        "linear-gradient(180deg, rgba(2, 5, 13, 0.58) 0%, rgba(7, 5, 12, 0.82) 100%), "
        f'url("data:image/png;base64,{encoded_image}")'
    )


def apply_theme() -> None:
    background = get_background_css_value(str(BACKGROUND_PATH))
    styles = """
    <style>
        :root {
            --night: #070913;
            --card: rgba(8, 12, 25, 0.84);
            --gold: #f7bf4f;
            --warm-white: #fff7e8;
            --muted: #c9ced9;
            --red: #e63f3f;
        }
        .stApp {
            background-image: BACKGROUND_IMAGE;
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        .block-container {
            max-width: 1100px;
            padding-top: 3.5rem;
            padding-bottom: 4rem;
        }
        .hero {
            text-align: center;
            padding: 1rem 1rem 2.2rem;
            color: var(--warm-white);
            text-shadow: 0 3px 22px rgba(0, 0, 0, 0.72);
        }
        .hero-kicker, .section-kicker {
            color: var(--gold);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.2em;
            text-transform: uppercase;
        }
        .hero h1 {
            color: var(--warm-white);
            font-family: Georgia, serif;
            font-size: clamp(2.4rem, 6vw, 4.8rem);
            line-height: 1;
            margin: 0.55rem 0 0.75rem;
        }
        .hero p {
            color: var(--muted);
            font-size: 1.08rem;
            margin: 0;
        }
        div[data-testid="stForm"] {
            background: var(--card);
            border: 1px solid rgba(247, 191, 79, 0.35);
            border-radius: 24px;
            box-shadow: 0 28px 70px rgba(0, 0, 0, 0.48);
            backdrop-filter: blur(16px);
            padding: 2rem 2rem 1.35rem;
        }
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p {
            color: var(--warm-white) !important;
            font-weight: 650;
        }
        div[data-baseweb="select"] > div,
        div[data-testid="stNumberInput"] input {
            background: rgba(255, 255, 255, 0.94) !important;
            border: 1px solid rgba(247, 191, 79, 0.55) !important;
            border-radius: 10px !important;
            color: #111827 !important;
        }
        div[data-baseweb="select"] * {
            color: #111827;
        }
        div[data-testid="stFormSubmitButton"] > button {
            width: 100%;
            border: 0;
            border-radius: 12px;
            background: linear-gradient(105deg, #d62d3d 0%, #f08b3e 52%, #f4c452 100%);
            color: #fff;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            padding: 0.65rem 1rem;
            box-shadow: 0 12px 24px rgba(189, 41, 49, 0.35);
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            filter: brightness(1.08);
            border: 0;
        }
        .result-heading {
            margin: 2rem 0 0.7rem;
            text-align: center;
        }
        div[data-testid="stMetric"] {
            background: rgba(7, 10, 21, 0.88);
            border: 1px solid rgba(247, 191, 79, 0.35);
            border-radius: 18px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 16px 38px rgba(0, 0, 0, 0.32);
        }
        div[data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
            font-weight: 700;
        }
        div[data-testid="stMetricValue"] {
            color: var(--gold);
            font-size: 2.15rem;
        }
        .stAlert {
            border-radius: 14px;
        }
        @media (max-width: 700px) {
            .block-container { padding: 1.5rem 1rem 3rem; }
            div[data-testid="stForm"] { padding: 1.35rem 1rem 1rem; }
        }
    </style>
    """
    st.markdown(styles.replace("BACKGROUND_IMAGE", background), unsafe_allow_html=True)


@st.cache_resource
def load_model(model_path: str):
    with Path(model_path).open("rb") as model_file:
        return pickle.load(model_file)


def overs_to_balls(overs: float) -> int:
    """Convert cricket notation (for example, 7.3) to legal balls bowled."""
    completed_overs = int(overs)
    balls_in_current_over = round((overs - completed_overs) * 10)

    if not 0 <= balls_in_current_over <= 5:
        raise ValueError("Use cricket notation: the digit after the decimal must be 0 to 5.")

    balls_bowled = completed_overs * 6 + balls_in_current_over
    if not 1 <= balls_bowled < 120:
        raise ValueError("Enter an innings state from 0.1 through 19.5 overs.")
    return balls_bowled


def get_win_probability(model, features: pd.DataFrame) -> float:
    probabilities = model.predict_proba(features)[0]
    classes = list(model.classes_)
    return float(probabilities[classes.index(1)])


def main() -> None:
    st.set_page_config(page_title="IPL Win Predictor", page_icon="🏏", layout="wide")
    apply_theme()
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Live Match Analytics</div>
            <h1>IPL Win Predictor</h1>
            <p>Read the match. Trust the numbers. Own the chase.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        model = load_model(str(MODEL_PATH))
    except (FileNotFoundError, EOFError, pickle.UnpicklingError, ModuleNotFoundError) as error:
        st.error("The trained model file `pipe.pkl` is not available or cannot be loaded.")
        st.info("Put `matches.csv` and `deliveries.csv` in this folder, run every cell in `Untitled.ipynb`, then restart the app.")
        st.caption(f"Details: {error}")
        st.stop()

    st.markdown('<div class="section-kicker">Match setup</div>', unsafe_allow_html=True)
    with st.form("match_state"):
        team_column, opponent_column = st.columns(2)
        with team_column:
            batting_team = st.selectbox("Chasing team", sorted(TEAMS))
        with opponent_column:
            bowling_team = st.selectbox("Bowling team", sorted(TEAMS), index=1)

        selected_city = st.selectbox("Host city", sorted(CITIES))

        target_column, score_column, over_column, wicket_column = st.columns(4)
        with target_column:
            target = st.number_input("Target", min_value=1, value=160, step=1)
        with score_column:
            score = st.number_input("Current score", min_value=0, value=0, step=1)
        with over_column:
            overs = st.number_input("Overs completed", min_value=0.1, max_value=19.5, value=0.1, step=0.1, format="%.1f")
        with wicket_column:
            wickets_lost = st.number_input("Wickets lost", min_value=0, max_value=9, value=0, step=1)

        submitted = st.form_submit_button("Predict the chase")

    if not submitted:
        return

    if batting_team == bowling_team:
        st.error("Choose two different teams.")
        return
    if score >= target:
        st.success(f"{batting_team} has already reached the target.")
        return

    try:
        balls_bowled = overs_to_balls(overs)
    except ValueError as error:
        st.error(str(error))
        return

    balls_left = 120 - balls_bowled
    runs_left = target - score
    wickets_remaining = 10 - wickets_lost
    current_run_rate = (score * 6) / balls_bowled
    required_run_rate = (runs_left * 6) / balls_left

    input_frame = pd.DataFrame(
        {
            "batting_team": [batting_team],
            "bowling_team": [bowling_team],
            "city": [selected_city],
            "runs_left": [runs_left],
            "balls_left": [balls_left],
            "wickets": [wickets_remaining],
            "total_runs_x": [target],
            "crr": [current_run_rate],
            "rrr": [required_run_rate],
        }
    )

    chasing_team_win_probability = get_win_probability(model, input_frame)
    bowling_team_win_probability = 1 - chasing_team_win_probability

    st.markdown(
        '<div class="result-heading"><div class="section-kicker">Win probability</div></div>',
        unsafe_allow_html=True,
    )
    chasing_metric, bowling_metric = st.columns(2)
    chasing_metric.metric(batting_team, f"{chasing_team_win_probability:.1%}")
    bowling_metric.metric(bowling_team, f"{bowling_team_win_probability:.1%}")


if __name__ == "__main__":
    main()
