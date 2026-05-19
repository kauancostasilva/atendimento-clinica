"""Script de seed para popular o sistema com dados de exemplo."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.client import Priority
from app.services.clinic_manager import ClinicManager
from app.services.persistence import save_state

def seed():
    manager = ClinicManager()

    # Clientes
    manager.register_client("Ana Oliveira", "(11) 9 8765-4321", Priority.NORMAL)
    manager.register_client("Bruno Mendes", "(11) 9 7654-3210", Priority.PRIORITY)
    manager.register_client("Carla Ramos", "(21) 9 6543-2109", Priority.NORMAL)
    manager.register_client("Diego Santos", "(21) 9 5432-1098", Priority.NORMAL)
    manager.register_client("Elena Costa", "(31) 9 4321-0987", Priority.PRIORITY)

    # Atendentes
    manager.register_attendant("Dr. João Ferreira")
    manager.register_attendant("Dra. Maria Souza")

    # Simula atendimentos completos
    # Atendimento 1: Bruno (prioritário) → Dr. João
    manager.open_service(2)  # Bruno
    manager.open_service(1)  # Ana
    manager.open_service(3)  # Carla
    manager.open_service(5)  # Elena (prioritária)
    manager.open_service(4)  # Diego

    s1 = manager.call_next(1)  # Dr. João chama Bruno (prioritário primeiro)
    s2 = manager.call_next(2)  # Dra. Maria chama Elena (prioritária)
    manager.finish_service(1, "Consulta de rotina.")
    manager.finish_service(2, "Urgência atendida com sucesso.")

    s3 = manager.call_next(1)  # Dr. João chama Ana
    manager.finish_service(1, "Primeira consulta.")

    s4 = manager.call_next(2)  # Dra. Maria chama Carla
    manager.finish_service(2)

    # Simula Ana vindo de novo
    manager.open_service(1)
    s5 = manager.call_next(1)
    manager.finish_service(1, "Retorno.")

    # Diego ainda na fila
    manager.open_service(4)

    save_state(manager)
    print("✔ Dados de exemplo carregados e salvos em clinic_data.json")
    print(f"  Clientes cadastrados: {len(manager.list_clients())}")
    print(f"  Atendentes cadastrados: {len(manager.list_attendants())}")
    print(f"  Atendimentos no histórico: {len(manager.get_history())}")

if __name__ == "__main__":
    seed()
