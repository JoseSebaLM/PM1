"""Módulo para consultar a Gemini: arma la petición, la envía y procesa la respuesta."""

import json
import os
import re

import requests
from dotenv import load_dotenv

# Cargar la llave desde el archivo .env (nunca se escribe en el código)
load_dotenv()

# Modelo elegido en docs/decision-arquitectura.md y sus precios (USD por token)
MODELO = "gemini-3.5-flash-lite"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
PRECIO_ENTRADA = 0.30 / 1_000_000
PRECIO_SALIDA = 2.50 / 1_000_000


def armar_peticion(pregunta, system_instruction=None, response_schema=None, modelo=MODELO):
    """Valida la pregunta y devuelve url, encabezados y cuerpo."""
    # Validar la entrada antes de gastar una petición
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta GEMINI_API_KEY: revisa tu archivo .env en la raíz del proyecto.")

    # Armar la petición; la llave va en un header (no en la URL)
    url = f"{URL_BASE}/{modelo}:generateContent"
    encabezados = {"x-goog-api-key": api_key}
    cuerpo = {"contents": [{"parts": [{"text": pregunta}]}]}

    # Opcional: prompt de sistema y salida en JSON con un esquema fijo
    if system_instruction:
        cuerpo["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if response_schema is not None:
        cuerpo["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, encabezados, cuerpo


def enviar_peticion(url, encabezados, cuerpo):
    """Envía la petición y devuelve la respuesta como diccionario."""
    # Errores de red: sin conexión o el servicio no responde a tiempo
    try:
        respuesta = requests.post(url, headers=encabezados, json=cuerpo, timeout=30)
    except requests.exceptions.ConnectionError as error:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.") from error
    except requests.exceptions.Timeout as error:
        raise RuntimeError("El servicio tardó demasiado en responder. Intenta de nuevo.") from error

    # Errores HTTP: llave inválida (400), cuota (429), servicio saturado (503), etc.
    if respuesta.status_code != 200:
        raise RuntimeError(f"La API respondió con error HTTP {respuesta.status_code}: {respuesta.text[:300]}")

    # Error de formato: la respuesta no es JSON
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError("La respuesta del servicio no llegó en formato JSON válido.") from error


def extraer_texto(datos):
    """Devuelve el texto generado por el modelo."""
    # Buscar la lista de partes de la respuesta
    try:
        partes = datos["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as error:
        raise RuntimeError("La respuesta no trae el texto generado en candidates[0].content.parts.") from error

    # Unir las partes de texto (a veces llegan varias); se omite el razonamiento interno ("thought")
    textos = [parte["text"] for parte in partes if "text" in parte and not parte.get("thought")]
    if not textos:
        raise RuntimeError("La respuesta llegó sin texto generado.")
    return "".join(textos)


def parsear_respuesta_json(texto, claves_requeridas):
    """Convierte el texto del modelo en diccionario y revisa que traiga las claves pedidas."""
    # Quitar marcas de markdown (```json ... ```) si el modelo las agregó
    texto_limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip())

    # Convertir a diccionario
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError as error:
        raise ValueError("La respuesta del modelo no es JSON válido.") from error

    # Validar la estructura, no solo que sea JSON
    if not isinstance(datos, dict):
        raise ValueError("La respuesta del modelo es JSON, pero no es un objeto con claves.")
    faltantes = [clave for clave in claves_requeridas if clave not in datos]
    if faltantes:
        raise ValueError(f"A la respuesta le faltan las claves: {faltantes}")
    return datos


def calcular_costo(datos, precio_entrada=PRECIO_ENTRADA, precio_salida=PRECIO_SALIDA):
    """Calcula el costo en USD de una respuesta usando usageMetadata."""
    # Leer el conteo de tokens que informa la API
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
    except KeyError as error:
        raise RuntimeError("La respuesta no trae usageMetadata para calcular el costo.") from error

    # Los tokens de "pensamiento" también se cobran como salida
    tokens_salida = uso.get("candidatesTokenCount", 0) + uso.get("thoughtsTokenCount", 0)
    return tokens_entrada * precio_entrada + tokens_salida * precio_salida


def obtener_dato_de_prueba(pregunta):
    """Hace una consulta simple: armar -> enviar -> extraer."""
    url, encabezados, cuerpo = armar_peticion(pregunta)
    datos = enviar_peticion(url, encabezados, cuerpo)
    return extraer_texto(datos)


# Prueba rápida de conexión: python src/consumir_gemini.py
if __name__ == "__main__":
    try:
        print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona."))
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
