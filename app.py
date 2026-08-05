#For login-required decorator, to protect certain routes from being accessed by unauthenticated users
from functools import wraps
#Flask: create web application, render_template: display HTML page, request: read data submit by user
from flask import (
    Flask,
    #to display message to user 
    flash,
    #to redirect user to another page
    redirect,
    #to display HTML page
    render_template, 
    #to read data submit by user
    request,
    #to store user session data
    session,
    url_for
)
#MySQL: connect to MySQL database, Error: handle database errors, IntegrityError: handle unique constraint errors
from mysql.connector import Error, IntegrityError
#hash password for secure storage
from werkzeug.security import (
    #to check if password match with hashed password in database
    check_password_hash,
    #to hash password for secure storage
    generate_password_hash
)
from database import get_database_connection 
#import own prediction function
from sentiment_service import predict_sentiment

#Create the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "fyp-development-secret-key"  #Own secret key

def login_required(view_function):
    #Decorator to protect routes that require user authentication
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        #Check if the user currently is logged in 
        if "user_id" not in session:
            flash(
                "Please log in to access this page.",
                "error"
            )
            #redirect to login page if user is not logged in
            return redirect(url_for("login"))
        #to allow the original view function to be called if the user is logged in
        return view_function(*args, **kwargs)

    return wrapped_view

#App currently have two routes(home page and sentiment analysis page)
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    #to prevent logged in user from accessing register page, redirect to home page
    if "user_id" in session:
        return redirect(url_for("home"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        #Validate empty fields
        if not username or not email or not password or not confirm_password:
            flash("Please complete all fields.", "error")
            return render_template("register.html")

        #Validate username length
        if len(username) < 3 or len(username) > 50:
            flash(
                "Username must contain between 3 and 50 characters.",
                "error"
            )
            return render_template("register.html")

        #Perform a email format check 
        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        #Validate password length
        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "error"
            )
            return render_template("register.html")

        #Check matching passwords
        if password != confirm_password:
            flash("The passwords do not match.", "error")
            return render_template("register.html")

        #Hash the password for secure storage(database not have mypassword123, would have long encoded hash)
        password_hash = generate_password_hash(password)

        connection = get_database_connection()

        if connection is None:
            flash(
                "The application could not connect to the database.",
                "error"
            )
            return render_template("register.html")

        cursor = None

        try:
            cursor = connection.cursor()

            insert_user_query = """
                INSERT INTO users(
                    username, 
                    email,
                    password_hash
                )
                -- Specify the columns for clarity
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                insert_user_query,
                (
                    username,
                    email,
                    password_hash
                )
            )
            #Save new record into database, if not commit, record will not be saved
            connection.commit()

            flash(
                "Your account was created successfully. Please log in.",
                "success"
            )

            return redirect(url_for("login"))

        except IntegrityError:
            connection.rollback()

            flash(
                "That username or email address is already registered.",
                "error"
            )

        except Error as error:
            connection.rollback()

            print("Registration database error:", error)

            flash(
                "Account registration failed. Please try again.",
                "error"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if connection.is_connected():
                connection.close()

    return render_template("register.html")

#Step 4: Add login route to receive both page visits and form submissions 
@app.route("/login", methods=["GET", "POST"])
def login():
    #to prevent logged in user from accessing login page, redirect to home page
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        #Read username or email 
        login_identifier = request.form.get("login_identifier", "").strip() 
        #Read password 
        password = request.form.get("password", "")

        #check if username/email and password are provided
        if not login_identifier or not password:
            flash(
                "Please enter your username or email and password.",
                "error"
            )

            return render_template("login.html")

        connection = get_database_connection()

        if connection is None:
            flash(
                "The application could not connect to the database.",
                "error"
            )
            return render_template("login.html")

        cursor = None 

        try:
            #Create a cursor that returns database rows as dictionaries
            cursor = connection.cursor(dictionary=True)

            find_user_query = """
                SELECT id, username, email, password_hash
                FROM users
                -- Allow user login using either username or email
                WHERE username = %s OR email = %s
                -- Tell the database to return only one record, since username and email are unique
                LIMIT 1
            """

            cursor.execute(
                find_user_query,
                (
                    login_identifier,
                    login_identifier.lower()
                )
            )

            #Read the matching user from database, if no matching user, user will be None
            user = cursor.fetchone()

            if user is None:
                flash(
                    "Invalid username, email, or password.",
                    "error"
                )
                return render_template("login.html")

            #return either true or false, if password match with hashed password in database
            password_is_correct = check_password_hash(
                user["password_hash"],
                password
            )

            #error message if password is incorrect 
            if not password_is_correct:
                flash(
                    "Invalid username, email, or password.",
                    "error"
                )
                return render_template("login.html")

            #Remove any old session data before creating a new login session 
            session.clear() 

            #Store user information in the session to keep the user logged in
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash(
                f"Welcome back, {user['username']}!",
                "success"
            )

            return redirect(url_for("home"))

        except Error as error:
            print("Login database error:", error)

            flash(
                "Login failed because of a database error.",
                "error"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if connection.is_connected():
                connection.close()
            
    return render_template("login.html")
            

#Step 4.7: Add logout functionality 
@app.route("/logout")
def logout():
    #Remove user information from the session to log the user out
    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("home"))

#Create home route, / = home page, GET = open page, POST = submit text for prediction
@app.route("/analysis", methods=["GET", "POST"])
#Add login_required decorator to protect the analysis route, only allow logged in user to access
@login_required
def analysis():
    result = None
    error_message = None

    if request.method == "POST":
        #Read submitted text
        user_text = request.form.get("user_text", "").strip()

        if not user_text:
            error_message = "Please enter some text before analysing."
        else: 
            try:
                #Call model to predict
                result = predict_sentiment(user_text)
            except Exception as error:
                error_message = f"Prediction failed: {error}"

    return render_template(
        "analysis.html",
        result=result,
        error_message=error_message
    )

if __name__ == "__main__":
    app.run(debug=True)