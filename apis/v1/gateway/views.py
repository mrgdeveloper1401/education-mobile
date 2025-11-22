from adrf.views import APIView
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound

from base.clasess.gateway import Gateway
from gateway_app.models import Gateway as GatewayModel
from subscription_app.models import SubscriptionPlan
from .serializer import GatewaySerializer
from ...utils.custom_permissions import AsyncIsAuthenticated
from ...utils.custom_response import response


class GatewayView(APIView):
    serializer_class = GatewaySerializer
    permission_classes = (AsyncIsAuthenticated,)

    async def _create_gateway_record(self, user_id, plan_id, result):
        await GatewayModel.objects.acreate(
            user_id=user_id,
            subscription_id=plan_id,
            track_id=result['trackId'],
            message_gateway=result['message'],
            result_gateway=result['result'],
        )

    async def check_plan(self, plan_id):
        obj = await SubscriptionPlan.objects.filter(id=plan_id, is_active=True).only("id", "discounted_price").alast()
        if not obj:
            raise NotFound("plan not found")
        return obj

    async def post(self, request):
        # import ipdb
        # ipdb.set_trace()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get user id
        user_id = request.user.id

        # get phone by user
        phone = request.user.mobile_phone

        # data
        plain_id = serializer.validated_data['plan']
        description = serializer.validated_data.get('description', None)
        coupon_code = serializer.validated_data.get('coupon_code', None)

        # check plan
        plan = await self.check_plan(plain_id)

        # get price
        price = plan.discounted_price

        # request gateway
        gate_way = Gateway()
        result = await gate_way.request_payment(
            amount=price,
            description=description,
            order_id=plain_id,
            mobile=phone,
        )

        # create gateway record
        await self._create_gateway_record(user_id, plan.id, result)

        # check result and return response
        if result['result'] == 100:
            return response(
                status_code=201,
                status=True,
                error=False,
                data=result,
                message="پردازش با موفقیت انجام شد"
            )
        else:
            return response(
                status_code=400,
                status=False,
                error=True,
                data=result,
                message="خطایی رخ داده هست"
            )


class VerifyPayment(APIView):
    permission_classes = (AsyncIsAuthenticated,)

    async def get(self, request, *args, **kwargs):
        query_params = request.query_params

        # get params
        success = query_params.get('success', None)
        status = query_params.get('status', None)
        track_id = query_params.get('trackId', None)

        # check params
        if not success or not status or not track_id:
            raise NotFound("query params error (verify_payment, status, trackId)")

        # get user
        user = await request.auser()
        user_id = user.id

        # check track id
        check_track_id = await GatewayModel.objects.filter(track_id=track_id, is_active=True, user_id=user_id).alast()
        if not await check_track_id.aexists():
            raise NotFound("track id not found")

        # check request into gateway

        return response(
            status_code=200,
            status=True,
            error=False,
            data={},
            message=_("پردازش با موفقیت انجام شد")
        )
