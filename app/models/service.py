"""Módulo de modelos de domínio - Atendimento (Service)."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ServiceStatus(Enum):
    """Status possíveis de um atendimento."""
    WAITING = "waiting"         # Na fila, aguardando
    IN_PROGRESS = "in_progress" # Em atendimento
    FINISHED = "finished"       # Finalizado


@dataclass
class Service:
    """Representa um atendimento no sistema.

    Attributes:
        service_id: Identificador único do atendimento.
        client_id: ID do cliente sendo atendido.
        client_name: Nome do cliente (desnormalizado para relatórios).
        attendant_id: ID do atendente responsável (None se ainda na fila).
        attendant_name: Nome do atendente (desnormalizado para relatórios).
        status: Status atual do atendimento.
        created_at: Data/hora de criação (entrada na fila).
        started_at: Data/hora de início do atendimento.
        finished_at: Data/hora de finalização.
        duration_seconds: Duração total em segundos.
        notes: Observações opcionais.
    """
    service_id: int
    client_id: int
    client_name: str
    attendant_id: int = None
    attendant_name: str = None
    status: ServiceStatus = ServiceStatus.WAITING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: str = None
    finished_at: str = None
    duration_seconds: float = None
    notes: str = ""

    def start(self, attendant_id: int, attendant_name: str) -> None:
        """Inicia o atendimento com o atendente especificado."""
        self.attendant_id = attendant_id
        self.attendant_name = attendant_name
        self.status = ServiceStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()

    def finish(self, notes: str = "") -> None:
        """Finaliza o atendimento e calcula a duração."""
        self.status = ServiceStatus.FINISHED
        self.finished_at = datetime.now().isoformat()
        self.notes = notes
        if self.started_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.finished_at)
            self.duration_seconds = (end - start).total_seconds()

    def wait_seconds(self) -> float:
        """Calcula quantos segundos o cliente está esperando na fila."""
        if self.status == ServiceStatus.WAITING:
            created = datetime.fromisoformat(self.created_at)
            return (datetime.now() - created).total_seconds()
        return 0.0

    def to_dict(self) -> dict:
        """Serializa o atendimento para dicionário."""
        return {
            "service_id": self.service_id,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "attendant_id": self.attendant_id,
            "attendant_name": self.attendant_name,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "Service":
        """Desserializa um atendimento a partir de dicionário."""
        return Service(
            service_id=data["service_id"],
            client_id=data["client_id"],
            client_name=data["client_name"],
            attendant_id=data.get("attendant_id"),
            attendant_name=data.get("attendant_name"),
            status=ServiceStatus(data.get("status", "waiting")),
            created_at=data.get("created_at", datetime.now().isoformat()),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            duration_seconds=data.get("duration_seconds"),
            notes=data.get("notes", ""),
        )

    def __str__(self) -> str:
        status_map = {
            ServiceStatus.WAITING: "Na Fila",
            ServiceStatus.IN_PROGRESS: "Em Atendimento",
            ServiceStatus.FINISHED: "Finalizado",
        }
        atendente = self.attendant_name or "—"
        duracao = f"{self.duration_seconds:.0f}s" if self.duration_seconds else "—"
        return (
            f"Atend.#{self.service_id} | Cliente: {self.client_name} | "
            f"Atendente: {atendente} | Status: {status_map[self.status]} | "
            f"Duração: {duracao}"
        )
