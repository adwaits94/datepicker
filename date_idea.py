from typing import List
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class DateIdea:
    name: str
    liked_by: List[str]
    location: List[str]
    tags: List[str] = field(default_factory=list)
    cost: int = 0
    max_people: int = 2
    cost_type: str = 'total'

    def cost_per_person(self) -> float:
        if self.cost_type == 'total' and self.max_people:
            return self.cost / self.max_people
        return self.cost

    def __repr__(self):
        return (
            f"<DateIdea {self.name} ({', '.join(self.liked_by)}) - {', '.join(self.location)} | "
            f"Cost per person: ₹{self.cost_per_person():.2f}>"
        )
