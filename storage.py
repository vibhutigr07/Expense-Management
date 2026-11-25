# storage.py
# Handles everything related to saving and loading data (CSV / TXT files).

import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPENSE_FILE = os.path.join(BASE_DIR, "expenses.csv")
BUDGET_FILE = os.path.join(BASE_DIR, "budget.txt")

CATEGORIES = ["Food", "Transport", "Stationery", "Entertainment", "Academic", "Other"]
HEADER = ["date", "category", "description", "amount"]
DATE_FORMAT = "%Y-%m-%d"


def is_valid_date(text):
    """Return True if text is a real date in YYYY-MM-DD format."""
    # check the shape of the text first: slicing, count() and isdigit()
    if len(text) != 10 or text.count("-") != 2:
        return False
    if not (text[:4].isdigit() and text[5:7].isdigit() and text[8:].isdigit()):
        return False
    try:
        datetime.strptime(text, DATE_FORMAT)
        return True
    except ValueError:
        return False


def clean_row(row):
    """Clean one CSV row: strip the spaces, Title Case the category, make the amount a float."""
    return {
        "date": row["date"].strip(),
        "category": row["category"].strip().title(),
        "description": row["description"].strip(),
        "amount": float(row["amount"]),
    }


def load_expenses():
    """Read all expenses from the CSV file and return them as a list of dictionaries."""
    expenses = []
    seen_categories = set()
    if not os.path.exists(EXPENSE_FILE):
        return expenses
    try:
        with open(EXPENSE_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    expense = clean_row(row)
                except (ValueError, KeyError, TypeError, AttributeError):
                    # skip a damaged row instead of crashing the whole program
                    print("Warning: skipped a damaged row in expenses.csv")
                    continue
                if not is_valid_date(expense["date"]):
                    print("Warning: skipped a row with a wrong date in expenses.csv")
                    continue
                seen_categories.add(expense["category"])
                expenses.append(expense)
    except OSError:
        print("Error: could not read expenses.csv")

    # set difference: categories found in the file that the program does not know
    unknown = seen_categories - set(CATEGORIES)
    if len(unknown) > 0:
        print("Note: unknown categories in expenses.csv:", ", ".join(sorted(unknown)))
    return expenses


def save_all_expenses(expenses):
    """Write the full list of expenses back to the CSV file."""
    try:
        with open(EXPENSE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
            for e in expenses:
                writer.writerow([e["date"], e["category"], e["description"], e["amount"]])
        return True
    except OSError:
        print("Error: could not save expenses.csv")
        return False


def add_expense(expenses, date, category, description, amount):
    """Add one expense to the list and save the file."""
    expenses.append({
        "date": date,
        "category": category,
        "description": description,
        "amount": amount,
    })
    return save_all_expenses(expenses)


def delete_expense(expenses, index):
    """Remove the expense at the given position (0-based) and save the file."""
    if not 0 <= index < len(expenses):
        return False
    expenses.pop(index)
    return save_all_expenses(expenses)


def load_budget():
    """Read the monthly budget from budget.txt. Returns 0 if not set yet."""
    if not os.path.exists(BUDGET_FILE):
        return 0.0
    try:
        with open(BUDGET_FILE) as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return 0.0


def save_budget(amount):
    """Save the monthly budget in budget.txt."""
    try:
        with open(BUDGET_FILE, "w") as f:
            f.write(str(amount))
        return True
    except OSError:
        print("Error: could not save the budget")
        return False
