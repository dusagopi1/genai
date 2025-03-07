from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://dusagopi1:dusagopi1@cluster0.cjpnc.mongodb.net/codellama?retryWrites=true&w=majority"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Define MongoDB Schema for Users
def create_users_collection():
    # Check if 'users' collection already exists
    existing_collections = mongo.db.list_collection_names()
    if "users" not in existing_collections:
        mongo.db.create_collection("users", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["email", "password", "created_at", "is_active"],
                "properties": {
                    "email": {
                        "bsonType": "string",
                        "pattern": "^.+@.+\\..+$",
                        "description": "Must be a valid email address"
                    },
                    "password": {
                        "bsonType": "string",
                        "minLength": 8,
                        "description": "Password must be hashed"
                    }                    
                }
            }
        })
        print("✅ Users collection created with schema validation!")
    else:
        print("⚠️ Users collection already exists, skipping creation.")
# Home Route
@app.route('/')
def home():
    return render_template('login.html')

# Register Route
@app.route('/register', methods=['GET'])
def register_pa():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.form  # Use request.form for HTML form data
        print("Received Data:", data)  # Debugging

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True
        }

        mongo.db.users.insert_one(user_data)

        return redirect("/")  # Redirect to login page after registration

    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 500

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = mongo.db.users.find_one({"email": email})
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])  # Store user ID in session
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")

    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')
# Dashboard Route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Run the function to ensure the schema exists
    create_users_collection()
    app.run(debug=True)
