from collections import defaultdict

class FixtureValidator:
    def validate(self, fixtures, teams):
        errors = []
        matches = fixtures['matches']
        
        # 1. Check each pair plays exactly twice (once home, once away)
        pair_counts = defaultdict(lambda: {'home': 0, 'away': 0})
        for match in matches:
            home, away = match['Home Team'], match['Away Team']
            pair = tuple(sorted([home, away]))
            if home < away:
                pair_counts[pair]['home'] += 1
            else:
                pair_counts[pair]['away'] += 1
        
        for pair, counts in pair_counts.items():
            if counts['home'] != 1 or counts['away'] != 1:
                errors.append(f"Pair {pair} has invalid home/away counts: {counts}")

        # 2. Enhanced Town Rule Check
        town_teams = defaultdict(list)
        for team in teams:
            town_teams[team['Town']].append(team['Team'])

        # Track first town match weekend
        first_town_weekend = None
        town_matches = []
        other_matches = []
        
        for match in matches:
            home, away, town = match['Home Team'], match['Away Team'], match['Town']
            is_town_match = (home in town_teams[town]) and (away in town_teams[town])
            if is_town_match:
                town_matches.append(match)
                if first_town_weekend is None or match['Weekend'] < first_town_weekend:
                    first_town_weekend = match['Weekend']
            else:
                other_matches.append(match)

        # Check if all teams played at least one inter-town match before first town match
        if town_matches:
            teams_inter_town = set()
            for match in other_matches:
                if match['Weekend'] < first_town_weekend:
                    teams_inter_town.add(match['Home Team'])
                    teams_inter_town.add(match['Away Team'])
            
            all_teams = set(team['Team'] for team in teams)
            if teams_inter_town != all_teams:
                errors.append("Town matches scheduled before all teams played inter-town matches")

        # 3. Weekend Constraint (max 4 teams/weekend)
        weekend_teams = defaultdict(set)
        for match in matches:
            weekend = match['Weekend']
            weekend_teams[weekend].add(match['Home Team'])
            weekend_teams[weekend].add(match['Away Team'])
            if len(weekend_teams[weekend]) > 4:
                errors.append(f"Weekend {weekend} has {len(weekend_teams[weekend])} teams (max 4)")

        return errors if errors else None