import joblib
from pathlib import Path

# Define the base directory for the model files
BASE_DIR = Path(__file__).resolve().parent

VECTORIZER_PATH = BASE_DIR / "model" / "tfidf_vectorizer.joblib"
MODEL_PATH = BASE_DIR / "model" / "sentiment_model.joblib"

#Load the saved TF-IDF vectorizer and calibrated SVM model
tfidf = joblib.load(VECTORIZER_PATH)
sentiment_model = joblib.load(MODEL_PATH)

SENTIMENT_NAMES = {
    -1: "Negative",
    0: "Neutral",
    1: "Positive"
}


def predict_sentiment(text: str) -> dict:
    #Clean the input text by removing leading and trailing whitespace
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("Text input cannot be empty.")

    text_tfidf = tfidf.transform([cleaned_text])

    predicted_label = int(
        sentiment_model.predict(text_tfidf)[0]
    )

    probabilities = sentiment_model.predict_proba(
        text_tfidf
    )[0]

    probability_results = {
        SENTIMENT_NAMES[int(label)]: round(
            float(probability) * 100,
            2
        )
        # Map each class label to its corresponding sentiment name and probability
        for label, probability in zip(
            sentiment_model.classes_,
            probabilities
        )
    }

    predicted_sentiment = SENTIMENT_NAMES[predicted_label]

    return{
        "text": cleaned_text,
        "label": predicted_label,
        "sentiment": predicted_sentiment,
        "confidence": probability_results[predicted_sentiment],
        "probabilities": probability_results
    }

#Test service before adding Flask(temporary use)
if __name__ == "__main__":
    result = predict_sentiment(
        "I feel calm and hopeful today"
    )

    print(result)