from transformers import pipeline

classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
labels = ["successful", "unsuccessful"]
hypothesis_template = "The sentiment of this review is {}."

from rich.table import Table
from rich.box import SQUARE
from rich.console import Console
rich_print = Console().print
_color = "cyan"
title = "FACEBOOK-BART Result"
table = Table(border_style=_color, title=title, box=SQUARE, min_width=len(title) - 10, width=70)
table.add_column("Message", justify="left", max_width=50)
table.add_column(labels[0], justify="left", max_width=15)
table.add_column(labels[1], justify="left", max_width=15)

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
for message in messages:
    prediction = classifier(message, labels, hypothesis_template=hypothesis_template, multi_label=True)
    print(prediction)
    table.add_row(*[message,str(round(prediction["scores"][prediction["labels"].index(labels[0])],4)),str(round(prediction["scores"][prediction["labels"].index(labels[1])],4))], style=_color)

rich_print(table)
print()