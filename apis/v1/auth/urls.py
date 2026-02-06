from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView, TokenBlacklistView
from rest_framework.routers import SimpleRouter
from . import views

app_name = "v1_auth"

router = SimpleRouter()
router.register("profile", views.UserProfileView, basename="profile")

urlpatterns = [
    # jwt token
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    #otp
    path("request_otp_phone/", views.RequestOtpView.as_view(), name='request_otp_phone'),
    path("login_by_phone_password/", views.LoginByPhonePasswordView.as_view(), name='login_by_phone_password'),
    path("signup_user/", views.UserSignUpView.as_view(), name='signup_user'),
    path("otp_verify/", views.OtpVerifyView.as_view(), name='otp_verify'),
    path('upload_photo_by_user/', views.UploadImageView.as_view(), name='upload_photo_by_user'),
] + router.urls
