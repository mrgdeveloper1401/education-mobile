from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ListSubscriptionView, InstallmentPlanViewSet, UserSubscriptionView

app_name = "v1_subscription"

router = SimpleRouter()
router.register("list", ListSubscriptionView, basename="subscription")
router.register("installment", InstallmentPlanViewSet, basename="installment")

urlpatterns = [
    path("user_subscription/", UserSubscriptionView.as_view(), name="user-subscription"),
] + router.urls
