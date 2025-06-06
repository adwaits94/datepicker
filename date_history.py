from typing import List, Dict, Optional
from datetime import datetime

class DateHistory:
    def __init__(self):
        self.history: List[Dict] = []

    def add_entry(self, activity_name: str, date: Optional[str] = None, cost_per_person: Optional[float] = None):
        """
        Adds an entry to the history with the given activity name, date, and cost per person.
        """
        self.history.append({
            "activity_name": activity_name,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "cost_per_person": cost_per_person
        })

    def get_history(self) -> List[Dict]:
        return self.history

    def clear(self):
        """Clears the history list."""
        self.history.clear()
