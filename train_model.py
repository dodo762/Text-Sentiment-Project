#Used to read and manage CSV dataset
import pandas as pd
#Import train-test split(divide into training and testing data)
from sklearn.model_selection import train_test_split
#For TF-IDF vectorization of text data(Converting text into numerical features)
from sklearn.feature_extraction.text import TfidfVectorizer
#For training the logistic regression model
from sklearn.linear_model import LogisticRegression
#For evaluating the model performance
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
#For training the linear SVM model
from sklearn.svm import LinearSVC

#Load the dataset
df = pd.read_csv("Twitter_Data.csv")

#Keep only the required columns(clean_Text = input feature, category = target label)
df = df[["clean_text", "category"]]

#Remove records with missing text or missing sentiment labels
df = df.dropna(subset=["clean_text", "category"])

#Convert the sentiment labels into integers(Exp: -1.0 -> -1)
df["category"] = df["category"].astype(int)

#Separate the input text and output labels
X = df["clean_text"]
y = df["category"]

#Split the dataset into 80% training data and 20% testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    #20% for testing, 80% for training
    test_size= 0.20,
    #same split is produced everytime when run the code
    random_state= 42,
    #keep approximately same proportion of negative, neutral, and positive records in both sets
    stratify= y
)

print("Total valid records:", len(df))
print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("\nTraining label distribution:")
print(y_train.value_counts())

print("\nTesting label distribution:")
print(y_test.value_counts())

tfidf = TfidfVectorizer(
    #Limit the number of features to 50,000 most important words
    max_features=50000,
    #Consider both single words and pairs of consecutive words(1-grams and 2-grams)Exp: happy, not happy
    ngram_range=(1, 2),
    #Ignore words that appear in less than 2 documents
    min_df=2,
    #Ignore words that appear in more than 95% of the documents
    max_df=0.95
)

#Learn vocabulary and word importancefrom the training text and convert training text into numbers
X_train_tfidf = tfidf.fit_transform(X_train)

#Convert testing text using the same learned vocabulary(convert training sentences into numerical vectors)
#Not use fit_transform() on testing data because it will learn new vocabulary from testing data which is not present in training data
X_test_tfidf = tfidf.transform(X_test)

print("\nTF-IDF conversion completed.")
print("Training feature shape:", X_train_tfidf.shape)
print("Testing feature shape:", X_test_tfidf.shape)

#Step 3: Logistic regression model training
logistic_model = LogisticRegression(
    #perform up to 1000 iterations to find a suitable solution(if value too small, may cause model stop before fully finish learning process)
    max_iter=1000,
    random_state=42
)

#Train model using TF-IDF training data
print("\nTraining the logistic regression model...")

#model get numerical TF-IDF features and correct sentiment labels
logistic_model.fit(X_train_tfidf, y_train)

print("Logistic regression training completed.")

#Step 4: Model evaluation
#Predict sentiment labels for the testing data 
y_pred = logistic_model.predict(X_test_tfidf)

#Calculate overall accuracy 
accuracy = accuracy_score(y_test, y_pred)

print("\nLogistic Regression Model Evaluation")
print("Accuracy:", accuracy)

#Display precision, recall, F1-score for each sentiment class
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        labels=[-1, 0, 1],
        target_names=["Negative", "Neutral", "Positive"],
        digits=4
    )
)

#Display confusion matrix to show how many records were correctly or incorrectly classified for each sentiment class
print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        y_pred,
        labels=[-1, 0, 1]
    )
)

#Step 5: Linear SVM model training
#Create linear SVM model
svm_model = LinearSVC(
    random_state=42,
)

print("\nTraining the linear SVM model...")

svm_model.fit(X_train_tfidf, y_train)

print("Linear SVM training completed.")

#Predict testing data 
svm_pred = svm_model.predict(X_test_tfidf)

#Calculate accuracy 
svm_accuracy = accuracy_score(y_test, svm_pred)

print("\nLinear SVM Model Evaluation")
print("Accuracy:", svm_accuracy)

#Display classification report for linear SVM model
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        svm_pred,
        labels=[-1, 0, 1],
        target_names=["Negative", "Neutral", "Positive"],
        digits=4
    )
)

#Display confusion matrix for linear SVM model
print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        svm_pred,
        labels=[-1, 0, 1]
    )
)