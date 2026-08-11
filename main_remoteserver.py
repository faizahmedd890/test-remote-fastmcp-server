from fastmcp import FastMCP
import os
import sqlite3
import aiosqlite
import json


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "expenses.db")
CATEGORIES_PATH = os.path.join(BASE_DIR, "categories.json")

print(f"Database path: {DB_PATH}")


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("ExpenseTracker")


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    """Create the SQLite database and expenses table."""

    try:
        with sqlite3.connect(DB_PATH) as conn:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                )
            """)

            conn.commit()

        print("Database initialized successfully.")
        print(f"Database file: {DB_PATH}")

    except Exception as e:
        print(f"Database initialization error: {e}")
        raise


# Initialize database when server starts
init_db()


# ============================================================
# TOOL 1: ADD EXPENSE
# ============================================================

@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Add a new expense to the database.
    """

    try:

        async with aiosqlite.connect(DB_PATH) as conn:

            cursor = await conn.execute(
                """
                INSERT INTO expenses
                (date, amount, category, subcategory, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (date, amount, category, subcategory, note)
            )

            expense_id = cursor.lastrowid

            await conn.commit()

        return {
            "status": "success",
            "id": expense_id,
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note,
            "message": "Expense added successfully"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }


# ============================================================
# TOOL 2: LIST EXPENSES
# ============================================================

@mcp.tool()
async def list_expenses(
    start_date: str,
    end_date: str
):
    """
    List all expenses within an inclusive date range.
    """

    try:

        async with aiosqlite.connect(DB_PATH) as conn:

            conn.row_factory = aiosqlite.Row

            cursor = await conn.execute(
                """
                SELECT
                    id,
                    date,
                    amount,
                    category,
                    subcategory,
                    note
                FROM expenses
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
                """,
                (start_date, end_date)
            )

            rows = await cursor.fetchall()

        return [dict(row) for row in rows]

    except Exception as e:

        return {
            "status": "error",
            "message": f"Error listing expenses: {str(e)}"
        }


# ============================================================
# TOOL 3: SUMMARIZE EXPENSES
# ============================================================

@mcp.tool()
async def summarize(
    start_date: str,
    end_date: str,
    category: str = None
):
    """
    Summarize expenses by category within an inclusive date range.

    If category is provided, only that category is summarized.
    """

    try:

        async with aiosqlite.connect(DB_PATH) as conn:

            conn.row_factory = aiosqlite.Row

            query = """
                SELECT
                    category,
                    SUM(amount) AS total_amount,
                    COUNT(*) AS count
                FROM expenses
                WHERE date BETWEEN ? AND ?
            """

            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)

            query += """
                GROUP BY category
                ORDER BY total_amount DESC
            """

            cursor = await conn.execute(query, params)

            rows = await cursor.fetchall()

        return [dict(row) for row in rows]

    except Exception as e:

        return {
            "status": "error",
            "message": f"Error summarizing expenses: {str(e)}"
        }


# ============================================================
# RESOURCE: EXPENSE CATEGORIES
# ============================================================

@mcp.resource(
    "expense:///categories",
    mime_type="application/json"
)
def categories():
    """
    Return the available expense categories.
    """

    default_categories = {
        "categories": [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business",
            "Other"
        ]
    }

    try:

        if os.path.exists(CATEGORIES_PATH):

            with open(
                CATEGORIES_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                return f.read()

        return json.dumps(
            default_categories,
            indent=2
        )

    except Exception as e:

        return json.dumps({
            "error": f"Could not load categories: {str(e)}"
        })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("Starting ExpenseTracker MCP server...")

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )