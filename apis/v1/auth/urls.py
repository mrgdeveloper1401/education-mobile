from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework.routers import SimpleRouter
from . import views

app_name = "v1_auth"

router = SimpleRouter()
router.register("profile", views.UserProfileView, basename="profile")

urlpatterns = [
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("request_otp_phone/", views.RequestOtpView.as_view(), name='request_otp_phone'),
    path("otp_verify/", views.OtpVerifyView.as_view(), name='otp_verify'),
] + router.urls
