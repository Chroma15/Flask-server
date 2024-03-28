from datetime import datetime
import os
from flask import Flask, request
import re

app = Flask(__name__)


@app.route("/task/add", methods=["POST"])
def add():
    task_name = request.form.get("Task", "")

    task_regex = r"^.{1,50}$"
    if not re.match(task_regex, task_name):
        return error("Task too short"), 400

    description = request.form.get("Description", "")
    if len(description) > 200:
        return error("Description is too large (max 200 chars)")

    due_date = request.form.get("DueDate", "")
    try:
        parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError as e:
        return error(str(e)), 400

    if parsed_due_date < datetime.now():
        return error("Date in the past"), 400

    completed = False

    with open("tasks.txt", "a") as fis:
        fis.write(f"{get_next_id()};{task_name};{description};{due_date};{completed}\n")

    return {"success": True}


@app.route("/task/update", methods=["PUT"])
def update():
    task_id = request.form.get("ID", "")
    saved_task = find_task(task_id)

    if not saved_task:
        return error("Task not found"), 404

    task_name = request.form.get("Task", "")

    if task_name:
        task_regex = r"^.{1,50}$"
        if not re.match(task_regex, task_name):
            return error("Task too short"), 400

        saved_task["name"] = task_name

    description = request.form.get("Description", "")
    if description:
        if len(description) > 200:
            return error("Description is too large (max 200 chars)")
        saved_task["description"] = description

    due_date = request.form.get("DueDate", "")

    if due_date:
        try:
            parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError as e:
            return error(str(e)), 400

        if parsed_due_date < datetime.now():
            return error("Date in the past"), 400

        saved_task["due_date"] = due_date

    completed = request.form.get("Completed", "")

    if completed:
        if completed != "True" and completed != "False":
            return error("Completed must be True or False"), 400

        saved_task["completed"] = completed

    update_task_in_file(saved_task)
    return {"success": True}


@app.route("/task/delete", methods=["DELETE"])
def remove():
    if not os.path.exists("tasks.txt"):
        return error("No tasks created")

    task_id = request.form.get("ID", "")
    saved_task = find_task(task_id)

    if not saved_task:
        return error("Task not found"), 404

    remove_task_in_file(task_id)
    return {"success": True}


def update_task_in_file(task):
    updated_content = ""
    with open("tasks.txt", "r") as fis:
        for line in fis.readlines():
            parts = line.split(";")
            current_id = parts[0]
            if task["id"] == current_id:
                task_id = task["id"]
                task_name = task["name"]
                description = task["description"]
                due_date = task["due_date"]
                completed = task["completed"]

                updated_content += (
                    f"{task_id};{task_name};{description};{due_date};{completed}\n"
                )
            else:
                updated_content += line

    with open("tasks.txt", "w") as fis:
        fis.write(updated_content)


def remove_task_in_file(task_id):
    updated_content = ""

    with open("tasks.txt", "r") as fis:
        for line in fis.readlines():
            parts = line.split(";")
            current_id = parts[0]
            if task_id != current_id:
                updated_content += line

    with open("tasks.txt", "w") as fis:
        fis.write(updated_content)


def find_task(task_id):
    with open("tasks.txt", "r") as fis:
        for line in fis.readlines():
            parts = line.split(";")
            current_id = parts[0]
            if task_id == current_id:
                return {
                    "id": parts[0],
                    "name": parts[1],
                    "description": parts[2],
                    "due_date": parts[3],
                    "completed": parts[4].strip(),
                }

    return None


def get_next_id():
    id = 0

    if os.path.exists("id.txt"):
        with open("id.txt", "r") as fis:
            id = int(fis.readline())

    id += 1

    with open("id.txt", "w") as fis:
        fis.write(str(id))

    return id


def error(msg: str):
    return {"success": False, "message": msg}


if __name__ == "__main__":
    app.run(debug=True)
