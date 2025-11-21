import datetime
import time
import random

from django.contrib.auth import aauthenticate, authenticate
from pytz import timezone as pytz_timezone
from django.core.cache import cache
from adrf.views import APIView as AsyncAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import mixins, viewsets
from asgiref.sync import sync_to_async

from auth_app.models import User, Student
from base.clasess.send_sms import SendSms
from base.utils.custom_throttle import OtpRateThrottle
from base.utils.grand_section_access import grant_mobile_sections_access
from core_app.models import Photo
from .serializers import (
    RequestOtpSerializer,
    OtpVerifySerializer,
    ProfileSerializer,
    UploadImageSerializer,
    LogInByPhoneSerializer
)
from apis.utils.custom_permissions import AsyncRemoveAuthenticationPermissions, AsyncIsAuthenticated, NotAuthenticate
from apis.utils.custom_response import response
from base.settings import SIMPLE_JWT
from ...utils.custom_exceptions import UserNotFoundException, UserBlockException


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
                token = await sync_to_async((RefreshToken.for_user))(user)
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
                await sync_to_async(grant_mobile_sections_access)(user.id) # access two section into user
                return response(
                    status=True,
                    message="پردازش با موفقیت انجام شد",
                    error=False,
                    status_code=200,
                    data=data
                )


class UserProfileView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.only(
        "first_name",
        "last_name",
        "mobile_phone",
        "image__image",
        "bio",
        'image__width',
        "image__height"
    ).select_related("image")

    def get_queryset(self):
        queryset = self.queryset.filter(id=self.request.user.id)
        return queryset


class UploadImageView(AsyncAPIView):
    serializer_class = UploadImageSerializer
    permission_classes = (AsyncIsAuthenticated,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data['image']
        # create instance
        image = await Photo.objects.acreate(
            image=image,
            upload_by_id=request.user.id,

        )
        return response(
            status=True,
            status_code=201,
            data={
                "image_id": image.id,
            },
            error=False,
            message="پردازش با موفقیت انجام شد"
        )


class LoginByPhonePasswordView(APIView):
    serializer_class = LogInByPhoneSerializer
    permission_classes = (NotAuthenticate,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # phone
        phone = serializer.validated_data['mobile_phone']
        password = serializer.validated_data['password']

        user = authenticate(request, mobile_phone=phone, password=password)
        if user is None:
            raise UserNotFoundException()
        else:
            if user.is_active is False:
                raise UserBlockException()
            else:
                token =  RefreshToken.for_user(user)
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
                grant_mobile_sections_access(user.id) # access two section into user
                return response(
                    status=True,
                    message="پردازش با موفقیت انجام شد",
                    error=False,
                    status_code=200,
                    data=data
                )
