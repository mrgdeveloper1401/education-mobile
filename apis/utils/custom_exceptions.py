from rest_framework.exceptions import APIException


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
