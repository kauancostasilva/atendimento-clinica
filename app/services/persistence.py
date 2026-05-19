"""Módulo de persistência - salva e carrega dados em JSON e exporta CSV."""
import csv
import json
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.clinic_manager import ClinicManager

logger = logging.getLogger(__name__)

DATA_FILE = "clinic_data.json"


def save_state(manager: "ClinicManager", filepath: str = DATA_FILE) -> None:
    """Serializa e salva todo o estado do ClinicManager em JSON.
    Complexidade: O(N) onde N é o total de entidades.
    """
    try:
        state = manager.to_dict()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.info("Estado salvo em '%s'.", filepath)
    except OSError as e:
        logger.error("Erro ao salvar estado: %s", e)
        raise


def load_state(manager: "ClinicManager", filepath: str = DATA_FILE) -> bool:
    """Carrega o estado salvo do JSON para o ClinicManager.
    Retorna True se carregado com sucesso, False se o arquivo não existir.
    Complexidade: O(N).
    """
    if not os.path.exists(filepath):
        logger.info("Arquivo '%s' não encontrado. Iniciando com estado vazio.", filepath)
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        manager.load_from_dict(data)
        logger.info("Estado carregado de '%s'.", filepath)
        return True
    except (OSError, json.JSONDecodeError, KeyError) as e:
        logger.error("Erro ao carregar estado: %s", e)
        raise ValueError(f"Erro ao carregar dados salvos: {e}") from e


def export_history_csv(manager: "ClinicManager", filepath: str = None) -> str:
    """Exporta o histórico completo de atendimentos para um arquivo CSV.
    Complexidade: O(N).
    Retorna o caminho do arquivo gerado.
    """
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"relatorio_atendimentos_{timestamp}.csv"

    history = manager.get_history()
    fieldnames = [
        "service_id", "client_id", "client_name",
        "attendant_id", "attendant_name", "status",
        "created_at", "started_at", "finished_at",
        "duration_seconds", "notes",
    ]
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for service in history:
                writer.writerow(service.to_dict())
        logger.info("Relatório de histórico exportado: '%s' (%d registros).", filepath, len(history))
        return filepath
    except OSError as e:
        logger.error("Erro ao exportar CSV: %s", e)
        raise


def export_performance_csv(manager: "ClinicManager", filepath: str = None) -> str:
    """Exporta relatório de desempenho por atendente em CSV.
    Complexidade: O(K log K) onde K é o número de atendentes com atendimentos.
    Retorna o caminho do arquivo gerado.
    """
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"relatorio_desempenho_{timestamp}.csv"

    report = manager.report_by_attendant()
    avg_total = manager.average_service_time()
    fieldnames = ["attendant_id", "name", "count", "total_seconds", "avg_seconds"]

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in report:
                avg = row["total_seconds"] / row["count"] if row["count"] > 0 else 0
                writer.writerow({
                    "attendant_id": row["attendant_id"],
                    "name": row["name"],
                    "count": row["count"],
                    "total_seconds": f"{row['total_seconds']:.1f}",
                    "avg_seconds": f"{avg:.1f}",
                })
            # Linha de média geral
            writer.writerow({
                "attendant_id": "—",
                "name": "MÉDIA GERAL",
                "count": "—",
                "total_seconds": "—",
                "avg_seconds": f"{avg_total:.1f}",
            })
        logger.info("Relatório de desempenho exportado: '%s'.", filepath)
        return filepath
    except OSError as e:
        logger.error("Erro ao exportar CSV de desempenho: %s", e)
        raise


def export_top_clients_csv(manager: "ClinicManager", n: int = 5, filepath: str = None) -> str:
    """Exporta top N clientes mais atendidos em CSV.
    Complexidade: O(K log K).
    """
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"relatorio_top_clientes_{timestamp}.csv"

    top = manager.top_clients(n)
    fieldnames = ["posicao", "client_id", "name", "count"]

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, item in enumerate(top, start=1):
                writer.writerow({
                    "posicao": i,
                    "client_id": item["client_id"],
                    "name": item["name"],
                    "count": item["count"],
                })
        logger.info("Top %d clientes exportado: '%s'.", n, filepath)
        return filepath
    except OSError as e:
        logger.error("Erro ao exportar top clientes CSV: %s", e)
        raise
