"""Módulo de modelos de domínio - Cliente."""
from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    """Nível de prioridade do cliente no atendimento."""
    NORMAL = "normal"
    PRIORITY = "priority"


@dataclass
class Client:
    """Representa um cliente cadastrado no sistema.

    Attributes:
        client_id: Identificador único do cliente.
        name: Nome completo do cliente.
        phone: Telefone de contato.
        priority: Nível de prioridade (normal ou prioritário).
        active: Indica se o cliente está ativo no sistema.
    """
    client_id: int
    name: str
    phone: str
    priority: Priority = Priority.NORMAL
    active: bool = True

    def to_dict(self) -> dict:
        """Serializa o cliente para dicionário (persistência)."""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "phone": self.phone,
            "priority": self.priority.value,
            "active": self.active,
        }

    @staticmethod
    def from_dict(data: dict) -> "Client":
        """Desserializa um cliente a partir de um dicionário."""
        return Client(
            client_id=data["client_id"],
            name=data["name"],
            phone=data["phone"],
            priority=Priority(data.get("priority", "normal")),
            active=data.get("active", True),
        )

    def __str__(self) -> str:
        prio_label = "[PRIORIDADE]" if self.priority == Priority.PRIORITY else "[NORMAL]"
        status = "Ativo" if self.active else "Inativo"
        return f"#{self.client_id} - {self.name} | Tel: {self.phone} | {prio_label} | {status}"
