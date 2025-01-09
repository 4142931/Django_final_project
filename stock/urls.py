from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_recommendations, name='stock_recommendations'),
]