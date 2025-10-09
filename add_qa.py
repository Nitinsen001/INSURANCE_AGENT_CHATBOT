import csv

# New Q&A data from the task
new_qa = [
    # Health Insurance
    ("I'm turning 26 and getting kicked off my parent's plan. What should I do?", "You have a 60-day Special Enrollment Period to get new coverage. You can look into your employer's plan, the Health Insurance Marketplace, or an individual plan. Don't miss this window, or you could face a coverage gap."),
    ("I just lost my job and my health insurance. What are my options?", "Sorry to hear that. You have options: 1) COBRA to continue your previous plan (but you pay the full premium), 2) A plan from the Health Insurance Marketplace (losing job qualifies you for a Special Enrollment Period), or 3) Joining a family member's plan if possible."),
    ("I'm getting married. How do I add my spouse to my plan?", "Congratulations! Marriage is a \"Qualifying Life Event.\" Contact your HR department or insurance company within 30-60 days of your marriage date to add your spouse to your plan."),
    ("I'm pregnant. What maternity services are covered under my plan?", "Congratulations! Under the ACA, most plans must cover prenatal care, delivery, and postpartum care. We recommend checking your specific plan details for copays, deductibles, and in-network hospital coverage."),
    ("I have a sore throat. Should I go to my primary doctor, an urgent care, or the ER?", "For a non-life-threatening issue like a sore throat, start with your primary doctor. If they're unavailable, an in-network urgent care is your most cost-effective option. Save the ER for true emergencies like difficulty breathing."),
    ("I need to see a dermatologist. Do I need a referral from my primary doctor?", "It depends on your plan. HMO plans typically require a referral. PPO plans usually let you see a specialist without one, but seeing an in-network dermatologist will save you money. Check your plan details or call us to confirm."),
    ("I got a bill from a doctor that seems too high. What should I do?", "First, check your Explanation of Benefits (EOB) from us—it shows what you owe. If the bill doesn't match the EOB, call the doctor's billing office. If it does, but you think there's an error, call the number on your insurance card for help."),
    ("My claim was denied. What do I do now?", "Don't panic. First, understand the reason for the denial (it will be in the denial letter). Often, it's missing information or a coding error. You can appeal the decision. Call us, and we can guide you through the appeals process."),

    # Auto Insurance
    ("I just bought a new car. How do I add it to my policy?", "Congrats on the new car! You typically have a 7-30 day grace period to add it. Contact your agent or call us immediately with the Vehicle Identification Number (VIN). Don't drive it uninsured!"),
    ("My teenager just got their license. How much will my premium increase?", "Adding a teen driver often increases premiums significantly, as they're considered high-risk. The exact amount varies, but you can ask about \"good student\" discounts or safe driver programs to help lower the cost."),
    ("I just got into a minor fender bender. What should I do first?", "1) Move to a safe location. 2) Check if anyone is hurt. 3) Exchange insurance and contact info with the other driver. 4) Take photos of the damage and the scene. 5) Report the claim to us, even if it's minor."),
    ("The other driver doesn't have insurance. What happens now?", "This is why you have Uninsured Motorist (UM) coverage. If you have this coverage, we will handle your damages and medical bills (subject to your policy terms). Then we will pursue the at-fault driver legally."),
    ("I hit a deer. Does this go under collision or comprehensive?", "Hitting an animal like a deer is covered under Comprehensive coverage, not Collision. This is good news because comprehensive claims often don't affect your premium as much as a collision claim would."),
    ("Will my rates go up if I file a claim?", "It depends. If it's your first not-at-fault accident (like being rear-ended), your rates may not increase. However, if you are at-fault or have multiple claims, you will likely see a premium increase at renewal."),
    ("My car was totaled. How do you determine its value?", "We determine the \"Actual Cash Value\" (ACV) – what your car was worth just before the accident. This is based on its make, model, year, mileage, condition, and comparable vehicles sold in your area."),
    ("I'm struggling to pay my premium this month. Can I get an extension?", "We understand. Please call us immediately! We may be able to offer a grace period or set up a payment plan. It's much worse to let your policy lapse, as that leads to cancellation and higher future costs."),

    # Home Insurance
    ("I'm buying a house. How much home insurance do I need?", "You need enough to completely rebuild your home (dwelling coverage), replace all your belongings (personal property), and protect your assets (liability). We can help you calculate the right amount based on your home's specs."),
    ("My basement flooded after heavy rain. Is this covered?", "Standard home insurance does NOT cover flooding from external sources like heavy rain or overflowing rivers. For that, you need a separate Flood Insurance policy. However, if a pipe burst inside your home, that would be covered."),
    ("A tree fell on my house during a storm. What's covered?", "The damage to your house (roof, structure) is covered under your dwelling coverage. The cost to remove the tree is also usually covered, up to a certain limit. We'll send an adjuster to assess the damage."),
    ("My jewelry was stolen. Is it covered under my standard policy?", "Standard policies have limited coverage for high-value items like jewelry (often $1,000-$2,000 total). If your items are worth more, you need to schedule a \"rider\" or \"endorsement\" for them, which provides broader coverage."),
    ("My pipe burst and flooded my kitchen. What should I do first?", "1) Shut off the main water supply. 2) Take photos/videos of the damage and the source. 3) Call us to start the claims process. 4) Start mitigating the damage—e.g., mopping up water—to prevent mold."),
    ("My home was damaged and I can't live there. Will insurance pay for a hotel?", "Yes, this is your \"Additional Living Expenses\" (ALE) coverage. It helps pay for a hotel, meals, and other costs if your home is uninhabitable due to a covered loss. Save your receipts."),
    ("I'm renovating my kitchen. Do I need to update my policy?", "Yes, absolutely. A kitchen renovation increases your home's rebuild value. Let us know before you start so we can adjust your dwelling coverage. This ensures you're fully protected during and after the renovation."),
    ("I work from home. Are my business equipment and inventory covered?", "Standard home policies have very limited coverage for business equipment (often $2,500 or less). If you have significant business property or liability exposure (like clients visiting), you may need a separate In-Home Business Policy."),

    # Life Insurance
    ("I'm 30 and healthy. Do I really need life insurance?", "Yes, if anyone depends on your income (a spouse, children, aging parents) or if you have shared debts (like a mortgage). It's also cheapest to buy when you're young and healthy. It's about protecting others."),
    ("How much life insurance do I need as a new parent?", "A common rule is 10-15 times your annual income. Consider future costs like college tuition, childcare, and paying off your mortgage. The goal is to ensure your family can maintain their lifestyle if you're gone."),
    ("What's better for me: term life or whole life insurance?", "Term life is pure protection for a set period (e.g., 20-30 years) and is affordable. Whole life is permanent, lasts your whole life, and has a cash value component but is more expensive. For most families, term is the best starting point."),
    ("My spouse passed away. How do I file a life insurance claim?", "We are so sorry for your loss. To file a claim, please call us. You will need a certified copy of the death certificate. We will guide you through the simple process and work to get you the benefit as quickly as possible."),
    ("I can't afford my premium this month. What are my options?", "Please call us immediately. Depending on your policy, you may have a grace period (usually 30 days). For whole life policies, you might use dividends or cash value to pay the premium. We can discuss options to avoid a lapse."),
    ("I need to see a dermatologist. Do I need a referral from my primary doctor?", "It depends on your plan. HMO plans typically require a referral. PPO plans usually let you see a specialist without one, but seeing an in-network dermatologist will save you money. Check your plan details or call us to confirm."),
    ("I got a bill from a doctor that seems too high. What should I do?", "First, check your Explanation of Benefits (EOB) from us—it shows what you owe. If the bill doesn't match the EOB, call the doctor's billing office. If it does, but you think there's an error, call the number on your insurance card for help."),
    ("My claim was denied. What do I do now?", "Don't panic. First, understand the reason for the denial (it will be in the denial letter). Often, it's missing information or a coding error. You can appeal the decision. Call us, and we can guide you through the appeals process."),

    # Travel Insurance
    ("I'm going to Europe for 2 weeks. Do I need travel insurance?", "It's highly recommended. It protects your trip investment from cancellation and, most importantly, covers emergency medical costs overseas, which your regular health plan often does not."),
    ("My flight was cancelled due to weather. Will insurance cover my hotel costs?", "Yes, if you have Trip Delay coverage. It typically reimburses you for extra accommodation, meals, and transportation expenses if your trip is delayed for a covered reason like severe weather."),
    ("I got sick on vacation and went to a hospital. What should I do?", "Your health comes first. Then, as soon as possible, call the emergency assistance number on your travel insurance card. They can help find a quality medical facility, arrange payments, and guide you through the claims process."),
    ("My luggage was lost by the airline. Does travel insurance cover this?", "Yes, Baggage Delay/Loss coverage can reimburse you for essential items you need to buy while waiting for your bags, and for the value of your belongings if they are lost entirely. Always file a report with the airline first."),

    # Business Insurance
    ("I just started a small LLC. What insurance do I need?", "At a minimum, consider General Liability (for customer injuries/slip-and-falls) and Professional Liability/Errors & Omissions (for mistakes in your work). If you have employees, Workers' Comp is legally required."),
    ("I'm a freelance consultant. Do I really need professional liability insurance?", "Absolutely. It protects you if a client sues you for financial loss due to your advice, errors, or missed deadlines. Even a baseless lawsuit can be expensive to defend, and this coverage handles those legal costs."),
    ("A client is suing me for mistakes in my work. What insurance covers this?", "Your Professional Liability (E&O) insurance is designed for this. It helps cover your legal defense costs and any settlements or judgments, up to your policy limits. Contact us immediately if you are served with a lawsuit."),
    ("One of my employees got hurt on the job. What do I do?", "1) Ensure they get immediate medical attention. 2) Document the incident. 3) Report the injury to your Workers' Compensation insurance carrier immediately. They will manage the medical care and lost wage payments."),
    ("Can I get a discount for bundling my auto and home insurance?", "Yes! This is called a \"multi-policy\" or \"bundle\" discount. It's one of the easiest ways to save. We can give you a quote that combines them to show you the savings."),
]

# Find the next ID
with open('insurance/kaggle_intents.csv', 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)
    last_id = int(rows[-1][0]) if rows else 999

# Append new Q&A
with open('insurance/kaggle_intents.csv', 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for i, (q, a) in enumerate(new_qa, start=last_id + 1):
        writer.writerow([i, q, a])

print(f"Added {len(new_qa)} new Q&A pairs to the CSV.")