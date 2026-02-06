from celery import shared_task

from base.clasess.send_sms import SmsIrClient


sms_client = SmsIrClient()

@shared_task
def send_otp_sms_celery(phone, code):
    sms_client.send_otp(phone, code)
