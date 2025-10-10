#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_agent.settings')
django.setup()

from insurance.nlp import detect_intent_and_entities

# Test all suggestion buttons and quick replies
test_cases = [
    # Suggestion Cards
    ("Premium Calculator", "premium_calculator"),
    ("Policy Documents", "policy_documents"),
    ("24/7 Support", "support_24_7"),
    ("Health Plans", "health_plans"),
    ("Find Doctors", "find_doctors"),
    ("Pharmacy", "pharmacy"),

    # Quick Replies - Main Menu
    ("Get a quote", "get_quote"),
    ("Policy information", "policy_information"),
    ("Claims assistance", "claims_assistance"),
    ("Coverage options", "coverage_options"),

    # Quick Replies - Policy Related
    ("Policy details", "policy_details"),
    ("Update policy", "update_policy"),
    ("Renew policy", "renew_policy"),

    # Quick Replies - Health Plan Types
    ("Individual plan", "individual_plan"),
    ("Family plan", "family_plan"),
    ("Compare plans", "compare_plans"),

    # Quick Replies - Family Size
    ("2 adults, 2 children", "family_size"),
    ("Only for myself", "individual_only"),
    ("For my parents", "parents_coverage"),

    # Insurance Type Selections
    ("I'm interested in Health Insurance", "health_insurance"),
    ("I'm interested in Auto Insurance", "auto_insurance"),
    ("I'm interested in Home Insurance", "home_insurance"),
    ("I'm interested in Life Insurance", "life_insurance"),
    ("I'm interested in Travel Insurance", "travel_insurance"),
    ("I'm interested in Business Insurance", "business_insurance"),
]

print("Testing all suggestion buttons and quick replies...")
print("=" * 60)

success_count = 0
total_count = len(test_cases)

for test_query, expected_intent in test_cases:
    result = detect_intent_and_entities(test_query)
    intent = result.get('intent')
    lang = result.get('lang')

    print(f"Query: '{test_query}'")
    print(f"Expected Intent: {expected_intent}")
    print(f"Detected Intent: {intent}")
    print(f"Language: {lang}")

    if intent == expected_intent:
        print("CORRECT: Intent matches expected")
        success_count += 1
    else:
        print("INCORRECT: Intent mismatch")

    print("-" * 40)

print(f"\nSUMMARY: {success_count}/{total_count} tests passed ({success_count/total_count*100:.1f}%)")

if success_count == total_count:
    print("ALL TESTS PASSED! All suggestion buttons should work correctly.")
else:
    print(f"WARNING: {total_count - success_count} tests failed. Some suggestion buttons may not work properly.")