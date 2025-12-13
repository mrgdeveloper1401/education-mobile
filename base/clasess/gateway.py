import asyncio

from decouple import config
import httpx

# from apis.utils.custom_exceptions import RequiredCoffeeBazaar

# ZIBAL
ZIBAL_API_KEY = config("ZIBAL_API_KEY", cast=str, default="")
ZIBAL_CALLBACK_URL = config("ZIBAL_CALLBACK_URL", cast=str, default="")
ZIBAL_REQUEST_URL = config("ZIBAL_REQUEST_URL", cast=str, default="")
ZIBAL_LAZY_REQUEST_URL = config("ZIBAL_LAZY_REQUEST_URL", cast=str, default="")
ZIBAL_VERIFY_URL = config("ZIBAL_VERIFY_URL", cast=str)

# coffee bazaar
# BAZAAR_REDIRECT_CLIENT_URL = config("BAZAAR_REDIRECT_CLIENT_URL", cast=str, default="")
# BAZAAR_REDIRECT_CLIENT_SECRET = config("BAZAAR_REDIRECT_CLIENT_SECRET", cast=str, default="")
# BAZAAR_REDIRECT_CLIENT_ID = config("BAZAAR_REDIRECT_CLIENT_ID", cast=str, default="")
# BAZAAR_TOKEN_API_KEY = config("BAZAAR_TOKEN_API_KEY", cast=str, default="")
BAZAAR_PAY_URL = config("BAZAAR_PAY_URL", cast=str, default="")

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


# coffee bazaar

async def bazaar(amount: int, destination: str = "developer", service_name: str = None):
    # check argument
    # if amount is None or destination is None or service_name is None:
    #     raise RequiredCoffeeBazaar()
    # header
    headers = {
        "Content-Type": "application/json",
    }
    # request into url
    url = BAZAAR_PAY_URL
    json = {
        "amount": amount,
        "destination": destination,
        "service_name": service_name,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, headers=headers, json=json)
    return response.json()


async def main():
    ...
    # g1 = Gateway()
    # result1 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result2 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result3 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result4 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result5 = await g1.request_payment(50000, "hello world", "123", "09391640664")
    # result6 = await bazaar(amount=10, destination="developers", service_name="codeima.ir")
    # print(result6)
    # print(result1)
    # print(result2)
    # print(result3)
    # print(result4)
    # print(result5)

if __name__ == "__main__":
    asyncio.run(main())
