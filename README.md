# ChatterBot Python API

API Flask para chatear y entrenar un bot con `chatterbot`.

## Rutas

- `GET /` - estado del servicio
- `POST /chat` - enviar un mensaje al bot
- `POST /train` - entrenar el bot con `X-Admin-Key`
- `GET /apidocs/` - documentación Swagger UI

## Instalación

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
export CHATBOT_ADMIN_KEY="tu_clave"
python app.py
```

## Ejemplos

### Chat

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d {text:Hola}
```

### Train

```bash
curl -X POST http://127.0.0.1:5000/train \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: tu_clave" \
  -d mode:list
```

## Swagger

La documentación interactiva queda en:

- `http://127.0.0.1:5000/apidocs/`

## Producción

Esta app usa SQLite local (`db.sqlite3`) y está pensada para un despliegue simple en servidor.
