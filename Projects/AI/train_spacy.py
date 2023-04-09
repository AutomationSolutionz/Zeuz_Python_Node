import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import pandas as pd
from spacy.pipeline.textcat import DEFAULT_SINGLE_TEXTCAT_MODEL
reviews=pd.read_csv("https://raw.githubusercontent.com/hanzhang0420/Women-Clothing-E-commerce/master/Womens%20Clothing%20E-Commerce%20Reviews.csv")

# Extract desired columns and view the dataframe
reviews = reviews[['Review Text','Recommended IND']].dropna()
reviews.head(10)

# Import spaCy ,load model
import spacy
nlp=spacy.load("en_core_web_sm")
print(nlp.pipe_names)

# Adding the built-in textcat component to the pipeline.
# textcat=nlp.create_pipe( "textcat")
textcat = nlp.add_pipe("textcat", last=True)
print(nlp.pipe_names)

# Adding the labels to textcat
textcat.add_label("POSITIVE")
textcat.add_label("NEGATIVE")

# Converting the dataframe into a list of tuples
reviews['tuples'] = reviews.apply(lambda row: (row['Review Text'],row['Recommended IND']), axis=1)
train =reviews['tuples'].tolist()
print(train[:10])

import random
def load_data(limit=0, split=0.8):
    train_data=train
    # Shuffle the data
    random.shuffle(train_data)
    texts, labels = zip(*train_data)
    # get the categories for each review
    cats = [{"POSITIVE": bool(y), "NEGATIVE": not bool(y)} for y in labels]

    # Splitting the training and evaluation data
    split = int(len(train_data) * split)
    return (texts[:split], cats[:split]), (texts[split:], cats[split:])

n_texts=23486

# Calling the load_data() function
(train_texts, train_cats), (dev_texts, dev_cats) = load_data(limit=n_texts)

# Processing the final format of training data
train_data = list(zip(train_texts,[{'cats': cats} for cats in train_cats]))
print(train_data[:10])


def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 0.0  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 0.0  # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if label == "NEGATIVE":
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.0
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.0
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision + recall) == 0:
        f_score = 0.0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {"textcat_p": precision, "textcat_r": recall, "textcat_f": f_score}


#("Number of training iterations", "n", int))
n_iter=10

from spacy.util import minibatch, compounding

# Disabling other components
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']
for name in other_pipes:
    nlp.disable_pipes(name)  # only train textcat
optimizer = nlp.initialize()

print("Training the model...")
print('{:^5}\t{:^5}\t{:^5}\t{:^5}'.format('LOSS', 'P', 'R', 'F'))

# Performing training
for i in range(n_iter):
    losses = {}
    batches = minibatch(train_data, size=compounding(4., 32., 1.001))
    for batch in batches:
        texts, annotations = zip(*batch)
        nlp.update(texts, annotations, sgd=optimizer, drop=0.2,
                   losses=losses)

  # Calling the evaluate() function and printing the scores
    with textcat.model.use_params(optimizer.averages):
        scores = evaluate(nlp.tokenizer, textcat, dev_texts, dev_cats)
    print('{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}'
          .format(losses['textcat'], scores['textcat_p'],
                  scores['textcat_r'], scores['textcat_f']))


# Testing the model
test_text="I hate this dress"
doc=nlp(test_text)
print(doc.cats)

print()
print()