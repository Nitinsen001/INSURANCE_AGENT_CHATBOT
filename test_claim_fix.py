#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_agent.settings')
django.setup()

from insurance.nlp import detect_intent_and_entities

# Test cases for claim-related queries
test_cases = [
    "check my claim",
    "Check my claim",
    "check claim",
    "claim check",
    "Check my claim status",
    "Claim ID 12345 status",
    "Mera claim status batao",
    "Mera claim check karo",
    "I want to check my claim",
    "How do I check my claim status"
]

print("Testing claim-related intent detection...")
print("=" * 50)

for test_query in test_cases:
    result = detect_intent_and_entities(test_query)
    intent = result.get('intent')
    claim_id = result.get('claim_id')
    lang = result.get('lang')

    print(f"Query: '{test_query}'")
    print(f"Detected Intent: {intent}")
    print(f"Claim ID: {claim_id}")
    print(f"Language: {lang}")

    # Check if intent is correct
    if intent == "ask_claim_status":
        print("CORRECT: Properly detected as ask_claim_status")
    elif intent == "check_claim_status" and claim_id:
        print("CORRECT: Properly detected as check_claim_status with claim ID")
    else:
        print("INCORRECT: Wrong intent detected")

    print("-" * 30)