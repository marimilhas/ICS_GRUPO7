from django.urls import path
from . import views

urlpatterns = [
    path('compras/', views.CompraCreateView.as_view(), name='comprar_entradas'),
    path('pases/', views.PaseListView.as_view(), name='lista_pases'),  # Para cargar pases
]
