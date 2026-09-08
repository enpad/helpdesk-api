# Helpdesk API

API REST interna de la mesa de ayuda. Administra tickets de soporte de las
tiendas, los comentarios de seguimiento y la asignación a agentes.

## Requisitos

- Python 3.11+

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
python run.py
```

La API queda en `http://localhost:8000`. Documentación interactiva en `/docs`.

Al arrancar se cargan datos de ejemplo (4 tickets y 3 agentes) desde
`app/storage/seed_data.py`.

## Pruebas

```bash
pytest
```

## Estructura

```
app/
├── config.py          Configuración de la aplicación
├── errors.py          Excepciones de dominio y su mapeo a HTTP
├── main.py            Ensamblado de la aplicación FastAPI
├── models/            Modelos Pydantic y enums del dominio
├── storage/           Almacenamiento en memoria (CRUD puro) y datos de ejemplo
├── services/          Reglas de negocio
└── routes/            Handlers HTTP
tests/                 Suite de pruebas con pytest
docs/api.md            Referencia de endpoints
```

## Ciclo de vida de un ticket

Un ticket nace en `open` y puede moverse a `in_progress`, `pending` o `closed`.
Un ticket cerrado se puede consultar y se puede **reabrir**, pero no se puede
editar, eliminar ni comentar mientras siga cerrado.

Las transiciones permitidas están declaradas en `ALLOWED_TRANSITIONS`, en
`app/services/ticket_service.py`.
