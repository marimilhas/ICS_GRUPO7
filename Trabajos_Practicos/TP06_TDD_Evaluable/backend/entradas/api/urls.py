from django.urls import path, include
from rest_framework.routers import DefaultRouter
from entradas.api.views import PaseViewSet, CompraViewSet, EntradaViewSet

router = DefaultRouter()
router.register(r'pases', PaseViewSet)
router.register(r'compras', CompraViewSet)
router.register(r'entradas', EntradaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
