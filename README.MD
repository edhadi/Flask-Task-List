
# Flask Task-List

This is a simple Task/To-Do list web application built using Flask.  Unlike many task list applications, this one doesn't rely on JavaScript for functionality, making it lightweight and easy to understand.



## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation and Usage](#installation-and-usage)
- [Screenshots](#screenshots)

## Features

- **Add Tasks**: Easily add tasks to your to-do list.
- **Status**: Categorize tasks as Not Started, In Progress, or Done for better organization.
- **Due To**: Set up a deadline for your task (optional) to help prioritize your workload.
- **Edit Task**: Modify task details such as title, description, status, and due date.
- **Delete Task**: Remove tasks from your list when they're no longer needed.


## Technologies Used

- **Flask**: A lightweight WSGI web application framework in Python.
- **HTML/CSS**: For the structure and styling of the web pages.
- **MongoDB**: A NoSQL database used to store task data.
## Installation and Usage

Before running this application, ensure you have the following dependencies installed:

- **Python 3.x**: The application is built using Python 3.x. You can download and install Python from the [official website](https://www.python.org).
- **MongoDB Atlas Setup**:
    - Sign up for a free account on [MongoDB Atlas](https://www.mongodb.com).
    - Create a new cluster by following the instructions provided in the MongoDB Atlas dashboard.
    - Once your cluster is created, click on "Connect" to configure your connection settings.
    - Choose "Connect Your Application" to get your connection string. Select the appropriate driver and version (e.g., Python and the latest version).

1.  **Clone this repository to your local machine**:
```bash
  git clone https://github.com/edhadi/Flask-Task-List.git
```
2. **Navigate to the project directory**:
```bash
  cd Flask-Task-List
```
3. **Install the Python dependencies**:
```bash
  pip install -r requirements.txt
```
4. **.env File Configuration**:
- Create **.env** file in your text editor and update the placeholders with your MongoDB connection details and application secret key:
```bash
MONGO_URL = YOUR_MONGO_URL
MONGO_USERNAME = YOUR_MONGO_USERNAME
MONGO_PASSWORD = YOUR_MONGO_PASSWORD
Database = YOUR_DATABASE_NAME
Collection = YOUR_COLLECTION_NAME
SECRET_KEY = APP_SECRET_KEY
```
5. **Run the application**
- **Windows**:
```bash
python app.py
```
- **Mac**:
```bash
python3 app.py
```
## Screenshots

![App Screenshot](https://github.com/edhadi/rau-projects/blob/main/Image%201.png?raw=true)

![App Screenshot](https://github.com/edhadi/rau-projects/blob/main/image%202.png?raw=true)

![App Screenshot](https://github.com/edhadi/rau-projects/blob/main/image%203.png?raw=true)
