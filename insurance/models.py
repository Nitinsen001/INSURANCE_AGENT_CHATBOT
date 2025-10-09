from django.db import models

# Create your models here.
class Claim(models.Model):
    claim_id = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=150)
    claim_type = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.claim_id} - {self.status}"


class FAQ(models.Model):
    question = models.TextField()
    answer_en = models.TextField(default="", help_text="Answer in English")
    answer_hi = models.TextField(default="", help_text="Answer in Hindi")
    tags = models.CharField(max_length=200, blank=True, help_text="comma separated tags")
    category = models.CharField(max_length=50, default='general', help_text="Category like 'general', 'auto_insurance'")

    @property
    def answer(self):
        # Backward compatibility, return English by default
        return self.answer_en or self.answer_hi

    def __str__(self):
        return self.question[:80]


class TrainingExample(models.Model):
    text = models.TextField(help_text="User utterance")
    intent = models.CharField(max_length=100, help_text="Intent label")

    def __str__(self):
        return f"{self.text[:50]} -> {self.intent}"