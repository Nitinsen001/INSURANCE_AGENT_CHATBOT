# Improved NLP utilities with ML-based intent classification using scikit-learn.

import re
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
    ("Suggest me a good policy", "policy_suggestion"),
    ("How are you?", "small_talk"),
    ("Kaise ho?", "small_talk"),
    ("how to file insurance", "how_to_apply"),
    ("how to file the insurance", "how_to_apply"),
    ("insurance file kaise kare", "how_to_apply"),
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

        # Load auto_insurance.csv
        auto_csv_path = os.path.join(os.path.dirname(__file__), 'auto_insurance.csv')
        if os.path.exists(auto_csv_path):
            df_auto = pd.read_csv(auto_csv_path, encoding='utf-8-sig')
            if 'question' in df_auto.columns and 'answer' in df_auto.columns:
                try:
                    for index, row in df_auto.iterrows():
                        question = row['question']
                        answer = row['answer']
                        if pd.notna(question) and pd.notna(answer) and question.strip() and answer.strip():
                            if not FAQ.objects.filter(question=question.strip()).exists():
                                FAQ.objects.create(
                                    question=question.strip(),
                                    answer_en=answer.strip(),
                                    category='auto_insurance'
                                )
                except Exception as e:
                    print(f"Error loading auto insurance FAQs: {e}")

        # Load home_insurance.csv
        home_csv_path = os.path.join(os.path.dirname(__file__), 'home_insurance.csv')
        if os.path.exists(home_csv_path):
            df_home = pd.read_csv(home_csv_path, encoding='utf-8-sig')
            if 'question' in df_home.columns and 'answer' in df_home.columns:
                try:
                    for index, row in df_home.iterrows():
                        question = row['question']
                        answer = row['answer']
                        if pd.notna(question) and pd.notna(answer) and question.strip() and answer.strip():
                            if not FAQ.objects.filter(question=question.strip()).exists():
                                FAQ.objects.create(
                                    question=question.strip(),
                                    answer_en=answer.strip(),
                                    category='home_insurance'
                                )
                except Exception as e:
                    print(f"Error loading home insurance FAQs: {e}")

        # Load life_insurance.csv
        life_csv_path = os.path.join(os.path.dirname(__file__), 'life_insurance.csv')
        if os.path.exists(life_csv_path):
            df_life = pd.read_csv(life_csv_path, encoding='utf-8-sig')
            if 'question' in df_life.columns and 'answer' in df_life.columns:
                try:
                    for index, row in df_life.iterrows():
                        question = row['question']
                        answer = row['answer']
                        if pd.notna(question) and pd.notna(answer) and question.strip() and answer.strip():
                            if not FAQ.objects.filter(question=question.strip()).exists():
                                FAQ.objects.create(
                                    question=question.strip(),
                                    answer_en=answer.strip(),
                                    category='life_insurance'
                                )
                except Exception as e:
                    print(f"Error loading life insurance FAQs: {e}")

        # Load travel_insurance.csv
        travel_csv_path = os.path.join(os.path.dirname(__file__), 'travel_insurance.csv')
        if os.path.exists(travel_csv_path):
            df_travel = pd.read_csv(travel_csv_path, encoding='utf-8-sig')
            if 'question' in df_travel.columns and 'answer' in df_travel.columns:
                try:
                    for index, row in df_travel.iterrows():
                        question = row['question']
                        answer = row['answer']
                        if pd.notna(question) and pd.notna(answer) and question.strip() and answer.strip():
                            if not FAQ.objects.filter(question=question.strip()).exists():
                                FAQ.objects.create(
                                    question=question.strip(),
                                    answer_en=answer.strip(),
                                    category='travel_insurance'
                                )
                except Exception as e:
                    print(f"Error loading travel insurance FAQs: {e}")

        # Load business_insurance.csv
        business_csv_path = os.path.join(os.path.dirname(__file__), 'business_insurance.csv')
        if os.path.exists(business_csv_path):
            df_business = pd.read_csv(business_csv_path, encoding='utf-8-sig')
            if 'question' in df_business.columns and 'answer' in df_business.columns:
                try:
                    for index, row in df_business.iterrows():
                        question = row['question']
                        answer = row['answer']
                        if pd.notna(question) and pd.notna(answer) and question.strip() and answer.strip():
                            if not FAQ.objects.filter(question=question.strip()).exists():
                                FAQ.objects.create(
                                    question=question.strip(),
                                    answer_en=answer.strip(),
                                    category='business_insurance'
                                )
                except Exception as e:
                    print(f"Error loading business insurance FAQs: {e}")

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

    # 2. Insurance category detection
    auto_keywords = ['auto', 'car', 'vehicle', 'driving', 'accident', 'collision', 'comprehensive', 'liability', 'auto insurance', 'car insurance', 'vehicle insurance']
    home_keywords = ['home', 'house', 'property', 'dwelling', 'homeowner', 'home insurance', 'house insurance', 'property insurance']
    life_keywords = ['life', 'life insurance', 'term life', 'whole life', 'universal life', 'permanent life']
    travel_keywords = ['travel', 'trip', 'vacation', 'travel insurance', 'trip insurance', 'journey']
    business_keywords = ['business', 'commercial', 'company', 'corporate', 'enterprise', 'business insurance', 'commercial insurance', 'liability insurance', 'workers compensation', 'professional liability']

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

    # 2. Renewal keywords
    if any(word in text_lower for word in ["renew", "renewal", "रिन्यू", "नवीनीकरण"]):
        return {"intent": "renew_policy", "claim_id": None, "lang": lang}

    # 3. Document keywords
    if any(word in text_lower for word in ["document", "papers", "कागजात", "दस्तावेज"]):
        return {"intent": "documents_needed", "claim_id": None, "lang": lang}

    # 4. Policy customization
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

# Enhanced FAQ search using semantic similarity with SentenceTransformer
def search_faqs(query, limit=3, lang='en', category=None):
    # Preprocess query
    query = preprocess_query(query)

    try:
        from sentence_transformers import SentenceTransformer, util
        import torch

        if not query.strip():
            return []

        if category:
            faqs = FAQ.objects.filter(category=category)
        else:
            faqs = FAQ.objects.filter(tags__icontains="insurance")
        if not faqs:
            faqs = FAQ.objects.all()
        if not faqs:
            return []

        # Use semantic similarity
        model = SentenceTransformer('all-MiniLM-L6-v2')
        questions = [f.question for f in faqs]
        faq_embeddings = model.encode(questions, convert_to_tensor=True)
        query_embedding = model.encode(query, convert_to_tensor=True)

        similarities = [util.cos_sim(query_embedding, emb).item() for emb in faq_embeddings]

        # Get top matches with threshold
        matches = []
        for idx, score in enumerate(similarities):
            if score > 0.45:  # Threshold for semantic similarity
                f = faqs[idx]
                answer = f.answer_hi if lang == 'hi' else f.answer_en
                matches.append({"question": f.question, "answer": answer, "score": score})

        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:limit]

    except ImportError:
        # Fallback to TF-IDF if sentence-transformers not available
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.feature_extraction.text import TfidfVectorizer

        if not query.strip():
            return []

        if category:
            faqs = FAQ.objects.filter(category=category)
        else:
            faqs = FAQ.objects.filter(tags__icontains="insurance")
        if not faqs:
            faqs = FAQ.objects.all()
        if not faqs:
            return []

        questions = [f.question for f in faqs]
        tags = [f.tags or "" for f in faqs]
        combined_texts = [q + " " + t for q, t in zip(questions, tags)]

        tfidf = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = tfidf.fit_transform(combined_texts)
        query_vec = tfidf.transform([query])
        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

        matches = []
        for idx, score in enumerate(similarities):
            if score > 0.2:
                f = faqs[idx]
                answer = f.answer_hi if lang == 'hi' else f.answer_en
                matches.append({"question": f.question, "answer": answer, "score": score})
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:limit]