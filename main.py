import os
import africastalking
from mcp.server.fastmcp import FastMCP
import sqlite3
from datetime import datetime
from pathlib import Path

mcp = FastMCP("AfricasTalking Airtime MCP")

DB_PATH = Path(__file__).parent / "airtime_transactions.db"


def init_database():
    """Initialize the SQLite database and create transactions table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                amount REAL NOT NULL,
                currency_code TEXT NOT NULL,
                transaction_time TIMESTAMP NOT NULL
            )
            """
        )
        conn.commit()


init_database()

username = os.getenv("username")
api_key = os.getenv("api_key")
currency_code = os.getenv("currency_code")
user_country = os.getenv("country", "kenya").lower()


COUNTRY_CODES = {
    "kenya": "+254",
    "uganda": "+256",
    "nigeria": "+234",
    "dr congo": "+243",
    "rwanda": "+250",
    "ethiopia": "+251",
    "south africa": "+27",
    "tanzania": "+255",
    "ghana": "+233",
    "malawi": "+265",
    "zambia": "+260",
    "zimbabwe": "+263",
    "ivory coast": "+225",
    "cameroon": "+237",
    "senegal": "+221",
    "mozambique": "+258",
}


africastalking.initialize(username, api_key)
airtime = africastalking.Airtime


def format_phone_number(phone_number):
    """
    Format the phone number to include the country code based on the user's country.
    If the number starts with '0', replace it with the country's code.
    If it starts with '+', assume it's already formatted.
    If no valid country is set, raise an error.

    Args:
        phone_number (str): The phone number to format.

    Returns:
        str: The formatted phone number with the country code.

    Raises:
        ValueError: If the country is not set or invalid.
    """
    phone_number = str(phone_number).strip()

    if user_country not in COUNTRY_CODES:
        raise ValueError(
            f"Invalid or unset country: {user_country}. Supported countries: {list(COUNTRY_CODES.keys())}"
        )

    country_code = COUNTRY_CODES[user_country]

    if phone_number.startswith("0"):
        return country_code + phone_number[1:]
    elif phone_number.startswith("+"):
        return phone_number
    else:
        return country_code + phone_number


def save_transaction(phone_number, amount, currency_code):
    """Save a transaction to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (phone_number, amount, currency_code, transaction_time)
            VALUES (?, ?, ?, ?)
            """,
            (phone_number, amount, currency_code, datetime.now()),
        )
        conn.commit()


@mcp.tool()
async def check_balance() -> str:
    """Check the airtime balance for your Africa's Talking account."""
    try:
        response = africastalking.Application.fetch_application_data()
        if "UserData" in response and "balance" in response["UserData"]:
            balance = response["UserData"]["balance"]
            return f"Account Balance: {balance}"
        else:
            return "Balance information not available at the moment. Try again later."
    except Exception as e:
        return f"Error fetching balance: {str(e)}"


@mcp.tool()
async def load_airtime(phone_number: str, amount: float, currency_code: str) -> str:
    """
    Load airtime to a specified telephone number and save the transaction.

    Args:
        phone_number: The phone number to send airtime to
        amount: The amount of airtime to send
        currency_code: The currency code

    Returns:
        A message indicating success or failure
    """
    try:
        formatted_number = format_phone_number(phone_number)
        airtime.send(
            phone_number=formatted_number, amount=amount, currency_code=currency_code
        )

        save_transaction(formatted_number, amount, currency_code)
        return (
            f"Successfully sent {currency_code} {amount} airtime to {formatted_number}"
        )

    except Exception as e:
        return f"Encountered an error while sending airtime: {str(e)}"


@mcp.tool()
async def get_last_topups(limit: int = 3) -> str:
    """Get the last N top-up transactions"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT phone_number, amount, currency_code, transaction_time
                FROM transactions
                ORDER BY transaction_time DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()

        if not rows:
            return "No top-up transactions found."

        result = f"Last {limit} top-up transactions:\n"
        for row in rows:
            try:
                transaction_time = datetime.strptime(
                    row[3], "%Y-%m-%d %H:%M:%S.%f"
                ).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                transaction_time = row[3]
            result += f"- {transaction_time}: {row[2]} {row[1]:.2f} to {row[0]}\n"
        return result
    except Exception as e:
        return f"Error fetching top-ups: {str(e)}"


@mcp.tool()
async def sum_last_n_topups(n: int = 3) -> str:
    """Calculate the sum of the last n successful top-ups, defaulting to 3."""
    if n <= 0:
        return "Please provide the number of top-ups whose total you need."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT amount, currency_code
                FROM transactions
                ORDER BY transaction_time DESC
                LIMIT ?
                """,
                (n,),
            )
            rows = cursor.fetchall()

        if not rows:
            return "No successful top-ups found."

        currencies = set(row[1] for row in rows)
        if len(currencies) > 1:
            return "Cannot sum amounts with different currencies."

        total = sum(amount for (amount, _) in rows)
        currency = rows[0][1]
        return f"Sum of last {n} successful top-ups:\n- {currency} {total:.2f}"
    except Exception as e:
        return f"Error calculating sum: {str(e)}"


@mcp.tool()
async def count_topups_by_number(phone_number: str) -> str:
    """Count the number of successful top-ups to a specific phone number."""
    try:
        formatted_number = format_phone_number(phone_number)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM transactions
                WHERE phone_number = ?
            """,
                (formatted_number,),
            )
            count = cursor.fetchone()[0]

        return f"Number of successful top-ups to {formatted_number}: {count}"
    except Exception as e:
        return f"Error counting top-ups: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
