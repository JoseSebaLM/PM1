# Decisión de arquitectura: elección de modelo

Medición: 2026-10-26, con [`medir_modelos.py`](medir_modelos.py). Datos crudos: [`resultados_medicion_modelos.json`](resultados_medicion_modelos.json).
Precios: [página oficial de Gemini](https://ai.google.dev/gemini-api/docs/pricing), capa de pago (el proyecto usa la capa gratuita).

## Modelo elegido

`gemini-3.5-flash-lite`

## Diagrama de arquitectura

Ver [diagrama_arquitectura.md](diagrama_arquitectura.md). El modelo es la constante `MODELO` de `src/consumir_gemini.py`.

## Comparación de candidatos

| Criterio | gemini-3.5-flash-lite | gemini-3.6-flash |
|---|---|---|
| Precio entrada / salida (USD por 1 M tokens) | 0,30 / 2,50 | 0,75 / 3,75 (se duplica en 2027) |
| Latencia promedio (4 mediciones) | 4,17 s | 10,34 s |
| Tokens de salida promedio | 94 | 694 (incluye "pensamiento") |
| Costo promedio por consulta | 0,000244 USD | 0,002625 USD |
| Calidad (3 preguntas PAES M1) | 3/3 correctas | 1/1 correcta, 2 sin respuesta (error 503) |

Calidad = matemáticamente correcta, da pista sin resolver cuando se pide, lenguaje para 4° medio.

## Justificación

PM1 responde dudas cortas a un estudiante que espera. Con calidad suficiente en ambos, pesan más la latencia y el costo: `gemini-3.5-flash-lite` es unas 2,5 veces más rápido y unas 10 veces más barato. Además respondió todas las consultas.

## Alternativa descartada y por qué

`gemini-3.6-flash`: "piensa" antes de responder (por eso genera ~7 veces más tokens), lo que aumenta el costo y la espera sin mejorar estas respuestas. También tuvo errores 503 (modelo saturado). Lo volvería a probar para problemas de varios pasos.

Nota: también intenté `gemini-3.8-flash`, pero no respondió ninguna consulta el 25 y el 26 de octubre (503 / timeout), así que no se pudo comparar.
