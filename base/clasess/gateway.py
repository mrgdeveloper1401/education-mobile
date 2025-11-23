import asyncio

from decouple import config
import httpx


ZIBAL_API_KEY = config("ZIBAL_API_KEY", cast=str, default="")
ZIBAL_CALLBACK_URL = config("ZIBAL_CALLBACK_URL", cast=str, default="")
ZIBAL_REQUEST_URL = config("ZIBAL_REQUEST_URL", cast=str, default="")
ZIBAL_LAZY_REQUEST_URL = config("ZIBAL_LAZY_REQUEST_URL", cast=str, default="")
ZIBAL_VERIFY_URL = config("ZIBAL_VERIFY_URL", cast=str)


class Gateway:
    def __init__(self):
        self.__merchant = ZIBAL_API_KEY
        self.__callback_url = ZIBAL_CALLBACK_URL
        self.__reqeust_payment_url = ZIBAL_REQUEST_URL
        self.__verify_payment_url = ZIBAL_VERIFY_URL
        self.headers = {
            "Content-Type": "application/json",
        }

    async def _post(self, body, url, headers=None):
        if headers:
            self.headers.update(headers)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                headers=headers,
                json=body,
            )
            return response.json()

    async def request_payment(
            self,
            amount,
            description,
            order_id,
            mobile
    ):
        data = {
            "merchant": self.__merchant,
            "amount": amount,
            "callbackUrl": self.__callback_url,
            "description": description,
            "orderId": order_id,
            "mobile": mobile
            }
        url = self.__reqeust_payment_url
        result = await self._post(data, url)
        return result

    async def verify_payment(self, track_id: int):
        data = {
            "merchant": self.__merchant,
            "trackId": track_id,
        }
        url = self.__verify_payment_url
        result = await self._post(data, url)
        return result


async def main():
    g1 = Gateway()
    result1 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result2 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result3 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result4 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result5 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    print(result1)
    # print(result2)
    # print(result3)
    # print(result4)
    # print(result5)

if __name__ == "__main__":
    asyncio.run(main())
