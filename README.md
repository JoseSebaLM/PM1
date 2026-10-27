# PM1 — Tutor de matemática PAES M1

Miniaplicación en Python que usa la API de Gemini para ayudar a estudiantes que preparan la PAES M1: **clasifica la duda por eje** y **da una pista sin resolver el ejercicio**.

Gate 1 del Módulo 1 · Especialización en Desarrollo con IA Generativa (Skillnest · Accenture).

El bootcamp autoriza usar un editor con IA, y usé **Claude Code** como asistente.

## Requisitos

- Python 3.11 o superior y Git
- Una API key gratuita de [Google AI Studio](https://aistudio.google.com/apikey)

## Instalación

Windows (PowerShell):

```powershell
git clone https://github.com/JoseSebaLM/PM1.git
cd PM1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env    # reemplaza tu_llave_aqui por tu llave y guarda
```

macOS / Linux: igual, pero con `python3 -m venv .venv`, `source .venv/bin/activate` y `cp .env.example .env`.

Si PowerShell no deja activar el entorno: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

## Ejecutar

Desde la raíz del proyecto, con el entorno activo:

| Comando | Qué hace |
|---|---|
| `python main.py` | Clasifica una duda de ejemplo y da una pista |
| `python main.py "¿Cómo calculo el 15 % de 8.000?"` | Lo mismo con tu duda |
| `python src/consumir_gemini.py` | Prueba de conexión |
| `python -m prompts.test_consistencia` | Prueba el banco de prompts |
| `python -m docs.medir_modelos` | Compara los modelos candidatos |

Salida de `python main.py` (el texto cambia en cada ejecución):

```text
Duda del estudiante: No entiendo cómo resolver 2(x - 3) = 4x + 2. ¿Me ayudas?
Eje PAES M1: algebra_y_funciones (confianza 1.00)
Respuesta del modelo (pista): Primero, aplica la propiedad distributiva en el lado izquierdo...
Concepto clave: Ecuación lineal de primer grado | Dificultad: baja
Costo estimado: 0.000286 USD
Proceso terminado sin errores.
```

Si algo falla, el programa muestra `No se pudo completar la operación:` y el motivo. Los errores 429 y 503 son temporales: espera y vuelve a intentar.

## Estructura

```text
main.py                     programa principal
src/consumir_gemini.py      armar_peticion, enviar_peticion, extraer_texto,
                            parsear_respuesta_json, calcular_costo
prompts/                    banco de prompts, prueba de consistencia y su registro
docs/                       diagrama, decisión de modelo, mediciones y evidencias
tests/                      pruebas automatizadas (Módulo 2)
```

## Documentación

- [Diagrama de arquitectura](docs/diagrama_arquitectura.md)
- [Decisión de modelo](docs/decision-arquitectura.md): `gemini-3.5-flash-lite`
- Evidencias: [primera petición](docs/evidencia_peticion_autenticada.txt) · [pruebas de errores](docs/evidencia_b7_pruebas_errores.txt)

## Banco de prompts

5 repeticiones por prompt con `gemini-3.5-flash-lite` (2026-10-26). Registro: [prompts/registro_resultados.json](prompts/registro_resultados.json).

| Prompt | Para qué | Esquema JSON | Válidas |
|---|---|---|---|
| `clasificar_eje` | Ubicar la duda en un eje PAES M1 | Sí | 5/5 |
| `generar_pista` | Pista sin resolver el ejercicio | Sí | 5/5 |
| `extraer_datos_problema` | Datos e incógnita de un enunciado | No (solo instrucción) | 5/5 |

## Seguridad

- La llave va solo en `.env`, que está en `.gitignore` y nunca se subió (`git log --all -- .env` está vacío).
- La llave viaja en el header `x-goog-api-key`, no en la URL.
- No se envían datos personales de estudiantes (la capa gratuita de Gemini puede usar lo enviado).

## Registro del ensayo de instalación limpia

- **2026-10-25:** clon desde GitHub en una carpeta nueva, entorno nuevo y solo los pasos de este README. `main.py`, la prueba de conexión y el banco de prompts corrieron sin errores. Sin hallazgos.
- **2026-10-26:** repetido tras simplificar el código y publicar este repositorio (`JoseSebaLM/PM1`), en Windows 11 con Python 3.14.3, fuera de la carpeta de trabajo. Instalación sin errores; `main.py`, la prueba de conexión y el banco de prompts (5/5 en los 3) corrieron sin traceback. En la copia clonada, `git status` no muestra `.env` y `git log --all -- .env` está vacío. Sin hallazgos.
