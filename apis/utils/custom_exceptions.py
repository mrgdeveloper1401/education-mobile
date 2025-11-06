from rest_framework.exceptions import APIException


class VolumeImageExceptions(APIException):
    status_code = 400
    default_detail = 'Volume Image Error'
    default_code = 1
