from date_manager import DateIdeaManager

if __name__ == "__main__":
    manager = DateIdeaManager("ideas.json")
    n_people = 2
    while True:
        idea = manager.sample_idea(liked_by="bf", location="outside", max_cost=500, n_people=n_people)
        if not idea:
            print("No suitable date idea found.")
            break
        print(f"Suggested date idea: {idea}")
        user_input = input("Accept this idea? (y = accept, n = new idea, c = cancel): ").strip().lower()
        if user_input == 'y':
            manager.record_date(idea, n_people=n_people)
            print("Date idea accepted and saved to history.")
            break
        elif user_input == 'n':
            continue
        elif user_input == 'c':
            print("Date idea cancelled. Not saved to history.")
            break
        else:
            print("Invalid input. Please enter 'y', 'n', or 'c'.")
    print("\nHistory:")
    print(manager.history.get_history())
    print("\nAnalysis:")
    print(manager.analyze())
    print("\nGenerating visualizations...")
    manager.generate_visualizations()
