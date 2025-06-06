import json
import random
from date_idea import DateIdea
from date_history import DateHistory
from typing import Optional, List
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib_venn import venn2
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime

class DateIdeaManager:
    def __init__(self, ideas_file: str):
        self.ideas: List[DateIdea] = self.load_ideas(ideas_file)
        self.history = DateHistory()

    def load_ideas(self, ideas_file: str) -> List[DateIdea]:
        with open(ideas_file, 'r', encoding='utf-8') as f:
            ideas_data = json.load(f)
        return [DateIdea(**idea) for idea in ideas_data]

    def _cost_per_person(self, idea, n_people):
        if idea.cost_type == 'total':
            return idea.cost / n_people if n_people else idea.cost
        return idea.cost

    def sample_idea(self, liked_by: Optional[str] = None, location: Optional[str] = None, max_cost: Optional[float] = None, n_people: Optional[int] = None) -> Optional[DateIdea]:
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
        filtered = [i for i in filtered if self._cost_per_person(i, n_people) <= max_cost]
        if not filtered:
            return None
        return random.choice(filtered)

    def record_date(self, idea: DateIdea, date: Optional[str] = None, n_people: Optional[int] = None):
        """ Records a date idea in the history. """
        if not isinstance(idea, DateIdea):
            raise ValueError("Expected a DateIdea instance")
        if n_people is None:
            raise ValueError("n_people must be specified to record cost per person.")
        cost_per_person = self._cost_per_person(idea, n_people)
        self.history.add_entry(idea.name, date, cost_per_person)  # Date is optional, will use current date if None

    def clear_history(self):
        """Clears the date history."""
        self.history.clear()

    def analyze(self):
        """
        Returns only suggestions for balancing activities.
        """
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
            stats['by_idea'][idea.name] += 1
            for person in idea.liked_by:
                stats['by_liked_by'][person] += 1
            for loc in idea.location:
                stats['by_location'][loc] += 1
            for tag in idea.tags:
                stats['by_tag'][tag] += 1
            stats['total'] += 1
        suggestions = []
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
        return suggestions

    def generate_visualizations(self):
        """
        Generates and displays the following visualizations (scrolling top to bottom):
        1. Bar chart: Number of times each activity was done (sorted by count)
        2. Venn Diagram: Percent of dates liked by bf, gf, and both
        3. Bar chart: Total count of tags (sorted by count)
        4. Bar chart: Money spent on dates per month
        """
        history = self.history.get_history()
        if not history:
            print("No history to visualize.")
            return
        # Helper: get DateIdea by name
        idea_by_name = {idea.name: idea for idea in self.ideas}
        # 1. Bar chart: Number of times each activity was done
        activity_counts = Counter(entry['activity_name'] for entry in history)
        activities, counts = zip(*sorted(activity_counts.items(), key=lambda x: x[1], reverse=True))
        plt.figure(figsize=(8, 4))
        plt.bar(activities, counts, color='skyblue')
        plt.title('Number of Times Each Activity Was Done')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.show()
        # 2. Venn Diagram: Percent of dates liked by bf, gf, both
        bf_set, gf_set = set(), set()
        for entry in history:
            idea = idea_by_name.get(entry['activity_name'])
            if not idea:
                continue
            if 'bf' in idea.liked_by:
                bf_set.add(entry['activity_name'] + entry['date'])
            if 'gf' in idea.liked_by:
                gf_set.add(entry['activity_name'] + entry['date'])
        plt.figure(figsize=(6, 6))
        venn2((bf_set, gf_set), set_labels=('bf', 'gf'))
        plt.title('Percent of Dates Liked by bf, gf, and Both')
        plt.show()
        # 3. Bar chart: Total count of tags (sorted by count)
        tag_counter = Counter()
        for entry in history:
            idea = idea_by_name.get(entry['activity_name'])
            if idea:
                tag_counter.update(idea.tags)
        if tag_counter:
            tags, tag_counts = zip(*sorted(tag_counter.items(), key=lambda x: x[1], reverse=True))
            plt.figure(figsize=(8, 4))
            plt.bar(tags, tag_counts, color='orange')
            plt.title('Total Count of Tags (All Time)')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            plt.tight_layout()
            plt.show()
        # 4. Bar chart: Money spent per person on dates per month
        month_spending = defaultdict(float)
        for entry in history:
            date_str = entry['date']
            try:
                month = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
            except Exception:
                continue
            cost_per_person = entry.get('cost_per_person')
            if cost_per_person is not None:
                month_spending[month] += cost_per_person
        if month_spending:
            months, spend = zip(*sorted(month_spending.items()))
            plt.figure(figsize=(8, 4))
            plt.bar(months, spend, color='green')
            plt.title('Money Spent Per Person on Dates Per Month (₹)')
            plt.ylabel('Total Spent Per Person (₹)')
            plt.xticks(rotation=45, ha='right')
            plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            plt.tight_layout()
            plt.show()
