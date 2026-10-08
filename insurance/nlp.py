# Improved NLP utilities with ML-based intent classification using scikit-learn.

import re
from functools import lru_cache
from .models import FAQ
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import os

# Basic spell correction dictionary
SPELL_CORRECTIONS = {
    "tekll": "tell",
    "documennts": "documents",
    "insurence": "insurance",
    "policcy": "policy",
    "claime": "claim",
    "renewl": "renewal",
    "documnt": "document",
    "insurnce": "insurance",
    "poliicy": "policy",
    "claimes": "claims",
    "renewals": "renewals",
}

def preprocess_query(query):
    """Preprocess query: lowercase, remove extra spaces, basic spell correction."""
    if not query:
        return query
    # Lowercase
    query = query.lower()
    # Remove extra spaces
    query = re.sub(r'\s+', ' ', query).strip()
    # Basic spell correction
    words = query.split()
    corrected_words = []
    for word in words:
        corrected_words.append(SPELL_CORRECTIONS.get(word, word))
    return ' '.join(corrected_words)

# Training data for intents
training_data = [
    ("What is insurance?", "what_is_insurance"),
    ("Insurance kya hai?", "what_is_insurance"),
    ("Tell me about insurance", "what_is_insurance"),
    ("Explain insurance", "what_is_insurance"),
    ("How to apply for insurance?", "how_to_apply"),
    ("Kaise insurance apply karu?", "how_to_apply"),
    ("I want to apply for insurance", "apply_for_insurance"),
    ("Mujhe insurance lena hai", "apply_for_insurance"),
    ("Check my claim status", "ask_claim_status"),
    ("Mera claim status batao", "ask_claim_status"),
    ("Check my claim", "ask_claim_status"),
    ("Mera claim check karo", "ask_claim_status"),
    ("Check claim", "ask_claim_status"),
    ("Claim check", "ask_claim_status"),
    # Premium Calculator
    ("Premium Calculator", "premium_calculator"),
    ("premium calculator", "premium_calculator"),
    ("calculate premium", "premium_calculator"),
    ("Tell me more about Premium Calculator", "premium_calculator"),
    # Policy Documents
    ("Policy Documents", "policy_documents"),
    ("policy documents", "policy_documents"),
    ("access documents", "policy_documents"),
    ("manage documents", "policy_documents"),
    ("Tell me more about Policy Documents", "policy_documents"),
    # 24/7 Support
    ("24/7 Support", "support_24_7"),
    ("24/7 support", "support_24_7"),
    ("customer support", "support_24_7"),
    ("contact support", "support_24_7"),
    ("Tell me more about 24/7 Support", "support_24_7"),
    # Health Plans
    ("Health Plans", "health_plans"),
    ("health plans", "health_plans"),
    ("compare health plans", "health_plans"),
    ("health insurance plans", "health_plans"),
    ("Tell me more about Health Plans", "health_plans"),
    # Find Doctors
    ("Find Doctors", "find_doctors"),
    ("find doctors", "find_doctors"),
    ("doctor search", "find_doctors"),
    ("search doctors", "find_doctors"),
    ("Tell me more about Find Doctors", "find_doctors"),
    # Pharmacy
    ("Pharmacy", "pharmacy"),
    ("pharmacy", "pharmacy"),
    ("drug coverage", "pharmacy"),
    ("pharmacy locations", "pharmacy"),
    ("Tell me more about Pharmacy", "pharmacy"),
    # Quote related
    ("Get a quote", "get_quote"),
    ("get a quote", "get_quote"),
    ("quote request", "get_quote"),
    ("insurance quote", "get_quote"),
    ("Auto insurance quote", "get_quote"),
    ("Home insurance quote", "get_quote"),
    ("Health insurance quote", "get_quote"),
    # Policy Information
    ("Policy information", "policy_information"),
    ("policy information", "policy_information"),
    ("policy info", "policy_information"),
    ("my policy", "policy_information"),
    ("Policy details", "policy_details"),
    ("policy details", "policy_details"),
    ("Update policy", "update_policy"),
    ("update policy", "update_policy"),
    ("Renew policy", "renew_policy"),
    ("renew policy", "renew_policy"),
    # Coverage Options
    ("Coverage options", "coverage_options"),
    ("coverage options", "coverage_options"),
    ("coverage info", "coverage_options"),
    ("what coverage", "coverage_options"),
    # Claims Assistance
    ("Claims assistance", "claims_assistance"),
    ("claims assistance", "claims_assistance"),
    ("help with claim", "claims_assistance"),
    ("claim help", "claims_assistance"),
    # Plan Types
    ("Individual plan", "individual_plan"),
    ("individual plan", "individual_plan"),
    ("Family plan", "family_plan"),
    ("family plan", "family_plan"),
    ("Compare plans", "compare_plans"),
    ("compare plans", "compare_plans"),
    # Family Size Options
    ("2 adults, 2 children", "family_size"),
    ("Only for myself", "individual_only"),
    ("For my parents", "parents_coverage"),
    ("Claim ID 12345 status", "check_claim_status"),
    ("Dawa ID 67890 ka status", "check_claim_status"),
    ("Hi", "greeting"),
    ("Hello", "greeting"),
    ("Namaste", "greeting"),
    ("Hlo", "greeting"),
    ("Hlooo", "greeting"),
    ("Hii", "greeting"),
    ("Kaise ho", "greeting"),
    ("How are you", "greeting"),
    ("Good morning", "greeting"),
    ("Hey bot", "greeting"),
    ("Hello there", "greeting"),
    ("Thanks", "thanks"),
    ("Thank you", "thanks"),
    ("Dhanyavaad", "thanks"),
    ("Shukriya", "thanks"),
    ("Shukhriya", "thanks"),
    ("ok", "acknowledge"),
    ("okay", "acknowledge"),
    ("hmm", "acknowledge"),
    ("haan theek hai", "acknowledge"),
    ("thik h", "acknowledge"),
    ("What are the documents needed?", "faq"),
    ("Which documents are required for insurance?", "faq"),
    ("Tell me which docs are required for insurance", "faq"),
    ("Documents needed for insurance", "faq"),
    ("Claim kaise file karu?", "faq"),
    ("Premium kitna hai?", "faq"),
    ("Insurance kya hota hai?", "what_is_insurance"),
    ("What is insurance?", "what_is_insurance"),
    ("Why insurance is important?", "why_insurance"),
    ("Insurance kyu lena chahiye?", "why_insurance"),
    ("How to apply for insurance?", "how_to_apply"),
    ("Insurance lene ka process batao?", "how_to_apply"),
    ("What documents are required for insurance?", "documents_needed"),
    ("Insurance ke liye kya papers chahiye?", "documents_needed"),
    ("Kya documents chahiye insurance ke liye?", "documents_needed"),
    ("Types of insurance", "types_of_insurance"),
    ("What is health insurance?", "health_insurance"),
    ("Life insurance ke benefits kya hai?", "life_insurance_benefits"),
    ("I want to renew my policy", "renew_policy"),
    ("Mujhe apni policy renew karni hai", "renew_policy"),
    ("What documents do I need?", "documents_needed"),
    ("document kya lagenge", "documents_needed"),
    ("kya lagenge", "documents_needed"),
    ("kya chahiye", "documents_needed"),
    ("kitne documents lagenge", "documents_needed"),
    ("Suggest me a good policy", "policy_suggestion"),
    ("How are you?", "small_talk"),
    ("Kaise ho?", "small_talk"),
    ("how to file insurance", "how_to_apply"),
    ("how to file the insurance", "how_to_apply"),
    ("insurance file kaise kare", "how_to_apply"),
    # Insurance type specific queries
    ("I'm interested in auto insurance", "auto_insurance"),
    ("I'm interested in car insurance", "auto_insurance"),
    ("I want auto insurance", "auto_insurance"),
    ("Tell me about auto insurance", "auto_insurance"),
    ("I'm interested in home insurance", "home_insurance"),
    ("I'm interested in house insurance", "home_insurance"),
    ("I want home insurance", "home_insurance"),
    ("Tell me about home insurance", "home_insurance"),
    ("I'm interested in life insurance", "life_insurance"),
    ("I want life insurance", "life_insurance"),
    ("Tell me about life insurance", "life_insurance"),
    ("I'm interested in travel insurance", "travel_insurance"),
    ("I want travel insurance", "travel_insurance"),
    ("Tell me about travel insurance", "travel_insurance"),
    ("I'm interested in business insurance", "business_insurance"),
    ("I want business insurance", "business_insurance"),
    ("Tell me about business insurance", "business_insurance"),
    ("Auto Insurance", "auto_insurance"),
    ("Home Insurance", "home_insurance"),
    ("Life Insurance", "life_insurance"),
    ("Travel Insurance", "travel_insurance"),
    ("Business Insurance", "business_insurance"),
    ("Default", "faq"),  # Fallback
]

# Load dynamic training examples from DB
try:
    from .models import TrainingExample
    db_examples = TrainingExample.objects.all()
    for ex in db_examples:
        training_data.append((ex.text, ex.intent))
except:
    pass  # In case DB not ready

# Duplicate insurance data to balance against CSV
insurance_data = training_data[:]  # Copy original
for _ in range(10):  # Add 10 more copies
    training_data.extend(insurance_data)

def _load_category_faqs(csv_filename, category):
    import pandas as pd
    from .models import FAQ

    csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
    if not os.path.exists(csv_path):
        return

    dataframe = pd.read_csv(csv_path, encoding='utf-8-sig')
    if not {'question', 'answer'}.issubset(dataframe.columns):
        return

    for _, row in dataframe.iterrows():
        question = row['question']
        answer = row['answer']
        if not (pd.notna(question) and pd.notna(answer)):
            continue

        question = question.strip()
        answer = answer.strip()
        if not question or not answer:
            continue

        matching_faqs = FAQ.objects.filter(question=question)
        if matching_faqs.exists():
            matching_faqs.update(answer_en=answer, category=category)
        else:
            FAQ.objects.create(
                question=question,
                answer_en=answer,
                category=category,
            )


def load_faqs():
    """Load FAQs from CSV"""
    kaggle_csv_path = os.path.join(os.path.dirname(__file__), 'kaggle_intents.csv')
    if os.path.exists(kaggle_csv_path):
        import pandas as pd
        df = pd.read_csv(kaggle_csv_path, encoding='utf-8-sig')
        if 'question' in df.columns and 'answer' in df.columns:
            # Load Insurance QA dataset into FAQ
            try:
                from .models import FAQ
                for index, row in df.iterrows():
                    question = row['question']
                    answer = row['answer']
                    if pd.notna(question) and pd.notna(answer) and question.strip() and answer.strip():
                        # Check if already exists
                        if not FAQ.objects.filter(question=question.strip()).exists():
                            FAQ.objects.create(
                                question=question.strip(),
                                answer_en=answer.strip(),
                                tags="insurance"
                            )
                # Add additional renewal FAQs
                renewal_faqs = [
                    ("how to renew my policy", "To renew your policy, log in to your account, choose the policy you want to renew, and make the payment before the expiry date."),
                    ("policy renewal process", "Visit our website, go to 'My Policies', select the policy and click on renew. You can also renew through our mobile app or customer care."),
                    ("mera insurance renew kaise hoga", "अपनी पॉलिसी को रिन्यू करने के लिए वेबसाइट या मोबाइल ऐप पर जाकर 'Renew Policy' पर क्लिक करें और भुगतान करें।"),
                    ("policy renewal time", "You can renew your policy up to 30 days before it expires."),
                    ("how to file insurance", "To apply for insurance, visit our website, fill out the application form, and submit required documents."),
                    ("how to file the insurance", "To apply for insurance, visit our website, fill out the application form, and submit required documents."),
                    ("insurance file kaise kare", "बीमा के लिए आवेदन करने के लिए, हमारी वेबसाइट पर जाएं, फॉर्म भरें और आवश्यक दस्तावेज जमा करें।"),
                ]
                for q, a in renewal_faqs:
                    if not FAQ.objects.filter(question=q).exists():
                        FAQ.objects.create(question=q, answer_en=a, tags="insurance")
            except Exception as e:
                print(f"Error loading FAQs: {e}")

        elif 'patterns' in df.columns and 'tag' in df.columns:
            # Fallback to old format for intents
            kaggle_data = []
            current_tag = None
            for index, row in df.iterrows():
                tag = row['tag']
                pattern = row['patterns']
                if pd.notna(tag) and tag.strip():
                    current_tag = tag.strip()
                if pd.notna(pattern) and pattern.strip() and current_tag:
                    kaggle_data.append((pattern.strip(), current_tag))
            training_data.extend(kaggle_data)

    for filename, category in (
        ('auto_insurance.csv', 'auto_insurance'),
        ('home_insurance.csv', 'home_insurance'),
        ('life_insurance.csv', 'life_insurance'),
        ('travel_insurance.csv', 'travel_insurance'),
        ('business_insurance.csv', 'business_insurance'),
    ):
        _load_category_faqs(filename, category)

# Load FAQs on import
load_faqs()

# Train model if not exists
model_path = os.path.join(os.path.dirname(__file__), 'intent_model.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')

if not os.path.exists(model_path):
    texts, labels = zip(*training_data)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    model = LogisticRegression()
    model.fit(X, labels)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
else:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)

def detect_language(text):
    """Simple language detection: if contains Devanagari, Hindi; else English."""
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'
    else:
        return 'en'

def detect_intent_and_entities(text):
    lang = detect_language(text)
    text_lower = text.lower()

    # Hybrid Logic: Rule-based checks first

    # 1. Claim ID detection
    claim_id_match = re.search(r'(?:claim\s*(?:id|no|number|idd)?|id|idd)\s*[=:]?\s*(\d{3,})', text_lower)
    if claim_id_match:
        return {"intent": "check_claim_status", "claim_id": claim_id_match.group(1), "lang": lang}

    bare_id = re.search(r"\b(\d{4,})\b", text_lower)
    if bare_id and ("claim" in text_lower or "दावा" in text_lower or "status" in text_lower or "स्थिति" in text_lower):
        return {"intent": "check_claim_status", "claim_id": bare_id.group(1), "lang": lang}

    # 2. Claim-related queries without ID (should ask for claim ID)
    claim_keywords = ["check claim", "check my claim", "claim status", "my claim", "दावा", "मेरा दावा", "claim check"]
    if any(keyword in text_lower for keyword in claim_keywords):
        return {"intent": "ask_claim_status", "claim_id": None, "lang": lang}

    # 3. Premium Calculator
    if "premium calculator" in text_lower or "calculate premium" in text_lower:
        return {"intent": "premium_calculator", "claim_id": None, "lang": lang}

    # 4. Policy Documents
    if "policy documents" in text_lower or "access documents" in text_lower or "manage documents" in text_lower:
        return {"intent": "policy_documents", "claim_id": None, "lang": lang}

    # 5. Policy Details (before more_details rule)
    if "policy details" in text_lower:
        return {"intent": "policy_details", "claim_id": None, "lang": lang}

    # 6. Family Size specific patterns
    if "2 adults" in text_lower and "2 children" in text_lower:
        return {"intent": "family_size", "claim_id": None, "lang": lang}
    if "only for myself" in text_lower:
        return {"intent": "individual_only", "claim_id": None, "lang": lang}
    if "for my parents" in text_lower:
        return {"intent": "parents_coverage", "claim_id": None, "lang": lang}

    # 7. Insurance type selections - made more flexible and case-insensitive
    insurance_keywords = {
        'health': ['health insurance', 'medical insurance', 'स्वास्थ्य बीमा'],
        'auto': ['auto insurance', 'car insurance', 'vehicle insurance', 'ऑटो बीमा', 'कार बीमा'],
        'home': ['home insurance', 'house insurance', 'property insurance', 'घर बीमा', 'मकान बीमा'],
        'life': ['life insurance', 'जीवन बीमा'],
        'travel': ['travel insurance', 'trip insurance', 'यात्रा बीमा'],
        'business': ['business insurance', 'commercial insurance', 'व्यापार बीमा']
    }

    for ins_type, keywords in insurance_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                intent_map = {
                    'health': 'health_insurance',
                    'auto': 'auto_insurance',
                    'home': 'home_insurance',
                    'life': 'life_insurance',
                    'travel': 'travel_insurance',
                    'business': 'business_insurance'
                }
                return {"intent": intent_map[ins_type], "claim_id": None, "lang": lang}

    # 8. Specific plan type patterns (before existing health insurance rules)
    if "family plan" in text_lower and not ("health_insurance_family" in text_lower):
        return {"intent": "family_plan", "claim_id": None, "lang": lang}

    # 2. Renewal keywords
    if any(word in text_lower for word in ["renew", "renewal", "रिन्यू", "नवीनीकरण"]):
        return {"intent": "renew_policy", "claim_id": None, "lang": lang}

    # 3. Document keywords (expanded for Hindi) - MOVED UP for priority
    document_keywords = [
        "document", "documents", "papers", "paper",
        "कागजात", "दस्तावेज", "कागज", "डॉक्यूमेंट",
        "kya lagenge", "kya chahiye", "kya documents", "kya papers",
        "क्या लगेंगे", "क्या चाहिए", "क्या दस्तावेज", "क्या कागजात",
        "kitne documents", "kitne papers", "कितने दस्तावेज", "कितने कागजात",
        "required documents", "जरूरी दस्तावेज", "आवश्यक दस्तावेज"
    ]
    if any(keyword in text_lower for keyword in document_keywords):
        return {"intent": "documents_needed", "claim_id": None, "lang": lang}

    # 4. Insurance category detection (only if not document-related)
    auto_keywords = ['auto', 'car', 'vehicle', 'driving', 'accident', 'collision', 'comprehensive', 'liability', 'auto insurance', 'car insurance', 'vehicle insurance']
    home_keywords = ['home', 'house', 'property', 'dwelling', 'homeowner', 'home insurance', 'house insurance', 'property insurance']
    life_keywords = ['life', 'life insurance', 'term life', 'whole life', 'universal life', 'permanent life']
    travel_keywords = ['travel', 'trip', 'vacation', 'travel insurance', 'trip insurance', 'journey']
    business_keywords = ['business', 'commercial', 'company', 'corporate', 'enterprise', 'business insurance', 'commercial insurance', 'व्यापार बीमा']

    if any(word in text_lower for word in auto_keywords):
        return {"intent": "faq", "category": "auto_insurance", "lang": lang}
    elif any(word in text_lower for word in home_keywords):
        return {"intent": "faq", "category": "home_insurance", "lang": lang}
    elif any(word in text_lower for word in life_keywords):
        return {"intent": "faq", "category": "life_insurance", "lang": lang}
    elif any(word in text_lower for word in travel_keywords):
        return {"intent": "faq", "category": "travel_insurance", "lang": lang}
    elif any(word in text_lower for word in business_keywords):
        return {"intent": "faq", "category": "business_insurance", "lang": lang}

    # 5. Policy customization
    if any(word in text_lower for word in ["suggest", "recommend", "premium", "rate", "सुझाव", "सिफारिश"]):
        return {"intent": "policy_suggestion", "claim_id": None, "lang": lang}

    # 5. Small talk
    if any(word in text_lower for word in ["how are you", "kaise ho", "how do you do"]):
        return {"intent": "small_talk", "claim_id": None, "lang": lang}

    # 6. Tell me more / More details
    if any(phrase in text_lower for phrase in ["tell me more", "more about it", "elaborate", "explain more", "aur batao", "aur janiye", "detail", "details"]):
        return {"intent": "more_details", "claim_id": None, "lang": lang}

    # 7. Compare plans
    if any(word in text_lower for word in ["compare", "comparison", "तुलना"]):
        return {"intent": "compare_plans", "claim_id": None, "lang": lang}

    # 8. Health plans
    if any(phrase in text_lower for phrase in ["health plans", "स्वास्थ्य योजनाएं"]):
        return {"intent": "health_plans", "claim_id": None, "lang": lang}

    # 9. Find doctors
    if any(phrase in text_lower for phrase in ["find doctors", "doctor search", "डॉक्टर खोजें"]):
        return {"intent": "find_doctors", "claim_id": None, "lang": lang}

    # 10. Pharmacy
    if any(word in text_lower for word in ["pharmacy", "फार्मेसी"]):
        return {"intent": "pharmacy", "claim_id": None, "lang": lang}

    # 11. Policy details
    if any(phrase in text_lower for phrase in ["policy details", "पॉलिसी विवरण"]):
        return {"intent": "policy_details", "claim_id": None, "lang": lang}

    # 12. Update policy
    if any(phrase in text_lower for phrase in ["update policy", "पॉलिसी अपडेट"]):
        return {"intent": "update_policy", "claim_id": None, "lang": lang}

    # Use ML for remaining intents
    X_test = vectorizer.transform([text])
    intent = model.predict(X_test)[0]

    return {"intent": intent, "claim_id": None, "lang": lang}

@lru_cache(maxsize=8)
def _get_faq_tfidf(corpus):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix


def search_faqs(query, limit=3, lang='en', category=None):
    query = preprocess_query(query)
    if not query.strip():
        return []

    if category:
        faqs = list(FAQ.objects.filter(category=category).order_by('pk'))
    else:
        faqs = list(FAQ.objects.filter(tags__icontains="insurance").order_by('pk'))
        if not faqs:
            faqs = list(FAQ.objects.all().order_by('pk'))
    if not faqs:
        return []

    corpus = tuple(f"{faq.question} {faq.tags or ''}" for faq in faqs)
    vectorizer, tfidf_matrix = _get_faq_tfidf(corpus)
    query_vec = vectorizer.transform([query])
    similarities = (query_vec @ tfidf_matrix.T).toarray().ravel()

    matches = []
    for faq, score in zip(faqs, similarities):
        if score > 0.2:
            answer = faq.answer_hi if lang == 'hi' else faq.answer_en
            matches.append(
                {"question": faq.question, "answer": answer, "score": float(score)}
            )
    matches.sort(key=lambda match: match["score"], reverse=True)
    return matches[:limit]