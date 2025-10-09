from django.contrib import admin
from .models import Claim, FAQ, TrainingExample

admin.site.register(Claim)
admin.site.register(FAQ)
admin.site.register(TrainingExample)
