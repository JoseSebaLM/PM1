"""Compara dos modelos de Gemini por latencia, costo y calidad (Bloque 9).

Uso (desde la raíz):  python -m docs.medir_modelos
"""

import json
import time
from datetime import date
from pathlib import Path

from src.consumir_gemini import armar_peticion, calcular_costo, enviar_peticion, extraer_texto

# Candidatos y precios en USD por 1 millón de tokens (ai.google.dev/gemini-api/docs/pricing)
MODELOS = {
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.6-flash": (0.75, 3.75),
}

# Latencia: la misma pregunta repetida 4 veces
PREGUNTA_LATENCIA = "Un alumno pregunta: ¿cómo despejo x en 3x + 5 = 20? Dale una pista sin resolverlo."
REPETICIONES = 4

# Calidad: una pregunta PAES M1 por eje, revisada a mano después
PREGUNTAS_CALIDAD = [
    "Soy estudiante de 4° medio. ¿Cómo despejo x en 2(x - 3) = 4x + 2? Dame solo una pista, sin resolverlo.",
    "Una polera costaba $12.000 y ahora cuesta $9.000. ¿Qué porcentaje de descuento tiene? Explícalo en pocos pasos.",
    "Si lanzo dos dados, ¿cuál es la probabilidad de que la suma sea 7? Explícalo en pocos pasos.",
]


def consultar(pregunta, modelo, precios):
    """Hace una consulta y devuelve latencia, costo y texto (o el error)."""
    url, encabezados, cuerpo = armar_peticion(pregunta, modelo=modelo)
    inicio = time.perf_counter()
    try:
        datos = enviar_peticion(url, encabezados, cuerpo)
        texto = extraer_texto(datos)
    except RuntimeError as error:
        return {"error": str(error)[:100]}
    latencia = time.perf_counter() - inicio

    # Precios de USD por millón a USD por token
    costo = calcular_costo(datos, precios[0] / 1_000_000, precios[1] / 1_000_000)
    uso = datos["usageMetadata"]
    return {
        "latencia_s": round(latencia, 2),
        "costo_usd": round(costo, 6),
        "tokens_salida": uso.get("candidatesTokenCount", 0) + uso.get("thoughtsTokenCount", 0),
        "texto": texto.strip(),
    }


resultados = {"fecha": str(date.today())}

for modelo, precios in MODELOS.items():
    print("Midiendo", modelo)

    # 1. Latencia y costo
    mediciones = []
    for i in range(REPETICIONES):
        mediciones.append(consultar(PREGUNTA_LATENCIA, modelo, precios))
        print("  latencia", i + 1, mediciones[-1].get("latencia_s", mediciones[-1].get("error")))
        time.sleep(2)

    # 2. Promedios, solo con las consultas que funcionaron
    ok = [m for m in mediciones if "error" not in m]
    resumen = {
        "exitosas": f"{len(ok)}/{REPETICIONES}",
        "latencia_promedio_s": round(sum(m["latencia_s"] for m in ok) / len(ok), 2) if ok else None,
        "costo_promedio_usd": round(sum(m["costo_usd"] for m in ok) / len(ok), 6) if ok else None,
        "tokens_salida_promedio": round(sum(m["tokens_salida"] for m in ok) / len(ok)) if ok else None,
    }
    print("  ", resumen)

    # 3. Calidad: guardar las respuestas para revisarlas
    calidad = []
    for pregunta in PREGUNTAS_CALIDAD:
        calidad.append({"pregunta": pregunta, **consultar(pregunta, modelo, precios)})
        time.sleep(2)

    resultados[modelo] = {"resumen": resumen, "latencias": [m.get("latencia_s") for m in mediciones], "calidad": calidad}

ruta = Path(__file__).parent / "resultados_medicion_modelos.json"
ruta.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
print("Resultados guardados en", ruta)
