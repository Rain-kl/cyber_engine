import asyncio
import functools
import json
import os.path
from typing import Callable, Any
from urllib.parse import urlparse
import httpx
from loguru import logger


class Retry:

    @staticmethod
    def async_retry(
        retries: int = 3,
        delay: float = 0,
        _log: str = "Running",
        success_log: bool = False,
        throw_error: bool = False,
    ) -> Callable:
        """
        Attempt to call a function, if it fails, try again with a specified delay.

        :param retries:  The max amount of retries you want for the function call
        :param delay:  The delay (in seconds) between each function retry
        :param _log:  The log message
        :param success_log:  Whether to log success
        :param throw_error:  Whether to throw error
        :return:  The result of the function call
        """

        def decorator(func) -> Callable:

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                for count in range(1, retries + 1):
                    try:
                        result = await func(*args, **kwargs)
                        if success_log:
                            logger.success(
                                f"{_log} Success: {func.__name__} {json.dumps([str(i) for i in args])}"
                            )
                        return result
                    except AssertionError as e:
                        raise e
                    except httpx.ReadTimeout as e:
                        logger.error(
                            f"{_log} __{func.__name__}__ Time out {count}: {str(e)}"
                        )
                    except Exception as e:
                        logger.error(
                            f"{_log} __{func.__name__}__ Failed {count}: {str(e)}"
                        )
                    finally:
                        await asyncio.sleep(delay)
                critical_log = f"{_log} __{func.__name__}__ Failed: retried {retries}, log：{func.__name__} {json.dumps([str(i) for i in args])}"
                logger.critical(critical_log)
                if throw_error:
                    raise Exception(critical_log)

            return async_wrapper

        return decorator


class AsyncSpider:
    def __init__(
        self,
        base_url: str,
        headers: dict = None,
        timeout: int = 10,
    ):
        assert base_url.startswith("http"), "base_url should start with http"
        assert not base_url.endswith("/"), "base_url should not end with /"
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout

    async def get(self, path: str, params=None) -> httpx.Response:
        assert not path.startswith("/"), "path should not start with /"
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                self.base_url + path,
                headers=self.headers,
                timeout=self.timeout,
                params=params,
            )
            return response

    async def post(self, path: str, data=None, _json=None) -> httpx.Response:
        assert path.startswith("/"), "path should not start with /"
        async with httpx.AsyncClient(verify=False) as client:
            response: httpx.Response = await client.post(
                self.base_url + path,
                headers=self.headers,
                timeout=self.timeout,
                data=data,
                json=_json,
            )
            return response
