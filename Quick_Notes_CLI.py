# ===================
# 1) Imports
# ===================

import json
from pathlib import Path
from datetime import date

# ===================
# 2) CONFIG / CONSTANTS
# ===================

APP_NAME = "Quick Notes CLI"
APP_VERSION = "0.1.0"

NOTES_FILE = Path("notes.json")

COMMANDS = {
    "1": "add",
    "add":"add",
    "add notes": "add",

    "2": "view",
    "view": "view",
    "view notes": "view",

    "3": "edit",
    "edit": "edit",
    "edit notes": "edit",

    "4": "delete",
    "delete": "delete",
    "delete notes": "delete",

    "5": "clear",
    "clear": "clear",
    "clear all": "clear",
    "clear all notes": "clear",

    "6": "exit",
    "exit": "exit",
    "exit app": "exit",
}

# ===================
# 3) DATA MODELS
# ===================

NOTES_MODEL = {
    "id": int,
    "name": str,
    "notes": str,
    "created on": "YYYY-MM-DD",
}

# ===================
# 4) CORE FUNCTION
# ===================

def add_notes(tracked_notes):
    note_name = input("Please enter the note's name: ").strip()
    notes = input("Please enter the note: ").strip()

    if not note_name:
        print("Invalid input, please try again.")
        return

    if not notes:
        print("Invalid input, please try again.")
        return

    new_note = {
        "id": get_next_id(tracked_notes),
        "name": note_name,
        "notes": notes,
        "created on": date.today().isoformat()
    }

    tracked_notes.append(new_note)
    save_notes(tracked_notes)

def get_next_id(tracked_notes) -> int:
    if not tracked_notes:
        return 1
    return max(note['id'] for note in tracked_notes) + 1

def save_notes(tracked_notes):
    with NOTES_FILE.open("w", encoding="utf-8") as f:
        json.dump(tracked_notes, f, indent=2)

def view_notes(tracked_notes):
    if not tracked_notes:
        print("You currently have zero notes saved.")
        return
    
    for note in tracked_notes:
        print(f"({note['id']}) {note['name']} | Notes: {note['notes']} | Created on: {note['created on']}")

def edit_notes(tracked_notes, note_id):
    for note in tracked_notes:
        if note['id'] == note_id:
            new_notes = input("Please enter new notes: ").strip()
            if not new_notes:
                return False
            
            note['notes'] = new_notes
            save_notes(tracked_notes)
            return note
    return None

def delete_notes(tracked_notes, note_id):
    for note in tracked_notes:
        if note['id'] == note_id:
            tracked_notes.remove(note)
            save_notes(tracked_notes)
            return note
    return None

def clear_notes(notes):
    notes.clear()
    save_notes(notes)

# ===================
# 5) UI \ INPUT-OUTPUT LAYER
# ===================

def show_menu() -> None:
    print(f"\n{APP_NAME} v{APP_VERSION}")

    print("Please make a choice from the menu: ")

    print("1) Add Notes.")
    print("2) View Notes.")
    print("3) Edit Notes.")
    print("4) Delete Notes.")
    print("5) Clear All Notes.")
    print("6) Exit App.")

def get_menu_choice() -> str:
    return input("Choice: ").strip().lower()

def get_action() -> str:
    choice = get_menu_choice()
    if choice in COMMANDS:
        return COMMANDS[choice]
    print("Invalid option, please try again.")
    return ""

# ===================
# 6) MAIN PROGRAM LOOP
# ===================
def main():

    if not NOTES_FILE.exists():
        with NOTES_FILE.open("w", encoding="utf-8") as f:
            json.dump([], f)

    with NOTES_FILE.open("r", encoding="utf-8") as f:
        notes = json.load(f)

    while True:
        show_menu()
        action = get_action()

        if not action:
            continue

        elif action == "add":
            add_notes(notes)

        elif action == "view":
            view_notes(notes)

        elif action == "edit":
            if not notes:
                print("You currently have zero notes saved.")
                continue

            view_notes(notes)
            edit_choice = input("Enter the note ID to edit: ").strip()

            try:
                note_id = int(edit_choice)
            except ValueError:
                print("Please enter a valid ID")
                continue

            edited = edit_notes(notes, note_id)
            if edited is None:
                print("No note found with that ID")
            elif edited is False:
                print("Edit cancelled")
            else:
                print(f"Edited: {edited['name']} | Notes: {edited['notes']}")

        elif action == "delete":
            if not notes:
                print("You currently have zero notes saved.")
                continue

            view_notes(notes)
            remove_choice = input("Enter the note ID to remove: ").strip()

            try:
                note_id = int(remove_choice)
            except ValueError:
                print("Please enter a valid ID")
                continue

            removed = delete_notes(notes, note_id)
            if removed is None:
                print("No note found with that ID")
            else:
                print(f"Removed: {removed['name']}")

        elif action == "clear":
            if not notes:
                print("You currently have zero notes saved")
                continue

            clear_confirm = input(
                "Are you sure that you wwant to clear ALL notes? This action cannot be undone! Y/N: " \
                "").strip().lower()
            if clear_confirm == "y":
                print("All saved notes have been cleared")
                clear_notes(notes)

        elif action == "exit":
            print(f"Thanks for using {APP_NAME} v{APP_VERSION}")
            break
    

# ===================
# 7) Run Guard
# ===================
if __name__ == "__main__":
    main()