from drf_spectacular.utils import OpenApiResponse, OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status


def otp_api_documentation(**kwargs):
    """
    دکوراتور مستندسازی برای APIهای OTP
    """
    return extend_schema_view(
        post=extend_schema(
            summary=kwargs.get('summary', "درخواست کد تأیید"),
            description=kwargs.get('description', """
            ارسال کد تأیید (OTP) به شماره موبایل کاربر.

            **محدودیت‌ها:**
            - هر شماره موبایل فقط می‌تواند هر ۱ دقیقه یکبار درخواست ارسال کند
            - کد ارسالی به مدت ۲ دقیقه معتبر است
            """),
            responses={
                status.HTTP_201_CREATED: OpenApiResponse(
                    description='کد تأیید با موفقیت ارسال شد',
                    examples=[
                        OpenApiExample(
                            'Success Response',
                            value={
                                "status": True,
                                "message": "پردازش با موفقیت انجام شد",
                                "error": False,
                                "status_code": 201,
                                "data": {
                                    "mobile": "09123456789",
                                    "exp_time": 1690000000
                                }
                            }
                        )
                    ]
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                    description='داده‌های ورودی نامعتبر است',
                    examples=[
                        OpenApiExample(
                            'Validation Error',
                            value={
                                "status": False,
                                "message": "خطا در اعتبارسنجی داده‌ها",
                                "error": {
                                    "mobile_phone": ["این فیلد ضروری است."]
                                },
                                "status_code": 400,
                                "data": None
                            }
                        )
                    ]
                ),
                status.HTTP_403_FORBIDDEN: OpenApiResponse(
                    description="کاربر احراز هویت شده نمیتواند دسترسی پیدا کند",
                    examples=[
                        OpenApiExample(
                            "Authentication Failed",
                            value={
                                "detail": "کاربر احراز هویت شده نمیتواند دسترسی پیدا کند"
                            }
                        )
                    ]
                ),
                status.HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(
                    description='تعداد درخواست‌ها بیش از حد مجاز',
                    examples=[
                        OpenApiExample(
                            'Rate Limit Error',
                            value={
                                "status": False,
                                "message": "لطفاً ۶۰ ثانیه دیگر مجدد تلاش کنید",
                                "error": "Rate limit exceeded",
                                "status_code": 429,
                                "data": None
                            }
                        )
                    ]
                ),
            }
        )
    )

