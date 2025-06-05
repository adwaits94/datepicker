import json
import random
from date_idea import DateIdea
from date_history import DateHistory

class DateIdeaManager:
    def __init__(self, ideas_file: str):
        self.ideas = self.load_ideas(ideas_file)
        self.history = DateHistory()

    def load_ideas(self, ideas_file: str):
        with open(ideas_file, 'r') as f:
            ideas_data = json.load(f)
        return [DateIdea(**idea) for idea in ideas_data]

    def sample_idea(self, liked_by=None, location=None):
        filtered = self.ideas
        if liked_by:
            filtered = [i for i in filtered if liked_by in i.liked_by]
        if location:
            # Accept both 'indoor'/'home' and 'outdoor'/'outside' for compatibility
            location_map = {"indoor": "home", "outdoor": "outside", "home": "home", "outside": "outside"}
            mapped_location = location_map.get(location, location)
            filtered = [i for i in filtered if mapped_location in i.location]
        if not filtered:
            return None
        return random.choice(filtered)

    def record_date(self, idea: DateIdea):
        self.history.add_entry(idea.name)

    def analyze(self):
        # Example: count how many times each idea was used
        stats = {}
        for entry in self.history.get_history():
            stats[entry['activity_name']] = stats.get(entry['activity_name'], 0) + 1
        return stats
