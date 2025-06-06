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
        from kivy.uix.widget import Widget
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
        self.manager.current = 'main'

class AddIdeaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        from kivy.uix.spinner import Spinner
        self.form = GridLayout(cols=2, spacing=5, size_hint_y=None)
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
        self.layout.add_widget(self.form)
        self.save_btn = Button(text='Save Idea', size_hint_y=None, height=50, on_press=self.on_save)
        self.layout.add_widget(self.save_btn)
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
        self.manager.current = 'main'

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
        self.manager.current = 'main'

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
        self.manager.current = 'main'

class VisualizationsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_app = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.image_box = BoxLayout(orientation='vertical', size_hint_y=0.9)
        self.layout.add_widget(self.image_box)
        self.refresh_btn = Button(text='Refresh Visualizations', size_hint_y=None, height=50, on_press=self.on_refresh)
        self.layout.add_widget(self.refresh_btn)
        self.back_btn = Button(text='Back', size_hint_y=None, height=50, on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        self.manager_app = getattr(app, 'manager', None)
        self.show_visualizations()

    def on_refresh(self, instance):
        self.show_visualizations()

    def show_visualizations(self):
        self.image_box.clear_widgets()
        if not self.manager_app or not hasattr(self.manager_app, 'history') or not hasattr(self.manager_app, 'ideas'):
            self.image_box.add_widget(Label(text='Error: Manager not loaded.'))
            return
        img_paths = self.generate_and_save_visualizations()
        for img_path in img_paths:
            if os.path.exists(img_path):
                self.image_box.add_widget(Image(source=img_path, allow_stretch=True, keep_ratio=True))

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
        # 1. Bar chart: Number of times each activity was done
        activity_counts = Counter(entry['activity_name'] for entry in history)
        activities, counts = zip(*sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)) if activity_counts else ([],[])
        if activities:
            plt.figure(figsize=(8, 4))
            plt.bar(activities, counts, color='skyblue')
            plt.title('Number of Times Each Activity Was Done')
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')
            plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            plt.tight_layout()
            img1 = 'activity_counts.png'
            plt.savefig(img1)
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
            plt.savefig(img2)
            plt.close()
            img_paths.append(img2)
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
            img3 = 'tag_counts.png'
            plt.savefig(img3)
            plt.close()
            img_paths.append(img3)
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
            img4 = 'monthly_spending.png'
            plt.savefig(img4)
            plt.close()
            img_paths.append(img4)
        return img_paths

    def go_back(self, instance):
        self.manager.current = 'main'
class DatePickerApp(App):
    def build(self):
        self.manager = DateIdeaManager(IDEAS_FILE)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainMenuScreen(name='main'))
        sm.add_widget(SampleIdeaScreen(name='sample'))
        sm.add_widget(AddIdeaScreen(name='add_idea'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(ClearHistoryScreen(name='clear_history'))
        sm.add_widget(AnalysisScreen(name='analysis'))
        sm.add_widget(VisualizationsScreen(name='visualizations'))
        return sm

if __name__ == '__main__':
    DatePickerApp().run()
