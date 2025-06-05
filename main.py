from date_manager import DateIdeaManager

if __name__ == "__main__":
    manager = DateIdeaManager("ideas.json")
    print("Sample idea for bf, indoor:")
    idea = manager.sample_idea(liked_by="bf", location="home")
    print(idea)
    if idea:
        manager.record_date(idea)
    print("\nHistory:")
    print(manager.history.get_history())
    print("\nAnalysis:")
    print(manager.analyze())
