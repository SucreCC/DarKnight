from __future__ import annotations

import json
from typing import Any

import requests

from darknight import logger
from darknight.services.config.settings import get_app_config

_TOKEN_CACHE: dict[str, tuple[str, float]] = {}


class PayPalError(Exception):
    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


def _config():
    return get_app_config().paypal


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict | None = None,
) -> dict:
    cfg = _config()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method,
        f"{cfg.api_base}{path}",
        headers=headers,
        json=json_body,
        timeout=30,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}

    if response.status_code >= 400:
        logger.error(f"PayPal API error {response.status_code}: {payload}")
        detail = payload.get("message") if isinstance(payload, dict) else str(payload)
        raise PayPalError(detail or "PayPal API request failed", response.status_code, payload)

    return payload if isinstance(payload, dict) else {"data": payload}


def get_access_token() -> str:
    import time

    cfg = _config()
    cache_key = cfg.client_id
    cached = _TOKEN_CACHE.get(cache_key)
    if cached and cached[1] > time.time():
        return cached[0]

    response = requests.post(
        f"{cfg.api_base}/v1/oauth2/token",
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=(cfg.client_id, cfg.client_secret),
        timeout=30,
    )
    payload = response.json()
    if response.status_code >= 400:
        raise PayPalError(payload.get("error_description", "Failed to authenticate with PayPal"))

    token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3000))
    _TOKEN_CACHE[cache_key] = (token, time.time() + max(expires_in - 60, 60))
    return token


def create_order(*, amount: float, currency: str, reference_id: str) -> str:
    token = get_access_token()
    payload = _request(
        "POST",
        "/v2/checkout/orders",
        token=token,
        json_body={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}",
                    },
                }
            ],
        },
    )
    order_id = payload.get("id")
    if not order_id:
        raise PayPalError("PayPal order ID missing in response")
    return order_id


def capture_order(paypal_order_id: str) -> dict:
    token = get_access_token()
    return _request(
        "POST",
        f"/v2/checkout/orders/{paypal_order_id}/capture",
        token=token,
    )


def verify_webhook(headers: dict[str, str], body: bytes) -> bool:
    cfg = _config()
    if not cfg.webhook_id:
        logger.warning("PayPal webhook_id not configured; skipping signature verification")
        return True

    token = get_access_token()
    verification = _request(
        "POST",
        "/v1/notifications/verify-webhook-signature",
        token=token,
        json_body={
            "auth_algo": headers.get("paypal-auth-algo", ""),
            "cert_url": headers.get("paypal-cert-url", ""),
            "transmission_id": headers.get("paypal-transmission-id", ""),
            "transmission_sig": headers.get("paypal-transmission-sig", ""),
            "transmission_time": headers.get("paypal-transmission-time", ""),
            "webhook_id": cfg.webhook_id,
            "webhook_event": json.loads(body.decode("utf-8")),
        },
    )
    return verification.get("verification_status") == "SUCCESS"


__all__ = ["PayPalError", "capture_order", "create_order", "get_access_token", "verify_webhook"]
