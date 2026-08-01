#Used to read and manage CSV dataset
import pandas as pd
#Import train-test split(divide into training and testing data)
from sklearn.model_selection import train_test_split

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