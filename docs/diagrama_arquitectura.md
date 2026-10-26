# Arquitectura de PM1

```mermaid
flowchart TD
    U["main.py<br/>duda del estudiante"] --> A
    B["prompts/banco.py<br/>prompt de sistema + esquema JSON"] --> A
    K[".env<br/>GEMINI_API_KEY"] --> A
    A["armar_peticion<br/>valida y arma url, header y cuerpo"] -->|petición| E
    E["enviar_peticion<br/>POST con timeout de 30 s"] <-->|HTTPS| G[("API Gemini")]
    E -->|respuesta en dict| X["extraer_texto"]
    E -->|usageMetadata| C["calcular_costo"]
    X -->|texto JSON| P["parsear_respuesta_json"]
    P -->|eje y pista| U
    C -->|costo en USD| U
```

| Dónde | Qué error se maneja |
|---|---|
| `armar_peticion` | Pregunta vacía o falta la llave → `ValueError` |
| `enviar_peticion` | Sin conexión, timeout, HTTP ≠ 200, respuesta que no es JSON → `RuntimeError` |
| `extraer_texto` | La respuesta no trae texto → `RuntimeError` |
| `parsear_respuesta_json` | JSON inválido o faltan claves → `ValueError` |

`main.py` atrapa `ValueError` y `RuntimeError` y muestra un mensaje claro, sin traceback.
