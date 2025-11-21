from adrf.views import APIView

from base.clasess.gateway import Gateway
from gateway_app.models import Gateway as GatewayModel
from .serializer import GatewaySerializer
from ...utils.custom_permissions import AsyncIsAuthenticated
from ...utils.custom_response import response


class GatewayView(APIView):
    serializer_class = GatewaySerializer
    permission_classes = (AsyncIsAuthenticated,)

    async def post(self, request):
        import ipdb
        ipdb.set_trace()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get user id
        user = await request.auser()
        user_id = user.id

        # get phone by user
        phone = user.mobile_phone

        # data
        price = serializer.validated_data['subscription'].discounted_price
        subscription_id = serializer.validated_data['subscription'].id
        description = serializer.validated_data['description']

        # request gateway
        gate_way = Gateway()
        result = await gate_way.request_payment(
            amount=price,
            description=description,
            order_id=subscription_id,
            mobile=phone,
        )

        # check result
        if result['result'] == 100:
            await GatewayModel.objects.acreate(
                user_id=user_id,
                subscription_id=subscription_id,
                track_id=result['track_id'],
                message_gateway=result['message'],
                result_gateway=result['result'],
            )
            return response(
                status_code=201,
                status=True,
                error=False,
                data=result,
                message="پردازش با موفقیت انجام شد"
            )
        else:
            await GatewayModel.objects.acreate(
                user_id=user_id,
                subscription_id=subscription_id,
                track_id=result['track_id'],
                message_gateway=result['message'],
                result_gateway=result['result'],
            )
            return response(
                status_code=400,
                status=False,
                error=True,
                data=result,
                message="خطایی رخ داده هست"
            )
