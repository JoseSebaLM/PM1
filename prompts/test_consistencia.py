"""Prueba cada prompt del banco varias veces y guarda cuántas respuestas fueron válidas.

Uso (desde la raíz):  python -m prompts.test_consistencia
"""

import json
import time
from datetime import date
from pathlib import Path

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import MODELO, armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json

INTENTOS = 5  # el curso pide al menos 3
PAUSA = 2  # segundos entre llamadas, para no provocar el error 429

registro = {"fecha": str(date.today()), "modelo": MODELO}

for prompt in BANCO_DE_PROMPTS:
    exitos = 0
    fallos = []

    # Repetir la misma consulta y contar las respuestas con JSON válido y las claves esperadas
    for intento in range(INTENTOS):
        try:
            url, encabezados, cuerpo = armar_peticion(
                prompt["ejemplo_usuario"], prompt["system_instruction"], prompt.get("response_schema")
            )
            texto = extraer_texto(enviar_peticion(url, encabezados, cuerpo))
            parsear_respuesta_json(texto, prompt["claves_esperadas"])
            exitos += 1
        except (ValueError, RuntimeError) as error:
            fallos.append(str(error)[:120])
            print(f"  intento {intento + 1} falló: {error}")
        time.sleep(PAUSA)

    print(f"{prompt['nombre']}: {exitos}/{INTENTOS} respuestas válidas")
    registro[prompt["nombre"]] = {"exitos": exitos, "intentos": INTENTOS, "fallos": fallos}

# Guardar el registro junto a este archivo
ruta = Path(__file__).parent / "registro_resultados.json"
ruta.write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
print("Registro guardado en", ruta)
