"""Pacote de modelos de domínio."""
from .client import Client, Priority
from .attendant import Attendant
from .service import Service, ServiceStatus

__all__ = ["Client", "Priority", "Attendant", "Service", "ServiceStatus"]
