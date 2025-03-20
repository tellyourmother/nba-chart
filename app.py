import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerGameLog

def get_player_id(player_name):
    """Retrieve the NBA Player ID based on their full name."""
    player_dict = players.get_players()
    for player in player_dict:
        if player['full_name'].lower() == player_name.lower():
            return player['id']
    return None  # Return None if player not found

def plot_last_15_games(player_name):
    """Fetch the last 15 game logs and generate the upgraded bar graph with lines."""
    player_id = get_player_id(player_name)

    if not player_id:
        st.error(f"⚠️ Player '{player_name}' not found! Please check the name and try again.")
        return

    st.success(f"📊 Generating stats for: {player_name} (Player ID: {player_id})")

    # Fetch the player's game logs (current season by default)
    gamelog = PlayerGameLog(player_id=player_id)
    df = gamelog.get_data_frames()[0]

    # Get the last 15 games
    df = df.head(15)

    # Convert relevant columns to numeric
    df[['PTS', 'REB', 'AST', 'STL', 'PLUS_MINUS', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'MIN']] = \
        df[['PTS', 'REB', 'AST', 'STL', 'PLUS_MINUS', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'MIN']].apply(pd.to_numeric)

    # Convert Game Date for X-axis labels
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df[::-1]  # Reverse for correct order

    # Extract opponent team abbreviation from MATCHUP column
    df["OPPONENT"] = df["MATCHUP"].apply(lambda x: x.split()[-1])

    # Identify Home/Away games
    df["HOME_AWAY"] = df["MATCHUP"].apply(lambda x: "H" if "vs" in x else "A")

    # Format X-axis labels
    game_labels = df.apply(lambda row: f"{row['GAME_DATE'].strftime('%b %d')} vs {row['OPPONENT']} ({row['HOME_AWAY']})", axis=1)

    # Calculate Averages
    avg_pts = df["PTS"].mean()
    avg_reb = df["REB"].mean()
    avg_ast = df["AST"].mean()
    avg_min = df["MIN"].mean()
    avg_fg_pct = df["FG_PCT"].mean() * 100
    avg_3p_pct = df["FG3_PCT"].mean() * 100

    # Set Dark Theme
    plt.style.use('dark_background')

    # Create Figure with Subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [4, 1]})
    ax1.set_facecolor("#1e1e1e")
    fig.patch.set_facecolor("#121212")

    # X-axis labels
    games = range(1, len(df) + 1)

    # Bar Chart for PTS, Stacked REB + AST
    bar_width = 0.3
    pts_colors = ["royalblue" if pts > avg_pts else "lightblue" for pts in df["PTS"]]

    ax1.bar(games, df["PTS"], color=pts_colors, alpha=0.8, label="Points", width=bar_width)
    ax1.bar([g + bar_width for g in games], df["REB"], color="orange", alpha=0.7, label="Rebounds", width=bar_width)
    ax1.bar([g + bar_width for g in games], df["AST"], bottom=df["REB"], color="green", alpha=0.7, label="Assists", width=bar_width)

    # Plot Lines for Minutes
    ax1.plot(games, df["MIN"], marker="*", linestyle="dashed", color="brown", label="Minutes", linewidth=2)

    # Labels & Titles
    ax1.set_xlabel("Game Date & Opponent (Last 15)")
    ax1.set_ylabel("Stats (Points, Rebounds, Assists, Minutes)")
    ax1.set_title(f"{player_name} - Last 15 Games Performance")
    ax1.set_xticks(games)
    ax1.set_xticklabels(game_labels, rotation=45, ha="right")

    # Legends
    ax1.legend(loc="upper left")

    # Side Panel: Display Averages
    ax2.axis("off")
    ax2.text(0.5, 0.85, f" Avg Points: {avg_pts:.1f}", fontsize=14, ha="center", fontweight="bold", color="blue")
    ax2.text(0.5, 0.75, f" Avg Rebounds: {avg_reb:.1f}", fontsize=14, ha="center", fontweight="bold", color="orange")
    ax2.text(0.5, 0.65, f" Avg Assists: {avg_ast:.1f}", fontsize=14, ha="center", fontweight="bold", color="green")
    ax2.text(0.5, 0.55, f" Avg Minutes: {avg_min:.1f}", fontsize=14, ha="center", fontweight="bold", color="brown")
    ax2.text(0.5, 0.45, f" FG%: {avg_fg_pct:.1f}%", fontsize=14, ha="center", fontweight="bold", color="gray")
    ax2.text(0.5, 0.35, f" 3P%: {avg_3p_pct:.1f}%", fontsize=14, ha="center", fontweight="bold", color="cyan")

    # Display Plot
    st.pyplot(fig)

# ---------- Streamlit UI ----------
st.title("📊 NBA Player Game Log Analyzer")
st.write("Enter an NBA player's full name to see their last 15 games performance.")

# Player Name Input
player_name = st.text_input("Enter Player's Full Name", "LeBron James")

# Button to trigger plot
if st.button("Generate Chart"):
    plot_last_15_games(player_name)
