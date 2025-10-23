# entradas/urls.py
from django.urls import path
from .views import comprar_entradas_view

urlpatterns = [
    path('comprar/', comprar_entradas_view, name='comprar_entradas'),
]
