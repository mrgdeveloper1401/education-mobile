from rest_framework.routers import SimpleRouter

from .views import ListSubscriptionView, InstallmentPlanViewSet

app_name = "v1_subscription"

router = SimpleRouter()
router.register("list", ListSubscriptionView, basename="subscription")
router.register("installment", InstallmentPlanViewSet, basename="installment")

urlpatterns = [
] + router.urls
