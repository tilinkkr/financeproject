from __future__ import annotations

import csv
import os
from math import isfinite
from pathlib import Path
from threading import Lock
from typing import Final

import pandas as pd


CSV_PATH: Final[Path] = Path(
    os.getenv(
        "FINCONTROL_CSV_PATH",
        str(Path(__file__).with_name("transactions.csv")),
    )
)
COLUMNS: Final[list[str]] = ["Date", "Type", "Category", "Amount", "Note"]
TRANSACTION_TYPES: Final[set[str]] = {"Income", "Expense"}

_WRITE_LOCK = Lock()


def _create_csv_if_missing(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with csv_path.open("x", encoding="utf-8", newline="") as file:
            pd.DataFrame(columns=COLUMNS).to_csv(file, index=False)
            file.flush()
            os.fsync(file.fileno())
    except FileExistsError:
        pass


def _validate_csv_schema(csv_path: Path) -> None:
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as file:
            header = next(csv.reader(file), None)
    except OSError as exc:
        raise RuntimeError(f"Unable to inspect '{csv_path}'.") from exc

    if header != COLUMNS:
        raise ValueError(
            f"CSV columns must be exactly: {', '.join(COLUMNS)}."
        )


def load_transactions(csv_path: str | Path = CSV_PATH) -> pd.DataFrame:
    path = Path(csv_path)
    _create_csv_if_missing(path)
    _validate_csv_schema(path)

    try:
        transactions = pd.read_csv(
            path,
            usecols=COLUMNS,
            dtype={
                "Type": "string",
                "Category": "string",
                "Amount": "float64",
                "Note": "string",
            },
            parse_dates=["Date"],
            keep_default_na=False,
        )
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        raise RuntimeError(f"Unable to load transactions from '{path}'.") from exc

    if list(transactions.columns) != COLUMNS:
        transactions = transactions.reindex(columns=COLUMNS)

    transactions["Date"] = pd.to_datetime(transactions["Date"], errors="coerce")
    if transactions["Date"].isna().any():
        raise ValueError(f"Invalid date value found in '{path}'.")

    return transactions


def append_transaction(
    date: str | pd.Timestamp,
    transaction_type: str,
    category: str,
    amount: float,
    note: str = "",
    csv_path: str | Path = CSV_PATH,
) -> None:
    path = Path(csv_path)
    parsed_date = pd.to_datetime(date, errors="coerce")

    if pd.isna(parsed_date):
        raise ValueError("date must be a valid date.")
    if transaction_type not in TRANSACTION_TYPES:
        raise ValueError("transaction_type must be 'Income' or 'Expense'.")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must be a non-empty string.")
    if not isinstance(note, str):
        raise TypeError("note must be a string.")

    try:
        parsed_amount = float(amount)
    except (TypeError, ValueError) as exc:
        raise ValueError("amount must be a valid number.") from exc

    if not isfinite(parsed_amount):
        raise ValueError("amount must be a finite number.")

    transaction = pd.DataFrame(
        [
            {
                "Date": parsed_date.strftime("%Y-%m-%d"),
                "Type": transaction_type,
                "Category": category.strip(),
                "Amount": parsed_amount,
                "Note": note,
            }
        ],
        columns=COLUMNS,
    )

    with _WRITE_LOCK:
        _create_csv_if_missing(path)
        _validate_csv_schema(path)
        try:
            with path.open("a", encoding="utf-8", newline="") as file:
                transaction.to_csv(file, header=False, index=False)
                file.flush()
                os.fsync(file.fileno())
        except OSError as exc:
            raise RuntimeError(f"Unable to append transaction to '{path}'.") from exc
