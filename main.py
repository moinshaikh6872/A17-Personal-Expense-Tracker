import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Personal Expense Tracker API")

# Allow the HTML page to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "expenses.json"

# Models for data validation
class ExpenseInput(BaseModel):
    description: str
    amount: float
    category: str

class Expense(ExpenseInput):
    id: int

# Helper functions for file persistence
def load_expenses() -> List[dict]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_expenses(expenses: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

# CRUD Endpoints
@app.get("/expenses", response_model=List[Expense])
def get_expenses():
    """Reads all expenses from the file."""
    return load_expenses()

@app.post("/expenses", response_model=Expense)
def add_expense(expense: ExpenseInput):
    """Adds a new expense and saves it to the file."""
    expenses = load_expenses()
    new_id = 1 if not expenses else max(e["id"] for e in expenses) + 1
    new_expense = {"id": new_id, "description": expense.description, "amount": expense.amount, "category": expense.category}
    
    expenses.append(new_expense)
    save_expenses(expenses)
    return new_expense

@app.put("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, expense_update: ExpenseInput):
    """Updates an existing expense in the file."""
    expenses = load_expenses()
    for i, exp in enumerate(expenses):
        if exp["id"] == expense_id:
            expenses[i]["description"] = expense_update.description
            expenses[i]["amount"] = expense_update.amount
            expenses[i]["category"] = expense_update.category
            save_expenses(expenses)
            return expenses[i]
    raise HTTPException(status_code=404, detail="Expense not found")

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    """Deletes an expense from the file."""
    expenses = load_expenses()
    for i, exp in enumerate(expenses):
        if exp["id"] == expense_id:
            del expenses[i]
            save_expenses(expenses)
            return {"message": "Expense deleted successfully"}
    raise HTTPException(status_code=404, detail="Expense not found")
