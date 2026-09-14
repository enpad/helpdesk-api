#!/usr/bin/env python3
"""Seeds varied ticket data against a running helpdesk-api instance.

Not meant to be shown during the demo. Its only purpose is to leave
non-trivial data (mixed priorities, statuses, and agent assignments) for
Claude's live, unscripted analysis in a notebook.

Usage:
    HELPDESK_BASE_URL=http://<public-ip>:8000 python3 seed_tickets.py [count]

Requires `requests` (see demo/notebooks/requirements.txt).
"""

import os
import random
import sys

import requests

STORE_TAGS = [f"tienda{n:02d}" for n in range(1, 21)]

TICKET_TEMPLATES = [
    ("No puedo iniciar sesion en POS", "El terminal no acepta el usuario del cajero.", "high"),
    ("Impresora de recibos sin papel", "La impresora fiscal no imprime tickets desde ayer.", "medium"),
    ("Lector de codigo de barras roto", "El scanner inalambrico dejo de leer codigos.", "medium"),
    ("Internet caido en sucursal", "La sucursal reporta sin conexion desde la manana.", "critical"),
    ("Actualizacion de precios pendiente", "Los precios de la promocion no se reflejan en el sistema.", "low"),
    ("Terminal de pago rechaza tarjetas", "El datafono rechaza todas las tarjetas de credito.", "critical"),
    ("Reporte diario no llega por correo", "El reporte de cierre de caja no se envio.", "low"),
    ("Bascula de piso descalibrada", "La bascula del area de frutas marca pesos incorrectos.", "medium"),
    ("Camara de seguridad sin senal", "La camara de la entrada principal no transmite video.", "high"),
    ("Sistema lento al abrir tickets", "Abrir un nuevo ticket de soporte tarda mas de un minuto.", "medium"),
]

# Deliberately skewed so status/priority/workload distributions aren't flat
# — gives the live analysis something real to say.
STATUS_WEIGHTS = [
    ("open", 0.35),
    ("in_progress", 0.25),
    ("pending", 0.15),
    ("closed", 0.25),
]


def pick_status() -> str:
    return random.choices(
        [s for s, _ in STATUS_WEIGHTS],
        weights=[w for _, w in STATUS_WEIGHTS],
    )[0]


def main() -> int:
    base_url = os.environ.get("HELPDESK_BASE_URL", "http://localhost:8000")
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 40

    agents = requests.get(f"{base_url}/agents", timeout=10).json()
    if not agents:
        print("No agents found — the API's seed data should have loaded some at startup.", file=sys.stderr)
        return 1
    agent_emails = [a["email"] for a in agents]

    created = 0
    for i in range(count):
        title, description, priority = random.choice(TICKET_TEMPLATES)
        store = random.choice(STORE_TAGS)
        payload = {
            "title": f"{title} ({store})",
            "description": description,
            "priority": priority,
            "requester_email": f"{store}@kindor.co",
        }
        response = requests.post(f"{base_url}/tickets", json=payload, timeout=10)
        response.raise_for_status()
        ticket = response.json()

        # Assign before closing — assignment is refused on already-closed tickets.
        if random.random() < 0.7:
            agent_email = random.choice(agent_emails)
            requests.post(
                f"{base_url}/tickets/{ticket['id']}/assign",
                json={"agent_email": agent_email},
                timeout=10,
            ).raise_for_status()

        new_status = pick_status()
        if new_status != "open":
            requests.patch(
                f"{base_url}/tickets/{ticket['id']}",
                json={"status": new_status},
                timeout=10,
            ).raise_for_status()

        created += 1

    print(f"Seeded {created} tickets against {base_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
