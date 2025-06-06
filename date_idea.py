from typing import List

class DateIdea:
    def __init__(self, name: str, liked_by: List[str], location: List[str], tags: List[str], cost: int, max_people: int, cost_type: str):
        self.name = name
        self.liked_by = liked_by  # ["bf", "gf"]
        self.location = location  # ["home", "outside"]
        self.tags = tags or []
        self.cost = cost
        self.max_people = max_people
        self.cost_type = cost_type

    def __repr__(self):
        # Calculate cost per person for display
        if self.cost_type == 'total' and self.max_people:
            cost_per_person = self.cost / self.max_people
        else:
            cost_per_person = self.cost
        return f"<DateIdea {self.name} ({', '.join(self.liked_by)}) - {', '.join(self.location)} | Cost per person: ₹{cost_per_person:.2f} | Max People: {self.max_people}>"
