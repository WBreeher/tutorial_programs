# ===================
# 1) Imports
# ===================

import json                                                         # Used to serialize (save) and deserialize (load) habit data to/from a JSON file
from pathlib import Path                                            # Used to create a file paht object for habits.json
from datetime import date, timedelta                                # Used to get today's date for habit creation and completion tracking, and timedelta for streak math

# ===================
# 2) CONFIG / CONSTANTS
# ===================

APP_NAME = "Habit Tracker"                                          # Application name displayed in the menu header
APP_VERSION = "0.1.0"                                               # Current version of the application

HABITS_FILE = Path("habits.json")                                   # File path object representing the JSON file where habits are stored

COMMANDS = {                                                        # All Menu Commands
    "1": "add",                                                     # Numeric shortcut to add a new habit
    "add": "add",                                                   # Text command to add ↑

    "2": "delete",                                                  # Numeric shortcut to delete a habit by ID
    "delete": "delete",                                             # Text command to delete ↑

    "3": "view",                                                    # Numeric shortcut to view all habits
    "view": "view",                                                 # Text command to view ↑

    "4": "clear",                                                   # Numeric shortcut to clear all habits
    "clear": "clear",                                               # Text command to clear ↑

    "5": "mark",                                                    # Numeric shortcut to mark a habit complete for today
    "mark": "mark",                                                 # Text command to mark ↑
    "mark complete": "mark",                                        # Alternate text command to mark ↑↑

    "6": "exit",                                                    # Numeric shortcut to exit the application
    "exit": "exit",                                                 # Text command to exit ↑
}

# ===================
# 3) DATA MODELS
# ===================

HABIT_MODEL = {                                                     # Conceptual Template of expected structure of each habit dict
    "id": int,                                                      # Unique integer indentifier for each habit
    "name": str,                                                    # Name of the habit entered by the user
    "created on": "YYYY-MM-DD",                                     # ISO-formatted date string of when the habit was created
    "completed_dates": []                                           # List of ISO-formatted date strings when the habit was completed
}

# ===================
# 4) CORE FUNCTIONS
# ===================

def add_habit(tracked_habit):                                       # Add new habit function
    habit_name = input("Please enter the habit's name: ").strip()   # Ask the user for the habit name ane remove extra whitespace

    new_habit = {                                                   # Create a new habit dict with a unique ID and today's creation date
        "id": get_next_id(tracked_habit),                           # Generate the next available unique ID
        "name": habit_name,                                         # Store the user-provided habit name
        "created on": date.today().isoformat(),                     # Store today's date as ISO string
        "completed_dates": []                                       # Start with no completion history
    }

    tracked_habit.append(new_habit)                                 # Add the new habit dict to the list of tracked habits
    save_habits(tracked_habit)                                      # Persist the updated habit list to the JSON file

def get_next_id(tracked_habits) -> int:                             # Get new ID function
    if not tracked_habits:                                          # If there are no habits yet,
        return 1                                                    # start IDs at 1.
    return max(habit['id'] for habit in tracked_habits) + 1         # Find the highest existing habit ID and return one higher

def view_habits(tracked_habits):                                    # New habits function
    if not tracked_habits:                                          # If the list is empty,
        print("You are not currently tracking any habits.")         # inform the user,
        return                                                      # then exit the function.

    for habit in tracked_habits:                                    # Loop through each habit dict in the list
        streak = get_streak(habit)                                  # Calls get_streak() math function
        print(f"({habit['id']}) {habit['name']} - Streak: {streak}")    # Display the habit's ID, name, and completion streak

def delete_habit(tracked_habits, habit_id):                         # Delete specific habit function
    for habit in tracked_habits:                                    # Loop through each habit dict in the list
        if habit["id"] == habit_id:                                 # If this habit's stored ID matches the user's ID input
            tracked_habits.remove(habit)                            # Remove the habit from the list
            save_habits(tracked_habits)                             # Persist the updated list to JSON
            return habit                                            # Return the removed habit dict
    return None                                                     # If no matching ID was found, return None

def clear_habits(habits):                                           # Clear entire habits list function
    habits.clear()                                                  # Removes ALL habits dicts from the list
    save_habits(habits)                                             # Persist the now-empty list to JSON
    print("Your current habits have been cleared.")                 # Inform the users that ALL habits have been cleared.

def save_habits(tracked_habits):                                    # Save habits to JSON function
    with HABITS_FILE.open("w", encoding="utf-8") as f:              # Open the JSON file in write mode (this overwrites existing content)
        json.dump(tracked_habits, f, indent=2)                      # Serialize the list of habit dicts to JSON with readable formatting

def mark_complete(tracked_habits, habit_id):                       # Mark daily completion function
    for habit in tracked_habits:                                    # Loops through each habit dict in the list
        if habit['id'] == habit_id:                                # Check if THIS habit's stored id matches the id the User asked for
            today_str = date.today().isoformat()                    # Get today's date as a JSON-safe string like "2026-02-25"

            if today_str not in habit['completed_dates']:           # If today is NOT already recorded, add it
                habit['completed_dates'].append(today_str)          # Store the date string
                save_habits(tracked_habits)                         # persist the updated list to JSON
                return True                                         # Signal success
            
            return False                                            # If today is already recorded, don't add a duplicate
        
    return None                                                     # If we finish the loop without finding the id, the habit doesn't exist

def get_streak(habit):                                              # Streak math function
    completed_set = {date.fromisoformat(d) for d in habit["completed_dates"]}   # Convert stored date strings to date objects for comparison

    streak = 0                                                      # Initialize streak counter at 0
    current_day = date.today()                                      # Start counting from today

    while current_day in completed_set:                             # While today's date (or pervious days) exist in the completion history, continue counting backward
        streak += 1                                                 # Increase streak count by 1 for each consecutive day found
        current_day -= timedelta(days=1)                            # Move one day backward

    return streak                                                   # Return total number of consecutive days completed up to today
# ===================
# 5) UI / INPUT-OUTPUT LAYER
# ===================

def show_menu() -> None:                                            # Show main menu function, does not return any value
    print(f"\n{APP_NAME} v{APP_VERSION}")                           # Display the application name and version at the top of the menu

    print("Please make a choice from the menu: ")                   # Prompt the user to choose an option

    print("1) Add.")                                                # Menu Options ↓↓↓↓↓↓
    print("2) Delete.")
    print("3) View.")
    print("4) Clear.")
    print("5) Mark Complete")
    print("6) Exit.")                                               # Menu Options ↑↑↑↑↑↑


def get_menu_choice() -> str:                                       # Prompts the user for input, returns a string
    return input("Choice: ").strip().lower()                        # Removes extra space, and ensure consistent comparison (e.g., "Add" and "add" match)


def get_action() -> str:                                            # Gets cleared action and matches to command, returns a string
    choice = get_menu_choice()                                      # Gets cleaned input from get_menu_choice()
    if choice in COMMANDS:                                          # If the input exists in the COMMANDS dict,
        return COMMANDS[choice]                                     # returns the standardized action string.
    print("Invalid option, please try again.")                      # If input is not recognized, informs the users
    return ""                                                       # Return empty string to signal invalid action to main loop


# ===================
# 6) MAIN PROGRAM LOOP
# ===================

def main():

    if not HABITS_FILE.exists():                                    # If the habits.json file does not exist yet,
        with HABITS_FILE.open("w", encoding="utf-8") as f:          # create it,
            json.dump([], f)                                        # and initialize it with an empty list

    with HABITS_FILE.open("r", encoding="utf-8") as f:              # Open the habits.json file in read mode
        habits = json.load(f)                                       # Load the JSON data into the 'habits' list

    while True:                                                     # Main Application Loop (runs until users choses Exit)
        show_menu()                                                 # Display the main menu options
        action = get_action()                                       # Converts user input into a standardized action string

        if not action:                                              # If the input was invalid (empty string returned)
            continue                                                # restart loop and show main menu again

        elif action == "add":                                       # Add Habit Action
            add_habit(habits)                                       # Call add_habit and pass in the habits list

        elif action == "delete":                                    # Delete Specific Habit Action 
            if not habits:                                          # If there are no habits,
                print("You have no added habits.")                  # inform user, 
                continue                                            # and restart loop

            view_habits(habits)                                     # Display all current habits (with IDs)

            remove_choice = input("Enter the habit ID to remove: ").strip()     # Ask the user which habit ID to remove

            try:                                                    # Try line
                habit_id = int(remove_choice)                       # attempt to convert the int to an integer

            except ValueError:                                      # Except Line
                print("Please enter a valid ID.")                   # if conversion fails (not a number), show error, 
                continue                                            # and restart loop

            removed = delete_habit(habits, habit_id)                # Attempt to delete the habit using the ID

            if removed is None:                                     # if delete_habit returned None,
                print("No habit found with that ID.")               # inform user that no matching ID was found

            else:                                                   # Otherwise,
                print(f"Removed: {removed['name']}")                # confirm which habit was removed

        elif action == "view":                                      # View All Habits Action
            view_habits(habits)                                     # Display all currently tracked habits

        elif action == "clear":                                     # Clear All Habits Action
            clear_confirm = input(                                  
                "Are you sure you want to clear ALL current habits? You can't undo this action! Y/N: "
            ).strip().lower()                                       # Asks for confirmation before clearing all habits

            if clear_confirm == "y":                                # Only clear if user confirms with 'y'
                clear_habits(habits)                                # Calls clear_habits function

        elif action == "mark":                                      # Daily Mark Complete Action
            if not habits:                                          # If there are no habits in the list,
                print("You have no habits to mark")                 # inform the user,
                continue                                            # and restart the loop
            
            view_habits(habits)                                     # Calls the view_habits function

            mark_choice = input("Please enter the habit's ID: ").strip()    # Asks the user which habit ID they want to mark as complete, stripping whitespace
            try:                                                    # Try line
                habit_id = int(mark_choice)                         # Attempts to conver input string to integer
            except ValueError:                                      # Except line
                print("Please enter a valid ID.")                   # if conversion fails (user entered text instead of a number), inform user,
                continue                                            # and restart the loop

            result = mark_complete(habits, habit_id)                # Calls mark_complete() and pass in full habits list and specific habit ID to mark
            if result is True:                                      # if returned True,
                print("Marked completed for today.")                # print confirmation of marking
            elif result is False:                                   # if returned False,
                print("Already marked completed today.")            # print confirmation of previous marking
            else:                                                   # if returned None,
                print("No habit found with that ID.")               # print confirmation that no habit was found under ID the user input


        elif action == "exit":                                      # Exit Application Action
            print(f"Thank you for using {APP_NAME} v{APP_VERSION}") # Prints exit message including app name and version
            break                                                   # Breaks out of the infinite loop to end the program


# ===================
# 7) Run Guard
# ===================

if __name__ == "__main__":
    # __name__ is a special built-in Python variable
    # When the file is run directly, __name__ is set to "__main__"
    # When a file is imported into another file, __main__ becomes the module name

    # This condition ensures that main() only runs
    # when this file is executed directly,
    # and NOT when it is imported as a module
    main()