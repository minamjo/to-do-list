from flask import Flask, render_template, request, redirect,url_for
# from dotenv import load_dotenv
import os

import openai


app = Flask(__name__,template_folder="templates")
openai.api_key = os.getenv("OPENAI_API_KEY")
# load_dotenv
todo_list = [{"task": "Study for math test","done":False}]

action_list = []

@app.route("/")
def index():
    return render_template("index.html",todo_list=todo_list,action_list=action_list,action_len=len(action_list))

@app.route("/add",methods=["POST"])
def add():
    todo = request.form['todo']
    todo_list.append({"task":todo, "done":False})
    return redirect(url_for("index"))

@app.route("/check/<int:id>")
def check(id):
    todo_list[id]['done']=not todo_list[id]['done']
    if id < len(action_list):
        action_list[id]['done']=not action_list[id]['done']
    return redirect(url_for('index'))

@app.route("/check_step/<int:id>")
def check_step(id):
    action_list[id]['done']=not action_list[id]['done']
    todo_list[id]['done']=not todo_list[id]['done']
    return redirect(url_for('index'))

@app.route("/delete/<int:id>")
def delete(id):
    del todo_list[id]
    if id < len(action_list):
        del action_list[id]
    return redirect(url_for("index"))

@app.route("/delete_step/<int:id>")
def delete_step(id):
    del action_list[id]
    return redirect(url_for("index"))

@app.route("/generate_action")
def generate_action():
    global action_list
    action_list.clear()
    for i in range(len(todo_list)):
        act_dict = dict()
        response = openai.Completion.create(model="text-davinci-003",
                                        prompt=generate_prompt(todo_list[i]['task']),
                                        temperature=0.6,
                                        max_tokens=200,
                                        top_p=1,
                                        frequency_penalty=0,
                                        presence_penalty=0
                                        )
        act_dict['task'] = response.choices[0].text
        act_dict['done']= todo_list[i]['done']
        act_dict['id']= i
        action_list.append(act_dict)
    return redirect(url_for("index"))

def generate_prompt(task):
    return """Given information about a task, suggest three action steps to take.
Desired Format:
Suggestion 1, suggestion 2, and suggestion 3
Task: Study for a math test
Next Steps: Review notes and class material, Practice math problems related to the topics being tested, and make a study plan and set aside dedicated time to study.
Task: Practice for a job interview
Next Steps: Research the company and potential questions thoroughly, create a list of talking points, and rehearse talking points in front of a mirror or with a friend
Task: Clean the kitchen
Next Steps: Empty the dishwasher, wipe down counters and appliances, and sweep and mop the floor
Task: Train for a marathon
Next Steps: Follow a training plan, increase mileage gradually, and get enough rest and nutrition
Task: {}
Next Steps: """.format(task)


if __name__ == '__main__':
    app.run(debug=True)