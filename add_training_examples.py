import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance_agent.settings')
django.setup()

from insurance.models import TrainingExample

# New training examples from feedback
new_examples = [
    ("2 adults, 2 children", "health_insurance_family"),
    ("Only for myself", "health_insurance_individual"),
    ("For my parents", "health_insurance_parents"),
    ("2 adults 2 children", "health_insurance_family"),
    ("only for myself", "health_insurance_individual"),
    ("for my parents", "health_insurance_parents"),
    ("I want coverage for my family", "health_insurance_family"),
    ("Individual plan", "health_insurance_individual"),
    ("Parents insurance", "health_insurance_parents"),
    ("Family plan", "health_insurance_family"),
    ("family plan", "health_insurance_family"),
    ("Compare plans", "compare_plans"),
    ("compare plans", "compare_plans"),
    ("Health Plans", "health_plans"),
    ("health plans", "health_plans"),
    ("Find Doctors", "find_doctors"),
    ("find doctors", "find_doctors"),
    ("Pharmacy", "pharmacy"),
    ("pharmacy", "pharmacy"),
    ("Policy details", "policy_details"),
    ("policy details", "policy_details"),
    ("Update policy", "update_policy"),
    ("update policy", "update_policy"),
    ("Renew policy", "renew_policy"),
    ("renew policy", "renew_policy"),
]

added_count = 0
for text, intent in new_examples:
    if not TrainingExample.objects.filter(text=text, intent=intent).exists():
        TrainingExample.objects.create(text=text, intent=intent)
        added_count += 1

print(f"Added {added_count} new training examples.")