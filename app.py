from flask import Flask, render_template, request, redirect,url_for

import os

import openai
from db import DB

app = Flask(__name__,template_folder="templates")
openai.api_key = os.getenv("OPENAI_API_KEY")

# username and password hidden
db = DB(
	host="localhost",
	port=3306,
	user=,
	password=,
	database="db_todo",
)


todo_list = db.select('tasks', [], {}, True)


action_list = db.select('action_steps', [], {}, True)

@app.route("/")
def index():
    todo_list = db.select('tasks', [], {}, True)
    action_list = db.select('action_steps', [], {}, True)
    return render_template("index.html",todo_list=todo_list,action_list=action_list,action_len=len(action_list))

@app.route("/add",methods=["POST"])
def add():
    todo = request.form['todo']
    db.insert('tasks',{'task':todo,'complete':False})
    return redirect(url_for("index"))

@app.route("/check/<int:id>")
def check(id):
    todo_list = db.select('tasks', [], {}, True)

    taskId = todo_list[id]['task_id']
    task = todo_list[id]
    if task:
        if task['complete'] == 0:
            db.update('tasks',{"complete":True},{"task_id":taskId})
        else:
            db.update('tasks', {"complete": False}, {"task_id": taskId})
    return redirect(url_for('index'))

@app.route("/check_step/<int:id>")
def check_step(id):
    action_list = db.select('action_steps',[],{},True)
    action = action_list[id]
    if action:
        if action['complete'] == 0:
            db.update('action_steps', {"complete": True}, {"action_id":action['action_id']})
        else:
            db.update('action_steps', {"complete": False}, {"action_id": action['action_id']})
    return redirect(url_for('index'))

@app.route("/delete/<int:id>")
def delete(id):
    todo_list = db.select('tasks', [], {}, True)
    taskId = todo_list[id]['task_id']

    db.delete('tasks',{'task_id':taskId})
    return redirect(url_for("index"))

@app.route("/delete_step/<int:id>")
def delete_step(id):
    action_list = db.select('action_steps', [], {}, True)
    actionId = action_list[id]['action_id']
    db.update('tasks',{'action_id':None},{'action_id':actionId})
    db.delete('action_steps',{'action_id':actionId})
    return redirect(url_for("index"))

@app.route("/generate_action")
def generate_action():
    todo_list = db.select('tasks', [], {}, True)

    for i in range(len(todo_list)):

        if not todo_list[i]['action_id']:
            task_gen = todo_list[i]['task']
            system_msg = "You are an assistant that helps generate action steps for given tasks."
            msgs = f"suggest three action steps to take for {task_gen}."

            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=[{"role": "system", "content": system_msg},
                                                              {"role": "user", "content": msgs}],
                                                    temperature=0.7,
                                                    max_tokens=100
                                                    )

            db.insert('action_steps', {'task_id':todo_list[i]['task_id'],
                                       'next_steps': response["choices"][0]['message']['content'],
                                       'complete':False, 'task':task_gen})
            actionId = db.select('action_steps', ['action_id'], {'task_id':todo_list[i]['task_id']}, False)['action_id']
            db.update('tasks', {'action_id': actionId},{'task_id': todo_list[i]['task_id']})



    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)