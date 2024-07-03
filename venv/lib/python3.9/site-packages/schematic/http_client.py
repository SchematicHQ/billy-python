import httpx


class OfflineHTTPClient(httpx.Client):
    def send(self, request, **kwargs):
        response = httpx.Response(
            status_code=200,
            json={"data": {}},
            request=request,
        )
        return response


class AsyncOfflineHTTPClient(httpx.AsyncClient):
    async def send(self, request, **kwargs):
        response = httpx.Response(
            status_code=200,
            json={"data": {}},
            request=request,
        )
        return response
