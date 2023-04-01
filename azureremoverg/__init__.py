import logging
import os

import azure.functions as func
import requests


def get_api_headers_decorator(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        return {
            "Authorization": f"Bearer {os.environ[args[0]] if 'EA' in args[0] else func(*args, **kwargs)}",
            "Content-Type": "application/json",
        }

    return wrapper


@get_api_headers_decorator
def get_api_headers(*args, **kwargs):
    oauth2_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    oauth2_body = {
        "client_id": os.environ[args[0]],
        "client_secret": os.environ[args[1]],
        "grant_type": "client_credentials",
        "scope" if "GRAPH" in args[0] else "resource": args[2],
    }
    try:
        return requests.post(
            url=args[3], headers=oauth2_headers, data=oauth2_body
        ).json()["access_token"]

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def main(mytimer: func.TimerRequest) -> None:
    logging.info("******* Starting the function *******")
    rest_api_headers = get_api_headers(
        "REST_CLIENT_ID",
        "REST_CLIENT_SECRET",
        "https://management.azure.com",
        f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}/oauth2/token",
    )
    try:
        logging.info(
            [
                requests.delete(
                    url=f"https://management.azure.com/subscriptions/{os.environ['SUBSCRIPTION_ID']}/resourcegroups/{rg['name']}?api-version=2020-06-01",
                    headers=rest_api_headers,
                )
                for rg in requests.get(
                    url=f"https://management.azure.com/subscriptions/{os.environ['SUBSCRIPTION_ID']}/resourcegroups?api-version=2020-06-01",
                    headers=rest_api_headers,
                ).json()["value"]
                # ).json()["value"] if not rg["name"].endswith("rg")
            ]
        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
