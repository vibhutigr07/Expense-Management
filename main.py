# main.py
# College Student Expense Management System
# Course: Computational Thinking and Programming (2026CSAE100)
#
# Run this file to start the program:  python main.py

import math
from datetime import date

import storage
import analysis

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt 
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

LINE_WIDTH = 66
BAR_WIDTH = 30
DESCRIPTION_WIDTH = 22
MENU_ITEMS = [
    "Add an expense",
    "View all expenses",
    "Delete an expense",
    "Total and category-wise spending",
    "Set monthly budget",
    "Monthly report (budget status and alerts)",
    "Find unusual spending days",
    "Save category chart as picture",
    "Exit",
]
EXIT_CHOICE = str(len(MENU_ITEMS))
MENU_CHOICES = []
for number in range(1, len(MENU_ITEMS) + 1):
    MENU_CHOICES.append(str(number))


# ---------------------------------------------------------------- input helpers

def ask_amount(prompt):
    """Keep asking until the user types a positive number."""
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print("  Invalid input. Please enter a number, for example 150 or 99.5")
            continue
        if not math.isfinite(value):
            print("  Invalid input. Please enter a normal number.")
            continue
        if value <= 0:
            print("  Amount must be greater than zero.")
            continue
        break                          # a good amount: leave the loop
    return round(value, 2)


def ask_date():
    """Ask for a date. Pressing Enter uses today's date."""
    today = date.today().strftime(storage.DATE_FORMAT)
    while True:
        text = input("Date (YYYY-MM-DD, press Enter for today): ").strip()
        if text == "":
            text = today
            break
        if not storage.is_valid_date(text):
            print("  Invalid date. Use the format YYYY-MM-DD, for example 2026-11-14")
            continue
        if text > today:
            print("  Date cannot be in the future.")
            continue
        break
    return text


def ask_category():
    """Show the category list and return the chosen category name."""
    print("Categories:")
    for number, name in enumerate(storage.CATEGORIES, start=1):
        print("  " + str(number) + ". " + name)
    while True:
        text = input("Choose category number: ").strip()
        if text.isdigit() and 1 <= int(text) <= len(storage.CATEGORIES):
            break
        print("  Invalid choice. Enter a number from 1 to", len(storage.CATEGORIES))
    return storage.CATEGORIES[int(text) - 1]


def ask_month(expenses):
    """Ask which month to analyse. Enter = current month."""
    current = date.today().strftime("%Y-%m")
    available = analysis.months_available(expenses)
    if available:
        print("Months with data:", ", ".join(available))
    while True:
        text = input(f"Month (YYYY-MM, press Enter for {current}): ").strip()
        if text == "":
            text = current
            break
        if len(text) == 7 and text.find("-") == 4 and storage.is_valid_date(text + "-01"):
            break
        print("  Invalid month. Use the format YYYY-MM, for example 2026-11")
    return text


def line(char="-", width=LINE_WIDTH):
    print(char * width)


# ---------------------------------------------------------------- menu actions

def add_expense_option(expenses):
    print("\n--- Add a new expense ---")
    when = ask_date()
    category = ask_category()
    description = input("Description (what was it for?): ").strip()
    description = description.replace(",", " ")      # a comma would break the CSV
    description = " ".join(description.split())      # remove the extra spaces
    if description == "":
        description = "-"
    amount = ask_amount("Amount in Rs: ")

    if storage.add_expense(expenses, when, category, description, amount):
        print(f"\nSaved: Rs {amount:.2f} on {category} ({when})")


def view_expenses_option(expenses):
    print("\n--- All expenses ---")
    if len(expenses) == 0:
        print("No expenses recorded yet.")
        return
    line()
    print(f"{'No':<4}{'Date':<12}{'Category':<15}{'Description':<24}{'Amount':>11}")
    line()
    for serial, e in enumerate(expenses, start=1):
        desc = e["description"][:DESCRIPTION_WIDTH]
        print(f"{serial:<4}{e['date']:<12}{e['category']:<15}{desc:<24}{e['amount']:>11.2f}")
    line()
    print(f"{'Total':<55}{analysis.total_spending(expenses):>11.2f}")


def delete_expense_option(expenses):
    print("\n--- Delete an expense ---")
    if len(expenses) == 0:
        print("Nothing to delete.")
        return
    view_expenses_option(expenses)
    text = input("Enter the number of the expense to delete (0 to cancel): ").strip()
    if not text.isdigit():
        print("  Invalid input. Nothing deleted.")
        return
    number = int(text)
    if number == 0:
        print("Cancelled.")
        return
    if not 1 <= number <= len(expenses):
        print("  No expense with that number.")
        return
    if storage.delete_expense(expenses, number - 1):
        print("Expense deleted.")


def text_bar(percent, width=BAR_WIDTH):
    filled = int(round(percent / 100 * width))
    return "#" * filled


def category_summary_option(expenses):
    print("\n--- Total and category-wise spending ---")
    if len(expenses) == 0:
        print("No expenses recorded yet.")
        return
    ranking = analysis.ranked_categories(expenses)
    line()
    print(f"{'Category':<15}{'Amount':>10}{'Share':>9}   Graph")
    line()
    for cat, amt, percent in ranking:
        print(f"{cat:<15}{amt:>10.2f}{percent:>8.1f}%   {text_bar(percent)}")
    line()
    print(f"{'Total':<15}{analysis.total_spending(expenses):>10.2f}")
    print(f"\nHighest spending category: {ranking[0][0]} (Rs {ranking[0][1]:.2f})")


def set_budget_option():
    print("\n--- Set monthly budget ---")
    old = storage.load_budget()
    if old > 0:
        print(f"Current monthly budget: Rs {old:.2f}")
    amount = ask_amount("Enter the new monthly budget in Rs: ")
    if storage.save_budget(amount):
        print(f"Monthly budget set to Rs {amount:.2f}")


def monthly_report_option(expenses):
    print("\n--- Monthly report ---")
    month = ask_month(expenses)
    budget = storage.load_budget()
    r = analysis.month_report(expenses, month, budget)

    if r["count"] == 0:
        print(f"No expenses found for {month}.")
        return

    print()
    line("=")
    print(f"  MONTHLY REPORT : {month}")
    line("=")
    print(f"  Number of expenses : {r['count']}")
    print(f"  Total spent        : Rs {r['spent']:.2f}")

    if budget > 0:
        print(f"  Monthly budget     : Rs {budget:.2f}")
        if r["remaining"] >= 0:
            print(f"  Remaining budget   : Rs {r['remaining']:.2f}")
        else:
            print(f"  Over budget by     : Rs {-r['remaining']:.2f}")
        print(f"  Budget used        : {r['percent']:.1f}%")
    else:
        print("  Monthly budget     : not set (use option 5)")

    print(f"  Average per day    : Rs {r['daily_avg']:.2f}")
    print(f"  Expected by month end at this rate: Rs {r['projected']:.2f}")
    line()
    print(f"  Status : {r['level']}")
    print(f"  {r['message']}")
    if r["level"] == "OVER BUDGET" or not r["will_exceed"]:
        pass       # on purpose: no extra alert (the status line already says it)
    else:
        print("  Alert: at the current daily average you will cross the budget")
        print("         before the month ends.")
    line()
    top_cat, top_amt, top_pct = r["top"]
    print(f"  Highest category : {top_cat} - Rs {top_amt:.2f} ({top_pct:.1f}%)")
    big = r["biggest"]
    print(f"  Biggest expense  : Rs {big['amount']:.2f} on {big['description']} ({big['date']})")
    line("=")


def unusual_days_option(expenses):
    print("\n--- Unusual spending days ---")
    month = ask_month(expenses)
    days = analysis.find_big_spending_days(expenses, month)
    if len(days) == 0:
        print(f"No unusual spending days found in {month}.")
        return
    print(f"Days in {month} where spending was more than {analysis.UNUSUAL_FACTOR} times the usual day:")
    for day, amt in days:
        print(f"  {day}  ->  Rs {amt:.2f}")


def chart_option(expenses):
    print("\n--- Category chart ---")
    if len(expenses) == 0:
        print("No expenses recorded yet.")
        return
    ranking = analysis.ranked_categories(expenses)
    if not HAS_MATPLOTLIB:
        print("Matplotlib is not installed, so the picture cannot be made.")
        print("The text graph in option 4 shows the same information.")
        return

    names = [item[0] for item in ranking]
    amounts = [item[1] for item in ranking]
    plt.figure(figsize=(7, 4))
    plt.bar(names, amounts, color="#3b6ea5")
    plt.ylim(0, max(amounts) * 1.1)                  # leave room for the labels
    for name, amount in zip(names, amounts):         # write the amount on each bar
        plt.text(name, amount, f"{amount:.0f}", ha="center", va="bottom")
    plt.title("Category-wise spending")
    plt.xlabel("Category")
    plt.ylabel("Amount (Rs)")
    plt.tight_layout()
    plt.savefig("category_chart.png", dpi=120)
    plt.close()
    print("Chart saved as category_chart.png")


# ---------------------------------------------------------------- main program

def show_menu():
    print()
    line("=")
    print("   COLLEGE STUDENT EXPENSE MANAGEMENT SYSTEM")
    line("=")
    for number, text in enumerate(MENU_ITEMS, start=1):
        print(f"  {number}. {text}")
    line("=")


def main():
    expenses = storage.load_expenses()
    print(f"Loaded {len(expenses)} saved expense(s).")

    while True:
        show_menu()
        choice = input(f"Enter your choice (1-{EXIT_CHOICE}): ").strip()

        if choice not in MENU_CHOICES:
            print(f"  Invalid choice. Please enter a number from 1 to {EXIT_CHOICE}.")
            continue

        if choice == "1":
            add_expense_option(expenses)
        elif choice == "2":
            view_expenses_option(expenses)
        elif choice == "3":
            delete_expense_option(expenses)
        elif choice == "4":
            category_summary_option(expenses)
        elif choice == "5":
            set_budget_option()
        elif choice == "6":
            monthly_report_option(expenses)
        elif choice == "7":
            unusual_days_option(expenses)
        elif choice == "8":
            chart_option(expenses)
        elif choice == EXIT_CHOICE:
            print("\nThank you for using the system. Your data is saved.")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram closed. Your saved data is safe.")
