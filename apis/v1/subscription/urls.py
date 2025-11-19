from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ListSubscriptionView

app_name = "v1_subscription"

router = SimpleRouter()
router.register("list", ListSubscriptionView, basename="subscription")

urlpatterns = [
] + router.urls
