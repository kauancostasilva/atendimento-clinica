"""Testes unitários das regras de negócio do ClinicManager."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.clinic_manager import ClinicManager
from app.models.client import Priority
from app.models.service import ServiceStatus


@pytest.fixture
def manager():
    """Fixture: ClinicManager limpo para cada teste."""
    return ClinicManager()


@pytest.fixture
def manager_with_data(manager):
    """Fixture: ClinicManager com clientes e atendentes pré-cadastrados."""
    manager.register_client("Ana Silva", "99111-1111", Priority.NORMAL)       # ID=1
    manager.register_client("Bruno Costa", "99222-2222", Priority.PRIORITY)   # ID=2
    manager.register_client("Carla Dias", "99333-3333", Priority.NORMAL)      # ID=3
    manager.register_attendant("Dr. João")                                    # ID=1
    manager.register_attendant("Dra. Maria")                                  # ID=2
    return manager


# ────────────────────────────────────────────────────────────────────────────── #
#  CADASTROS                                                                    #
# ────────────────────────────────────────────────────────────────────────────── #

class TestRegistration:
    def test_register_client_normal(self, manager):
        client = manager.register_client("João", "99000-0000")
        assert client.client_id == 1
        assert client.name == "João"
        assert client.priority == Priority.NORMAL
        assert client.active is True

    def test_register_client_priority(self, manager):
        client = manager.register_client("Maria", "99000-0001", Priority.PRIORITY)
        assert client.priority == Priority.PRIORITY

    def test_register_client_empty_name_raises(self, manager):
        with pytest.raises(ValueError, match="nome"):
            manager.register_client("", "99000-0000")

    def test_register_client_empty_phone_raises(self, manager):
        with pytest.raises(ValueError, match="telefone"):
            manager.register_client("José", "")

    def test_register_client_auto_increment_id(self, manager):
        c1 = manager.register_client("A", "1")
        c2 = manager.register_client("B", "2")
        assert c2.client_id == c1.client_id + 1

    def test_register_attendant(self, manager):
        att = manager.register_attendant("Dr. Pedro")
        assert att.attendant_id == 1
        assert att.name == "Dr. Pedro"
        assert att.busy is False

    def test_register_attendant_empty_name_raises(self, manager):
        with pytest.raises(ValueError, match="nome"):
            manager.register_attendant("  ")

    def test_find_client_by_id_binary_search(self, manager_with_data):
        client = manager_with_data.find_client_by_id(2)
        assert client is not None
        assert client.name == "Bruno Costa"

    def test_find_client_by_id_not_found(self, manager_with_data):
        assert manager_with_data.find_client_by_id(999) is None


# ────────────────────────────────────────────────────────────────────────────── #
#  FILAS E PRIORIDADE                                                           #
# ────────────────────────────────────────────────────────────────────────────── #

class TestQueues:
    def test_normal_client_goes_to_normal_queue(self, manager_with_data):
        manager_with_data.open_service(1)  # Ana - NORMAL
        pq, nq = manager_with_data.get_queue_status()
        assert len(nq) == 1
        assert len(pq) == 0

    def test_priority_client_goes_to_priority_queue(self, manager_with_data):
        manager_with_data.open_service(2)  # Bruno - PRIORITY
        pq, nq = manager_with_data.get_queue_status()
        assert len(pq) == 1
        assert len(nq) == 0

    def test_priority_called_before_normal(self, manager_with_data):
        manager_with_data.open_service(1)  # Ana - NORMAL (entra primeiro)
        manager_with_data.open_service(2)  # Bruno - PRIORITY (entra depois)
        service = manager_with_data.call_next(1)  # Dr. João chama o próximo
        assert service.client_name == "Bruno Costa"  # Prioritário deve sair primeiro

    def test_normal_fifo_order(self, manager_with_data):
        manager_with_data.open_service(1)  # Ana
        manager_with_data.open_service(3)  # Carla
        s1 = manager_with_data.call_next(1)
        assert s1.client_name == "Ana Silva"  # Primeiro a entrar

    def test_open_service_inactive_client_raises(self, manager_with_data):
        manager_with_data.deactivate_client(1)
        with pytest.raises(ValueError, match="inativo"):
            manager_with_data.open_service(1)

    def test_open_service_duplicate_raises(self, manager_with_data):
        manager_with_data.open_service(1)
        with pytest.raises(ValueError, match="aberto"):
            manager_with_data.open_service(1)

    def test_call_next_empty_queue_raises(self, manager_with_data):
        with pytest.raises(ValueError, match="fila"):
            manager_with_data.call_next(1)

    def test_call_next_busy_attendant_raises(self, manager_with_data):
        manager_with_data.open_service(1)
        manager_with_data.call_next(1)
        manager_with_data.open_service(3)
        with pytest.raises(ValueError, match="ocupado"):
            manager_with_data.call_next(1)


# ────────────────────────────────────────────────────────────────────────────── #
#  FINALIZAÇÃO E UNDO                                                           #
# ────────────────────────────────────────────────────────────────────────────── #

class TestFinishAndUndo:
    def _setup_in_progress(self, manager_with_data):
        """Coloca Ana na fila e Dr. João a chama."""
        manager_with_data.open_service(1)
        return manager_with_data.call_next(1)

    def test_finish_service_sets_status_finished(self, manager_with_data):
        self._setup_in_progress(manager_with_data)
        service = manager_with_data.finish_service(1, notes="Sem intercorrências")
        assert service.status == ServiceStatus.FINISHED
        assert service.finished_at is not None
        assert service.notes == "Sem intercorrências"

    def test_finish_service_frees_attendant(self, manager_with_data):
        self._setup_in_progress(manager_with_data)
        manager_with_data.finish_service(1)
        att = manager_with_data.find_attendant_by_id(1)
        assert att.busy is False
        assert att.current_service_id is None

    def test_finish_service_not_busy_raises(self, manager_with_data):
        with pytest.raises(ValueError, match="atendendo"):
            manager_with_data.finish_service(1)

    def test_undo_restores_in_progress(self, manager_with_data):
        service = self._setup_in_progress(manager_with_data)
        manager_with_data.finish_service(1)
        restored = manager_with_data.undo_last_finish()
        assert restored.status == ServiceStatus.IN_PROGRESS
        assert restored.finished_at is None
        att = manager_with_data.find_attendant_by_id(1)
        assert att.busy is True
        assert att.current_service_id == service.service_id

    def test_undo_empty_stack_raises(self, manager_with_data):
        with pytest.raises(ValueError, match="desfazer"):
            manager_with_data.undo_last_finish()

    def test_undo_twice(self, manager_with_data):
        """Testa desfazer duas ações consecutivas (dois atendentes)."""
        manager_with_data.open_service(1)
        manager_with_data.open_service(3)
        manager_with_data.call_next(1)  # Dr. João atende Ana
        manager_with_data.call_next(2)  # Dra. Maria atende Carla
        manager_with_data.finish_service(1)
        manager_with_data.finish_service(2)
        manager_with_data.undo_last_finish()  # Desfaz Carla
        manager_with_data.undo_last_finish()  # Desfaz Ana
        assert manager_with_data.find_attendant_by_id(1).busy is True
        assert manager_with_data.find_attendant_by_id(2).busy is True


# ────────────────────────────────────────────────────────────────────────────── #
#  CLIENTES ATIVOS E LISTA ENCADEADA                                            #
# ────────────────────────────────────────────────────────────────────────────── #

class TestActiveClients:
    def test_deactivate_client(self, manager_with_data):
        manager_with_data.deactivate_client(3)
        client = manager_with_data.find_client_by_id(3)
        assert client.active is False

    def test_deactivate_client_with_open_service_raises(self, manager_with_data):
        manager_with_data.open_service(1)
        manager_with_data.call_next(1)
        with pytest.raises(ValueError, match="aberto"):
            manager_with_data.deactivate_client(1)

    def test_deactivate_client_in_queue_raises(self, manager_with_data):
        manager_with_data.open_service(1)
        with pytest.raises(ValueError, match="fila"):
            manager_with_data.deactivate_client(1)

    def test_remove_inactive_updates_linked_list(self, manager_with_data):
        manager_with_data.deactivate_client(3)
        removed = manager_with_data.remove_inactive_clients()
        assert any(c.client_id == 3 for c in removed)
        active = manager_with_data.list_active_clients()
        assert not any(c.client_id == 3 for c in active)


# ────────────────────────────────────────────────────────────────────────────── #
#  RELATÓRIOS                                                                   #
# ────────────────────────────────────────────────────────────────────────────── #

class TestReports:
    def _full_service_cycle(self, manager_with_data, client_id: int, attendant_id: int):
        """Helper: abre serviço, chama e finaliza."""
        manager_with_data.open_service(client_id)
        manager_with_data.call_next(attendant_id)
        manager_with_data.finish_service(attendant_id)

    def test_average_service_time_no_services(self, manager_with_data):
        assert manager_with_data.average_service_time() == 0.0

    def test_average_service_time_with_services(self, manager_with_data):
        self._full_service_cycle(manager_with_data, 1, 1)
        avg = manager_with_data.average_service_time()
        assert avg >= 0.0  # Pode ser 0 se foi instantâneo no teste

    def test_top_clients(self, manager_with_data):
        # Ana (ID=1) é atendida 2x, Carla (ID=3) 1x
        self._full_service_cycle(manager_with_data, 1, 1)
        self._full_service_cycle(manager_with_data, 1, 1)
        self._full_service_cycle(manager_with_data, 3, 1)
        top = manager_with_data.top_clients(5)
        assert top[0]["client_id"] == 1
        assert top[0]["count"] == 2

    def test_history_filter_by_client(self, manager_with_data):
        self._full_service_cycle(manager_with_data, 1, 1)
        self._full_service_cycle(manager_with_data, 3, 1)
        history = manager_with_data.get_history(client_id=1)
        assert all(s.client_id == 1 for s in history)

    def test_report_by_attendant(self, manager_with_data):
        self._full_service_cycle(manager_with_data, 1, 1)
        self._full_service_cycle(manager_with_data, 3, 1)
        report = manager_with_data.report_by_attendant()
        assert len(report) >= 1
        assert report[0]["attendant_id"] == 1

    def test_recursive_sum_durations(self, manager_with_data):
        """Testa a rotina recursiva de soma de durações."""
        self._full_service_cycle(manager_with_data, 1, 1)
        finished = [s for s in manager_with_data.get_history() if s.duration_seconds is not None]
        total = manager_with_data._recursive_sum_durations(finished, 0)
        assert total >= 0.0
