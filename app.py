from __future__ import annotations

import calendar
from datetime import date
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from data_storage import append_transaction, load_transactions
from summary import (
    calculate_financial_totals,
    calculate_top_spending_category,
    group_expenses_by_category,
)


st.set_page_config(
    page_title="FinControl",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #1d4ed8;
        --primary-dark: #1e40af;
        --text: #0f172a;
        --muted: #64748b;
        --border: #e2e8f0;
        --surface: #ffffff;
        --background: #f8fafc;
        --success: #15803d;
        --success-bg: #f0fdf4;
        --danger: #dc2626;
        --danger-bg: #fef2f2;
        --warning: #d97706;
        --warning-bg: #fffbeb;
    }

    html, body, [class*="css"] {
        font-family: "Inter", ui-sans-serif, system-ui, sans-serif;
    }

    .stApp {
        background: var(--background);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stStatusWidget"],
    #MainMenu {
        display: none !important;
    }

    [data-testid="stToolbar"] [data-testid="stBaseButton-header"],
    [data-testid="stMainMenuButton"] {
        display: none !important;
    }

    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] small {
        color: var(--text) !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.75rem;
    }

    .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--text);
        letter-spacing: -0.02em;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.25rem 0 1.25rem;
    }

    .brand-mark {
        display: grid;
        place-items: center;
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: var(--primary);
        color: white;
        font-size: 20px;
        font-weight: 700;
    }

    .brand-title {
        color: var(--text);
        font-size: 17px;
        font-weight: 700;
        line-height: 1.2;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 12px;
        margin-top: 2px;
    }

    .sidebar-guide {
        padding: 1rem;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: #f8fafc;
        margin-bottom: 0.5rem;
    }

    .sidebar-guide-title {
        color: var(--text);
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }

    .sidebar-guide-item {
        color: #475569;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 0.4rem;
    }

    .page-header {
        margin-bottom: 1.25rem;
    }

    .eyebrow {
        color: var(--primary);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .page-title {
        color: var(--text);
        font-size: clamp(28px, 3vw, 36px);
        font-weight: 700;
        line-height: 1.15;
        letter-spacing: -0.035em;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 15px;
        margin-top: 0.45rem;
    }

    .metric-card {
        position: relative;
        min-height: 142px;
        padding: 1.25rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        overflow: hidden;
    }

    .metric-label {
        color: var(--muted);
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: var(--text);
        font-size: clamp(24px, 2.2vw, 31px);
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        letter-spacing: -0.035em;
        margin-top: 0.9rem;
        white-space: nowrap;
    }

    .metric-note {
        color: var(--muted);
        font-size: 12px;
        margin-top: 0.35rem;
    }

    .metric-accent {
        position: absolute;
        inset: auto 0 0 0;
        height: 4px;
    }

    .metric-card.income .metric-accent { background: #16a34a; }
    .metric-card.expense .metric-accent { background: #dc2626; }
    .metric-card.balance .metric-accent { background: #2563eb; }
    .metric-card.category .metric-accent { background: #8b5cf6; }

    .insight-card {
        height: 100%;
        min-height: 280px;
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #bfdbfe;
        background: #eff6ff;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .insight-card.warning {
        border-color: #fde68a;
        background: var(--warning-bg);
    }

    .insight-card.danger {
        border-color: #fecaca;
        background: var(--danger-bg);
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        width: fit-content;
        padding: 0.35rem 0.65rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.75);
        color: var(--primary);
        font-size: 12px;
        font-weight: 700;
    }

    .warning .status-pill { color: var(--warning); }
    .danger .status-pill { color: var(--danger); }

    .insight-title {
        color: var(--text);
        font-size: 18px;
        font-weight: 650;
        margin-top: 1rem;
    }

    .daily-amount {
        color: var(--primary);
        font-size: 38px;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        letter-spacing: -0.04em;
        margin-top: 0.4rem;
    }

    .warning .daily-amount { color: var(--warning); }
    .danger .daily-amount { color: var(--danger); }

    .insight-copy {
        color: #475569;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 0.65rem;
    }

    .progress-track {
        height: 9px;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.25);
        overflow: hidden;
        margin-top: 1.25rem;
    }

    .progress-value {
        height: 100%;
        border-radius: inherit;
        background: var(--primary);
    }

    .warning .progress-value { background: var(--warning); }
    .danger .progress-value { background: var(--danger); }

    .progress-copy {
        display: flex;
        justify-content: space-between;
        color: var(--muted);
        font-size: 12px;
        margin-top: 0.55rem;
    }

    .section-card {
        padding: 1.25rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    .section-title {
        color: var(--text);
        font-size: 18px;
        font-weight: 650;
        margin-bottom: 0.2rem;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 1rem;
    }

    .chart-breakdown {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.6rem 1rem;
        margin-top: 0.25rem;
    }

    .chart-breakdown-item {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr) auto;
        align-items: center;
        gap: 0.55rem;
        min-width: 0;
        padding: 0.6rem 0.7rem;
        border: 1px solid var(--border);
        border-radius: 10px;
        background: #ffffff;
    }

    .chart-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
    }

    .chart-category {
        min-width: 0;
        color: var(--text);
        font-size: 12px;
        font-weight: 600;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .chart-amount {
        color: #475569;
        font-size: 12px;
        font-variant-numeric: tabular-nums;
        text-align: right;
        white-space: nowrap;
    }

    .empty-state {
        min-height: 300px;
        padding: 3rem 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
    }

    .empty-icon {
        display: grid;
        place-items: center;
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: #f1f5f9;
        color: #475569;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .empty-title {
        color: var(--text);
        font-size: 18px;
        font-weight: 650;
    }

    .empty-copy {
        max-width: 480px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.6;
        margin-top: 0.4rem;
    }

    .over-budget-banner {
        display: flex;
        align-items: flex-start;
        gap: 0.85rem;
        padding: 1rem 1.15rem;
        margin-bottom: 1rem;
        border: 1px solid #fecaca;
        border-radius: 14px;
        background: var(--danger-bg);
        color: #991b1b;
    }

    .over-budget-title {
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .over-budget-copy {
        font-size: 14px;
        line-height: 1.5;
    }

    div[data-testid="stForm"] {
        border: 0;
        padding: 0;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 44px;
        border-radius: 10px;
        font-weight: 600;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {
        background: var(--primary);
        border-color: var(--primary);
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover {
        background: var(--primary-dark);
        border-color: var(--primary-dark);
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    [data-testid="stDateInput"] > div > div {
        border-radius: 10px;
        background: #ffffff;
        color: var(--text);
    }

    input, textarea {
        color: var(--text) !important;
        background: #ffffff !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
    }

    @media (max-width: 767px) {
        .block-container {
            padding: 1.25rem 1rem 3rem;
        }

        .metric-card {
            min-height: 124px;
        }

        .chart-breakdown {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def metric_card(
    label: str,
    value: str,
    note: str,
    accent: str,
) -> str:
    return f"""
    <div class="metric-card {escape(accent)}">
        <div class="metric-label">{escape(label)}</div>
        <div class="metric-value">{escape(value)}</div>
        <div class="metric-note">{escape(note)}</div>
        <div class="metric-accent"></div>
    </div>
    """


@st.dialog("Add Transaction", width="small")
def add_transaction_dialog() -> None:
    st.caption("Record income or spending. All fields except Note are required.")

    with st.form("transaction_dialog_form", clear_on_submit=True):
        transaction_type = st.segmented_control(
            "Type",
            options=("Expense", "Income"),
            default="Expense",
            selection_mode="single",
        )
        amount = st.number_input(
            "Amount",
            min_value=0.01,
            value=0.01,
            step=0.01,
            format="%.2f",
        )
        category = st.text_input(
            "Category",
            placeholder="e.g. Groceries, Salary, Housing",
        )
        transaction_date = st.date_input("Date", value=date.today())
        note = st.text_area(
            "Note (optional)",
            placeholder="Add a short description",
            height=90,
        )
        submitted = st.form_submit_button(
            "Save Transaction",
            width="stretch",
        )

    if submitted:
        try:
            append_transaction(
                date=transaction_date,
                transaction_type=transaction_type or "Expense",
                category=category,
                amount=amount,
                note=note,
            )
        except (TypeError, ValueError, RuntimeError) as exc:
            st.error(str(exc))
        else:
            st.session_state.transaction_saved = True
            st.rerun()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">$</div>
            <div>
                <div class="brand-title">FinControl</div>
                <div class="brand-subtitle">Personal Finance Tracker</div>
            </div>
        </div>
        <div class="sidebar-guide">
            <div class="sidebar-guide-title">Everything is on this page</div>
            <div class="sidebar-guide-item">1. Add income or expenses.</div>
            <div class="sidebar-guide-item">2. Review summary cards and chart.</div>
            <div class="sidebar-guide-item">3. Filter the transaction list below.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "+ Add Transaction",
        type="primary",
        width="stretch",
        key="sidebar_add_transaction",
    ):
        add_transaction_dialog()

    st.divider()
    st.markdown("#### Monthly budget")
    monthly_budget = st.number_input(
        "Budget target",
        min_value=0.0,
        value=2000.0,
        step=100.0,
        format="%.2f",
        help="Used to calculate your safe daily spending for this month.",
    )
    st.caption("Adjust this target at any time. It does not change transaction data.")


try:
    transactions = load_transactions()
except (ValueError, RuntimeError) as exc:
    st.error(f"Could not load transactions: {exc}")
    st.stop()

if st.session_state.pop("transaction_saved", False):
    st.toast("Transaction added successfully.")

total_income, total_expense, net_balance = calculate_financial_totals(
    transactions
)
spending_by_category = group_expenses_by_category(transactions)
top_category, top_category_amount = calculate_top_spending_category(
    transactions,
    spending_by_category,
)

today = date.today()
month_start = pd.Timestamp(today.replace(day=1))
next_month_start = month_start + pd.offsets.MonthBegin(1)
current_month_mask = (
    transactions["Date"].ge(month_start)
    & transactions["Date"].lt(next_month_start)
    & transactions["Type"].eq("Expense")
)
current_month_expense = float(
    transactions.loc[current_month_mask, "Amount"].sum()
)

last_day = calendar.monthrange(today.year, today.month)[1]
remaining_days = last_day - today.day + 1
remaining_budget = monthly_budget - current_month_expense
safe_daily_spending = max(remaining_budget, 0.0) / remaining_days
budget_usage = (
    current_month_expense / monthly_budget if monthly_budget > 0 else 0.0
)
progress_width = min(max(budget_usage * 100, 0.0), 100.0)

if remaining_budget < 0:
    budget_status = "Over budget"
    insight_style = "danger"
elif budget_usage >= 0.8:
    budget_status = "Approaching limit"
    insight_style = "warning"
else:
    budget_status = "On track"
    insight_style = ""

header_copy, header_action = st.columns([4, 1], vertical_alignment="center")
with header_copy:
    st.markdown(
        f"""
        <div class="page-header">
            <div class="eyebrow">{escape(today.strftime("%B %Y"))}</div>
            <div class="page-title">Financial Overview</div>
            <div class="page-subtitle">
                Track your income, spending, and monthly budget at a glance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_action:
    if st.button(
        "+ Add Transaction",
        type="primary",
        width="stretch",
        key="header_add_transaction",
    ):
        add_transaction_dialog()

metric_columns = st.columns(4)
metric_columns[0].markdown(
    metric_card(
        "Total Income",
        money(total_income),
        "Across all recorded transactions",
        "income",
    ),
    unsafe_allow_html=True,
)
metric_columns[1].markdown(
    metric_card(
        "Total Expenses",
        money(total_expense),
        "Across all recorded transactions",
        "expense",
    ),
    unsafe_allow_html=True,
)
metric_columns[2].markdown(
    metric_card(
        "Net Balance",
        money(net_balance),
        "Income minus expenses",
        "balance",
    ),
    unsafe_allow_html=True,
)
metric_columns[3].markdown(
    metric_card(
        "Top Spending Category",
        top_category,
        f"{money(top_category_amount)} spent",
        "category",
    ),
    unsafe_allow_html=True,
)

st.write("")

if remaining_budget < 0:
    st.markdown(
        f"""
        <div class="over-budget-banner" role="alert">
            <div>
                <div class="over-budget-title">Monthly budget exceeded</div>
                <div class="over-budget-copy">
                    Current-month expenses are
                    <strong>{escape(money(abs(remaining_budget)))}</strong>
                    above your {escape(money(monthly_budget))} target.
                    Review recent expenses before making non-essential purchases.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

insight_column, chart_column = st.columns([4, 8])

with insight_column:
    if remaining_budget < 0:
        insight_copy = (
            f"You have no remaining budget for the next {remaining_days} "
            "day(s). Safe daily spending is limited to essential purchases."
        )
    else:
        insight_copy = (
            f"You can spend {money(safe_daily_spending)} per day for the "
            f"remaining {remaining_days} day(s) and stay within your target."
        )

    st.markdown(
        f"""
        <div class="insight-card {escape(insight_style)}">
            <div>
                <div class="status-pill">{escape(budget_status)}</div>
                <div class="insight-title">Safe Daily Spending</div>
                <div class="daily-amount">{escape(money(safe_daily_spending))}</div>
                <div class="insight-copy">{escape(insight_copy)}</div>
            </div>
            <div>
                <div class="progress-track" aria-label="Monthly budget usage">
                    <div class="progress-value" style="width:{progress_width:.1f}%"></div>
                </div>
                <div class="progress-copy">
                    <span>{escape(money(current_month_expense))} spent</span>
                    <span>{budget_usage * 100:.0f}% of {escape(money(monthly_budget))}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with chart_column:
    st.markdown(
        """
        <div class="section-title">Expenses by Category</div>
        <div class="section-subtitle">
            Interactive breakdown of all recorded expenses.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if spending_by_category.empty:
        st.info("Add an expense to display the category chart.")
    else:
        chart_colors = [
            "#2563eb",
            "#14b8a6",
            "#f59e0b",
            "#8b5cf6",
            "#ec4899",
            "#64748b",
        ]
        expense_chart = px.pie(
            spending_by_category,
            names="Category",
            values="Amount",
            hole=0.58,
            color_discrete_sequence=chart_colors,
        )
        expense_chart.update_traces(
            textposition="inside",
            textinfo="label+percent",
            hovertemplate=(
                "%{label}<br>$%{value:,.2f}<br>%{percent}<extra></extra>"
            ),
            marker={"line": {"color": "#ffffff", "width": 2}},
        )
        expense_chart.update_layout(
            height=300,
            margin={"l": 10, "r": 10, "t": 10, "b": 10},
            legend={
                "visible": False,
            },
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter", "color": "#334155"},
            annotations=[
                {
                    "text": (
                        f"Total<br><b>{money(total_expense)}</b>"
                    ),
                    "x": 0.5,
                    "y": 0.5,
                    "font": {"size": 15, "color": "#0f172a"},
                    "showarrow": False,
                }
            ],
        )
        st.plotly_chart(
            expense_chart,
            width="stretch",
            config={"displayModeBar": False},
        )

        breakdown_items = []
        for index, row in spending_by_category.reset_index(drop=True).iterrows():
            category = str(row["Category"])
            amount = float(row["Amount"])
            percentage = (
                amount / total_expense * 100 if total_expense > 0 else 0.0
            )
            color = chart_colors[index % len(chart_colors)]
            breakdown_items.append(
                '<div class="chart-breakdown-item">'
                f'<div class="chart-dot" style="background:{color}"></div>'
                f'<div class="chart-category">{escape(category)}</div>'
                '<div class="chart-amount">'
                f'{escape(money(amount))} · {percentage:.1f}%'
                "</div></div>"
            )

        st.markdown(
            '<div class="chart-breakdown">'
            + "".join(breakdown_items)
            + "</div>",
            unsafe_allow_html=True,
        )

st.write("")
st.markdown(
    """
    <div class="section-title">Transactions</div>
    <div class="section-subtitle">
        Review and filter your complete financial activity.
    </div>
    """,
    unsafe_allow_html=True,
)

if transactions.empty:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">+</div>
            <div class="empty-title">No transactions yet</div>
            <div class="empty-copy">
                Add your first income or expense to start building your
                financial overview, category chart, and spending insight.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "Add First Transaction",
        type="primary",
        width="stretch",
        key="empty_add_transaction",
    ):
        add_transaction_dialog()
else:
    filter_one, filter_two, filter_three = st.columns([2, 2, 3])
    with filter_one:
        type_filter = st.selectbox(
            "Type",
            options=("All", "Income", "Expense"),
        )
    with filter_two:
        category_options = [
            "All",
            *sorted(transactions["Category"].dropna().unique().tolist()),
        ]
        category_filter = st.selectbox(
            "Category",
            options=category_options,
        )
    with filter_three:
        minimum_date = transactions["Date"].min().date()
        maximum_date = transactions["Date"].max().date()
        selected_dates = st.date_input(
            "Date range",
            value=(minimum_date, maximum_date),
            min_value=minimum_date,
            max_value=maximum_date,
        )

    filtered_transactions = transactions

    if type_filter != "All":
        filtered_transactions = filtered_transactions.loc[
            filtered_transactions["Type"].eq(type_filter)
        ]

    if category_filter != "All":
        filtered_transactions = filtered_transactions.loc[
            filtered_transactions["Category"].eq(category_filter)
        ]

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = map(pd.Timestamp, selected_dates)
        filtered_transactions = (
            filtered_transactions.sort_values("Date")
            .set_index("Date")
            .loc[start_date:end_date]
            .reset_index()
        )

    filtered_transactions = filtered_transactions.sort_values(
        "Date",
        ascending=False,
        ignore_index=True,
    )

    st.caption(
        f"{len(filtered_transactions):,} of {len(transactions):,} "
        "transaction(s)"
    )

    if filtered_transactions.empty:
        st.info("No transactions match the selected filters.")
    else:
        st.dataframe(
            filtered_transactions,
            width="stretch",
            hide_index=True,
            column_order=("Date", "Type", "Category", "Note", "Amount"),
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    format="MMM DD, YYYY",
                ),
                "Type": st.column_config.TextColumn("Type"),
                "Category": st.column_config.TextColumn("Category"),
                "Note": st.column_config.TextColumn("Note"),
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f",
                ),
            },
            height=min(420, 38 + len(filtered_transactions) * 36),
        )
