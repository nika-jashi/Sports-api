from random import shuffle


def generate_eliminations(league_teams_data):
    shuffle(league_teams_data)  # Shuffle teams randomly

    matches = []

    # Group teams into pairs (2 per match)
    for i in range(0, len(league_teams_data), 2):
        team1 = league_teams_data[i]
        team2 = league_teams_data[i + 1] if i + 1 < len(league_teams_data) else None  # Handle odd count

        matches.append({
            'home': team1,
            'away': team2
        })

    return matches
# def create_new_brackets_after_wins(started_tournament_teams_data):


#print(generate_eliminations(league_teams_data=["team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8"]))