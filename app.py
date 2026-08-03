#Flask: create web application, render_template: display HTML page, request: read data submit by user
from flask import Flask, render_template, request 
#import own prediction function
from sentiment_service import predict_sentiment

#Create the Flask application
app = Flask(__name__)

#Create home route, / = home page, GET = open page, POST = submit text for prediction
@app.route("/", methods=["GET", "POST"])
def index():
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
        "index.html",
        result=result,
        error_message=error_message
    )

if __name__ == "__main__":
    app.run(debug=True)