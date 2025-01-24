import traceback
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    username = db.Column(db.String(150), unique=True, nullable=False)
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

@app.route('/api/add_transaction/<username>', methods=['POST'])
def add_transaction(username):
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    
    data = request.get_json()

    # Validate incoming data
    description = data.get("description")
    amount = data.get("amount")
    transaction_type = data.get("transaction_type")
    timestamp = data.get("timestamp")

    if not description or not isinstance(amount, (int, float)) or not transaction_type or not timestamp:
        return jsonify({"success": False, "message": "Invalid data"}), 400

    # Create the new transaction
    transaction = {
        "description": description,
        "amount": amount,
        "transaction_type": transaction_type,
        "timestamp": datetime.fromisoformat(timestamp),  
    }
    try:
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        error_message = str(e)
        print("Error while saving transaction:", error_message)  # Log error message for debugging
        print(traceback.format_exc())  # This will print the stack trace
        return jsonify({"success": False, "message": f"Error saving transaction: {error_message}"}), 500


    db.session.add(transaction)
    db.session.commit()
    
    # Return success response
    return jsonify({"success": True, "message": "Transaction added successfully!"}), 200


@app.route('/api/graphs/<username>', methods=['GET'])
def get_data(username):
    user_data = Data.query.filter_by(username=username).first_or_404()
    transactions = user_data.transactions
    return jsonify([{
    'amount': transaction.amount,
    'transaction_type': transaction.transaction_type,
    'description': transaction.description,
    'timestamp': transaction.timestamp.isoformat()
    } for transaction in transactions])
    
    
def populate():
    user = User.query.filter_by(username='admin').first()
    if not user:
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('password', method='pbkdf2:sha256')
        )
        db.session.add(admin_user)
        db.session.commit()
        user_id = admin_user.id
    else:
        user_id = user.id

    financial_data = Data.query.filter_by(user_id=user_id).first()
    if not financial_data:
        # Create default financial data for admin
        financial_data = Data(
            user_id=user_id,
            username=user.username,
            account_name="Default Account",
            account_type="Savings",
            balance=420.0,
            currency="USD"
        )
        db.session.add(financial_data)
        db.session.commit()

        # Add sample transactions for admin
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