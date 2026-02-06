import httpx
from decouple import config

class SmsIrClient:
    def __init__(self):
        self.client = httpx.Client(
            base_url=config("SMS_IR_BASE_URL"),
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": config("SMS_IR_API_KEY")
            },
            timeout=config("SMS_IR_REQUEST_OTP_TIMEOUT", cast=float, default=10)
        )

    def send_otp(self, phone: str, code: str) -> str:
        payload = {
            "Mobile": phone,
            "TemplateId": config("SMS_IR_OTP_TEMPLATE_ID", cast=int),
            "parameters": [{"name": "CODE", "value": code}]
        }

        response = self.client.post("/send/verify", json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("status")
