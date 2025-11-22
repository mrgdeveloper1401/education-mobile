from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ChallengeViewSet, SubmitChallengeView

app_name = "v1_challenge"

router = SimpleRouter()

router.register("list", ChallengeViewSet, basename="challenge")

urlpatterns = [
    path("list/<int:pk>/submit/", SubmitChallengeView.as_view(), name="submit-challenge"),
] + router.urls
