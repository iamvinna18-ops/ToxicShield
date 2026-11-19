
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "tsmaitry/devica-toxicity-xlmr-large"

print("Loading ToxicShield multilingual AI model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)

model.eval()

device = torch.device("cpu")
model.to(device)

print("ToxicShield AI model loaded successfully!")


def detect_toxicity(comment):

    if not isinstance(comment, str) or not comment.strip():
        return {
            "category": "Invalid",
            "confidence": 0.0
        }

    inputs = tokenizer(
        comment,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    inputs = {key: value.to(device)
              for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(
        outputs.logits, dim=-1
    )[0]

    predicted_index = torch.argmax(probabilities).item()

    labels = model.config.id2label

    category = labels.get(
        predicted_index,
        labels.get(str(predicted_index), str(predicted_index))
    )

    confidence = probabilities[predicted_index].item()

    return {
        "category": str(category),
        "confidence": round(confidence * 100, 2)
    }


if __name__ == "__main__":

    test_comments = [
        "You are amazing!",
        "I hate you!",
        "Thank you for sharing this video.",
        "This is a terrible and abusive comment."
    ]

    for comment in test_comments:
        result = detect_toxicity(comment)

        print("\nComment:", comment)
        print("Result:", result)
