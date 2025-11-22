from rest_framework.urls import path

from apis.v1.gateway.views import GatewayView, VerifyPayment

app_name = 'v1_gateway'

urlpatterns = [
    path('request_gateway/', GatewayView.as_view(), name='gateway'),
    path("verify_payment/", VerifyPayment.as_view(), name='verify_payment'),
]
