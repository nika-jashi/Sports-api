import itertools

def generate_unique_matches(league_teams_data: list) -> list:
    """ Generate unique home/away matches for league format """

    first_meeting_matches = [{"home": i[0], "away": i[1]} for i in itertools.combinations(league_teams_data, 2)]
    second_meeting_matches = [{"home": i[1], "away": i[0]} for i in itertools.combinations(league_teams_data, 2)]
    return first_meeting_matches + second_meeting_matches
