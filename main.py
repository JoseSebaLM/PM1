"""PM1: tutor de matemática PAES M1 (miniaplicación del Gate 1).

Uso:  python main.py
      python main.py "¿Cómo despejo x en 3x + 5 = 20?"
"""

import sys

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import armar_peticion, calcular_costo, enviar_peticion, extraer_texto, parsear_respuesta_json

DUDA_DE_EJEMPLO = "No entiendo cómo resolver 2(x - 3) = 4x + 2. ¿Me ayudas?"

# Los prompts del banco, buscables por su nombre
PROMPTS = {prompt["nombre"]: prompt for prompt in BANCO_DE_PROMPTS}


def consultar(nombre_prompt, duda):
    """Envía la duda con un prompt del banco y devuelve (respuesta en dict, costo en USD)."""
    prompt = PROMPTS[nombre_prompt]
    url, encabezados, cuerpo = armar_peticion(duda, prompt["system_instruction"], prompt.get("response_schema"))
    datos = enviar_peticion(url, encabezados, cuerpo)
    respuesta = parsear_respuesta_json(extraer_texto(datos), prompt["claves_esperadas"])
    return respuesta, calcular_costo(datos)


def main():
    # Usar la duda escrita en la terminal o, si no hay, la de ejemplo
    duda = " ".join(sys.argv[1:]) or DUDA_DE_EJEMPLO
    print("Duda del estudiante:", duda)

    # Dos consultas: clasificar la duda por eje y generar una pista sin resolver
    try:
        eje, costo_eje = consultar("clasificar_eje", duda)
        pista, costo_pista = consultar("generar_pista", duda)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
        sys.exit(1)

    # Mostrar el resultado
    print(f"Eje PAES M1: {eje['eje']} (confianza {eje['confianza']:.2f})")
    print(f"Respuesta del modelo (pista): {pista['pista']}")
    print(f"Concepto clave: {pista['concepto_clave']} | Dificultad: {pista['dificultad']}")
    print(f"Costo estimado: {costo_eje + costo_pista:.6f} USD")
    print("Proceso terminado sin errores.")


if __name__ == "__main__":
    main()
