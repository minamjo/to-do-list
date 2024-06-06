from flask import Flask, render_template, request, redirect,url_for

import os

import openai


app = Flask(__name__,template_folder="templates")
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    if len(todo_list) == len(action_list):
        action_list[id]['done']=not action_list[id]['done']
    return redirect(url_for('index'))

@app.route("/check_step/<int:id>")
def check_step(id):
    action_list[id]['done']=not action_list[id]['done']
    if len(action_list) == len(todo_list):
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
    if len(action_list) != len(todo_list):
        action_list.clear()
        for i in range(len(todo_list)):
            act_dict = dict()
            task_gen = todo_list[i]['task']
            system_msg ="You are an assistant that helps generate action steps for given tasks."
            msgs = f"suggest three action steps to take for {task_gen}."
          #  messages = system_msg+msgs
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=[{"role":"system","content":system_msg},
                                                        {"role":"user", "content":msgs}],
                                            temperature=0.7
                                            )
            act_dict['task']= todo_list[i]['task']
            act_dict['action'] = response["choices"][0]['message']['content']
            act_dict['done']= todo_list[i]['done']
        
            action_list.append(act_dict)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)