from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3


app = Flask(__name__)
app.secret_key = 'dummyCreds123'
db_name = "users.db"

# Database handlers
def get_user_password(user_email)->str:
    # get password for a username based on email id
    db_connect = sqlite3.connect(db_name)

    with db_connect as conn:
        cursor = conn.cursor()
        # get user password
        cursor.execute("SELECT password FROM Users WHERE email = ?", (user_email,))
    return cursor.fetchone()[0]


def check_user_exists(user_email)->bool:
    "Check if user exists in the database"
    
    # create database connection
    db_connect = sqlite3.connect(db_name)

    try:
        with db_connect as conn:
            cursor = conn.cursor()

            # verify if user already exists
            cursor.execute("SELECT 1 FROM Users WHERE email = ?", (user_email,))
            if cursor.fetchone():
                return True
            else:
                return False
    except sqlite3.IntegrityError as e:
        print('SQL integrity error')
        
    

def create_user(user_data: tuple)->str:
    """create user in the database"""

    # fetch email to verify user exists
    user_email = user_data[1]

    # create database connection
    db_connect = sqlite3.connect(db_name)
    try:
        with db_connect as conn:
            cursor = conn.cursor()

            # verify if user already exists
            cursor.execute("SELECT 1 FROM Users WHERE email = ?", (user_email,))
            if cursor.fetchone():
                return 'User exists'
            
            # if new user, insert data into the Users table
            cursor.execute(
                "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",user_data)
            # Commit the transaction
            conn.commit()
            return "User created successfully"
    except sqlite3.IntegrityError as e:
        print(f"Integrity error occurred: {e}")
    except sqlite3.OperationalError as e:
        print(f"Operational error occurred: {e}")


# Routes
@app.route("/")
def index():
    return render_template("index.html", session=session)


@app.route("/debug_session")
def debug_session():
    print(session)
    return "Check your console for session details."


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash("Passwords do not match!")
        return redirect(url_for('index'))
    
    user_data = (name, email, password)
    create_user(user_data)
    
    # flash(create_user_msg)
    return redirect(url_for('index'))


@app.route("/signin", methods=["POST", "GET"])
def signin():
    email = request.form.get('signin_email')
    password = request.form.get('signin_password')
    print(f"Email: {email}, Password: {password}")

    if not email or not password:
        flash("Both email and password are required.", "error")
        return redirect(url_for('home'))

    # Check if user exists
    if check_user_exists(user_email=email):
        db_pwd = get_user_password(user_email=email)
        if db_pwd and password == db_pwd:
            session['username'] = email
            flash("Login successful!", "success")
        else:
            flash("Invalid password.", "error")
    else:
        flash("User does not exist. Please sign up first.", "error")

    return redirect(url_for('home'))

    
@app.route("/home")
def home():
    if 'username' not in session:
        flash("Please log in to access the dashboard.", "info")
        return redirect(url_for('index', next=request.url))
    
    # Render the home page for authenticated users
    return render_template("home.html", session=session)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
