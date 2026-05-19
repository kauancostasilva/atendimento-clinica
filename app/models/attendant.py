"""Módulo de modelos de domínio - Atendente."""
from dataclasses import dataclass


@dataclass
class Attendant:
    """Representa um atendente cadastrado no sistema.

    Attributes:
        attendant_id: Identificador único do atendente.
        name: Nome do atendente.
        busy: Indica se o atendente está ocupado no momento.
        current_service_id: ID do atendimento em aberto (None se livre).
    """
    attendant_id: int
    name: str
    busy: bool = False
    current_service_id: int = None

    def to_dict(self) -> dict:
        """Serializa o atendente para dicionário."""
        return {
            "attendant_id": self.attendant_id,
            "name": self.name,
            "busy": self.busy,
            "current_service_id": self.current_service_id,
        }

    @staticmethod
    def from_dict(data: dict) -> "Attendant":
        """Desserializa um atendente a partir de dicionário."""
        return Attendant(
            attendant_id=data["attendant_id"],
            name=data["name"],
            busy=data.get("busy", False),
            current_service_id=data.get("current_service_id"),
        )

    def __str__(self) -> str:
        status = f"Atendendo serviço #{self.current_service_id}" if self.busy else "Disponível"
        return f"#{self.attendant_id} - {self.name} | {status}"
