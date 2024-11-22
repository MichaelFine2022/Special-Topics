from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask_SQLAlchemy

from config import app

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def index():
    return render_template('login.html')

@app.route("/signIn",methods=["POST"])
def create_user():
    username = request.json.get("username")
    if not username:
        return jsonify({"message":"Failed"}),400