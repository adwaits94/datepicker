# Date Idea Picker

This project helps you manage, track, and analyze date ideas with customizable attributes. It features a Kivy-based graphical interface for desktop and Android (via Buildozer).

---

## Features

- **Add, view, and edit date ideas** with attributes:
  - Liked by (bf/gf/both)
  - Location (home/outside/both)
  - Tags
  - Cost (total or per person)
  - Max people
  - Cost type
- **Sample ideas** by filters (liked by, location, max cost, group size)
- **Track history** of used ideas and expenses
- **Clear history** (all or last N entries)
- **Analysis**: Suggestions for balancing activities by person, location, or tag
- **Visualizations**: Bar charts and Venn diagrams for activity counts, tags, liked by, and spending
- **Edit or delete** any idea
- **Android APK packaging** via Buildozer

---

## Structure

- [`date_idea.py`](date_idea.py): `DateIdea` dataclass (all attributes)
- [`date_history.py`](date_history.py): `DateHistory` class (history management)
- [`date_manager.py`](date_manager.py): `DateIdeaManager` (sampling, analysis, visualizations)
- [`ideas.json`](ideas.json): List of date ideas (editable)
- [`history.json`](history.json): Usage history (auto-managed)
- [`main.py`](main.py): Kivy GUI app (entry point for desktop and Android)
- [`environment.yml`](environment.yml): Conda/micromamba environment file

---

## Getting Started

1. **Add your date ideas** to `ideas.json` (include `cost`, `max_people`, and `cost_type` for each idea).
2. **Run the GUI app**:
   ```bash
   python main.py
   ```
   (or `python main_kivy.py` if you haven't renamed it)

---

## Example Usage (Python API)

```python
from date_manager import DateIdeaManager

manager = DateIdeaManager("ideas.json")
# n_people and max_cost are required
idea = manager.sample_idea(liked_by="bf", location="home", max_cost=10, n_people=2)
print(idea)
```
- If an idea's `cost_type` is 'total', the cost is divided by `n_people` for per-person budgeting.
- If `cost_type` is 'per_person', the cost is used as is.

> **Note:** Both `n_people` and `max_cost` are required when sampling an idea.

---

## Android APK Packaging

1. **Use WSL/Ubuntu** (Buildozer does not work on Windows natively).
2. Install dependencies (see [Kivy docs](https://kivy.org/doc/stable/guide/packaging-android.html)).
3. Copy your project to WSL.
4. In your project folder:
   ```bash
   buildozer init
   # Edit buildozer.spec: set requirements (kivy, matplotlib, matplotlib-venn), include .json files, etc.
   buildozer -v android debug
   ```
5. The APK will be in the `bin/` directory. Install it on your device or use:
   ```bash
   buildozer android deploy run
   ```

---

## Tips

- **For Android:** Rename or copy your Kivy app file to `main.py` before building.
- **All data** is stored in `ideas.json` and `history.json` in the app directory.
- **Edit/View Ideas:** Use the in-app "View/Edit Date Ideas" screen to update or delete ideas.

---

## Future

- More advanced analysis and filtering
- Improved mobile UI/UX
- Cloud sync or sharing
- Session sharing between bf and gf

---

## License

MIT License