import os
import africastalking
from mcp.server.fastmcp import FastMCP
import sqlite3
from datetime import datetime
from pathlib import Path

mcp = FastMCP("AfricasTalking Airtime MCP")

DB_PATH = Path(__file__).parent / "airtime_transactions.db"


def init_database():
    """Initializes the database and creates the transactions table.

    This function connects to the SQLite database file defined by DB_PATH.
    If the 'transactions' table does not already exist, it is created with
    columns for storing transaction details.
    """
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
user_country = os.getenv("country").lower()


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
    """Formats a phone number to include the international country code.

    This function takes a phone number as a string and formats it based on
    the user's country, which is determined by the `user_country` global
    variable. It handles numbers that start with '0', '+', or a digit.

    Args:
        phone_number (str): The phone number to be formatted.

    Returns:
        str: The phone number with the country code prepended.

    Raises:
        ValueError: If the `user_country` is not in the `COUNTRY_CODES` map.
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
    """Saves a single airtime transaction to the SQLite database.

    Args:
        phone_number (str): The recipient's phone number.
        amount (float): The amount of airtime sent.
        currency_code (str): The currency of the transaction (e.g., "KES").
    """
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
    """Checks the airtime balance of the Africa's Talking account.

    This tool connects to the Africa's Talking API to fetch the user's
    current application data, which includes the account balance.

    Returns:
        str: A message displaying the account balance or an error if the
             balance cannot be retrieved.
    """
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
    """Sends airtime to a specified phone number and logs the transaction.

    This tool formats the phone number, sends the airtime using the
    Africa's Talking API, and saves a record of the transaction in the
    database.

    Args:
        phone_number (str): The recipient's phone number.
        amount (float): The amount of airtime to send.
        currency_code (str): The currency for the transaction (e.g., "KES").

    Returns:
        str: A message indicating the status of the airtime transaction.
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
    """Retrieves the last N top-up transactions from the database.

    Args:
        limit (int, optional): The number of recent transactions to fetch.
                               Defaults to 3.

    Returns:
        str: A formatted string listing the last N transactions or a message
             if no transactions are found.
    """
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
    """Calculates the sum of the last 'n' successful top-ups.

    This tool retrieves the last 'n' transactions from the database and
    calculates their total sum. It ensures that all transactions are in the
    same currency before summing.

    Args:
        n (int, optional): The number of recent top-ups to sum. Defaults to 3.

    Returns:
        str: The total sum of the last 'n' top-ups or an error message if
             the currencies are mixed or no transactions are found.
    """
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
    """Counts the number of top-ups for a specific phone number.

    Args:
        phone_number (str): The phone number to count transactions for.

    Returns:
        str: The total count of top-ups for the given number or an error message.
    """
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
