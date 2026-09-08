"""Datos de ejemplo para desarrollo local."""

from app.models.agent import AgentCreate
from app.models.enums import TicketPriority
from app.models.ticket import TicketCreate
from app.storage.memory import agents, tickets

SAMPLE_AGENTS = [
    AgentCreate(name="Ana Rivera", email="ana.rivera@helpdesk.example", team="infra"),
    AgentCreate(name="Luis Cordero", email="luis.cordero@helpdesk.example", team="apps"),
    AgentCreate(name="Marta Solis", email="marta.solis@helpdesk.example", team="apps"),
]

SAMPLE_TICKETS = [
    TicketCreate(
        title="La caja 4 no imprime tickets",
        description="Desde la apertura la impresora de la caja 4 no responde a ninguna venta.",
        priority=TicketPriority.HIGH,
        requester_email="tienda0142@retail.example",
    ),
    TicketCreate(
        title="Error al aplicar cupon de descuento",
        description="Al capturar el cupon VERANO25 el punto de venta marca codigo invalido.",
        priority=TicketPriority.MEDIUM,
        requester_email="tienda0233@retail.example",
    ),
    TicketCreate(
        title="Inventario no refleja la ultima recepcion",
        description="Se recibio mercancia ayer y el sistema sigue mostrando el stock anterior.",
        priority=TicketPriority.CRITICAL,
        requester_email="tienda0088@retail.example",
    ),
    TicketCreate(
        title="Solicitud de acceso al portal de proveedores",
        description="El nuevo encargado de piso necesita credenciales para el portal.",
        priority=TicketPriority.LOW,
        requester_email="tienda0311@retail.example",
    ),
]


def load() -> None:
    if tickets.list_all():
        return
    for agent in SAMPLE_AGENTS:
        agents.create(agent)
    for ticket in SAMPLE_TICKETS:
        tickets.create(ticket)
