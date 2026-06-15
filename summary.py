from __future__ import annotations

import pandas as pd


def calculate_financial_totals(
    transactions: pd.DataFrame,
) -> tuple[float, float, float]:
    totals_by_type = (
        transactions.groupby("Type", observed=True)["Amount"]
        .sum()
        .reindex(["Income", "Expense"], fill_value=0.0)
    )

    total_income = float(totals_by_type["Income"])
    total_expense = float(totals_by_type["Expense"])
    net_balance = total_income - total_expense

    return total_income, total_expense, net_balance


def group_expenses_by_category(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    expenses = transactions.loc[
        transactions["Type"].eq("Expense"),
        ["Category", "Amount"],
    ]

    return (
        expenses.groupby("Category", as_index=False, observed=True)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False, ignore_index=True)
    )


def calculate_top_spending_category(
    transactions: pd.DataFrame,
    spending_by_category: pd.DataFrame | None = None,
) -> tuple[str, float]:
    if spending_by_category is None:
        spending_by_category = group_expenses_by_category(transactions)

    if spending_by_category.empty:
        return "No expenses", 0.0

    top_category = spending_by_category.iloc[0]
    return str(top_category["Category"]), float(top_category["Amount"])
