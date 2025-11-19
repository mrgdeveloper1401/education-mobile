from django.urls import path

from .views import ListSubscriptionView

app_name = "v1_subscription"

urlpatterns = [
    path("list/", ListSubscriptionView.as_view(), name="subscription-list"),
]
