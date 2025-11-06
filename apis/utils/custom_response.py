from typing import Any, Union

from rest_framework.response import Response


def response(status: bool, message: str, data: Any, error: Union[None, bool], status_code: int = 200) -> Response:
    return Response(
        {
            "status": status,
            "message": message,
            "data": data,
            "error": error,
        },
        status=status_code,
    )
