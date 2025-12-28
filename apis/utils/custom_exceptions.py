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


class ChallengeBlockedException(APIException):
    status_code = 403
    default_detail = "مجموع نمرات شما صفر هست نمیتوانید جواب رو ببیند"
    default_code = "challenge_blocked"


class ChallengeBlockTwoException(APIException):
    status_code = 403
    default_detail = "مجموع نمرات شما کم تر ۲۰ هست"
    default_code = "challenge_block_2"


class PreventSendSubmitChallengeException(APIException):
    status_code = 403
    default_detail = "شما قبلا برای این چالش جواب رو فرستادید"
    default_code = "prevent_send_submit_challenge"


class ExamIsOpenException(APIException):
    status_code = 400
    default_detail = "ازمون قبلی باز هست"
    default_code = "exam_is_open"


class RequiredCoffeeBazaar(APIException):
    status_code = 400
    default_detail = "قیمت و سرویس و مقصد اجباری هست"
    default_code = "required_cofee_bazaar"


class GatewayNotFound(APIException):
    status_code = 404
    default_detail = "درگاه پرداخت باید زیبال باشد یا بازار"
    default_code = "gateway_not_found"


class InvalidIpGateway(APIException):
    status_code = 403
    default_code = "invalid_ip"


class RequestTimeOut(APIException):
    status_code = 400
    default_detail = "request time out"
    default_code = "request_time_out"


class SubscriptionAlreadyExists(APIException):
    status_code = 403
    default_detail = "شما از قبل اشتراک فعال دارید"
    default_code = "subscription_already_exists"
