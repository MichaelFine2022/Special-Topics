from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password 

    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_json(self):
        return{
            "id":self.id,
            "username":self.username,
            "password":self.password,}

#base login page
@app.route('/')
def index():
    return render_template('login.html')

#redirection to signin page
@app.route("/tosignin",methods=["GET"])
def toSignIn():
    return render_template('signin.html')

@app.route("/tologin",methods=["GET"])
def toLogin():
    return render_template('login.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)