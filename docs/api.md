# Referencia de endpoints

## Tickets

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/tickets` | Crear un ticket |
| GET | `/tickets` | Listar tickets (`status`, `priority`, `assigned_to`, `skip`, `limit`) |
| GET | `/tickets/{id}` | Consultar un ticket |
| PATCH | `/tickets/{id}` | Actualizar campos de un ticket |
| DELETE | `/tickets/{id}` | Eliminar un ticket |
| GET | `/tickets/stats/summary` | Conteos por estado y prioridad |
| GET | `/tickets/stats/workload` | Tickets abiertos por agente |

## Comentarios

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/tickets/{id}/comments` | Agregar un comentario |
| GET | `/tickets/{id}/comments` | Listar comentarios del ticket |

## Agentes y asignación

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/agents` | Listar agentes |
| POST | `/agents` | Dar de alta un agente |
| POST | `/tickets/{id}/assign` | Asignar el ticket a un agente |
| DELETE | `/tickets/{id}/assign` | Quitar la asignación |

## Códigos de error

Los errores de dominio responden `{"error": "..."}`.

| Código | Significado |
|---|---|
| 404 | El recurso no existe |
| 409 | La petición es válida pero choca con el estado actual del recurso |
| 422 | El payload no cumple el esquema |

## Pendientes conocidos

- El listado de tickets no permite filtrar por rango de fechas.
- No hay autenticación en ningún endpoint.
