from django.urls import path
from . import views
from .views import comprar_entradas_view

urlpatterns = [
    # Esta ruta se resuelve como: /api/ + comprar/ = /api/comprar/
    path('comprar/', comprar_entradas_view, name='comprar_entradas'),
]
