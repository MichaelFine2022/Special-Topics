from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
db = SQLAlchemy(app)
app.secret_key = 'secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password) 

    def __repr__(self):
        return f'<User {self.username}>'
    
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    
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
@app.route("/signin",methods=["GET"])
def toSignIn():
    return render_template('signin.html')

#user authentication handled by flask and getting the login page
@app.route("/login",methods=["GET","POST"])
def Login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to a dashboard or home page after login
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#route to log the user out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#route to get into the main page
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)