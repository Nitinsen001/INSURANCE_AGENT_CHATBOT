from unittest.mock import patch

from django.test import TestCase

from .models import FAQ
from .nlp import _load_category_faqs, search_faqs


class InsuranceCategoryTests(TestCase):
    def test_each_non_health_type_uses_its_own_faq_category(self):
        expected_categories = {
            "Auto Insurance": "auto_insurance",
            "Home Insurance": "home_insurance",
            "Life Insurance": "life_insurance",
            "Travel Insurance": "travel_insurance",
            "Business Insurance": "business_insurance",
        }

        with patch("insurance.views.search_faqs") as search:
            search.side_effect = lambda query, lang="en", category=None: [
                {
                    "question": f"Question from {category}",
                    "answer": f"Answer from {category}",
                }
            ]

            for label, category in expected_categories.items():
                with self.subTest(label=label):
                    response = self.client.get(
                        "/api/query/",
                        {"text": f"I'm interested in {label}"},
                    )

                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.json()["text"], f"Answer from {category}"
                    )
                    self.assertEqual(
                        search.call_args.kwargs["category"], category
                    )

    def test_category_search_does_not_fall_back_to_another_category(self):
        FAQ.objects.create(
            question="What is health insurance?",
            answer_en="Health-only answer",
            category="general",
            tags="insurance",
        )

        self.assertEqual(
            search_faqs("health insurance", category="auto_insurance"),
            [],
        )

    def test_category_csv_updates_faqs_already_loaded_as_general(self):
        question = "What is car insurance?"
        FAQ.objects.create(
            question=question,
            answer_en="Stale general answer",
            category="general",
            tags="insurance",
        )

        _load_category_faqs("auto_insurance.csv", "auto_insurance")

        faq = FAQ.objects.get(question=question)
        self.assertEqual(faq.category, "auto_insurance")
        self.assertIn("contract between you and an insurance company", faq.answer_en)
