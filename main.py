from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://missions:acceptit@localhost:8889/missions"
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "#decoderring"

db = SQLAlchemy(app)

class Mission(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    done = db.Column(db.Boolean)
    owner = db.Column(db.Integer, db.ForeignKey('agent.id'))

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.done = False

class Agent(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    mission = "db.relationship('Mission', backref='owner')"

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route("/", methods=["GET", "POST"])
def index():
    owner = Agent.query.filter_by(email=session["email"]).first()
    if request.method == "POST":
        mission = str(request.form["mission"])
        print(mission,owner.id)
        new_mission = Mission(mission,(owner.id))
        db.session.add(new_mission)
        db.session.commit()
    missions = Mission.query.filter_by(done=False,owner=owner.id).all()
    done_missions = Mission.query.filter_by(done=True,owner=owner.id).all()
    return render_template('missions.html',Title = "Mission Log", missions=missions, done=done_missions, email=session['email'])

@app.route('/delete-mission', methods=['POST'])
def delete_task():

    mission_id = int(request.form['mission-id'])
    mission = Mission.query.get(mission_id)
    mission.done = True
    db.session.add(mission)
    db.session.commit()

    return redirect('/')

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return render_template("login.html", Title="Agent Terminal")

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = (request.form["email"]).lower()
        password = request.form["pass1"]
        agent = Agent.query.filter_by(email=email).first()
        if agent and agent.password == password:
            session['email'] = email
            flash("ACCESS GRANTED","success")
            return redirect("/")
        else:
            flash('ACCESS DENIED',"error")
            return redirect("/login")
    else:
        return render_template("login.html", Title="Agent Terminal")

@app.route('/logout', methods=['GET'])
def logout():
    del session['email']
    return redirect('/')

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = (request.form["email"]).lower()
        password = request.form["pass1"]
        passwordv = request.form["pass2"]
        if password != passwordv or (len(password)<3 or len(password) >20):
            flash("ERROR: CODEPHRASE", "error")
            return render_template("register.html", Title="Agent Registration")
        existing_agent = Agent.query.filter_by(email=email).first()
        if not existing_agent:
            new_agent = Agent(email,password)
            db.session.add(new_agent)
            db.session.commit()
            session['email'] = email
            flash("Agent Accepted","success")
            return render_template("login.html", Title="Agent Terminal", email=email)
        else:
            flash("ERROR: DOUBLE AGENT","error")
            return render_template("register.html", Title="Agent Registration")
    return render_template("register.html", Title="Agent Registration")

if __name__ == "__main__":
    app.run()
