from django.urls import path, include
from rest_framework.routers import DefaultRouter
from entradas.api.views import PaseViewSet, CompraViewSet
from .views import ComprarEntradasView, ValidarCompraView  # 👈 corregido

router = DefaultRouter()
router.register(r'pases', PaseViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # reemplazamos /entradas/ por tu vista
    path('compras/', ComprarEntradasView.as_view(), name='comprar_entradas'),
    path('validar-compra/', ValidarCompraView.as_view(), name='validar_compra'),
]