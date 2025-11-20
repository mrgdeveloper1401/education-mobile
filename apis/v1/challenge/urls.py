from rest_framework.routers import SimpleRouter

from .views import ChallengeViewSet

app_name = "v1_challenge"

router = SimpleRouter()

router.register("list", ChallengeViewSet, basename="challenge")

urlpatterns = router.urls