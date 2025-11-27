import time
from datetime import timedelta
from uuid import uuid4

from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets
from rest_framework.exceptions import NotFound, NotAcceptable, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from base.clasess.gateway import Gateway
from discount_app.models import Coupon
from gateway_app.models import Gateway as GatewayModel, ResultGateway
from subscription_app.models import SubscriptionPlan, UserSubscription
from .serializer import GatewaySerializer, ListRetrieveGatewaySerializer, ListRetrieveResultGateWaySerializer
from ...utils.custom_exceptions import PlanAlreadyExistsException, TooManyRequests, PaymentTooManyRequests, \
    AmountTooManyRequests, CartdIsInvalid, SwitchError, CartNotFound
from ...utils.custom_pagination import TwentyPageNumberPagination
from ...utils.custom_permissions import AsyncIsAuthenticated
from ...utils.custom_response import response


class GatewayView(APIView):
    serializer_class = GatewaySerializer
    permission_classes = (AsyncIsAuthenticated,)

    async def _create_gateway_record(self, user_id, plan_id, result, is_complete: bool = False):
        await GatewayModel.objects.acreate(
            user_id=user_id,
            subscription_id=plan_id,
            track_id=result['trackId'],
            message_gateway=result['message'],
            result_gateway=result['result'],
            is_complete=is_complete
        )

    async def check_plan(self, plan_id):
        obj = await SubscriptionPlan.objects.filter(
            id=plan_id,
            is_active=True
        ).only(
            "id",
            "discounted_price",
            "duration"
        ).alast()
        if not obj:
            raise NotFound("plan not found")
        return obj

    async def calc_price_by_coupon(self, price_plan, coupon):
        price = price_plan
        coupon.amount = int(coupon.amount)

        if coupon.coupon_type == "amount":
            price -= coupon.amount
        else:
            calc_discount = price *  coupon.amount / 100
            price -= calc_discount

        return min(price, 0)

    async def check_active_plan(self, plan, user_id):
        """check user dose have active plan"""
        user_plan = await UserSubscription.objects.filter(
            is_active=True,
            user_id=user_id,
        ).only(
            "id", "status"
        ).alast()
        if user_plan and user_plan.status == "active":
            raise PlanAlreadyExistsException()

    async def _create_user_plan(self, user_id, plan_id, duration, transaction_id):
        start_date = timezone.now()
        end_date = timezone.now() + timedelta(days=duration * 30)
        await UserSubscription.objects.acreate(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            status="reserve",
            transaction_id=transaction_id
        )

    async def _check_have_plan(self, plan_id, user_id):
        plan = await UserSubscription.objects.filter(
            id=plan_id,
            user_id=user_id,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            status="active"
        ).aexists()
        if plan:
            raise PermissionDenied("شما از قبل پلن فعالی رو دارید")

    async def post(self, request):
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

        # check have plan
        await self._check_have_plan(plain_id, user_id)

        # check plan
        plan = await self.check_plan(plain_id)

        # check active plan
        await self.check_active_plan(plan, user_id)

        # get price
        price = plan.discounted_price

        # check coupon
        if coupon_code:
            coupon = await Coupon.objects.filter(code=coupon_code, is_active=True).alast()
            if not coupon.is_valid():
                raise NotFound("coupon not found")
            else:
                price = await self.calc_price_by_coupon(price, coupon)

        # check price is zero
        if price == 0:
            result = {
                "trackId": None,
                "message": "پرداخت با موفقیت انجام شد",
                "result": 100
            }
            await self._create_gateway_record(user_id, plan.id, result, is_complete=True)
            await UserSubscription.objects.acreate(
                user_id=user_id,
                plan_id=plan.id,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=plan.duration),
                transaction_id=f'{int(time.time())}_{uuid4().time}',
                status="active"
            )
            return response(
                status_code=201,
                error=False,
                message="پردازش با موفقیت انجام شد",
                data=result,
                status=True
            )

        # request gateway
        gate_way = Gateway()
        price = price * 10
        result = await gate_way.request_payment(
            amount=price,
            description=description,
            order_id=plain_id,
            mobile=phone,
        )

        # create gateway record
        await self._create_gateway_record(user_id, plan.id, result)

        # create user plan
        transaction_id = f'{int(time.time())}_{uuid4().time}'
        await self._create_user_plan(user_id, plan.id, plan.duration, transaction_id)

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


class ListRetrieveGatewayViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    pagination --> 20 item
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ListRetrieveGatewaySerializer
    pagination_class = TwentyPageNumberPagination

    def get_queryset(self):
        fields = ("subscription__name", "is_complete", "created_at", "updated_at")
        return GatewayModel.objects.filter(
            user_id=self.request.user.id
        ).select_related("subscription").only(*fields)


class VerifyPayment(APIView):
    permission_classes = (AsyncIsAuthenticated,)

    async def get(self, request, *args, **kwargs):
        query_params = request.query_params

        # get params
        success = query_params.get('success', None)
        status = query_params.get('status', None)
        track_id = query_params.get('trackId', None)
        order_id = query_params.get('orderld', None)

        # check params
        if not success or not status or not track_id:
            raise NotFound("query params error (verify_payment, status, trackId)")

        # get user
        user_id = request.user.id

        # check track id
        check_track_id = await GatewayModel.objects.filter(
            track_id=track_id,
            is_active=True,
            user_id=user_id).alast()
        if not check_track_id:
            raise NotFound("track id not found")

        # check plan
        user_plan = await sync_to_async(lambda: UserSubscription.objects.filter(
            is_active=True,
            user_id=user_id,
            status="reserve",
            id=order_id
        ).only("status"))()
        if not await user_plan.aexists():
            raise NotFound("user plan not found")

        # verify payment on zibal gateway
        gateway = Gateway()
        verify_payment = await gateway.verify_payment(check_track_id)

        # check verify payment
        status_verify_payment = verify_payment.get('status', None)
        # result_verify_payment = verify_payment.get('result', None)

        match status_verify_payment:
            case 1:
                    # update status
                    await user_plan.aupdate(status="active")
                    await check_track_id.asave(is_complete=True)

                    # data
                    data = {
                        "trackId": track_id,
                        "success": success,
                        "plan_id": user_plan.id,
                        "plan_status": user_plan.status,
                    }
                    return response(
                        status_code=200,
                        status=True,
                        error=False,
                        data=data,
                        message=_("پردازش با موفقیت انجام شد")
                    )

            case -1:
                await user_plan.aupdate(status="reserve")
                return response(
                    status_code=204,
                    status=True,
                    error=False,
                    data={},
                    message="در حال انجام پردازش"
                )

            case -2:
                return response(
                    status_code=400,
                    status=False,
                    error=True,
                    data=None,
                    message="درگاه پرداخت به مشکل خورده هست"
                )

            case 3:
                return response(
                    status_code=400,
                    status=False,
                    error=True,
                    data=None,
                    message="عملیات توسط کاربر لغو شده هست"
                )

            case 7:
                raise TooManyRequests()

            case 8:
                raise PaymentTooManyRequests()

            case 9:
                raise AmountTooManyRequests()

            case 10:
                raise CartdIsInvalid()

            case 11:
                raise SwitchError()

            case 12:
                raise CartNotFound()

            case _:
                raise NotAcceptable()


class ListRetrieveResultGateWayViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ListRetrieveResultGateWaySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        gateway_id = self.kwargs.get('gateway_pk')
        user_id = self.request.user.id

        fields = self.serializer_class.Meta.fields

        return ResultGateway.objects.filter(
            gateway_id=gateway_id,
            gateway__user_id=user_id,
            gateway__is_active=True,
            is_active=True,
        ).only(*fields)
