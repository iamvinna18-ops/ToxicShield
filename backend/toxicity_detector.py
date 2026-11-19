# -*- coding: utf-8 -*-
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Smaller multilingual toxicity model (141M parameters, 34 languages).
MODEL_NAME = "Horizon-Labs/multilingual-toxicity-small"
TOXICITY_THRESHOLD = 0.25

print("Loading ToxicShield multilingual toxicity model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

model.eval()
device = torch.device("cpu")
model.to(device)

# This model uses seven independent labels and sigmoid probabilities.
id2label = model.config.id2label
toxicity_index = next(
    (
        int(index)
        for index, label in id2label.items()
        if str(label).lower() == "toxicity"
    ),
    0,
)


def detect_toxicity(comment):
    """Return ToxicShield's existing category/confidence response format."""
    if not isinstance(comment, str) or not comment.strip():
        return {"category": "Invalid", "confidence": 0.0}

    inputs = tokenizer(
        comment,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.sigmoid(outputs.logits)[0]
    toxicity_score = float(probabilities[toxicity_index].item())

    category = "Toxic" if toxicity_score >= TOXICITY_THRESHOLD else "Non-toxic"

    return {
        "category": category,
        "confidence": round(toxicity_score * 100, 2)
    }


if __name__ == "__main__":
    test_comments = [
        "You are amazing!",
        "I hate you!",
        "Thank you for sharing this video.",
        "This is a terrible and abusive comment.",
        "Eres un inútil, lárgate de aquí.",
        "तुम बहुत अच्छे हो।"
    ]

    for comment in test_comments:
        inputs = tokenizer(
            comment,
            return_tensors="pt",
            truncation=True,
            max_length=256
        )

        with torch.no_grad():
            outputs = model(**inputs)

        scores = torch.sigmoid(outputs.logits)[0]

        print("\nComment:", comment)

        for index, score in enumerate(scores):
            label = model.config.id2label[index]
            print(label, ":", round(score.item() * 100, 2), "%")