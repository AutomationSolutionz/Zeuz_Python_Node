from nltk.sentiment.util import mark_negation
from nltk.sentiment import SentimentIntensityAnalyzer

# Define the two sentences to compare
sentence1 = "you have logged in to your account successfully"
sentence2 = "verification failed"

# Apply negation handling to the sentences
sentence1_neg = mark_negation(sentence1.split())
sentence2_neg = mark_negation(sentence2.split())

# Compute the sentiment polarities of the sentences
sia = SentimentIntensityAnalyzer()


messages = [
    "Authentication passed",
    "you have successfully logged in",
    "you could log in",
    "login success",
    "Credentials matched",
    "login successful",
    "Login Failed",
    "You could not login",
    "Login unsuccessful",
    "Credentials did not match",
    "Credentials mismatched"
]

polarity1 = sia.polarity_scores(" ".join(sentence1_neg))['compound']
polarity2 = sia.polarity_scores(" ".join(sentence2_neg))['compound']

