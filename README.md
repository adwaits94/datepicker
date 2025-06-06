# Date Idea Picker - Python Project

This project helps you manage, track, and analyze date ideas with customizable attributes. Designed for easy configuration and future Android app integration.

## Features
- Store date ideas with attributes (liked by bf/gf/both, home/outside/both, tags, cost, and max_people)
- Track which ideas are used and when
- Analyze history to balance future suggestions (by person, location, tag, cost, and n_people)
- Filter and sample ideas by preferences, location, maximum cost, and group size
- Easy configuration via JSON file
- Modular code for future Android app backend

## Structure
- `date_idea.py`: DateIdea class (now includes `cost` and `max_people`)
- `date_history.py`: DateHistory class
- `date_manager.py`: DateIdeaManager class (sampling supports `max_cost` and `max_people`)
- `ideas.json`: Configurable list of date ideas (each with a `cost` and `max_people` attribute)
- `main.py`: Example usage

## Getting Started
1. Add your date ideas to `ideas.json` (include a `cost` and `max_people` for each idea)
2. Run `main.py` to interact with the system

## Example Usage
```python
manager = DateIdeaManager("ideas.json")
idea = manager.sample_idea(liked_by="bf", location="home", max_cost=10, max_people=2)
print(idea)
```

## Future
- Android app integration (Kivy, BeeWare, or REST API)
- More advanced analysis and filtering
