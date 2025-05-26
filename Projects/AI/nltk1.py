import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))


def preprocess(sentence):
    # Tokenize the sentence into words
    words = word_tokenize(sentence)
    words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]

    return ' '.join(words)


def similarity(sentence1, sentence2):
    # Preprocess the two sentences
    sentence1 = preprocess(sentence1)
    sentence2 = preprocess(sentence2)

    # Create a set of unique words in both sentences
    words = set(sentence1.split() + sentence2.split())

    # Create frequency vectors for the two sentences
    vector1 = [sentence1.split().count(word) for word in words]
    vector2 = [sentence2.split().count(word) for word in words]

    # Calculate the cosine similarity between the two frequency vectors
    dot_product = sum([vector1[i] * vector2[i] for i in range(len(vector1))])
    magnitude1 = sum([vector1[i] * 2 for i in range(len(vector1))]) * 0.5
    magnitude2 = sum([vector2[i] * 2 for i in range(len(vector2))]) * 0.5
    cosine_similarity = dot_product / (magnitude1 * magnitude2)

    # Return the cosine similarity
    return cosine_similarity


# Example usage
sentence1 = "you could successfully log in"
sentence2 = "you have successfully logged in"

similarity_score = similarity(sentence1, sentence2)

if similarity_score > 0.5:
    print("The sentences are similar.")
else:
    print("The sentences are not similar.")