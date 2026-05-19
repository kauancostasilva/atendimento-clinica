"""Pacote de serviços e regras de negócio."""
from .clinic_manager import ClinicManager
from .persistence import save_state, load_state, export_history_csv, export_performance_csv, export_top_clients_csv
from .algorithms import quicksort, merge_sort, insertion_sort, top_n

__all__ = [
    "ClinicManager",
    "save_state", "load_state",
    "export_history_csv", "export_performance_csv", "export_top_clients_csv",
    "quicksort", "merge_sort", "insertion_sort", "top_n",
]
