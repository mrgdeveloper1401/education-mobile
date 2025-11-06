from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

app_name = "v1_auth"

urlpatterns = [
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("request_otp_phone/", views.RequestOtpView.as_view(), name='request_otp_phone'),
    path("otp_verify/", views.OtpVerifyView.as_view(), name='otp_verify'),
]
