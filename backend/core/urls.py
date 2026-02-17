from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet, AccountViewSet, AccountHistoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'account-history', AccountHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]