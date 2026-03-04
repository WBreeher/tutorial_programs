# ===================
# 1) Imports
# ===================

import json
from pathlib import Path
from datetime import date, timedelta
import hashlib
from getpass import getpass

# ===================
# 2) CONFIG / CONSTANTS
# ===================

APP_NAME = "Password Saver"
APP_VERSION = "0.1.0"

MASTER_FILE = Path("master.txt")
PASSWORD_FILE = Path("password.json")

COMMANDS = {
    "1": "add",
    "add": "add",
    "add password": "add",

    "2": "view",
    "view": "view",
    "view passwords": "view",

    "3": "delete",
    "delete": "delete",
    "delete password": "delete",

    "4": "edit",
    "edit": "edit",
    "edit password": "edit",

    "5": "exit",
    "exit": "exit",
    "exit app": "exit",
}

# ===================
# 3) DATA MODELS (Conceptual)
# ===================

PASSWORD_MODEL = {
    "id": int,
    "site": str,
    "username": str,
    "password": str,
    "created on": "YYYY-MM-DD",
}

# ===================
# 4) CORE FUNCTIONS
# ===================

def check_master_password() -> bool:
    """Creates a master password on first run; otherwise prompts for it."""
    if not MASTER_FILE.exists():
        print("No master password found. Creating one.")
        while True:
            pw = getpass("Set master password: ")
            confirm = getpass("Confirm master password: ")

            if not pw:
                print("Master password cannot be blank.")
                continue
            if pw != confirm:
                print("Passwords do not match. Try again.\n")
                continue
            break

        hashed = hashlib.sha256(pw.encode()).hexdigest()
        with MASTER_FILE.open("w", encoding="utf-8") as f:
            f.write(hashed)

        print("Master password saved.")
        return True

    # Existing master password: verify
    with MASTER_FILE.open("r", encoding="utf-8") as f:
        saved_hash = f.read().strip()

    pw = getpass("Enter master password: ")
    user_hash = hashlib.sha256(pw.encode()).hexdigest()

    if user_hash == saved_hash:
        print("Access granted.")
        return True

    print("Invalid master password.")
    return False


def save_passwords(tracked_password) -> None:
    with PASSWORD_FILE.open("w", encoding="utf-8") as f:
        json.dump(tracked_password, f, indent=2)


def get_next_id(tracked_password) -> int:
    if not tracked_password:
        return 1
    return max(password["id"] for password in tracked_password) + 1


def get_next_change(password) -> str:
    created_date = date.fromisoformat(password["created on"])
    next_change = created_date + timedelta(days=180)
    return next_change.isoformat()


def mask_password(pw: str) -> str:
    if not pw:
        return ""
    if len(pw) <= 2:
        return "*" * len(pw)
    return pw[0] + ("*" * (len(pw) - 2)) + pw[-1]


def add_password(tracked_password) -> None:
    pass_site = input("Please enter the site you'd like the password to be saved for: ").strip()
    if not pass_site:
        print("Invalid input, please try again.")
        return

    pass_username = input("Please enter the username for the password: ").strip()
    if not pass_username:
        print("Invalid input, please try again.")
        return

    pass_password = input("Please enter the password: ").strip()
    if not pass_password:
        print("Invalid input, please try again.")
        return

    saved_password = {
        "id": get_next_id(tracked_password),
        "site": pass_site,
        "username": pass_username,
        "password": pass_password,
        "created on": date.today().isoformat(),
    }

    tracked_password.append(saved_password)
    save_passwords(tracked_password)
    print(f"Saved password for {pass_site} (ID: {saved_password['id']}).")


def view_passwords(tracked_password) -> None:
    """Lists all passwords with masking + 'soon' / 'overdue' warnings."""
    if not tracked_password:
        print("You have zero passwords saved.")
        return

    today = date.today()

    for password in tracked_password:
        next_change = get_next_change(password)              # ISO string
        next_change_date = date.fromisoformat(next_change)   # date object
        masked = mask_password(password["password"])

        print(f"\n({password['id']}) | Site: {password['site']} | Username: {password['username']} | Password: {masked}")
        print(f"Created on: {password['created on']} | Change password on: {next_change}")

        soon_start = next_change_date - timedelta(days=7)
        if soon_start <= today < next_change_date:
            print("⚠ A password should be changed soon.")
        elif today >= next_change_date:
            print("⛔ Password change overdue.")


def reveal_password(tracked_password, password_id):
    for password in tracked_password:
        if password["id"] == password_id:
            return password
    return None


def delete_passwords(tracked_password, password_id):
    for password in tracked_password:
        if password["id"] == password_id:
            tracked_password.remove(password)
            save_passwords(tracked_password)
            return password
    return None


def edit_password(tracked_password, password_id):
    for password in tracked_password:
        if password["id"] == password_id:
            new_password = input("Please enter new password (blank = cancel): ").strip()
            if not new_password:
                return False

            password["password"] = new_password
            password["created on"] = date.today().isoformat()
            save_passwords(tracked_password)
            return password
    return None

# ===================
# 5) UI / INPUT-OUTPUT LAYER
# ===================

def show_menu() -> None:
    print(f"\nYou are using {APP_NAME} v{APP_VERSION}")
    print("Please make a choice from the menu:")
    print("1) Add Password")
    print("2) View Passwords")
    print("3) Delete Password")
    print("4) Edit Password")
    print("5) Exit App")


def get_menu_choice() -> str:
    return input("Choice: ").strip().lower()


def get_action() -> str:
    choice = get_menu_choice()
    if choice in COMMANDS:
        return COMMANDS[choice]
    print("Invalid selection, please try again.")
    return ""


def view_passwords_menu(tracked_password) -> None:
    """View submenu: masked list + reveal-by-id option + back."""
    if not tracked_password:
        print("You have zero passwords saved.")
        return

    while True:
        view_passwords(tracked_password)

        print("\nView Menu:")
        print("1) Reveal a password by ID")
        print("2) Back")

        choice = input("Choice: ").strip().lower()

        if choice in ("2", "back", "b"):
            return

        if choice in ("1", "reveal", "r"):
            raw = input("Enter the password ID to reveal: ").strip()
            try:
                password_id = int(raw)
            except ValueError:
                print("Please enter a valid numeric ID.")
                continue

            found = reveal_password(tracked_password, password_id)
            if found is None:
                print("No password found with that ID.")
                continue

            print("\n=== REVEALED ===")
            print(f"Site: {found['site']}")
            print(f"Username: {found['username']}")
            print(f"Password: {found['password']}\n")
            input("Press Enter to continue...")
            continue

        print("Invalid option. Please try again.")

# ===================
# 6) MAIN PROGRAM LOOP
# ===================

def main():
    if not check_master_password():
        return

    if not PASSWORD_FILE.exists():
        with PASSWORD_FILE.open("w", encoding="utf-8") as f:
            json.dump([], f)

    with PASSWORD_FILE.open("r", encoding="utf-8") as f:
        passwords = json.load(f)

    while True:
        show_menu()
        action = get_action()

        if not action:
            continue

        if action == "add":
            add_password(passwords)

        elif action == "view":
            view_passwords_menu(passwords)

        elif action == "edit":
            if not passwords:
                print("You have zero passwords saved.")
                continue

            view_passwords(passwords)
            edit_choice = input("Enter the password ID to edit: ").strip()

            try:
                password_id = int(edit_choice)
            except ValueError:
                print("Please enter a valid ID.")
                continue

            edited = edit_password(passwords, password_id)
            if edited is None:
                print("No password found with that ID.")
            elif edited is False:
                print("Edit cancelled.")
            else:
                print("Password updated (created-on date reset).")

        elif action == "delete":
            if not passwords:
                print("You have zero passwords saved.")
                continue

            view_passwords(passwords)
            remove_choice = input("Enter the password ID to delete: ").strip()

            try:
                password_id = int(remove_choice)
            except ValueError:
                print("Please enter a valid ID.")
                continue

            removed = delete_passwords(passwords, password_id)
            if removed is None:
                print("No password found with that ID.")
            else:
                print(f"Removed password for site: {removed['site']}")

        elif action == "exit":
            print(f"Thanks for using {APP_NAME} v{APP_VERSION}.")
            break

# ===================
# 7) Run Guard
# ===================

if __name__ == "__main__":
    main()