import joblib

#Load the saved TF-IDF vectorizer
tfidf = joblib.load(
    "model/tfidf_vectorizer.joblib"
)

#Load the saved calibrated SVM model
sentiment_model = joblib.load(
    "model/sentiment_model.joblib"
)

#Convert numerical labels into readable names
sentiment_names = {
    -1: "Negative",
    0: "Neutral",
    1: "Positive"
}

def predict_sentiment(text):
    #Convert the new text using the saved vectorizer
    text_tfidf = tfidf.transform([text])

    #Predict the sentiment label
    predicted_label = sentiment_model.predict(text_tfidf)[0]

    #Get probabilities for every class 
    probabilities = sentiment_model.predict_proba(text_tfidf)[0]

    #Find the probability of the predicted class
    class_list = list(sentiment_model.classes_)
    predicted_index = class_list.index(predicted_label)
    confidence = probabilities[predicted_index]

    return{
        "text": text,
        "label": int(predicted_label),
        "sentiment": sentiment_names[predicted_label],
        "confidence": float(confidence),
        "probabilities": {
            sentiment_names[int(label)]: float(probability)
            for label, probability in zip(
                sentiment_model.classes_,
                probabilities
            )
        }
    }

#Test the saved model
test_text = "I am feeling stressed and disappointed today"

result = predict_sentiment(test_text)

print("Text:", result["text"])
print("Predicted sentiment:", result["sentiment"])
print(
    "Confidence:",
    f'{result["confidence"] * 100:.2f}%'
)

print("All probabilities:")

for sentiment, probability in result["probabilities"].items():
    print(
        f"{sentiment}: {probability * 100:.2f}%"
    )