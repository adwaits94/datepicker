from date_manager import DateIdeaManager

if __name__ == "__main__":
    manager = DateIdeaManager("ideas.json")
    # n_people and max_cost are required
    idea = manager.sample_idea(liked_by="bf", location="outside", max_cost=500, n_people=2)
    print(idea)
    if idea:
        manager.record_date(idea)
    print("\nHistory:")
    print(manager.history.get_history())
    print("\nAnalysis:")
    print(manager.analyze())
