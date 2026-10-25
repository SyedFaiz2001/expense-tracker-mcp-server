"""def main() -> None:
    print("Hello from expense-tracker-mcp-server!")

main()

import random
from fastmcp import FastMCP

#Create an instance of FastMCP with the name "Demo Server"
mcp = FastMCP(name = "Demo Server")

@mcp.tool
def roll_dice(n_dice : int = 1) -> list[int]:
    #Rolls a specified number of dice and returns the results as a list of integers.
    return[random.randint(1,6) for _ in range(n_dice)]

@mcp.tool
def add_numbers(a: float, b: float) -> float:
    return a + b

if __name__ == "__main__":
    mcp.run()"""

#Run this command: uv run fastmcp dev inspector --inspector-version latest "src\expense_tracker_mcp_server\main.py"

from fastmcp import FastMCP
#from fastapi import FastAPI <- Won't work since I am having issues installing fastapi and uvicorn on my machine. I will try to fix this later. For now, I will use FastMCP to create the API server.
import os
import sqlite3

DB_Path = os.path.join(os.path.dirname(__file__), 'expenses.db')
Categories_Path = os.path.join(os.path.dirname(__file__), 'categories.json')

mcp = FastMCP(name = "ExpenseTracker")

#app = FastAPI(title ="Expense Tracker API")

def init_db():
    with sqlite3.connect(DB_Path) as c :
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
            )
            """
        )

init_db()

@mcp.resource("expense://categories", mime_type = "application/json")
def categories():
    with open(Categories_Path, 'r', encoding = 'utf-8') as f :
        return f.read()

@mcp.tool
def add_expense(date, amount, category, subcategory='', note=''):
    '''Adds a new expense to the database. Returns a dictionary with the status and the id of the newly added expense.'''
    with sqlite3.connect(DB_Path) as c:
        cur = c.execute(
            "INSERT INTO expenses (date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category, subcategory, note)
            )
        return {"status": 'ok', "id": cur.lastrowid}

@mcp.tool
def list_expenses(start_date, end_date):
    '''Lists all expenses in the database between the specified dates, ordered by id ascending.'''
    with sqlite3.connect(DB_Path) as c:
        cur = c.execute("""
            SELECT * 
            FROM expenses 
            WHERE date BETWEEN ? AND ? 
            ORDER BY id ASC
            """,
            (start_date, end_date))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]

@mcp.tool
def summarize_expenses(start_date, end_date, category= None):
    with sqlite3.connect(DB_Path) as c :
        query = ("""
            SELECT category, SUM(amount) as Total
            FROM expenses
            WHERE date BETWEEN ? AND ?""")

        param = [start_date, end_date]
        if category:
            query += " AND category = ?"
            param.append(category)

        query += " GROUP BY category ORDER BY category ASC"
        cur = c.execute(query, param)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]

if __name__ == "__main__":
    mcp.run()