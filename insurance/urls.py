
from django.urls import path
from . import views
urlpatterns = [
path("", views.chat_ui, name="chat_ui"),
path("api/query/", views.api_query, name="api_query"),
]