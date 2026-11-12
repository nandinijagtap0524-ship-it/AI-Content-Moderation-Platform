import unittest

from moderation import ContentModerator


class ContentModeratorTests(unittest.TestCase):
    def setUp(self):
        self.moderator = ContentModerator()

    def test_classifies_representative_training_examples(self):
        examples = {
            "safe": "Thank you for sharing your helpful advice",
            "harassment": "You are worthless and nobody likes you",
            "hate": "People of that ethnicity do not belong here",
            "violence": "I want to hurt that person",
            "sexual": "The message contains an explicit sexual proposition",
            "self_harm": "I am thinking about hurting myself",
        }

        for expected, text in examples.items():
            with self.subTest(category=expected):
                self.assertEqual(self.moderator.moderate(text)["category"], expected)

    def test_returns_normalized_scores_and_action(self):
        result = self.moderator.moderate("I appreciate your kind support today")

        self.assertAlmostEqual(sum(result["scores"].values()), 1.0, places=5)
        self.assertEqual(result["action"], "allow")
        self.assertIn("confidence", result)

    def test_rejects_text_without_tokens(self):
        with self.assertRaises(ValueError):
            self.moderator.moderate(" !!! ")


if __name__ == "__main__":
    unittest.main()
