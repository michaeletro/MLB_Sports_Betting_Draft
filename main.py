import re
import pandas as pd
import statsapi

class PlayerStats:
    def __init__(self, player_id):
        self.player_id = player_id
        self.stats = self.get_stats()

    def parse_year_by_year_stat_block(self, stat_str):
        # Split by year headers like '2018 Hitting'
        blocks = re.split(r'\n(?=\d{4} Hitting)', stat_str.strip())
        # Each block corresponds to a year of stats
        year_stats = []

        for block in blocks:
            lines = block.strip().split('\n')
            if not lines:
                continue

            # First line is the year
            header = lines[0]
            match = re.match(r'(\d{4}) Hitting', header)
            if not match:
                continue
            year = int(match.group(1))

            stat_dict = {'year': year}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value == '.---':
                        stat_dict[key] = None
                    else:
                        try:
                            stat_dict[key] = float(value) if '.' in value else int(value)
                        except:
                            stat_dict[key] = value
            year_stats.append(stat_dict)

        return pd.DataFrame(year_stats)

    def get_stats(self, type="yearByYear"):
        raw_stats = statsapi.player_stats(self.player_id, group="[hitting,pitching]", type=type)
        if type == "yearByYear":
            # Parse the year-by-year stats block
            return self.parse_year_by_year_stat_block(raw_stats)
        # For other types, we assume a single block of stats
        # Extract the stats from the raw string
        stat_lines = re.findall(r"(\w+):\s+([\d\.]+|\.---)", raw_stats)

        # Build a dictionary
        stat_dict = {}
        for key, value in stat_lines:
            if value == ".---":
                stat_dict[key] = None
            else:
                try:
                    stat_dict[key] = float(value) if '.' in value else int(value)
                except:
                    stat_dict[key] = value
        series_to_return = pd.Series(stat_dict)
        series_to_return.name = statsapi.lookup_player(self.player_id)[0]['fullName']
        return series_to_return

# Example usage
# Assuming you have a valid player ID for Shohei Ohtani
player_id = statsapi.lookup_player("Shohei Ohtani")[0]['id']
player_stats = PlayerStats(player_id)
print(player_stats.get_stats())