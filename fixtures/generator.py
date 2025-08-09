import pandas as pd
import random
from collections import defaultdict

class FixtureGenerator:
    def __init__(self, csv_file):
        self.teams = pd.read_csv(csv_file).to_dict('records')
        self.validate_teams()
    
    def validate_teams(self):
        if len(self.teams) != 10:
            raise ValueError("Exactly 10 teams required")
        
        towns = defaultdict(list)
        for team in self.teams:
            towns[team['Town']].append(team['Team'])
        
        for town, teams in towns.items():
            if len(teams) < 2:
                raise ValueError(f"Town {town} needs at least 2 teams")

    def generate_fixtures(self):
        # Generate all Leg 1 matches (no duplicates)
        matches = []
        for i in range(len(self.teams)):
            for j in range(i + 1, len(self.teams)):
                home = self.teams[i]
                away = self.teams[j]
                matches.append({
                    'home': home,
                    'away': away,
                    'town_match': home['Town'] == away['Town']
                })

        # Split into town and non-town matches (Leg 1)
        town_matches = [m for m in matches if m['town_match']]
        other_matches = [m for m in matches if not m['town_match']]
        random.shuffle(town_matches)
        random.shuffle(other_matches)

        # Generate Leg 2 (reverse home/away)
        second_leg = [{
            'home': m['away'],
            'away': m['home'],
            'town_match': m['town_match']
        } for m in matches]

        # Split Leg 2 into town and non-town
        second_leg_town = [m for m in second_leg if m['town_match']]
        second_leg_other = [m for m in second_leg if not m['town_match']]

        # Combine in CORRECT ORDER:
        # 1. Leg 1 inter-town
        # 2. Leg 1 town
        # 3. Leg 2 inter-town
        # 4. Leg 2 town
        all_matches = (
            other_matches +      # Leg 1 inter-town
            town_matches +       # Leg 1 town
            second_leg_other +   # Leg 2 inter-town
            second_leg_town       # Leg 2 town
        )

        # Schedule weekends (2 matches per weekend)
        weekends = []
        weekend_num = 1
        while all_matches:
            weekend_matches = []
            teams_playing = set()

            for match in all_matches[:]:
                if (match['home']['Team'] not in teams_playing and 
                    match['away']['Team'] not in teams_playing):
                    
                    weekend_matches.append(match)
                    teams_playing.update([match['home']['Team'], match['away']['Team']])
                    all_matches.remove(match)
                    
                    if len(weekend_matches) == 2:
                        break

            if weekend_matches:
                weekends.append({
                    'weekend_num': weekend_num,
                    'matches': weekend_matches
                })
                weekend_num += 1

        # Format output
        formatted = []
        total_weekends = len(weekends)
        for weekend in weekends:
            for match in weekend['matches']:
                leg = 1 if weekend['weekend_num'] <= (total_weekends / 2) else 2
                formatted.append({
                    'Weekend': weekend['weekend_num'],
                    'Leg': leg,
                    'Home Team': match['home']['Team'],
                    'Away Team': match['away']['Team'],
                    'Stadium': match['home']['Stadium'],
                    'Town': match['home']['Town']
                })

        return {
            'matches': formatted,
            'teams': self.teams,
            'weekends': weekends
        }