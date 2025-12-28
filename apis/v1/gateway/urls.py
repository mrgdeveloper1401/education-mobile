from rest_framework.urls import path
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter

from apis.v1.gateway.views import (
    GatewayView,
    VerifyPayment,
    ListRetrieveGatewayViewSet,
    ListRetrieveResultGateWayViewSet,
    CheckSubscriptionView
)


app_name = 'v1_gateway'

router = SimpleRouter()

router.register('gateway', ListRetrieveGatewayViewSet, basename='gateway')

gateway_router = NestedSimpleRouter(router, 'gateway', lookup='gateway')
gateway_router.register("result_gateway", ListRetrieveResultGateWayViewSet, basename='result_gateway')

urlpatterns = [
    path('request_gateway/', GatewayView.as_view(), name='gateway'),
    path("verify_payment/", VerifyPayment.as_view(), name='verify_payment'),
    path("check_active_plan/", CheckSubscriptionView.as_view(), name='check_active_plan')
] + router.urls + gateway_router.urls
