# ===================
# 1) Imports
# ===================

import json                                  # Provides JSON load/dump so we can save and load expenses from a .json file
from pathlib import Path                     # Provides Path objects for clean, cross-platform file paths
from datetime import date, timedelta         # date gives today's date; timedelta is imported but not used yet (can be removed)

# ===================
# 2) CONFIG / CONSTANTS
# ===================

APP_NAME = "Expense Tracker CLI"            # Name shown in the menu header
APP_VERSION = "0.1.0"                       # Version shown in the menu header

EXPENSE_FILE = Path("expenses.json")        # Path object pointing to the JSON file where expenses are stored

INIT_COMMANDS = {                           # Maps user input strings to standardized "main menu" actions
    "a": "add",                             # Shortcut key for add action
    "add": "add",                           # Text command for add action
    "add expense": "add",                   # Alternate text command for add action
    "b": "delete",                          # Shortcut key for delete action
    "delete": "delete",                     # Text command for delete action
    "delete expense": "delete",             # Alternate text command for delete action
    "c": "report",                          # Shortcut key for report action
    "report": "report",                     # Text command for report action
    "report expenses": "report",            # Alternate text command for report action
    "see expenses": "report",               # Alternate text command for report action
    "view expenses": "report",              # Alternate text command for report action
    "d": "exit",                            # Shortcut key for exit action
    "exit": "exit",                         # Text command for exit action
}

ADD_COMMANDS = {                            # Maps user input strings to standardized actions in the "Add Expense" submenu
    "a": "add",                             # Shortcut key to add an expense
    "add": "add",                           # Text command to add an expense
    "add expense": "add",                   # Alternate text command to add an expense
    "b": "back",                            # Shortcut key to go back to main menu
    "back": "back",                         # Text command to go back
    "go back": "back",                      # Alternate text command to go back
}

DEL_COMMANDS = {                            # Maps user input strings to standardized actions in the "Delete Expense" submenu
    "a": "delete",                          # Shortcut key to delete a specific expense by ID
    "delete": "delete",                     # Text command to delete a specific expense
    "delete specific": "delete",            # Alternate text command to delete a specific expense
    "delete specific expense": "delete",    # Alternate text command to delete a specific expense
    "b": "clear",                           # Shortcut key to clear ALL expenses
    "clear": "clear",                       # Text command to clear ALL expenses
    "clear all": "clear",                   # Alternate text command to clear ALL expenses
    "clear all expenses": "clear",          # Alternate text command to clear ALL expenses
    "c": "back",                            # Shortcut key to go back to main menu
    "back": "back",                         # Text command to go back
    "go back": "back",                      # Alternate text command to go back
}

CATEGORIES = (                              # Tuple of allowed categories (enforced during add)
    "Housing", "Food",                      # Common categories for budgeting/reporting
    "Transportation", "Utilities",           # Common categories for budgeting/reporting
    "Healthcare", "Savings",                # Common categories for budgeting/reporting
    "Debt", "Shopping",                     # Common categories for budgeting/reporting
    "Entertainment")                        # Common categories for budgeting/reporting

# ===================
# 3) DATA MODELS
# ===================

EXPENSE_MODEL = {                           # Conceptual template of what each expense dictionary should look like
    "id": int,                              # Unique integer ID used for delete-by-id and identification
    "name": str,                            # Name/label of the expense (e.g., "Groceries", "Rent")
    "amount": float,                        # Dollar amount stored as a float (validated in add_expense)
    "category": str,                        # Category name stored as a string (validated against CATEGORIES)
    "created on": "YYYY-MM-DD",             # ISO date string representing when it was added
    "notes": []                             # Placeholder list for future notes feature (currently unused)
}

# ===================
# 4) CORE FUNCTION
# ===================

def add_expense(tracked_expense):                                                   # Adds a new expense entry to the tracked_expense list
    expense_name = input("Please enter the name of the expense: ").strip()          # Prompt user for expense name and strip extra whitespace

    while True:                                                                     # Loop until user provides a valid numeric amount
        raw_amount = input("Please enter the amount: ").strip()                     # Read the amount as a string and strip whitespace
        try:                                                                        # Try to convert the string to a float
            expense_amount = float(raw_amount)                                      # Convert input to float; may raise ValueError if invalid
            if expense_amount < 0:                                                  # Reject negative values
                print("Amounts cannot be negative.")                                # Inform user negative amounts are not allowed
                continue                                                            # Restart amount prompt loop
            break                                                                   # Exit loop after valid, non-negative amount is entered
        except ValueError:                                                          # If float conversion fails (e.g., "abc")
            print("Please enter a valid number (example: 12.50)")                   # Tell user how to input a valid amount

    while True:                                                                     # Loop until user provides a valid category
        expense_category = input(                                                   # Prompt user for category choice
            "Category Types: Housing, Food, Transportation, Utilities, Healthcare, Savings, Debt, Shopping, or Entertainment "
        ).strip().title()                                                           # Normalize input by stripping spaces and Title-Casing for matching

        if expense_category in CATEGORIES:                                          # Check if category is one of the allowed categories
            break                                                                   # Exit loop if category is valid
        else:                                                                       # Otherwise, category is invalid
            print("Invalid category. PLease try again.")                            # Ask user to try again

    new_expense = {                                                                 # Build the expense dictionary that will be saved/printed later
        "id": get_next_id(tracked_expense),                                         # Generate a unique ID based on the current tracked list
        "name": expense_name,                                                       # Store the user-entered name
        "amount": expense_amount,                                                   # Store the validated float amount
        "category": expense_category,                                               # Store the validated category
        "created on": date.today().isoformat(),                                     # Store today's date as ISO string (YYYY-MM-DD)
        "notes": []                                                                 # Initialize notes as empty list for future expansion
    }                                                                               # End of new_expense dict

    tracked_expense.append(new_expense)                                             # Add the new expense to the in-memory list
    save_to_expense(tracked_expense)                                                # Persist the updated list to expenses.json

def get_next_id(tracked_expense):                                                   # Generates the next unique ID for a new expense
    if not tracked_expense:                                                         # If list is empty (no expenses yet)
        return 1                                                                    # Start IDs at 1
    return max(expense['id'] for expense in tracked_expense) + 1                    # Find current max ID in list and return max+1

def delete_expense(tracked_expense, expense_id):                                    # Deletes one expense by its ID and returns the deleted dict
    for expense in tracked_expense:                                                 # Loop through each expense dict in the list
        if expense['id'] == expense_id:                                             # Check if this expense's ID matches the requested ID
            tracked_expense.remove(expense)                                         # Remove the matching expense from the list
            save_to_expense(tracked_expense)                                        # Save updated list to JSON so deletion persists
            return expense                                                          # Return the removed expense dict for confirmation messages
    return None                                                                     # If no ID matched, return None to signal "not found"

def clear_all_expense(expense):                                                     # Clears ALL expenses from the list
    expense.clear()                                                                 # Remove every expense dict from the list in memory
    save_to_expense(expense)                                                        # Save the empty list to JSON to persist the clearing
    print("All expenses have been cleared.")                                        # Inform user that all expenses are removed

def view_expense(tracked_expense):                                                  # Displays all expenses in a simple list format
    if not tracked_expense:                                                         # If list is empty
        print("You have no expenses saved.")                                        # Inform user there is nothing to view
        return                                                                      # Exit function early

    for expense in tracked_expense:                                                 # Loop through each expense dict
        print(f"({expense['id']}) ({expense['name']}) - Amount: ({expense['amount']})")  # Print ID, name, and amount for each expense

def view_monthly_report(tracked_expense):                                           # View Monthly Report function
    if not tracked_expense:                                                         # If there are no expenses saved at all, stop early
        print("No expenses recorded yet.")
        return

    today = date.today()                                                            # Get today's date as a real date object

    current_month = today.month                                                     # Extract the current month and year
    current_year = today.year
    
    category_totals = {category: 0.0 for category in CATEGORIES}                    # Create a dictionary that will hold totals for each category, Every category starts at 0.0

    total_spent = 0.0                                                               # Track total money spent for this month

    for expense in tracked_expense:                                                 # Loop through every saved expense

        expense_date = date.fromisoformat(expense["created on"])                    # Convert the stored ISO string date back into a real date object

        if expense_date.month == current_month and expense_date.year == current_year:   # Only continue if this expense is from the current month AND year

            category = expense["category"]                                          # Grab the category and amount
            amount = expense["amount"]

            category_totals[category] += amount                                     # Add the amount to the correct category total

            total_spent += amount                                                   # Add to overall monthly total

    print(f"\n=== Expense Report for {today.strftime('%B %Y')} ===")                # Print the report header

    print(f"Total spent this month: ${total_spent:.2f}\n")                          # Print the monthly total formatted to 2 decimal places

    for category in CATEGORIES:                                                     # Loop through categories in fixed order and print their totals
        print(f"{category}: ${category_totals[category]:.2f}")

def save_to_expense(tracked_expense):                                               # Saves the current expenses list to the JSON file
    with EXPENSE_FILE.open("w", encoding="utf-8") as f:                             # Open expenses.json in write mode (overwrites existing file)
        json.dump(tracked_expense, f, indent=2)                                     # Dump list of dicts into JSON with indentation for readability

# ===================
# 5) UI \ INPUT-OUTPUT LAYER
# ===================

def main_menu() -> None:                                                            # Displays the main menu options (returns nothing)
    print(f"\n{APP_NAME} v{APP_VERSION}")                                           # Print header with app name and version
    print("Please make a choice from the menu: ")                                   # Prompt user to choose an option
    print("A) Add Expense.")                                                        # Print option A
    print("B) Delete Expense.")                                                     # Print option B
    print("C) View Report.")                                                        # Print option C
    print("D) Exit.")                                                               # Print option D

def get_init_choice() -> str:                                                       # Reads the user's main menu choice (returns a string)
    return input("Choice: ").strip().lower()                                        # Get input, strip whitespace, lowercase for matching dict keys

def get_init_action() -> str:                                                       # Converts raw choice into standardized action string
    choice = get_init_choice()                                                      # Get the cleaned user choice from get_init_choice()
    if choice in INIT_COMMANDS:                                                     # If the choice matches a key in INIT_COMMANDS
        return INIT_COMMANDS[choice]                                                # Return standardized action ("add", "delete", "report", "exit")
    print("Invalid option, please try again.")                                      # Inform user choice was invalid
    return ""                                                                       # Return empty string to signal invalid action to the main loop

def add_menu() -> None:                                                             # Displays the "Add Expense" submenu options
    print("\n You are viewing the 'Add Expense' menu")                              # Print submenu header
    print("Please make a choice from the menu: ")                                   # Prompt user to choose an option
    print("A) Add Expense")                                                         # Print add action option
    print("B) Go Back")                                                             # Print back option

def get_add_choice() -> str:                                                        # Reads the user's add submenu choice (returns a string)
    return input("Choice: ").strip().lower()                                        # Get input, strip whitespace, lowercase for matching dict keys

def get_add_action() -> str:                                                        # Converts raw add submenu choice into standardized action string
    choice = get_add_choice()                                                       # Get the cleaned user choice from get_add_choice()
    if choice in ADD_COMMANDS:                                                      # If choice matches a key in ADD_COMMANDS
        return ADD_COMMANDS[choice]                                                 # Return standardized action ("add" or "back")
    print("Invalid option, please try again.")                                      # Inform user choice was invalid
    return ""                                                                       # Return empty string to signal invalid action to submenu loop

def del_menu() -> None:                                                             # Displays the "Delete Expense" submenu options
    print("\n You are viewing the 'Delete Expense' menu")                           # Print submenu header
    print("Please make a choice from the menu: ")                                   # Prompt user to choose an option
    print("A) Delete Specific Expense")                                             # Print delete-specific option
    print("B) Clear All Expenses")                                                  # Print clear-all option
    print("C) Go back")                                                             # Print go-back option

def get_del_choice() -> str:                                                        # Reads the user's delete submenu choice (returns a string)
    return input("Choice: ").strip().lower()                                        # Get input, strip whitespace, lowercase for matching dict keys

def get_del_action() -> str:                                                        # Converts raw delete submenu choice into standardized action string
    choice = get_del_choice()                                                       # Get the cleaned user choice from get_del_choice()
    if choice in DEL_COMMANDS:                                                      # If choice matches a key in DEL_COMMANDS
        return DEL_COMMANDS[choice]                                                 # Return standardized action ("delete", "clear", or "back")
    print("Invalid option, please try again.")                                      # Inform user choice was invalid
    return ""                                                                       # Return empty string to signal invalid action to submenu loop

# ===================
# 6) MAIN PROGRAM LOOP
# ===================

def main():                                                                         # Main entry point that runs the application loop
    if not EXPENSE_FILE.exists():                                                   # If expenses.json does not exist yet
        with EXPENSE_FILE.open("w", encoding="utf-8") as f:                         # Create/open expenses.json in write mode
            json.dump([], f)                                                        # Initialize file with an empty list so json.load works later

    with EXPENSE_FILE.open("r", encoding="utf-8") as f:                             # Open expenses.json in read mode
        expense = json.load(f)                                                      # Load JSON list into Python list named 'expense'

    while True:                                                                     # Main program loop (runs until user exits)
        main_menu()                                                                 # Display the main menu
        action = get_init_action()                                                  # Convert user input into standardized action

        if not action:                                                              # If action is empty string (invalid input)
            continue                                                                # Restart loop and show the menu again

        elif action == "add":                                                       # If user chose add
            while True:                                                             # Enter the "Add Expense" submenu loop
                add_menu()                                                          # Display add submenu options
                action = get_add_action()                                           # Get standardized add submenu action

                if not action:                                                      # If action is invalid (empty string)
                    continue                                                        # Restart add submenu loop

                if action == "add":                                                 # If user chose to add an expense
                    add_expense(expense)                                            # Call add_expense with the full expense list

                elif action == "back":                                              # If user chose to go back
                    break                                                           # Exit add submenu loop and return to main menu

        elif action == "delete":                                                    # If user chose delete
            while True:                                                             # Enter the "Delete Expense" submenu loop
                del_menu()                                                          # Display delete submenu options
                action = get_del_action()                                           # Get standardized delete submenu action

                if not action:                                                      # If action is invalid (empty string)
                    continue                                                        # Restart delete submenu loop

                if action == "delete":                                              # If user chose delete specific expense
                    if not expense:                                                 # If there are no saved expenses
                        print("You have no expenses saved.")                        # Inform user nothing can be deleted
                        continue                                                    # Restart delete submenu loop

                    view_expense(expense)                                           # Show expenses so user can see IDs

                    remove_choice = input("Please enter the specific ID to remove: ")  # Prompt user for an expense ID to delete

                    try:                                                            # Attempt to convert input to integer
                        expense_id = int(remove_choice)                             # Convert input string into integer ID
                    except ValueError:                                              # If conversion fails (not a number)
                        print("Please enter a valid ID")                            # Inform user input must be numeric
                        continue                                                    # Restart delete submenu loop

                    removed = delete_expense(expense, expense_id)                   # Attempt deletion and store returned dict/None

                    if removed is None:                                             # If delete_expense returned None (not found)
                        print("No expense found with that ID.")                     # Inform user ID did not match any expense
                    else:                                                           # Otherwise, deletion succeeded
                        print(f"Removed: {removed['name']}")                        # Confirm which expense was removed by printing its name

                elif action == "clear":                                             # If user chose clear all expenses
                    clear_all_expense(expense)                                      # Clear all expenses and save empty list

                elif action == "back":                                              # If user chose go back
                    break                                                           # Exit delete submenu loop and return to main menu

        elif action == "report":                                                    # If user chose report
            view_monthly_report(expense)                                                    # Print report totals (total spent + totals by category)

        elif action == "exit":                                                      # If user chose exit
            print(f"Thanks for using {APP_NAME} v{APP_VERSION}")                    # Print a friendly exit message with name/version
            break                                                                   # Break out of main loop to end program

# ===================
# 7) Run Guard
# ===================

if __name__ == "__main__":                                                          # Only run main() when this file is executed directly
    main()                                                                          # Start the program by calling main()