from rest_framework.urls import path

from apis.v1.gateway.views import GatewayView

app_name = 'v1_gateway'

urlpatterns = [
    path('request_gateway/', GatewayView.as_view(), name='gateway'),
]
