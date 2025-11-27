from rest_framework.urls import path
from rest_framework.routers import SimpleRouter

from apis.v1.gateway.views import GatewayView, VerifyPayment, ListRetrieveGatewayViewSet


app_name = 'v1_gateway'

router = SimpleRouter()

router.register('gateway', ListRetrieveGatewayViewSet, basename='gateway')

urlpatterns = [
    path('request_gateway/', GatewayView.as_view(), name='gateway'),
    path("verify_payment/", VerifyPayment.as_view(), name='verify_payment'),
] + router.urls
