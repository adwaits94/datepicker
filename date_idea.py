from typing import List

class DateIdea:
    def __init__(self, name: str, liked_by: List[str], location: List[str], tags: List[str], cost: int = 0, max_people: int = 2):
        self.name = name
        self.liked_by = liked_by  # ["bf", "gf"]
        self.location = location  # ["home", "outside"]
        self.tags = tags or []
        self.cost = cost
        self.max_people = max_people

    def __repr__(self):
        return f"<DateIdea {self.name} ({', '.join(self.liked_by)}) - {', '.join(self.location)} | Cost: {self.cost} | Max People: {self.max_people}>"
