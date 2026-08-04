#Flask: create web application, render_template: display HTML page, request: read data submit by user
from flask import (
    Flask, 
    flash,
    redirect,
    render_template, 
    request,
    url_for
)
#MySQL: connect to MySQL database, Error: handle database errors, IntegrityError: handle unique constraint errors
from mysql.connector import Error, IntegrityError
#hash password for secure storage
from werkzeug.security import generate_password_hash 
from database import get_database_connection 
#import own prediction function
from sentiment_service import predict_sentiment

#Create the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "fyp-development-secret-key"  #Own secret key

#App currently have two routes(home page and sentiment analysis page)
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
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

#Step 4: Add temporary login route
@app.route("/login")
def login():
    return render_template("login.html")
            

#Create home route, / = home page, GET = open page, POST = submit text for prediction
@app.route("/analysis", methods=["GET", "POST"])
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