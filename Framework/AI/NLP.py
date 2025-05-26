from pathlib import Path
import os
from Framework.Utilities import CommonUtil

print(os.path.abspath(__file__))

AI_dir = Path(os.path.abspath(__file__).split("AI")[0])/"AI"
models_dir = AI_dir/"models"
facebook_bart_model_file = models_dir/"Facebook-birt-pos-neg-sentiment.sav"

AI_dir = str(AI_dir)
models_dir = str(models_dir)
facebook_bart_model_file = str(facebook_bart_model_file)


def binary_classification(message:str, labels: list, confidence:float=0.6, hypothesis_template:str="The sentiment of this review is {}."):
    from transformers import pipeline
    classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
    prediction = classifier(message, labels, hypothesis_template=hypothesis_template, multi_label=True)
    score = prediction["scores"][0]
    if score >= confidence:
        CommonUtil.ExecLog("[Facebook-Bart]", f'"{message}" got {round(score,4)} score on "{labels[0]}" category', 1)
        return {"status": "passed"}
    else:
        CommonUtil.ExecLog("[Facebook-Bart]", f'"{message}" got {round(score,4)} score on "{labels[0]}" category', 3)
        return {"status": "zeuz_failed"}


def category_score(message:str, label: str, hypothesis_template:str="The sentiment of this review is {}."):
    from transformers import pipeline
    classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
    prediction = classifier(message, [label], hypothesis_template=hypothesis_template, multi_label=True)
    score = prediction["scores"][0]
    CommonUtil.ExecLog("[Facebook-Bart]", f'"{message}" got {round(score,4)} score on "{label}" category', 1)
    return {"score": score}


if __name__ == "__main___":
    pass