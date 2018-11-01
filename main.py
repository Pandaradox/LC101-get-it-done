from flask import Flask, redirect, request, render_template
import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True


tasks = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        tasks.append(request.form['task'])
    return render_template('todos.html',Title = "Get It Done", tasks=tasks)

app.run()
