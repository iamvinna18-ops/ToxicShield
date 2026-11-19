# -*- coding: utf-8 -*-
import re
import unicodedata
from collections import Counter
from unittest import result


# Suspicious promotional phrases

SPAM_PHRASES = [
    "earn money fast",
    "click here",
    "claim your prize",
    "claim your free prize",
    "free prize",
    "limited offer",
    "you have won",
    "winner selected",
    "investment opportunity",
    "work from home",
    "follow for follow",
    "buy followers",
    "free followers",
    "whatsapp me",
    "telegram me",
    "send otp",
    "guaranteed profit",
    "dm me",
    "check my bio",
    "make money online",
    "get rich quick",
    "free cash",
    "act now"
]


def normalize_comment(comment):
    """Normalize text for duplicate detection."""

    text = unicodedata.normalize("NFKC", comment)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_spam(comment, duplicate_count=1):

    if not isinstance(comment, str) or not comment.strip():
        return {
            "is_spam": False,
            "risk_score": 0,
            "reasons": ["Empty comment"]
        }

    text = comment.lower()
    score = 0
    reasons = []

    # 1. Detect suspicious links
    urls = re.findall(
        r"https?://\S+|www\.\S+",
        text
    )

    if urls:
        score += 30
        reasons.append("Contains a URL")

    if len(urls) > 1:
        score += 20
        reasons.append("Contains multiple URLs")

    # 2. Detect promotional phrases
    matches = [
        phrase for phrase in SPAM_PHRASES
        if phrase in text
    ]

    if matches:
        score += min(80, 45 * len(matches))
        reasons.append("Promotional or suspicious phrase detected")

    # 3. Detect excessive repeated characters
    if re.search(r"(.)\1{5,}", text):
        score += 15
        reasons.append("Excessive repeated characters")

    # 4. Detect excessive uppercase text
    letters = [c for c in comment if c.isalpha()]

    if len(letters) >= 12:
        uppercase_ratio = sum(
            c.isupper() for c in letters
        ) / len(letters)

        if uppercase_ratio > 0.85:
            score += 15
            reasons.append("Excessive uppercase text")

    # 5. Detect repeated identical comments
    if duplicate_count > 1:
        score += 40
        reasons.append("Repeated identical comment")

    score = min(score, 100)

    return {
        "is_spam": score >= 40,
        "risk_score": score,
        "reasons": reasons if reasons else [
            "No obvious spam indicators"
        ]
    }


def analyze_spam_batch(comments):
    """Detect spam and repeated comments in a batch."""

    normalized = [
        normalize_comment(c) if isinstance(c, str) else ""
        for c in comments
    ]

    counts = Counter(normalized)

    results = []

    for comment, normalized_comment in zip(
        comments, normalized
    ):
        result = detect_spam(
            comment,
            duplicate_count=counts[normalized_comment]
        )

        result["comment"] = comment
        results.append(result)

    return results


if __name__ == "__main__":

    test_comments = [
        "You are amazing!",
        "Click the link to earn money fast!",
        "FREE MONEY!!!",
        "Visit https://example.com",
        "Nice video!",
        "You are amazing!",
        "You are amazing!"
    ]

    results = analyze_spam_batch(test_comments)

    for item in results:
        print("\nComment:", item["comment"])
        print("Spam:", item["is_spam"])
        print("Risk score:", item["risk_score"])
        print("Reasons:", item["reasons"])
