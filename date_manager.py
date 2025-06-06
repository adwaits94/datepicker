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

    def sample_idea(self, liked_by=None, location=None, max_cost=None, n_people=None):
        if n_people is None:
            raise ValueError("You must specify n_people (number of people) when sampling an idea.")
        if max_cost is None:
            raise ValueError("You must specify max_cost when sampling an idea.")
        filtered = self.ideas
        if liked_by:
            filtered = [i for i in filtered if liked_by in i.liked_by]
        if location:
            filtered = [i for i in filtered if location in i.location]
        filtered = [i for i in filtered if n_people <= i.max_people]
        def cost_filter(idea):
            if idea.cost_type == 'total':
                per_person_cost = idea.cost / n_people if n_people else idea.cost
                return per_person_cost <= max_cost
            else:  # 'per_person'
                return idea.cost <= max_cost
        filtered = [i for i in filtered if cost_filter(i)]
        if not filtered:
            return None
        return random.choice(filtered)

    def record_date(self, idea: DateIdea, date=None):
        """ Records a date idea in the history. """
        if not isinstance(idea, DateIdea):
            raise ValueError("Expected a DateIdea instance")
        self.history.add_entry(idea.name, date)  # Date is optional, will use current date if None

    def clear_history(self):
        """Clears the date history."""
        self.history.clear()

    def analyze(self):
        """
        Returns analysis of history:
        - Count by idea
        - Count by liked_by (bf/gf)
        - Count by location (home/outside)
        - Count by tag
        - Suggestions for balancing
        """
        # Collect all possible values from self.ideas
        all_liked_by = set()
        all_locations = set()
        all_tags = set()
        all_ideas = set()
        for idea in self.ideas:
            all_ideas.add(idea.name)
            all_liked_by.update(idea.liked_by)
            all_locations.update(idea.location)
            all_tags.update(idea.tags)
        stats = {
            'by_idea': {name: 0 for name in all_ideas},
            'by_liked_by': {person: 0 for person in all_liked_by},
            'by_location': {loc: 0 for loc in all_locations},
            'by_tag': {tag: 0 for tag in all_tags},
            'total': 0
        }
        for entry in self.history.get_history():
            idea = next((i for i in self.ideas if i.name == entry['activity_name']), None)
            if not idea:
                continue
            # By idea
            stats['by_idea'][idea.name] += 1
            # By liked_by
            for person in idea.liked_by:
                stats['by_liked_by'][person] += 1
            # By location
            for loc in idea.location:
                stats['by_location'][loc] += 1
            # By tag
            for tag in idea.tags:
                stats['by_tag'][tag] += 1
            stats['total'] += 1
        # Suggestions for balancing
        suggestions = []
        # Suggest all attributes with the minimum count (ties included), consolidated by attribute
        if stats['by_location'] and len(stats['by_location']) > 1:
            min_count = min(stats['by_location'].values())
            min_locs = [loc for loc, count in stats['by_location'].items() if count == min_count]
            if min_locs:
                suggestions.append(f"Try more activities at: {', '.join(min_locs)}")
        if stats['by_liked_by'] and len(stats['by_liked_by']) > 1:
            min_count = min(stats['by_liked_by'].values())
            min_people = [person for person, count in stats['by_liked_by'].items() if count == min_count]
            if min_people:
                suggestions.append(f"Try more activities liked by: {', '.join(min_people)}")
        if stats['by_tag'] and len(stats['by_tag']) > 1:
            min_count = min(stats['by_tag'].values())
            min_tags = [tag for tag, count in stats['by_tag'].items() if count == min_count]
            if min_tags:
                suggestions.append(f"Try more activities with tag: {', '.join(min_tags)}")
        stats['suggestions'] = suggestions
        return stats
