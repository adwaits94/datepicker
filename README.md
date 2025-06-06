# Date Idea Picker - Python Project

This project helps you manage, track, and analyze date ideas with customizable attributes. Designed for easy configuration and future Android app integration.

## Features
- Store date ideas with attributes (liked by bf/gf/both, home/outside/both, tags, cost, max_people, and cost_type)
- Track which ideas are used and when
- Analyze history to balance future suggestions (by person, location, tag, cost, and group size)
- Filter and sample ideas by preferences, location, maximum cost (per person), and group size
- Supports both 'total' and 'per_person' cost types for flexible budgeting
- Easy configuration via JSON file
- Modular code for future Android app backend

## Structure
- `date_idea.py`: DateIdea class (now includes `cost`, `max_people`, and `cost_type`)
- `date_history.py`: DateHistory class
- `date_manager.py`: DateIdeaManager class (sampling supports `max_cost`, `n_people`, and cost_type logic)
- `ideas.json`: Configurable list of date ideas (each with a `cost`, `max_people`, and `cost_type` attribute)
- `main.py`: Example usage

## Getting Started
1. Add your date ideas to `ideas.json` (include a `cost`, `max_people`, and `cost_type` for each idea)
2. Run `main.py` to interact with the system

## Example Usage
```python
manager = DateIdeaManager("ideas.json")
# n_people and max_cost are required
idea = manager.sample_idea(liked_by="bf", location="home", max_cost=10, n_people=2)
print(idea)
```
- If an idea's `cost_type` is 'total', the cost is divided by `n_people` for per-person budgeting.
- If `cost_type` is 'per_person', the cost is used as is.

> **Note:** Both `n_people` and `max_cost` are now required when sampling an idea.

## Future
- Android app integration (Kivy, BeeWare, or REST API)
- More advanced analysis and filtering
- Graph for home/outside
- Fix Edit/View Date Idea screen
- Share and persist sessions between bf and gf