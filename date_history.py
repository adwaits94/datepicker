from typing import List, Dict
from datetime import datetime

class DateHistory:
    def __init__(self):
        self.history: List[Dict] = []

    def add_entry(self, activity_name: str, date=None):
        """
        Adds an entry to the history with the given activity name and date.
        """
        self.history.append({
            "activity_name": activity_name,
            "date": date or datetime.now().strftime("%Y-%m-%d")
        })

    def get_history(self):
        return self.history
