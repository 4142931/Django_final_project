from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.example_view, name='recommend_news'),
]
