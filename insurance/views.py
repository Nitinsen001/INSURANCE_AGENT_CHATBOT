from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Claim
from .nlp import detect_intent_and_entities, search_faqs
import logging
import random

logger = logging.getLogger(__name__)

# Create your views here.
def chat_ui(request):
    """Return chat HTML page"""
    return render(request, "insurance/chat.html")

@csrf_exempt
def api_query(request):
    """Single endpoint that accepts user text and returns bot response JSON"""
    try:
        text = request.GET.get("text", "").strip()

        if not text:
            return JsonResponse({"error": "No text provided."}, status=400)
        intent_data = detect_intent_and_entities(text)
        intent = intent_data.get("intent")
        lang = intent_data.get("lang", "en")
        category = intent_data.get("category")

        # Reset is_detailed for new requests
        request.session['is_detailed'] = False
        request.session.save()

        # Handle more_details intent
        if intent == "more_details":
            last_intent = request.session.get('last_intent')
            if last_intent:
                intent = last_intent
                # Mark that this is a detailed response
                request.session['is_detailed'] = True
            else:
                if lang == "hi":
                    return JsonResponse({"type": "error", "text": "क्षमा करें, मुझे पिछली बातचीत का संदर्भ नहीं मिला। कृपया अपना प्रश्न फिर से बताएं।"})
                else:
                    return JsonResponse({"type": "error", "text": "Sorry, I don't have context from previous conversation. Please ask your question again."})
        else:
            # Store current intent for future "more details" requests
            request.session['last_intent'] = intent
            request.session['last_query'] = text
            request.session['is_detailed'] = False
        # handle claim status with claim id
        if intent == "check_claim_status":
            claim_id = intent_data.get("claim_id")
            if claim_id:
                try:
                    claim = Claim.objects.get(claim_id=claim_id)
                    from django.utils import timezone
                    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                    if lang == "hi":
                        resp_text = (
                            f"दावा आईडी {claim.claim_id} {claim.customer_name} के लिए वर्तमान में '{claim.status}' है। "
                            f"प्रकार: {claim.claim_type}. राशि: {float(claim.amount):.2f}। "
                            f"अंतिम अपडेट: {claim.created_at.strftime('%Y-%m-%d')}। यदि स्थिति 'Approved' है, तो भुगतान जल्द ही किया जाएगा।"
                        )
                    else:
                        resp_text = (
                            f"Claim ID {claim.claim_id} for {claim.customer_name} is currently '{claim.status}'. "
                            f"Type: {claim.claim_type}. Amount: {float(claim.amount):.2f}. "
                            f"Last updated: {claim.created_at.strftime('%Y-%m-%d')}. If approved, settlement will follow soon."
                        )
                    return JsonResponse({"type": "claim_status", "text": resp_text,
                    "data": {
                        "claim_id": claim.claim_id,
                        "status": claim.status,
                        "amount": float(claim.amount),
                        "claim_type": claim.claim_type,
                        "last_updated": claim.created_at.strftime('%Y-%m-%d'),
                        "checked_at": current_time,
                    }})
                except Claim.DoesNotExist:
                    if lang == "hi":
                        return JsonResponse({"type": "error", "text": "दावा आईडी नहीं मिला। कृपया अपना दावा आईडी जांचें और पुनः प्रयास करें।"})
                    else:
                        return JsonResponse({"type": "error", "text": "Claim ID not found. Please check your Claim ID and try again."})
            else:
                # user asked about claim status but no id given
                if lang == "hi":
                    return JsonResponse({"type": "followup", "text": "अपना दावा आईडी दें (उदाहरण: दावा आईडी = 12345) ताकि मैं स्थिति जांच सकूं।"})
                else:
                    return JsonResponse({"type": "followup", "text": "Please provide your Claim ID (e.g. Claim ID = 12345) so I can check the status."})
        # handle specific intents
        if intent == "what_is_insurance":
            is_detailed = request.session.get('is_detailed', False)
            if is_detailed:
                if lang == "hi":
                    detailed_text = ("बीमा एक वित्तीय उत्पाद है जो अप्रत्याशित घटनाओं से होने वाले नुकसान को कवर करता है। यह विभिन्न प्रकार का होता है जैसे स्वास्थ्य बीमा, ऑटो बीमा, घर बीमा, जीवन बीमा आदि। बीमा कंपनियां प्रीमियम के बदले में जोखिम वहन करती हैं और दावा होने पर राशि का भुगतान करती हैं। बीमा लेने से व्यक्ति की वित्तीय सुरक्षा बढ़ती है और परिवार को आर्थिक संकट से बचाया जा सकता है।")
                else:
                    detailed_text = ("Insurance is a financial product that covers losses from unexpected events. It comes in various types like health insurance, auto insurance, home insurance, life insurance, etc. Insurance companies bear the risk in exchange for premiums and pay out claims when incidents occur. Having insurance increases a person's financial security and can protect the family from economic crises.")
                return JsonResponse({"type": "faq", "text": detailed_text})
            else:
                faqs = search_faqs("What is insurance?", lang=lang)
                if faqs:
                    return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
                else:
                    if lang == "hi":
                        return JsonResponse({"type": "faq", "text": "बीमा एक अनुबंध है जो नुकसान के खिलाफ वित्तीय सुरक्षा प्रदान करता है।"})
                    else:
                        return JsonResponse({"type": "faq", "text": "Insurance is a contract that provides financial protection against losses."})
        if intent == "how_to_apply":
            faqs = search_faqs("How to apply for insurance?", lang=lang)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "बीमा के लिए आवेदन करने के लिए, हमारी वेबसाइट पर जाएं या हमारे एजेंट से संपर्क करें।"})
                else:
                    return JsonResponse({"type": "faq", "text": "To apply for insurance, visit our website or contact our agent."})
        if intent == "why_insurance":
            faqs = search_faqs("Why insurance is important?", lang=lang)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "बीमा वित्तीय सुरक्षा प्रदान करता है और अप्रत्याशित घटनाओं से बचाता है।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Insurance provides financial protection against unexpected events."})
        if intent == "documents_needed":
            # Context-aware response
            last_intent = request.session.get('last_intent')
            if last_intent in ['what_is_insurance', 'life_insurance_benefits', 'renew_policy', 'policy_suggestion', 'apply_for_insurance']:
                # Direct response for insurance documents
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "बीमा के लिए आवश्यक दस्तावेजों में पहचान प्रमाण (पैन कार्ड, आधार कार्ड), पता प्रमाण, आय प्रमाण, और मेडिकल रिपोर्ट (स्वास्थ्य बीमा के लिए) शामिल हैं। कृपया विशिष्ट बीमा प्रकार बताएं अधिक जानकारी के लिए।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Documents needed for insurance include ID proof (PAN card, Aadhaar), address proof, income proof, and medical reports (for health insurance). Please specify the insurance type for more details."})
            else:
                faqs = search_faqs("What documents are required for insurance?", lang=lang)
                if faqs:
                    return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
                else:
                    if lang == "hi":
                        return JsonResponse({"type": "faq", "text": "बीमा के लिए आवश्यक दस्तावेजों में पहचान प्रमाण, पता प्रमाण और आय प्रमाण शामिल हैं।"})
                    else:
                        return JsonResponse({"type": "faq", "text": "Documents needed for insurance include ID proof, address proof, and income proof."})
        if intent == "types_of_insurance":
            faqs = search_faqs("Types of insurance", lang=lang)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "बीमा के प्रकार: स्वास्थ्य, जीवन, ऑटो, घर, यात्रा आदि।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Types of insurance: Health, Life, Auto, Home, Travel, etc."})
        if intent == "health_insurance":
            faqs = search_faqs("What is health insurance?", lang=lang)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "स्वास्थ्य बीमा चिकित्सा व्ययों को कवर करता है।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Health insurance covers medical expenses."})
        if intent == "health_insurance_family":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "परिवार स्वास्थ्य बीमा के लिए, हम परिवार योजनाएं प्रदान करते हैं जो पति-पत्नी और बच्चों को कवर करती हैं। कृपया परिवार के सदस्यों की संख्या और आयु बताएं।"})
            else:
                return JsonResponse({"type": "faq", "text": "For family health insurance, we offer family plans that cover spouses and children with comprehensive medical coverage. Could you tell me how many family members you'd like to cover and their ages?"})
        if intent == "health_insurance_individual":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "व्यक्तिगत स्वास्थ्य बीमा के लिए, हम व्यक्तिगत योजनाएं प्रदान करते हैं जो केवल आपकी चिकित्सा व्ययों को कवर करती हैं। कृपया अधिक जानकारी के लिए हमसे संपर्क करें।"})
            else:
                return JsonResponse({"type": "faq", "text": "For individual health insurance, we offer individual plans that cover only your medical expenses. Please contact us for more details."})
        if intent == "health_insurance_parents":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "माता-पिता के स्वास्थ्य बीमा के लिए, हम विशेष योजनाएं प्रदान करते हैं जो बुजुर्गों की चिकित्सा आवश्यकताओं को कवर करती हैं। कृपया उनके आयु और स्वास्थ्य स्थिति के बारे में बताएं।"})
            else:
                return JsonResponse({"type": "faq", "text": "For parents' health insurance, we offer special plans that cover seniors' medical needs. Please tell me about their ages and health conditions."})
        if intent == "compare_plans":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "हम विभिन्न स्वास्थ्य बीमा योजनाओं की तुलना करने में मदद कर सकते हैं। कृपया अपनी आवश्यकताएं बताएं जैसे परिवार का आकार, बजट आदि।"})
            else:
                return JsonResponse({"type": "faq", "text": "We can help you compare different health insurance plans. Please tell us your requirements like family size, budget, etc."})
        if intent == "health_plans":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "हमारे स्वास्थ्य बीमा योजनाओं में व्यक्तिगत, परिवार और वरिष्ठ नागरिक योजनाएं शामिल हैं। अधिक जानकारी के लिए संपर्क करें।"})
            else:
                return JsonResponse({"type": "faq", "text": "Our health insurance plans include individual, family, and senior citizen plans. Contact us for more details."})
        if intent == "find_doctors":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "हमारे नेटवर्क में डॉक्टर खोजने के लिए, हमारी वेबसाइट पर जाएं या ऐप डाउनलोड करें। आप अपने स्थान के आधार पर डॉक्टर ढूंढ सकते हैं।"})
            else:
                return JsonResponse({"type": "faq", "text": "To find doctors in our network, visit our website or download the app. You can search doctors based on your location."})
        if intent == "pharmacy":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "दवा कवरेज और फार्मेसी स्थान जांचने के लिए, हमारी वेबसाइट पर जाएं या ग्राहक सेवा से संपर्क करें।"})
            else:
                return JsonResponse({"type": "faq", "text": "To check drug coverage and pharmacy locations, visit our website or contact customer service."})
        if intent == "policy_details":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "पॉलिसी विवरण देखने के लिए, अपने खाते में लॉग इन करें या ग्राहक सेवा से संपर्क करें।"})
            else:
                return JsonResponse({"type": "faq", "text": "To view policy details, log in to your account or contact customer service."})
        if intent == "update_policy":
            if lang == "hi":
                return JsonResponse({"type": "faq", "text": "पॉलिसी अपडेट करने के लिए, अपने खाते में लॉग इन करें और 'Update Policy' विकल्प चुनें।"})
            else:
                return JsonResponse({"type": "faq", "text": "To update your policy, log in to your account and select the 'Update Policy' option."})
        if intent == "life_insurance_benefits":
            is_detailed = request.session.get('is_detailed', False)
            if is_detailed:
                if lang == "hi":
                    detailed_text = ("जीवन बीमा कई प्रकार के लाभ प्रदान करता है: 1) परिवार को वित्तीय सुरक्षा - बीमाधारक की मृत्यु के बाद परिवार को बड़ी राशि मिलती है। 2) टैक्स लाभ - प्रीमियम पर टैक्स छूट मिलती है। 3) ऋण सुरक्षा - पॉलिसी को गिरवी रखकर ऋण लिया जा सकता है। 4) बचत - कुछ पॉलिसी में कैश वैल्यू जमा होती है। 5) व्यापक कवरेज - दुर्घटना या बीमारी से मृत्यु पर भी लाभ मिलता है।")
                else:
                    detailed_text = ("Life insurance provides several benefits: 1) Financial security for family - Family receives a lump sum after the insured's death. 2) Tax benefits - Tax deductions on premiums. 3) Loan security - Policy can be used as collateral for loans. 4) Savings - Some policies accumulate cash value. 5) Comprehensive coverage - Benefits even in case of accidental or illness-related death.")
                return JsonResponse({"type": "faq", "text": detailed_text})
            else:
                faqs = search_faqs("Life insurance benefits", lang=lang)
                if faqs:
                    return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
                else:
                    if lang == "hi":
                        return JsonResponse({"type": "faq", "text": "जीवन बीमा लाभ: परिवार को वित्तीय सुरक्षा।"})
                    else:
                        return JsonResponse({"type": "faq", "text": "Life insurance benefits: Financial security for family."})
        if intent == "renew_policy":
            is_detailed = request.session.get('is_detailed', False)
            if is_detailed:
                if lang == "hi":
                    detailed_text = ("पॉलिसी रिन्यू करने के लिए: 1) अपनी पॉलिसी नंबर जांचें। 2) एक्सपायरी डेट से 30 दिन पहले रिन्यू करें। 3) ऑनलाइन पोर्टल या मोबाइल ऐप पर लॉग इन करें। 4) रिन्यू बटन पर क्लिक करें। 5) भुगतान विधि चुनें (क्रेडिट कार्ड, डेबिट कार्ड, नेट बैंकिंग)। 6) पेमेंट कन्फर्मेशन प्राप्त करें। 7) रिन्यूड पॉलिसी डॉक्यूमेंट डाउनलोड करें। समय पर रिन्यू न करने पर पॉलिसी कैंसल हो सकती है।")
                else:
                    detailed_text = ("To renew your policy: 1) Check your policy number. 2) Renew 30 days before expiry date. 3) Login to online portal or mobile app. 4) Click renew button. 5) Choose payment method (credit card, debit card, net banking). 6) Receive payment confirmation. 7) Download renewed policy document. Failure to renew on time may result in policy cancellation.")
                return JsonResponse({"type": "faq", "text": detailed_text})
            else:
                faqs = search_faqs("how to renew my policy", lang=lang)
                if faqs:
                    return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
                else:
                    if lang == "hi":
                        return JsonResponse({"type": "faq", "text": "पॉलिसी रिन्यू के लिए वेबसाइट पर जाएं और भुगतान करें।"})
                    else:
                        return JsonResponse({"type": "faq", "text": "To renew your policy, visit the website and make payment."})
        if intent == "policy_suggestion":
            faqs = search_faqs("suggest best policy", lang=lang)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "आपके लिए सबसे अच्छी पॉलिसी सुझाने के लिए अधिक जानकारी दें।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Provide more details to suggest the best policy for you."})
        if intent == "small_talk":
            if lang == "hi":
                return JsonResponse({"type": "small_talk", "text": "मैं ठीक हूं, धन्यवाद! आप कैसे हैं?"})
            else:
                return JsonResponse({"type": "small_talk", "text": "I'm doing well, thanks! How about you?"})
        if intent == "apply_for_insurance":
            faqs = search_faqs("I want to take insurance", lang=lang)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "बेहतरीन! बीमा प्राप्त करने के लिए, प्रकार निर्दिष्ट करें और अपने विवरण प्रदान करें।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Great! To get insurance, specify the type and provide your details."})
        # handle small talk
        if intent == "greeting":
            if lang == "hi":
                responses = ["नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?", "नमस्ते! क्या मैं आपकी मदद कर सकता हूं?", "हैलो! आज मैं आपकी कैसे सहायता कर सकता हूं?"]
                return JsonResponse({"type": "greeting", "text": random.choice(responses)})
            else:
                responses = ["Hello! How can I help you today?", "Hi there! Need any assistance?", "Hey! What can I do for you today?"]
                return JsonResponse({"type": "greeting", "text": random.choice(responses)})
        if intent == "thanks":
            if lang == "hi":
                return JsonResponse({"type": "thanks", "text": "आपका स्वागत है! यदि कोई और सवाल है तो पूछें।"})
            else:
                return JsonResponse({"type": "thanks", "text": "You're welcome! Feel free to ask if you have more questions."})
        if intent == "acknowledge":
            if lang == "hi":
                return JsonResponse({"type": "acknowledge", "text": "ठीक है! क्या आप कुछ और जानना चाहेंगे?"})
            else:
                return JsonResponse({"type": "acknowledge", "text": "Okay! Would you like to know anything else?"})
        # handle ask claim status
        if intent == "ask_claim_status":
            if lang == "hi":
                return JsonResponse({"type": "followup", "text": "अपना दावा आईडी दें (उदाहरण: दावा आईडी = 12345) ताकि मैं स्थिति जांच सकूं।"})
            else:
                return JsonResponse({"type": "followup", "text": "Please provide your Claim ID (e.g. Claim ID = 12345) so I can check the status."})
        # handle document intent (from CSV)
        if intent == "document":
            # Make it context-aware
            last_intent = request.session.get('last_intent')
            search_query = "documents needed for insurance" if last_intent in ['what_is_insurance', 'life_insurance_benefits', 'renew_policy', 'policy_suggestion', 'apply_for_insurance'] else "documents needed"
            faqs = search_faqs(search_query, lang=lang, category=category)
            if faqs:
                return JsonResponse({"type": "faq", "text": faqs[0]["answer"], "question": faqs[0]["question"]})
            else:
                if lang == "hi":
                    return JsonResponse({"type": "faq", "text": "बीमा के लिए आवश्यक दस्तावेजों में पहचान प्रमाण, पता प्रमाण और आय प्रमाण शामिल हैं।"})
                else:
                    return JsonResponse({"type": "faq", "text": "Documents needed for insurance include ID proof, address proof, and income proof."})
        # handle FAQ
        if intent == "faq":
            is_detailed = request.session.get('is_detailed', False)
            if is_detailed:
                # For detailed response, check the last query to provide relevant details
                last_query = request.session.get('last_query', '').lower()
                if 'creditor' in last_query or 'take' in last_query:
                    # Provide more details about creditors and life insurance
                    if lang == "hi":
                        response_text = "क्रेडिटर जीवन बीमा के बाद ले सकते हैं यदि बीमा राशि मृतक की संपत्ति में जाए। प्रोबेट के दौरान क्रेडिटर दावा कर सकते हैं। हालांकि, यदि लाभार्थी कोई व्यक्ति है, तो क्रेडिटर लाभ नहीं ले सकते। अपवाद: यदि लाभार्थी ऋण का सह-हस्ताक्षरकर्ता है। अतिरिक्त जानकारी: जीवन बीमा पॉलिसी को सही तरीके से नामांकित करना महत्वपूर्ण है ताकि परिवार सुरक्षित रहे।"
                    else:
                        response_text = "Creditors can take life insurance after death if the proceeds go to the deceased's estate. They can claim during probate. However, if the beneficiary is a person, creditors cannot take the benefit. Exceptions: If the beneficiary is a co-signer to the debt. Additional info: Properly naming beneficiaries on life insurance policies is crucial to protect the family."
                    return JsonResponse({"type": "faq", "text": response_text,
                    "question": "More details about creditors and life insurance"})
                else:
                    # General detailed response
                    if lang == "hi":
                        response_text = "जीवन बीमा कई प्रकार के लाभ प्रदान करता है: 1) परिवार को वित्तीय सुरक्षा। 2) टैक्स लाभ। 3) ऋण सुरक्षा। 4) बचत। 5) व्यापक कवरेज। अधिक जानकारी के लिए हमसे संपर्क करें।"
                    else:
                        response_text = "Life insurance provides several benefits: 1) Financial security for family. 2) Tax benefits. 3) Loan security. 4) Savings. 5) Comprehensive coverage. Contact us for more information."
                    return JsonResponse({"type": "faq", "text": response_text,
                    "question": "More details about life insurance"})
            else:
                # Normal FAQ search - make it context-aware
                last_intent = request.session.get('last_intent')
                search_query = text

                # If last intent was insurance-related and current query mentions "it" or "document", make it more specific
                if last_intent in ['what_is_insurance', 'life_insurance_benefits', 'renew_policy', 'policy_suggestion', 'apply_for_insurance'] and ('it' in text.lower() or 'document' in text.lower() or 'documents' in text.lower()):
                    if 'document' in text.lower() or 'documents' in text.lower():
                        search_query = "documents needed for insurance"
                    else:
                        search_query = "insurance " + text

                faqs = search_faqs(search_query, lang=lang)
                if faqs:
                    # return top match with dynamic enhancement
                    top = faqs[0]
                    response_text = top["answer"]
                    # Add dynamic suggestion if more matches exist
                    if len(faqs) > 1:
                        if lang == "hi":
                            response_text += f" यदि आप और जानना चाहते हैं, तो '{faqs[1]['question']}' के बारे में पूछें।"
                        else:
                            response_text += f" If you'd like more info, ask about '{faqs[1]['question']}'."
                    # Store this FAQ for potential "more details" request
                    request.session['last_faq_question'] = top['question']
                    request.session['last_faq_answer'] = top['answer']
                    request.session.save()
                    return JsonResponse({"type": "faq", "text": response_text,
                    "question": top["question"]})
                else:
                    # No good FAQ match -> escalate
                    if lang == "hi":
                        return JsonResponse({"type": "escalate", "text": "आपकी क्वेरी थोड़ी जटिल है। मैं इसे मानव एजेंट को फॉरवर्ड कर रहा हूं। यदि आप फॉलो-अप चाहते हैं तो संपर्क विवरण साझा करें।"})
                    else:
                        return JsonResponse({"type": "escalate", "text": "Your query is a bit complex. I am forwarding it to a human agent. Please share contact details if you want follow-up."})
        # default fallback
        if lang == "hi":
            return JsonResponse({"type": "escalate", "text": "माफ करें, मैं आपकी बात समझ नहीं पाया। कृपया फिर से कहें या दावा आईडी प्रदान करें।"})
        else:
            return JsonResponse({"type": "escalate", "text": "Sorry, I didn't understand your message. Please rephrase or provide Claim ID."})
    except Exception as e:
        logger.error(f"Error in api_query: {str(e)}")
        return JsonResponse({"type": "error", "text": "An internal error occurred. Please try again later."}, status=500)