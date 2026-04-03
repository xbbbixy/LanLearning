from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_sentence, name='analyze'),
    path('define/', views.get_word_definition, name='define'),
]
