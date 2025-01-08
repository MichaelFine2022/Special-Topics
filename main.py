from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'


# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    account_name = db.Column(db.String(150), nullable=False)  
    account_type = db.Column(db.String(50), nullable=False)  
    balance = db.Column(db.Float, nullable=False)  
    currency = db.Column(db.String(10), nullable=False, default="USD")  
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

    transactions = db.relationship('Transaction', backref='data', lazy=True)

    def __repr__(self):
        return f"<Data(account_name='{self.account_name}', balance={self.balance}, currency='{self.currency}')>"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    financial_data_id = db.Column(db.Integer, db.ForeignKey('data.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False) 
    description = db.Column(db.String(200), nullable=True)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  

    def __repr__(self):
        return f"<Transaction(amount={self.amount}, type='{self.transaction_type}', timestamp='{self.timestamp}')>"

# Create the database and tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists','error')
            return render_template('signup.html')
        if User.query.filter_by(email=email).first():
            flash('Email already in use','error')
            return render_template('signup.html')
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Add new user to database
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/reset', methods=["GET", "POST"])
def reset():
    if request.method == 'GET':
        return render_template('reset.html')
    else:
        username = request.form.get('username')
        new_password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash('Password successfully reset.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'error')
            return "User not found."    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check user in database
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/api/graphs/<username>', methods=['GET'])
@login_required
def get_data(username):
    data = Data.query.filter_by(username=username).first_or_404()
    data = data.transactions
    return jsonify(data)

def populate():
    financial_data = Data.query.filter_by(username='admin').first()
    if not financial_data:
        # Creates default financial data for admin
        financial_data = Data(
            username='admin',
            user_id=1,
            account_name="Default Account",
            account_type="Savings",
            balance=420.0,
            currency="USD"
        )
        db.session.add(financial_data)
        db.session.commit()

        # sample transactions for admin
        transactions = [
            Transaction(
                financial_data_id=financial_data.id,
                amount=-50.0,
                transaction_type='Expense',
                description='Groceries'
            ),
            Transaction(
                financial_data_id=financial_data.id,
                amount=100.0,
                transaction_type='Income',
                description='Data Sale'
            ),
        ]
        db.session.add_all(transactions)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate()
    app.run(debug=True)