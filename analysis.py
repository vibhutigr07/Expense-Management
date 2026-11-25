# analysis.py
# All the calculations and rules of the project live here.

import calendar
from datetime import date

# limits used by the budget status (percent of the budget used)
SAFE_LIMIT = 50
WARNING_LIMIT = 80
FULL_BUDGET = 100
# a day is "unusual" if it is more than this many times the usual day
UNUSUAL_FACTOR = 2


def total_spending(expenses):
    """Sum of all amounts in the given list."""
    total = 0
    for e in expenses:
        total += e["amount"]
    return total


def filter_by_month(expenses, month):
    """Return only the expenses of one month. month looks like '2026-11'."""
    result = []
    for e in expenses:
        if not e["date"].startswith(month):
            continue                      # not this month, go to the next expense
        result.append(e)
    return result


def category_totals(expenses):
    """Return a dictionary like {'Food': 1200.0, 'Transport': 300.0}."""
    totals = {}
    for e in expenses:
        cat = e["category"]
        totals[cat] = totals.get(cat, 0) + e["amount"]       # the counting pattern
    return totals


def ranked_categories(expenses):
    """Categories sorted from highest spending to lowest.
    Each item is (category, amount, percentage of total)."""
    totals = category_totals(expenses)
    grand_total = total_spending(expenses)

    ranking = []
    for cat, amt in totals.items():
        percent = (amt / grand_total * 100) if grand_total > 0 else 0
        ranking.append((cat, amt, percent))

    # sort from highest amount to lowest (simple selection sort)
    for i in range(len(ranking)):
        biggest = i
        for j in range(i + 1, len(ranking)):
            if ranking[j][1] > ranking[biggest][1]:
                biggest = j
        temp = ranking[i]
        ranking[i] = ranking[biggest]
        ranking[biggest] = temp
    return ranking


def months_available(expenses):
    """List of months (YYYY-MM) that have at least one expense, oldest first."""
    months = set()
    for e in expenses:
        months.add(e["date"][:7])          # slice the first 7 characters: 2026-11
    return sorted(months)


def days_in_month(month):
    year = int(month[:4])
    mon = int(month[5:7])
    return calendar.monthrange(year, mon)[1]


def days_passed(month, today=None):
    """How many days of that month are over (used for the daily average)."""
    if today is None:
        today = date.today()
    this_month = today.strftime("%Y-%m")
    if month == this_month:
        return today.day
    return days_in_month(month)


def budget_status(spent, budget):
    """Rule based check of the budget. Returns (percent used, level, message)."""
    if budget <= 0:
        return 0, "NOT SET", "No budget has been set yet."

    percent = spent / budget * 100
    # ladder: highest limit first, so the first true condition wins
    if percent > FULL_BUDGET:
        level = "OVER BUDGET"
        message = "You have crossed your budget. Stop non-essential spending."
    elif percent >= WARNING_LIMIT:
        level = "WARNING"
        message = f"You have used {WARNING_LIMIT}% or more of your budget. Spend carefully."
    elif percent >= SAFE_LIMIT:
        level = "MODERATE"
        message = "More than half of the budget is used. Keep an eye on it."
    else:
        level = "SAFE"
        message = "Spending is under control."
    return percent, level, message


def month_report(expenses, month, budget, today=None):
    """Build a summary of one month. Returns a dictionary with all the numbers."""
    month_expenses = filter_by_month(expenses, month)
    spent = total_spending(month_expenses)
    passed = days_passed(month, today)
    total_days = days_in_month(month)

    daily_avg = spent / passed if passed > 0 else 0
    projected = daily_avg * total_days          # expected spending by the month end
    percent, level, message = budget_status(spent, budget)

    ranking = ranked_categories(month_expenses)
    top = ranking[0] if ranking else None

    # biggest single expense of the month
    biggest = None
    for e in month_expenses:
        if biggest is None or e["amount"] > biggest["amount"]:
            biggest = e

    return {
        "month": month,
        "count": len(month_expenses),
        "spent": spent,
        "budget": budget,
        "remaining": budget - spent,
        "percent": percent,
        "level": level,
        "message": message,
        "daily_avg": daily_avg,
        "projected": projected,
        "will_exceed": budget > 0 and projected > budget,
        "ranking": ranking,
        "top": top,
        "biggest": biggest,
    }


def find_big_spending_days(expenses, month, limit=UNUSUAL_FACTOR):
    """Return the days of a month where spending was more than `limit` times
    the daily average. Useful for spotting unusual spending."""
    month_expenses = filter_by_month(expenses, month)

    per_day = {}
    for e in month_expenses:
        if e["date"] in per_day:
            per_day[e["date"]] += e["amount"]
        else:
            per_day[e["date"]] = e["amount"]

    if not per_day:
        return []

    all_days_total = 0
    for day in per_day:
        all_days_total += per_day[day]
    average = all_days_total / len(per_day)

    unusual = []
    for day, amt in per_day.items():
        if amt > limit * average:
            unusual.append((day, amt))
    unusual.sort()
    return unusual
