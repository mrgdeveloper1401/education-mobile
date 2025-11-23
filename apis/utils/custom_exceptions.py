from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


class VolumeImageExceptions(APIException):
    status_code = 400
    default_detail = 'Volume Image Error'
    default_code = 1


class AuthenticationFailed(APIException):
    status_code = 403
    default_detail = 'کاربر احراز هویت شده نمیتواند دسترسی پیدا کند'
    default_code = 2


class UserBlockException(APIException):
    status_code = 403
    default_detail = "حساب کاربری شما مسدود میباشد با پشتیبان تماس بگیرد"
    default_code = 3


class PlanAlreadyExistsException(APIException):
    status_code = 403
    default_detail = "کاربر محترم شما از قبل اشتراک فعال دارید"
    default_code = 4


class TooManyRequests(APIException):
    status_code = HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'تعداد درخواست‌ها بیش از حد مجاز می‌باشد'
    default_code = "too_many_requests"


class PaymentTooManyRequests(APIException):
    status_code = HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'تعداد پرداخت های اینترنتی بیش از حد مجاز می‌باشد'
    default_code = "payment_too_many_requests"


class AmountTooManyRequests(APIException):
    status_code = HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'مبلغ پرداخت اینترنتی بیش از حد مجاز می‌باشد'
    default_code = "amount_too_many_requests"


class CartdIsInvalid(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = "صادر کننده کارت نامعتبر میباشد"
    default_code = "cart_invalid"


class SwitchError(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = "خطای سوییچ"
    default_code = "switch_error"


class CartNotFound(APIException):
    status_code = HTTP_404_NOT_FOUND
    default_detail = "کارت قابل دسترسی نمی‌باشد"
    default_code = "cart_not_found"