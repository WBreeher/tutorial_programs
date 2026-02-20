# ===================
# 1) Imports
# ===================

import json
from pathlib import Path

# ===================
# 2) CONFIG / CONSTANTS
# ===================

TASKS_FILE = Path("tasks.json")

APP_NAME = "To-Do List Application"
APP_VERSION = "0.1.0"

COMMANDS = {
    "a": "add",
    "add": "add",
    "b": "remove",
    "remove": "remove",
    "c": "view",
    "view": "view",
    "d": "clear",
    "clear": "clear",
    "e": "exit",
    "exit": "exit",
}

# ===================
# 3) DATA MODELS
# ===================



# ===================
# 4) CORE FUNCTION
# ===================

def add_task(tasks): # Add Task to To-Do list function
    new_task = input("Please enter new task: ").strip()
    if not new_task:
        print("No new task added, please try again.")
    else:
        tasks.append(new_task)
        save_tasks(tasks)
        print(f"{new_task} has been added to your To-Do List.")

def remove_task(tasks, index):  # Remove Specific Task from To-Do list function
    removed = tasks.pop(index)
    save_tasks(tasks)
    return removed

def view_tasks(tasks):   # View To-Do list function
    if not tasks:
        print("Your To-Do list is empty")
    else:
        for i, task in enumerate(tasks, start=1):
            print(f"{i}) {task}")

def clear_list(tasks):  # Clear entire To-Do list function
    tasks.clear()
    save_tasks(tasks)
    print("Your To-Do list has been cleared.")

def save_tasks(tasks): # Save tasks to json file for persistent loading
    with TASKS_FILE.open("w", encoding="utf-8") as f:
        json.dump(tasks, f)

# ===================
# 5) UI \ INPUT-OUTPUT LAYER
# ===================

def show_menu() -> None: # prints the main menu
    print(f"\n{APP_NAME} v{APP_VERSION}")
    print("Please make a choice from the menu: ")
    print("A) Add.")
    print("B) Remove.")
    print("C) View.")
    print("D) Clear.")
    print("E) Exit.")

def get_menu_choice() -> str: # collects and cleans input
    return input("Choice: ").strip().lower()

def get_action() -> str: # turns raw input into an action
    choice = get_menu_choice()
    if choice in COMMANDS:
        return COMMANDS[choice]
    print("Invalid option, please try again.")
    return ""

# ===================
# 6) MAIN PROGRAM LOOP
# ===================
def main():

    if not TASKS_FILE.exists(): # Ensure file exists on first start and future loads
        with TASKS_FILE.open("w", encoding="utf-8") as f:
            json.dump([], f)

    with TASKS_FILE.open("r", encoding="utf-8") as f:
        task_file = json.load(f)

        tasks = task_file

    while True:  
        show_menu()

        action = get_action()

        if not action:
            continue

        elif action == "add":
            add_task(tasks)

        elif action == "remove":
            if not tasks:
                print("Your To-Do list is empty")
                continue

            view_tasks(tasks)

            remove_choice = input("Which number would you like removed?").strip()

            try:
                selected_choice = int(remove_choice)
                index = selected_choice - 1

                if 0 <= index < len(tasks):
                    removed = remove_task(tasks, index)
                    print(f"'{removed}' has been removed.")
                else:
                    print("Invalid number. Please try again.")

            except ValueError:
                print("Please enter a valid number")

        elif action == "view":
            view_tasks(tasks)

        elif action == "clear":
            clear_confirm = input("Are you sure you want to clear the To-Do list? You can't undo this action! Y/N: ").strip().lower()

            if clear_confirm == "y":
                clear_list(tasks)

            else:
                continue

        elif action == "exit":
            print(f"Thank you for using {APP_NAME} v{APP_VERSION}")
            break

# ===================
# 7) Run Guard
# ===================
if __name__ == "__main__":
    main()