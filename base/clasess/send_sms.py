# import asyncio
from typing import Any, Union
import httpx
from decouple import config


class SendSms:
    def __init__(self):
        self.API_KEY = config("SMS_IR_API_KEY", cast=str, default="api_key")
        self.BASE_URL = config("SMS_IR_BASE_URL", cast=str, default="https://api.sms.ir/v1/")
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.API_KEY,
        }

    async def _post(self, url: str, data: Any, headers: dict = None):
        if headers:
            self.headers.update(headers)

        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=data, headers=headers)
            return response.json()

    async def send_otp_sms(self, mobile: str, otp: Union[int, str]):
        verify_url = f"{self.BASE_URL}send/verify"
        json = {
            "Mobile": mobile,
            "TemplateId": config("SMS_IR_OTP_TEMPLATE_ID", cast=int, default=1234),
            "parameters": [
                {
                    "name": "CODE",
                    "value": otp
                }
            ]
        }
        return await self._post(verify_url, data=json, headers=self.headers)


# async def main():
#     send_sms = SendSms()
#     res = await send_sms.send_otp_sms("09391640664", "1234")
#     print(res)
#
#
# asyncio.run(main())