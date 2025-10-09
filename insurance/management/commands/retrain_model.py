from django.core.management.base import BaseCommand
from insurance.nlp import *  # This will trigger retraining

class Command(BaseCommand):
    help = 'Retrains the NLP model with updated data'

    def handle(self, *args, **options):
        self.stdout.write('Retraining model...')
        # Importing nlp triggers the training if model doesn't exist
        # But since we want to force retrain, we need to delete files first
        import os
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'intent_model.pkl')
        vectorizer_path = os.path.join(os.path.dirname(__file__), '..', '..', 'vectorizer.pkl')
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(vectorizer_path):
            os.remove(vectorizer_path)
        # Clear and reload FAQs
        from insurance.models import FAQ
        FAQ.objects.all().delete()
        self.stdout.write('FAQs cleared.')
        # Now import to retrain
        import insurance.nlp
        # Reload FAQs
        insurance.nlp.load_faqs()
        self.stdout.write(self.style.SUCCESS('Model retrained and FAQs reloaded successfully'))