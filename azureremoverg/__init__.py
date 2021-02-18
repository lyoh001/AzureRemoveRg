import logging
import os

import azure.functions as func
import requests


def get_rest_api_token():
    oauth2_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    oauth2_body = {
        "client_id": os.environ["REST_CLIENT_ID"],
        "client_secret": os.environ["REST_CLIENT_SECRET"],
        "grant_type": "client_credentials",
        "resource": "https://management.azure.com",
    }
    oauth2_url = (
        f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}/oauth2/token"
    )
    try:
        return requests.post(
            url=oauth2_url, headers=oauth2_headers, data=oauth2_body
        ).json()["access_token"]
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_rest_api_headers(token):
    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }


def main(mytimer: func.TimerRequest) -> None:
    logging.info("******* Starting the function *******")
    rest_api_headers = get_rest_api_headers(get_rest_api_token())
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
            ]
        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
