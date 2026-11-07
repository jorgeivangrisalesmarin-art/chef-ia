"""Cliente HTTP genérico para NVIDIA build.nvidia.com con reintentos y polling."""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

import requests

import config

logger = logging.getLogger(__name__)


class NvidiaAPIError(Exception):
    """Error genérico de la API."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class AuthError(NvidiaAPIError):
    """Clave inválida o sin permisos (401/403)."""


class RateLimitError(NvidiaAPIError):
    """Límite de tasa excedido (429)."""


def _mask(text: str, api_key: str) -> str:
    return text.replace(api_key, "***") if api_key else text


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _raise_for_status(resp: requests.Response, api_key: str) -> None:
    code = resp.status_code
    detail = _mask(resp.text[:300], api_key)
    if code in (401, 403):
        raise AuthError("Clave de API inválida o sin permisos.", code)
    if code == 429:
        raise RateLimitError("Límite de solicitudes alcanzado. Intenta en unos minutos.", code)
    raise NvidiaAPIError(f"Error del servicio ({code}): {detail}", code)


def _request(method: str, url: str, api_key: str, payload: dict | None, timeout: int) -> requests.Response:
    """Realiza la solicitud con reintentos para 429, 5xx y errores de red."""
    last_exc: Exception | None = None
    for attempt in range(config.HTTP_MAX_RETRIES + 1):
        try:
            resp = requests.request(method, url, headers=_headers(api_key), json=payload, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
            logger.warning("Fallo de red (intento %d): %s", attempt + 1, type(exc).__name__)
        else:
            if resp.status_code in (200, 202):
                return resp
            if resp.status_code not in (429,) and resp.status_code < 500:
                _raise_for_status(resp, api_key)
            if attempt == config.HTTP_MAX_RETRIES:
                _raise_for_status(resp, api_key)
            logger.warning("Estado %d, reintentando", resp.status_code)
        if attempt < config.HTTP_MAX_RETRIES:
            time.sleep(config.BACKOFF_BASE_S * (2 ** attempt))
    raise NvidiaAPIError("No se pudo conectar con el servicio (tiempo agotado).") from last_exc


def post_json(
    url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: int = config.HTTP_TIMEOUT_S,
    poll_timeout: int = config.POLL_TIMEOUT_S,
    on_progress: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """POST JSON; si responde 202 hace polling hasta obtener el resultado."""
    if not api_key:
        raise AuthError("Falta la clave de API.")
    resp = _request("POST", url, api_key, payload, timeout)
    if resp.status_code == 202:
        reqid = resp.headers.get("NVCF-REQID")
        if not reqid:
            raise NvidiaAPIError("Respuesta asíncrona sin identificador de solicitud.")
        resp = _poll(reqid, api_key, timeout, poll_timeout, on_progress)
    try:
        return resp.json()
    except ValueError as exc:
        raise NvidiaAPIError("La respuesta del servicio no es JSON válido.") from exc


def _poll(reqid: str, api_key: str, timeout: int, poll_timeout: int,
          on_progress: Callable[[str], None] | None) -> requests.Response:
    deadline = time.monotonic() + poll_timeout
    interval = config.POLL_INTERVAL_S
    url = config.NVCF_STATUS_URL.format(reqid=reqid)
    while time.monotonic() < deadline:
        time.sleep(interval)
        resp = _request("GET", url, api_key, None, timeout)
        if resp.status_code == 200:
            return resp
        waited = int(poll_timeout - (deadline - time.monotonic()))
        if on_progress:
            on_progress(f"Generando… {waited}s")
        interval = min(interval * 1.5, config.POLL_MAX_INTERVAL_S)
    raise NvidiaAPIError("Tiempo de espera agotado generando el contenido.")


def chat_completion(
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    max_tokens: int,
) -> str:
    """Llama a /chat/completions (compatible con OpenAI) y devuelve el texto."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    data = post_json(config.NVIDIA_CHAT_URL, api_key, payload)
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise NvidiaAPIError("La respuesta del modelo no tiene el formato esperado.") from exc
    if not content:
        raise NvidiaAPIError("El modelo devolvió una respuesta vacía.")
    return content
