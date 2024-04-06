from bson import ObjectId
from math import ceil
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash, session
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import hashlib
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
database_tasks_collection = os.getenv("database_tasks_collection")
database_users_collection = os.getenv("database_user_collection")

# MongoDB connection
uri = f"mongodb+srv://{mongo_username}:{mongo_password}@{mongo_url}/?retryWrites=true&w=majority"
client = MongoClient(uri)

# MongoDB database and collection connection
database: Database = client.get_database(f"{database_name}")
tasks_collection: Collection = database.get_collection(f"{database_tasks_collection}")
users_collection: Collection = database.get_collection(f"{database_users_collection}")

# Templates
index_template = "index.html"
register_template = "authentication/register.html"
login_template = "authentication/login.html"
admin_template = "administration/admin.html"
admin_edit_user_template = "administration/admin_edit_user.html"

# Routes
@app.route('/', methods=['GET', 'POST'])
def main():
    if "username" not in session:
        return render_template(index_template)
    else:
        username = session["username"]
        tasks = list(tasks_collection.find({"Username": username}))
    return render_template(index_template, tasks=tasks)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        repeat_password = request.form.get("passwordRepeat")

        existing_user = users_collection.find_one({"$or": [{"username": username}]})

        if not username or not password or not repeat_password:
            flash('Fields cannot be empty', 'error')
            return redirect(url_for('register'))
        
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if password != repeat_password:
            flash("Passwords don't match", 'error')
            return redirect(url_for('register'))
        
        hasher = hashlib.shake_256()
        hasher.update(password.encode("utf-8"))
        hashed_password = hasher.digest(32)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            "created": timestamp,
            "username": username,
            "password": hashed_password,
            "admin": 0,
            "tasks": 0
        }
        users_collection.insert_one(data)

        flash('You have registered successfully', 'success')
        return redirect(url_for('login'))

    return render_template(register_template)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({"username": username})

        if not username or not password:
            flash('Fields cannot be empty', 'error')
            return redirect(url_for('login'))

        if user:
            stored_password = user.get("password")
            hasher = hashlib.shake_256()
            hasher.update(password.encode('utf-8'))
            hashed_password = hasher.digest(32)

            if hashed_password == stored_password:
                session["username"] = user["username"]
                session["admin"] = user.get("admin", 0)
                return redirect(url_for('main'))
            else:
                flash('Incorrect password', 'error')
                return redirect(url_for('login'))
        else:
            flash("User doesn't exist", 'error')
            return redirect(url_for('login'))

    return render_template(login_template)

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('username')
    flash('You have succesfully logged out', 'success')
    return redirect(url_for('main'))

def check_admin_session():
    if "username" not in session:
        flash('You do not have permission to access this page', 'error')
        return False
    
    current_user = users_collection.find_one({"username": session["username"]})
    if current_user and current_user.get("admin", 0) != 1:
        flash('You must be an admin to access this page.', 'error')
        return False
    
    return True

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not check_admin_session():
        return redirect(url_for('main'))
    total_users = users_collection.count_documents({})
    total_tasks = tasks_collection.count_documents({})
    return render_template(admin_template, total_users=total_users, total_tasks=total_tasks)

@app.route('/admin/users', methods=['POST','GET'])
def admin_users():
    if not check_admin_session():
        return redirect(url_for('main'))
    if request.method == 'POST':
        user_name = request.form.get('username')
        user_password = request.form.get('password')

        if not user_name or not user_password:
            flash('Fields cannot be empty', 'error')
            return redirect(url_for('admin_users'))
        else:
            hasher = hashlib.shake_256()
            hasher.update(user_password.encode("utf-8"))
            hashed_password = hasher.digest(32)

            existing_user = users_collection.find_one({"$or": [{"username": user_name}]})

            if existing_user:
                flash(f'User {user_name} already exists', 'error')
                return redirect(url_for('admin_users'))
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {
                    "created": timestamp,
                    "username": user_name,
                    "password": hashed_password,
                    "admin": 0,
                    "tasks": 0
                }
                users_collection.insert_one(data)
                flash(f'User {user_name} added successfully', 'success')
                return redirect(url_for('admin_users'))

    page = int(request.args.get('page', 1))
    per_page = 5
    total_users = users_collection.count_documents({})
    total_pages = ceil(total_users / per_page)
    offset = (page - 1) * per_page
    
    users = list(users_collection.find({}, {"password": 0}).skip(offset).limit(per_page))

    return render_template('administration/admin_users.html', users=users, total_pages=total_pages, page=page)

@app.route('/admin/edit_user/<user_id>', methods=['POST', 'GET'])
def admin_edit_user(user_id):
    if not check_admin_session():
        return redirect(url_for('main'))
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        admin_status = request.form.get("admin")
        if user:
            hasher = hashlib.shake_256()
            hasher.update(password.encode("utf-8"))
            hashed_password = hasher.digest(32)
            update_query = {}
            if username:
                update_query["username"] = username
            if password:
                update_query["password"] = hashed_password
            if admin_status is not None:
                update_query["admin"] = int(admin_status)
            if update_query:
                users_collection.update_one({"_id": user["_id"]}, {"$set": update_query})
                flash('User successfully updated', 'success')
                return redirect(url_for('admin_users'))
            else:
                flash('No fields provided for update', 'error')
                return redirect(url_for('admin_users'))

    return render_template(admin_edit_user_template, user=user)

@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    if not check_admin_session():
        return redirect(url_for('main'))
    delete_user = request.form.get("deleteUser")
    if delete_user:
        result = users_collection.delete_one({"_id": ObjectId(delete_user)})
        if result.deleted_count == 1:
            flash("User deleted succefully", "success")
        else:
            flash("Error deleting user", "error")
    else:
        flash("Invalid request", "error")
    
    return redirect(url_for('admin_users'))

@app.route('/add_task', methods=['POST'])
def add_task():
    taskName = request.form.get("taskName")
    taskDescription = request.form.get("taskDescription")
    taskStatus = request.form.get("status")
    dueTo = request.form.get("dueTo")
    
    if dueTo:
        try:
            dueTo_datetime = datetime.fromisoformat(dueTo.replace("T", " "))
        except ValueError:
            flash('Invalid due date format', 'error')
            return redirect(url_for('main'))
    else:
        dueTo_datetime = None

    if "username" not in session:
        flash('You must login first', 'error')
    elif not taskName or not taskDescription:
        flash('Fields cannot be empty', 'error')  
    else:
        data = {
            "Username": session['username'],
            "Name": taskName,
            "Description": taskDescription,
            "Status": taskStatus,
            "DueTo": dueTo_datetime.strftime("%Y-%m-%d %H:%M") if dueTo_datetime else None
        }
        tasks_collection.insert_one(data)
        users_collection.update_one({"username": session['username']}, {"$inc": {"tasks": 1}})
        flash("Task added succefully", "success")

    return redirect(url_for("main"))

@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_id = request.form.get("task_id")
    if task_id:
        result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count == 1:
            flash("Task deleted succefully", "success")
            users_collection.update_one({"username": session['username']}, {"$inc": {"tasks": -1}})
        else:
            flash("Error deleting task.", "error")
    else:
        flash("Invalid request.", "error")
    
    return redirect(url_for("main"))

@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    if task:
        if request.method == 'POST':
            task_name = request.form.get("taskName")
            task_description = request.form.get("taskDescription")
            task_status = request.form.get("status")
            tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"Name": task_name, "Description": task_description, "Status": task_status}})
            flash("Task updated successfully", "success")
            return redirect(url_for("main"))
        return render_template("edit_task.html", task=task)
    else:
        flash("Task not found", "error")
        return redirect(url_for("main"))

if __name__ == "__main__":
    app.run(port=5001,debug=True)