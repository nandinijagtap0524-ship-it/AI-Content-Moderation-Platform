"""A tiny Multinomial Naive Bayes text classifier for moderation demos."""

import math
import re
from collections import Counter, defaultdict


TRAINING_EXAMPLES = {
    "safe": [
        "Thank you for sharing your helpful advice",
        "I appreciate your kind support today",
        "That was a thoughtful and welcoming message",
        "We can work together and solve this problem",
        "I enjoyed reading your creative story",
        "Please let me know if you need any help",
        "Congratulations on your wonderful achievement",
        "The community is friendly and supportive",
        "I respectfully disagree with that suggestion",
        "Have a nice day and take care",
        "Your explanation was clear and useful",
        "Thanks for being patient with everyone",
    ],
    "harassment": [
        "You are worthless and nobody likes you",
        "I will keep bothering you every day",
        "You are stupid and should leave",
        "Everyone should mock that person",
        "Stop messaging me you annoying loser",
        "You deserve to be humiliated",
        "I am targeting you with cruel insults",
        "Nobody wants you around here",
        "You are pathetic and completely useless",
        "I will make fun of you again",
        "That person should be bullied out of the group",
        "You are a disgusting fool",
    ],
    "hate": [
        "People of that ethnicity do not belong here",
        "That religion makes its followers inferior",
        "Women should not have equal rights",
        "Men from that group are all dangerous",
        "Keep immigrants from that nationality out",
        "That community is less human than others",
        "People with disabilities should be excluded",
        "A hateful slur was directed at a minority group",
        "That race deserves to be treated unfairly",
        "Members of that faith should be rejected",
        "LGBTQ people should be denied basic respect",
        "That culture should be driven away",
    ],
    "violence": [
        "I want to hurt that person",
        "Bring a weapon and attack the crowd",
        "The plan describes how to injure someone",
        "Threaten them with physical violence",
        "I will assault you when you leave",
        "The message encourages a violent attack",
        "Someone threatened to beat up a neighbor",
        "They discussed causing serious physical harm",
        "I want revenge and will attack them",
        "The threat says to hurt the entire group",
        "Instructions describe an attempt to physically harm someone",
        "They are planning a brutal assault",
    ],
    "sexual": [
        "The message contains an explicit sexual proposition",
        "They sent an unwanted sexual comment",
        "This describes graphic adult sexual activity",
        "The text makes a crude sexual request",
        "An explicit sexual image was mentioned",
        "They are pressuring someone for sexual content",
        "The comment is sexually explicit and unwanted",
        "This is an adult sexual solicitation",
        "They sent graphic sexual messages",
        "The post contains an explicit sexual description",
        "The message makes an unwanted sexual advance",
        "An adult requested intimate sexual material",
    ],
    "self_harm": [
        "I am thinking about hurting myself",
        "I feel hopeless and might harm myself",
        "The message says they want to end their life",
        "I have thoughts of self injury",
        "They said they may take their own life",
        "I do not feel safe with myself tonight",
        "The post expresses suicidal thoughts",
        "I might hurt myself and need support",
        "They are considering self harm",
        "I feel like I cannot keep going",
        "The person needs help with thoughts of suicide",
        "They mentioned plans to injure themselves",
    ],
}


def tokenize(text):
    """Return lowercase word and adjacent-word features."""
    words = re.findall(r"[a-z0-9']+", text.lower())
    return words + [f"{left}_{right}" for left, right in zip(words, words[1:])]


class ContentModerator:
    def __init__(self):
        self.labels = tuple(TRAINING_EXAMPLES)
        self.word_counts = defaultdict(Counter)
        self.total_words = Counter()
        self.document_counts = Counter()
        self.vocabulary = set()

        for label, examples in TRAINING_EXAMPLES.items():
            for example in examples:
                features = tokenize(example)
                self.document_counts[label] += 1
                self.word_counts[label].update(features)
                self.total_words[label] += len(features)
                self.vocabulary.update(features)

    def moderate(self, text):
        features = tokenize(text)
        if not features:
            raise ValueError("Text must contain at least one letter or number")

        vocabulary_size = len(self.vocabulary)
        document_total = sum(self.document_counts.values())
        scores = {}
        for label in self.labels:
            score = math.log(self.document_counts[label] / document_total)
            denominator = self.total_words[label] + vocabulary_size
            for feature in features:
                score += math.log((self.word_counts[label][feature] + 1) / denominator)
            scores[label] = score

        max_score = max(scores.values())
        probabilities = {
            label: math.exp(score - max_score) for label, score in scores.items()
        }
        probability_total = sum(probabilities.values())
        probabilities = {
            label: value / probability_total for label, value in probabilities.items()
        }

        category = max(probabilities, key=probabilities.get)
        confidence = probabilities[category]
        action = "allow" if category == "safe" else "review"
        if category != "safe" and confidence >= 0.55:
            action = "restrict"
        elif confidence < 0.40:
            action = "review"

        input_words = set(re.findall(r"[a-z0-9']+", text.lower()))
        matched_terms = sorted(
            word for word in input_words
            if word in self.vocabulary and len(word) > 2
        )[:5]

        return {
            "category": category,
            "action": action,
            "confidence": round(confidence, 3),
            "matched_terms": matched_terms,
            "scores": {
                label: round(probabilities[label], 6)
                for label in sorted(probabilities)
            },
        }
