# main_kivy.py
# Kivy-based Android app entry point for DatePicker
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics.texture import Texture
from kivy.clock import mainthread
import os
from date_manager import DateIdeaManager
from kivy.uix.gridlayout import GridLayout

# Set window size for desktop testing
Window.size = (400, 700)

IDEAS_FILE = 'ideas.json'

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Button(text='Sample Date Idea', size_hint_y=None, height=60, on_press=self.sample_idea))
        layout.add_widget(Button(text='Add Date Idea', size_hint_y=None, height=60, on_press=self.add_idea))
        layout.add_widget(Button(text='View/Edit Date Ideas', size_hint_y=None, height=60, on_press=self.edit_ideas))
        layout.add_widget(Button(text='View History', size_hint_y=None, height=60, on_press=self.view_history))
        layout.add_widget(Button(text='Clear History', size_hint_y=None, height=60, on_press=self.clear_history))
        layout.add_widget(Button(text='Show Analysis', size_hint_y=None, height=60, on_press=self.show_analysis))
        layout.add_widget(Button(text='Show Visualizations', size_hint_y=None, height=60, on_press=self.show_visualizations))
        self.add_widget(layout)

    def sample_idea(self, instance):
        self.manager.current = 'sample'

    def add_idea(self, instance):
        self.manager.current = 'add_idea'

    def view_history(self, instance):
        self.manager.current = 'history'

    def clear_history(self, instance):
        self.manager.current = 'clear_history'

    def show_analysis(self, instance):
        self.manager.current = 'analysis'

    def show_visualizations(self, instance):
        self.manager.current = 'visualizations'

    def edit_ideas(self, instance):
        self.manager.current = 'edit_ideas'

class SampleIdeaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None  # Will be set in on_enter
        self.sampled_idea = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        # Filter form
        from kivy.uix.spinner import Spinner
        self.form = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.liked_by_spinner = Spinner(text='Select', values=['bf', 'gf', 'both'], size_hint_y=None, height=40)
        self.location_spinner = Spinner(text='Select', values=['home', 'outside', 'both'], size_hint_y=None, height=40)
        self.max_cost_input = TextInput(hint_text='Max Cost (₹)', input_filter='float', multiline=False, size_hint_y=None, height=40)
        self.n_people_input = TextInput(hint_text='Number of People', input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.form.add_widget(Label(text='Liked By:'))
        self.form.add_widget(self.liked_by_spinner)
        self.form.add_widget(Label(text='Location:'))
        self.form.add_widget(self.location_spinner)
        self.form.add_widget(Label(text='Max Cost:'))
        self.form.add_widget(self.max_cost_input)
        self.form.add_widget(Label(text='People:'))
        self.form.add_widget(self.n_people_input)
        self.layout.add_widget(self.form)
        # Add a spacer to push the idea label and buttons down
        self.layout.add_widget(Widget(size_hint_y=0.2))
        self.idea_label = Label(text='', size_hint_y=None, height=160)
        self.layout.add_widget(self.idea_label)
        self.sample_btn = Button(text='Sample Idea', size_hint_y=None, height=50, on_press=self.on_sample)
        self.layout.add_widget(self.sample_btn)
        # Accept/Reject/Cancel buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.accept_btn = Button(text='Accept', on_press=self.on_accept)
        self.reject_btn = Button(text='Reject', on_press=self.on_reject)
        self.cancel_btn = Button(text='Cancel', on_press=self.on_cancel)
        btn_layout.add_widget(self.accept_btn)
        btn_layout.add_widget(self.reject_btn)
        btn_layout.add_widget(self.cancel_btn)
        self.layout.add_widget(btn_layout)
        self.add_widget(self.layout)

    def on_enter(self):
        # Get manager from App
        self.manager_app = getattr(App.get_running_app(), 'manager', None)
        self.idea_label.text = ''
        self.sampled_idea = None

    def on_sample(self, instance):
        liked_by = self.liked_by_spinner.text
        location = self.location_spinner.text
        try:
            max_cost = float(self.max_cost_input.text)
            n_people = int(self.n_people_input.text)
        except Exception:
            self.idea_label.text = 'Please enter valid numbers for cost and people.'
            return
        # Map 'both' to None for filter
        liked_by = None if liked_by == 'Select' or liked_by == 'both' else liked_by
        location = None if location == 'Select' or location == 'both' else location
        # Ensure manager_app is initialized
        if self.manager_app is None:
            self.manager_app = getattr(App.get_running_app(), 'manager', None)
            if self.manager_app is None:
                self.idea_label.text = 'Error: Manager not loaded.'
                return
        try:
            idea = self.manager_app.sample_idea(liked_by=liked_by, location=location, max_cost=max_cost, n_people=n_people)
        except Exception as e:
            self.idea_label.text = str(e)
            return
        if not idea:
            self.idea_label.text = 'No suitable date idea found.'
            self.sampled_idea = None
            return
        self.sampled_idea = idea
        # Show idea details
        self.idea_label.text = f"[b]{idea.name}[/b]\nLiked by: {', '.join(idea.liked_by)}\nLocation: {', '.join(idea.location)}\nTags: {', '.join(idea.tags)}\nCost per person: ₹{self.manager_app._cost_per_person(idea, n_people):.2f}"
        self.idea_label.markup = True
        self.idea_label.height = max(160, self.idea_label.texture_size[1] + 20)

    def on_accept(self, instance):
        if not self.sampled_idea:
            self.idea_label.text = 'Sample an idea first.'
            return
        try:
            n_people = int(self.n_people_input.text)
        except Exception:
            self.idea_label.text = 'Enter valid number of people.'
            return
        if not self.manager_app:
            self.idea_label.text = 'Error: Manager not loaded.'
            return
        self.manager_app.record_date(self.sampled_idea, n_people=n_people)
        popup = Popup(title='Saved', content=Label(text='Date idea saved to history!'), size_hint=(0.7, 0.3))
        popup.open()
        self.idea_label.text = ''
        self.sampled_idea = None

    def on_reject(self, instance):
        self.on_sample(instance)

    def on_cancel(self, instance):
        self.manager.current = 'main_menu'

class AddIdeaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        # Use a ScrollView to make the form scrollable and prevent overlap
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.scroll = ScrollView(size_hint=(1, 1))
        from kivy.uix.gridlayout import GridLayout
        self.form = GridLayout(cols=2, spacing=5, size_hint_y=None, padding=[0, 0, 0, 20])
        self.form.height = 7 * 50  # 7 rows, 50px each (approximate)
        from kivy.uix.spinner import Spinner
        self.name_input = TextInput(hint_text='Name', multiline=False, size_hint_y=None, height=40)
        self.liked_by_spinner = Spinner(text='Select', values=['bf', 'gf', 'both'], size_hint_y=None, height=40)
        self.location_spinner = Spinner(text='Select', values=['home', 'outside', 'both'], size_hint_y=None, height=40)
        self.tags_input = TextInput(hint_text='Tags (comma separated)', multiline=False, size_hint_y=None, height=40)
        self.cost_input = TextInput(hint_text='Cost', input_filter='float', multiline=False, size_hint_y=None, height=40)
        self.max_people_input = TextInput(hint_text='Max People', input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.cost_type_spinner = Spinner(text='total', values=['total', 'per_person'], size_hint_y=None, height=40)
        self.form.add_widget(Label(text='Name:'))
        self.form.add_widget(self.name_input)
        self.form.add_widget(Label(text='Liked By:'))
        self.form.add_widget(self.liked_by_spinner)
        self.form.add_widget(Label(text='Location:'))
        self.form.add_widget(self.location_spinner)
        self.form.add_widget(Label(text='Tags:'))
        self.form.add_widget(self.tags_input)
        self.form.add_widget(Label(text='Cost:'))
        self.form.add_widget(self.cost_input)
        self.form.add_widget(Label(text='Max People:'))
        self.form.add_widget(self.max_people_input)
        self.form.add_widget(Label(text='Cost Type:'))
        self.form.add_widget(self.cost_type_spinner)
        self.scroll.add_widget(self.form)
        self.layout.add_widget(self.scroll)
        # Add Save and Cancel buttons in a horizontal BoxLayout
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.save_btn = Button(text='Save Idea', on_press=self.on_save)
        self.cancel_btn = Button(text='Cancel', on_press=self.on_cancel)
        btn_layout.add_widget(self.save_btn)
        btn_layout.add_widget(self.cancel_btn)
        self.layout.add_widget(btn_layout)
        self.status_label = Label(text='', size_hint_y=None, height=40)
        self.layout.add_widget(self.status_label)
        self.add_widget(self.layout)

    def on_enter(self):
        self.manager_app = getattr(App.get_running_app(), 'manager', None)
        self.status_label.text = ''

    def on_save(self, instance):
        name = self.name_input.text.strip()
        liked_by = [self.liked_by_spinner.text] if self.liked_by_spinner.text != 'both' else ['bf', 'gf']
        location = [self.location_spinner.text] if self.location_spinner.text != 'both' else ['home', 'outside']
        tags = [t.strip() for t in self.tags_input.text.split(',') if t.strip()]
        try:
            cost = float(self.cost_input.text)
            max_people = int(self.max_people_input.text)
        except Exception:
            self.status_label.text = 'Enter valid numbers for cost and max people.'
            return
        cost_type = self.cost_type_spinner.text
        if not name:
            self.status_label.text = 'Name is required.'
            return
        # Save to ideas.json
        import json
        idea = {
            'name': name,
            'liked_by': liked_by,
            'location': location,
            'tags': tags,
            'cost': cost,
            'max_people': max_people,
            'cost_type': cost_type
        }
        try:
            with open('ideas.json', 'r', encoding='utf-8') as f:
                ideas = json.load(f)
        except Exception:
            ideas = []
        ideas.append(idea)
        with open('ideas.json', 'w', encoding='utf-8') as f:
            json.dump(ideas, f, ensure_ascii=False, indent=2)
        # Reload ideas in manager
        if self.manager_app:
            self.manager_app.ideas = self.manager_app.load_ideas('ideas.json')
        self.status_label.text = 'Idea saved!'
        self.name_input.text = ''
        self.tags_input.text = ''
        self.cost_input.text = ''
        self.max_people_input.text = ''
        self.liked_by_spinner.text = 'Select'
        self.location_spinner.text = 'Select'
        self.cost_type_spinner.text = 'total'

    def on_cancel(self, instance):
        self.manager.current = 'main_menu'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.history_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.scroll.add_widget(self.history_grid)
        self.layout.add_widget(self.scroll)
        self.back_btn = Button(text='Back', size_hint_y=None, height=50, on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        self.manager_app = getattr(app, 'manager', None)
        self.history_grid.clear_widgets()
        history = self.manager_app.history.get_history() if self.manager_app else []
        if not history:
            self.history_grid.add_widget(Label(text='No history yet.'))
        else:
            for entry in reversed(history):
                text = f"[b]{entry['activity_name']}[/b] | {entry['date']} | ₹{entry.get('cost_per_person', 0):.2f}"
                lbl = Label(text=text, markup=True, size_hint_y=None, height=40)
                self.history_grid.add_widget(lbl)

    def go_back(self, instance):
        self.manager.current = 'main_menu'

class ClearHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.info_label = Label(text='Clear all history or last N entries:', size_hint_y=None, height=40)
        self.layout.add_widget(self.info_label)
        self.n_input = TextInput(hint_text='Number of entries (leave blank for all)', input_filter='int', multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.n_input)
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.clear_btn = Button(text='Clear', on_press=self.on_clear)
        self.back_btn = Button(text='Back', on_press=self.go_back)
        btn_layout.add_widget(self.clear_btn)
        btn_layout.add_widget(self.back_btn)
        self.layout.add_widget(btn_layout)
        self.status_label = Label(text='', size_hint_y=None, height=40)
        self.layout.add_widget(self.status_label)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        self.manager_app = getattr(app, 'manager', None)
        self.status_label.text = ''
        self.n_input.text = ''

    def on_clear(self, instance):
        if not self.manager_app:
            self.status_label.text = 'Error: Manager not loaded.'
            return
        n_text = self.n_input.text.strip()
        try:
            n = int(n_text) if n_text else None
        except Exception:
            self.status_label.text = 'Enter a valid number.'
            return
        self.manager_app.history.clear(n)
        self.status_label.text = f"History cleared{' (last ' + n_text + ' entries)' if n else ' (all)'}!"

    def go_back(self, instance):
        self.manager.current = 'main_menu'

class AnalysisScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.scroll = ScrollView(size_hint=(1, 0.8), do_scroll_x=False)
        # Use a single Label, always fill width, update height after setting text
        self.suggestions_label = Label(
            text='',
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=(10, 10),
        )
        self.scroll.add_widget(self.suggestions_label)
        self.layout.add_widget(self.scroll)
        self.back_btn = Button(text='Back', size_hint_y=None, height=50, on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)

    def update_label_size(self):
        # Always fill the scrollview width, minus padding
        width = self.scroll.width - 20
        self.suggestions_label.text_size = (width, None)
        self.suggestions_label.width = width
        self.suggestions_label.texture_update()
        self.suggestions_label.height = self.suggestions_label.texture_size[1]

    def on_enter(self):
        app = App.get_running_app()
        self.manager_app = getattr(app, 'manager', None)
        suggestions = self.manager_app.analyze() if self.manager_app else []
        if suggestions:
            self.suggestions_label.text = '\n\n'.join(suggestions)
        else:
            self.suggestions_label.text = 'No suggestions. Try more activities!'
        self.update_label_size()

    def go_back(self, instance):
        self.manager.current = 'main_menu'

class VisualizationsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.image_box = BoxLayout(orientation='vertical', size_hint_y=0.7)
        self.layout.add_widget(self.image_box)
        # Navigation buttons
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.prev_btn = Button(text='Previous', on_press=self.on_prev)
        self.next_btn = Button(text='Next', on_press=self.on_next)
        nav_layout.add_widget(self.prev_btn)
        nav_layout.add_widget(self.next_btn)
        self.layout.add_widget(nav_layout)
        self.refresh_btn = Button(text='Refresh Visualizations', size_hint_y=None, height=50, on_press=self.on_refresh)
        self.layout.add_widget(self.refresh_btn)
        self.back_btn = Button(text='Back', size_hint_y=None, height=50, on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)
        self.img_paths = []
        self.current_index = 0

    def on_enter(self):
        app = App.get_running_app()
        self.manager_app = getattr(app, 'manager', None)
        self.show_visualizations()

    def on_refresh(self, instance=None):
        self.show_visualizations()

    def show_visualizations(self):
        self.img_paths = self.generate_and_save_visualizations()
        self.current_index = 0
        self.update_image()

    def update_image(self):
        self.image_box.clear_widgets()
        if not self.img_paths:
            self.image_box.add_widget(Label(text='No visualizations available.'))
            self.prev_btn.disabled = True
            self.next_btn.disabled = True
            return
        img_path = self.img_paths[self.current_index]
        if os.path.exists(img_path):
            self.image_box.add_widget(Image(source=img_path, allow_stretch=True, keep_ratio=True))
        # Update button states
        self.prev_btn.disabled = self.current_index == 0
        self.next_btn.disabled = self.current_index == len(self.img_paths) - 1

    def on_prev(self, instance):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def on_next(self, instance):
        if self.current_index < len(self.img_paths) - 1:
            self.current_index += 1
            self.update_image()

    def generate_and_save_visualizations(self):
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        from matplotlib_venn import venn2
        from collections import Counter, defaultdict
        from datetime import datetime
        if not self.manager_app or not hasattr(self.manager_app, 'history') or not hasattr(self.manager_app, 'ideas'):
            return []
        history = self.manager_app.history.get_history()
        if not history:
            return []
        idea_by_name = {idea.name: idea for idea in self.manager_app.ideas}
        img_paths = []
        # 1. Bar chart: Number of times each activity was done (horizontal)
        activity_counts = Counter(entry['activity_name'] for entry in history)
        activities, counts = zip(*sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)) if activity_counts else ([],[])
        if activities:
            plt.figure(figsize=(5, max(3, len(activities)*0.6)))
            plt.barh(activities, counts, color='skyblue')
            plt.title('Number of Times Each Activity Was Done')
            plt.xlabel('Count')
            plt.ylabel('Activity')
            plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            plt.tight_layout()
            img1 = 'activity_counts.png'
            plt.savefig(img1, bbox_inches='tight')
            plt.close()
            img_paths.append(img1)
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
        if bf_set or gf_set:
            plt.figure(figsize=(6, 6))
            venn2((bf_set, gf_set), set_labels=('bf', 'gf'))
            plt.title('Percent of Dates Liked by bf, gf, and Both')
            img2 = 'liked_by_venn.png'
            plt.savefig(img2, bbox_inches='tight')
            plt.close()
            img_paths.append(img2)
        # 3. Bar chart: Total count of tags (sorted by count, horizontal)
        tag_counter = Counter()
        for entry in history:
            idea = idea_by_name.get(entry['activity_name'])
            if idea:
                tag_counter.update(idea.tags)
        if tag_counter:
            tags, tag_counts = zip(*sorted(tag_counter.items(), key=lambda x: x[1], reverse=True))
            plt.figure(figsize=(5, max(3, len(tags)*0.6)))
            plt.barh(tags, tag_counts, color='orange')
            plt.title('Total Count of Tags (All Time)')
            plt.xlabel('Count')
            plt.ylabel('Tag')
            plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            plt.tight_layout()
            img3 = 'tag_counts.png'
            plt.savefig(img3, bbox_inches='tight')
            plt.close()
            img_paths.append(img3)
        # 4. Bar chart: Money spent per person on dates per month (horizontal)
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
            plt.figure(figsize=(5, max(3, len(months)*0.6)))
            plt.barh(months, spend, color='green')
            plt.title('Money Spent Per Person on Dates Per Month (₹)')
            plt.xlabel('Total Spent Per Person (₹)')
            plt.ylabel('Month')
            # Only set integer ticks if all values are integers
            if all(float(x).is_integer() for x in spend):
                plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            plt.tight_layout()
            img4 = 'monthly_spending.png'
            plt.savefig(img4, bbox_inches='tight')
            plt.close()
            img_paths.append(img4)
        return img_paths

    def go_back(self, instance):
        self.manager.current = 'main_menu'

class EditIdeasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.ideas_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=30, padding=[0, 0, 0, 20])
        self.ideas_box.height = 0  # Will be set dynamically
        self.scroll.add_widget(self.ideas_box)
        self.layout.add_widget(self.scroll)
        self.back_btn = Button(text='Back', size_hint_y=None, height=50, on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        self.status_label = Label(text='', size_hint_y=None, height=40)
        self.layout.add_widget(self.status_label)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        self.manager_app = getattr(app, 'manager', None)
        self.refresh_ideas()
        self.scroll.scroll_y = 1

    def refresh_ideas(self):
        import json
        self.ideas_box.clear_widgets()
        try:
            with open('ideas.json', 'r', encoding='utf-8') as f:
                ideas = json.load(f)
        except Exception:
            ideas = []
        total_height = 0
        for idx, idea in enumerate(ideas):
            editor = self._make_idea_editor(idea, idx, ideas)
            self.ideas_box.add_widget(editor)
            # Add a separator for clarity
            if idx < len(ideas) - 1:
                self.ideas_box.add_widget(Widget(size_hint_y=None, height=10))
                total_height += 10
            total_height += editor.height
        self.ideas_box.height = max(1, total_height)

    def _make_idea_editor(self, idea, idx, all_ideas):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.spinner import Spinner

        box = BoxLayout(orientation='vertical', spacing=6, padding=10, size_hint_y=None)
        # Each field: label + input
        fields = []

        name_input = TextInput(text=idea.get('name', ''), multiline=False, size_hint_y=None, height=40)
        fields.append((Label(text='Name:', size_hint_y=None, height=20), name_input))

        liked_by_spinner = Spinner(
            text=','.join(idea.get('liked_by', [])),
            values=['bf', 'gf', 'both'],
            size_hint_y=None, height=40
        )
        fields.append((Label(text='Liked By:', size_hint_y=None, height=20), liked_by_spinner))

        location_spinner = Spinner(
            text=','.join(idea.get('location', [])),
            values=['home', 'outside', 'both'],
            size_hint_y=None, height=40
        )
        fields.append((Label(text='Location:', size_hint_y=None, height=20), location_spinner))

        tags_input = TextInput(text=','.join(idea.get('tags', [])), multiline=False, size_hint_y=None, height=40)
        fields.append((Label(text='Tags:', size_hint_y=None, height=20), tags_input))

        cost_input = TextInput(text=str(idea.get('cost', '')), input_filter='float', multiline=False, size_hint_y=None, height=40)
        fields.append((Label(text='Cost:', size_hint_y=None, height=20), cost_input))

        max_people_input = TextInput(text=str(idea.get('max_people', '')), input_filter='int', multiline=False, size_hint_y=None, height=40)
        fields.append((Label(text='Max People:', size_hint_y=None, height=20), max_people_input))

        cost_type_spinner = Spinner(
            text=idea.get('cost_type', 'total'),
            values=['total', 'per_person'],
            size_hint_y=None, height=40
        )
        fields.append((Label(text='Cost Type:', size_hint_y=None, height=20), cost_type_spinner))

        for label, widget in fields:
            box.add_widget(label)
            box.add_widget(widget)

        status = Label(text='', size_hint_y=None, height=30)
        def on_save(_):
            new_idea = {
                'name': name_input.text.strip(),
                'liked_by': [liked_by_spinner.text] if liked_by_spinner.text != 'both' else ['bf', 'gf'],
                'location': [location_spinner.text] if location_spinner.text != 'both' else ['home', 'outside'],
                'tags': [t.strip() for t in tags_input.text.split(',') if t.strip()],
                'cost': float(cost_input.text) if cost_input.text else 0.0,
                'max_people': int(max_people_input.text) if max_people_input.text else 1,
                'cost_type': cost_type_spinner.text
            }
            all_ideas[idx] = new_idea
            try:
                with open('ideas.json', 'w', encoding='utf-8') as f:
                    import json
                    json.dump(all_ideas, f, ensure_ascii=False, indent=2)
                status.text = 'Saved!'
            except Exception as e:
                status.text = f'Error: {e}'
            if self.manager_app:
                self.manager_app.ideas = self.manager_app.load_ideas('ideas.json')
        def on_delete(_):
            del all_ideas[idx]
            try:
                with open('ideas.json', 'w', encoding='utf-8') as f:
                    import json
                    json.dump(all_ideas, f, ensure_ascii=False, indent=2)
                status.text = 'Deleted!'
            except Exception as e:
                status.text = f'Error: {e}'
            if self.manager_app:
                self.manager_app.ideas = self.manager_app.load_ideas('ideas.json')
            self.refresh_ideas()
        save_btn = Button(text='Save Changes', size_hint_y=None, height=40, on_press=on_save)
        delete_btn = Button(text='Delete', size_hint_y=None, height=40, on_press=on_delete)
        btns = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        btns.add_widget(save_btn)
        btns.add_widget(delete_btn)
        box.add_widget(btns)
        box.add_widget(status)
        # Dynamically set height
        box.height = 8*40 + 7*20 + 40 + 30 + 20  # 8 fields, 7 labels, buttons, status, padding
        return box

    def go_back(self, instance):
        self.manager.current = 'main_menu'

class DatePickerApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        # sm.app = self  # Remove this line, not needed
        self.manager = DateIdeaManager(IDEAS_FILE)  # Use 'manager' for consistency
        # Expose ideas and history for screens that expect them
        self.ideas = self.manager.ideas
        self.history = self.manager.history
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(SampleIdeaScreen(name='sample'))
        sm.add_widget(AddIdeaScreen(name='add_idea'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(ClearHistoryScreen(name='clear_history'))
        sm.add_widget(AnalysisScreen(name='analysis'))
        sm.add_widget(VisualizationsScreen(name='visualizations'))
        sm.add_widget(EditIdeasScreen(name='edit_ideas'))
        return sm

if __name__ == '__main__':
    DatePickerApp().run()
