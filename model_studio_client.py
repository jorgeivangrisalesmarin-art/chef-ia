"""Cliente HTTP para Alibaba Cloud Model Studio (DashScope) con reintentos."""
from __future__ import annotations

import logging
import time
from typing import Any

import requests

import config

logger = logging.getLogger(__name__)


class ModelStudioError(Exception):
    """Error genérico de la API."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class AuthError(ModelStudioError):
    """Clave inválida o sin permisos (401/403)."""


class RateLimitError(ModelStudioError):
    """Límite de tasa excedido (429)."""


def _mask(text: str, api_key: str) -> str:
    return text.replace(api_key, "***") if api_key else text


def _headers(api_key: str | None) -> dict[str, str]:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _raise_for_status(resp: requests.Response, api_key: str) -> None:
    code = resp.status_code
    detail = _mask(resp.text[:300], api_key)
    if code in (401, 403):
        raise AuthError("Clave de API inválida o sin permisos.", code)
    if code == 429:
        raise RateLimitError("Límite de solicitudes alcanzado. Intenta en unos minutos.", code)
    raise ModelStudioError(f"Error del servicio ({code}): {detail}", code)


def _request(method: str, url: str, api_key: str | None, payload: dict | None,
             timeout: int) -> requests.Response:
    """Realiza la solicitud con reintentos para 429, 5xx y errores de red."""
    last_exc: Exception | None = None
    for attempt in range(config.HTTP_MAX_RETRIES + 1):
        try:
            resp = requests.request(method, url, headers=_headers(api_key), json=payload, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
            logger.warning("Fallo de red (intento %d): %s", attempt + 1, type(exc).__name__)
        else:
            if resp.status_code == 200:
                return resp
            if resp.status_code not in (429,) and resp.status_code < 500:
                _raise_for_status(resp, api_key or "")
            if attempt == config.HTTP_MAX_RETRIES:
                _raise_for_status(resp, api_key or "")
            logger.warning("Estado %d, reintentando", resp.status_code)
        if attempt < config.HTTP_MAX_RETRIES:
            time.sleep(config.BACKOFF_BASE_S * (2 ** attempt))
    raise ModelStudioError("No se pudo conectar con el servicio (tiempo agotado).") from last_exc


def _json_of(resp: requests.Response) -> dict[str, Any]:
    try:
        return resp.json()
    except ValueError as exc:
        raise ModelStudioError("La respuesta del servicio no es JSON válido.") from exc


def chat_completion(
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    max_tokens: int,
    enable_thinking: bool | None = None,
) -> str:
    """Llama a /chat/completions (compatible con OpenAI) y devuelve el texto."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if enable_thinking is not None:
        payload["enable_thinking"] = enable_thinking
    data = _json_of(_request("POST", config.CHAT_URL, api_key, payload, config.HTTP_TIMEOUT_S))
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelStudioError("La respuesta del modelo no tiene el formato esperado.") from exc
    if not content:
        raise ModelStudioError("El modelo devolvió una respuesta vacía.")
    return content


def generate_image(api_key: str, model: str, prompt: str, size: str,
                   prompt_extend: bool = True) -> str:
    """Genera una imagen (qwen-image) y devuelve la URL firmada del resultado."""
    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": [{"text": prompt}]}]},
        "parameters": {"size": size, "n": 1, "prompt_extend": prompt_extend},
    }
    data = _json_of(_request("POST", config.MULTIMODAL_URL, api_key, payload, config.IMAGE_TIMEOUT_S))
    try:
        content = data["output"]["choices"][0]["message"]["content"]
        url = next(part["image"] for part in content if isinstance(part, dict) and part.get("image"))
    except (KeyError, IndexError, TypeError, StopIteration) as exc:
        raise ModelStudioError(
            f"El servicio de imágenes no devolvió una imagen: {data.get('message', 'sin detalle')}"
        ) from exc
    return url


def download_bytes(url: str, timeout: int = config.HTTP_TIMEOUT_S) -> bytes:
    """Descarga los bytes de una URL firmada.

    Sin cabeceras personalizadas: la firma de OSS incluye las cabeceras de la
    petición y cualquier Content-Type/Accept adicional rompe la validación
    (SignatureDoesNotMatch, 403).
    """
    last_exc: Exception | None = None
    for attempt in range(config.HTTP_MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
            logger.warning("Fallo de red descargando la imagen (intento %d)", attempt + 1)
        else:
            if resp.status_code == 200 and resp.content:
                return resp.content
            logger.warning("Descarga de imagen respondió %d", resp.status_code)
        if attempt < config.HTTP_MAX_RETRIES:
            time.sleep(config.BACKOFF_BASE_S * (2 ** attempt))
    raise ModelStudioError("No se pudo descargar la imagen generada (URL firmada).") from last_exc
