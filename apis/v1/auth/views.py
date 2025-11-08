import datetime
import time
import random

from pytz import timezone as pytz_timezone
from django.core.cache import cache
from adrf.views import APIView as AsyncAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import mixins, viewsets, permissions

from auth_app.models import User, Student
from base.clasess.send_sms import SendSms
from base.utils.custom_throttle import OtpRateThrottle
from .serializers import RequestOtpSerializer, OtpVerifySerializer, ProfileSerializer
from apis.utils.custom_permissions import AsyncRemoveAuthenticationPermissions
from apis.utils.custom_response import response
from base.settings import SIMPLE_JWT

class RequestOtpView(AsyncAPIView):
    serializer_class = RequestOtpSerializer
    permission_classes = (AsyncRemoveAuthenticationPermissions,)
    throttle_classes = (OtpRateThrottle,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get phone
        phone = serializer.validated_data['mobile_phone']

        # get or create user
        user, created = await User.objects.aget_or_create(mobile_phone=phone)
        if created:
            await Student.objects.acreate(user_id=user.id)

        # set key in redis
        get_ip = request.META.get('REMOTE_ADDR', "X-FORWARDED-FOR")
        random_code = random.randint(100000, 999999)
        redis_key = f'{phone}_{get_ip}_{random_code}'
        await cache.aset(redis_key, random_code, timeout=120)

        # send otp sms
        sms = SendSms()
        await sms.send_otp_sms(user.mobile_phone, random_code)

        # return response
        data = {
            "mobile": phone,
            "exp_time": int(time.time() + 120)
        }
        return response(
            status=True,
            message="پردازش با موفقیت انجام شد",
            error=False,
            status_code=201,
            data=data,
        )


class OtpVerifyView(AsyncAPIView):
    serializer_class = OtpVerifySerializer
    permission_classes = (AsyncRemoveAuthenticationPermissions,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['mobile_phone']
        otp = serializer.validated_data['otp']

        # get in redis
        get_ip = request.META.get('REMOTE_ADDR', "X-FORWARDED-FOR")
        redis_key = f'{phone}_{get_ip}_{otp}'
        get_redis_key = await cache.aget(redis_key)
        if get_redis_key is None:
            return response(
                status=False,
                message="کد اشتباه یا منقضی شد هست",
                error=True,
                status_code=404,
                data=None
            )
        else:
            user = await User.objects.filter(mobile_phone=phone).only("mobile_phone", "is_active").afirst()
            if user.is_active is False:
                return response(
                    status=False,
                    message="حساب شما مسدود شده هست!",
                    status_code=403,
                    error=True,
                    data=None
                )
            else:
                token = RefreshToken.for_user(user)
                iran_timezone = pytz_timezone("Asia/Tehran")
                expire_timestamp = int(time.time()) + SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds
                expire_date = datetime.datetime.fromtimestamp(expire_timestamp, tz=iran_timezone)
                data = {
                    "mobile": phone,
                    "access_token": str(token.access_token),
                    "refresh_token": str(token),
                    "jwt": "Bearer",
                    "expire_timestamp_access_token": expire_timestamp,
                    "expire_date_access_token": expire_date
                }
                await cache.adelete(redis_key)
                return response(
                    status=True,
                    message="پردازش با موفقیت انجام شد",
                    error=False,
                    status_code=200,
                    data=data
                )


class UserProfileView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id).only(
            "first_name",
            "last_name",
            "bio",
            "image"
        )
