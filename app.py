from bson import ObjectId
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

# App Config
app = Flask(__name__)

# Load from .env
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
mongo_url = os.getenv("MONGO_URL")
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
database_name = os.getenv("Database")
database_collection = os.getenv("Collection")

# MongoDB connection
uri = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_url}/?retryWrites=true&w=majority"
client = MongoClient(uri)

# MongoDB database and collection connection
database: Database = client.get_database(f"{database_name}")
collection: Collection = database.get_collection(f"{database_collection}")

# Templates
index_template = "index.html"

# Routes
@app.route('/', methods=['GET', 'POST'])
def main():
    tasks = list(collection.find())
    return render_template(index_template, tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    taskName = request.form.get("taskName")
    taskDescription = request.form.get("taskDescription")
    taskStatus = request.form.get("status")
    dueTo = request.form.get("dueTo")
    
    if not taskName or not taskDescription:
        flash('Fields cannot be empty', 'error')

    if dueTo:
        try:
            dueTo_datetime = datetime.fromisoformat(dueTo.replace("T", " "))
        except ValueError:
            flash('Invalid due date format', 'error')
            return redirect(url_for('main'))
    else:
        dueTo_datetime = None    

    data = {
        "Name": taskName,
        "Description": taskDescription,
        "Status": taskStatus,
        "DueTo": dueTo_datetime.strftime("%Y-%m-%d %H:%M") if dueTo_datetime else None
    }
    collection.insert_one(data)
    flash("Task added succefully", "success")

    return redirect(url_for("main"))

@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_id = request.form.get("task_id")
    if task_id:
        result = collection.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count == 1:
            flash("Task deleted succefully", "success")
        else:
            flash("Error deleting task.", "error")
    else:
        flash("Invalid request.", "error")
    
    return redirect(url_for("main"))

@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = collection.find_one({"_id": ObjectId(task_id)})
    if task:
        if request.method == 'POST':
            task_name = request.form.get("taskName")
            task_description = request.form.get("taskDescription")
            task_status = request.form.get("status")
            collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"Name": task_name, "Description": task_description, "Status": task_status}})
            flash("Task updated successfully", "success")
            return redirect(url_for("main"))
        return render_template("edit_task.html", task=task)
    else:
        flash("Task not found", "error")
        return redirect(url_for("main"))

if __name__ == "__main__":
    app.run(debug=True)