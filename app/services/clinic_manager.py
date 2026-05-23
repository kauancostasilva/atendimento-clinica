"""Gerenciador central da clínica - Camada de Regras de Negócio."""
import logging
from datetime import datetime
from typing import Optional, List, Tuple

from app.models.client import Client, Priority
from app.models.attendant import Attendant
from app.models.service import Service, ServiceStatus
from app.structures.stack import Stack
from app.structures.queue import Queue
from app.structures.linked_list import LinkedList
from app.structures.sorted_vector import SortedVector
from app.services.algorithms import quicksort, top_n

# Tempo máximo de espera antes de emitir alerta (em segundos)
WAIT_ALERT_THRESHOLD_SECONDS = 900  # 15 minutos

logging.basicConfig(
    filename="clinic.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ClinicManager:
    """Coordena todo o estado e as regras de negócio da clínica.

    Estruturas utilizadas:
        - SortedVector: cadastro de clientes ordenado por ID para busca binária O(log N)
        - LinkedList: lista de clientes ativos para remoção eficiente de inativos O(N)
        - Queue (normal): fila de atendimento FIFO para clientes normais O(1) enqueue/dequeue
        - Queue (priority): fila de prioridade FIFO para clientes urgentes O(1) enqueue/dequeue
        - Stack: pilha de undo para desfazer a última finalização O(1) push/pop
        - list: vetor não ordenado para cadastro temporário de atendentes e histórico completo
    """

    def __init__(self):
        # Cadastros
        self._clients_vector: SortedVector = SortedVector()    # Busca binária O(log N)
        self._active_clients: LinkedList = LinkedList()         # Clientes ativos
        self._attendants: list = []                             # Vetor não ordenado de atendentes
        self._next_client_id: int = 1
        self._next_attendant_id: int = 1
        self._next_service_id: int = 1

        # Filas de atendimento
        self._priority_queue: Queue = Queue()                   # Fila prioritária FIFO O(1)
        self._normal_queue: Queue = Queue()                     # Fila normal FIFO O(1)

        # Histórico e undo
        self._history: list = []                                # Todos os atendimentos
        self._undo_stack: Stack = Stack()                       # Pilha de undo O(1)

    # ------------------------------------------------------------------ #
    #  CLIENTES                                                           #
    # ------------------------------------------------------------------ #

    def register_client(self, name: str, phone: str, priority: Priority = Priority.NORMAL) -> Client:
        """Cadastra um novo cliente. Insere no vetor ordenado e na lista encadeada.
        Complexidade: O(N) inserção ordenada + O(N) append na lista encadeada.
        """
        if not name.strip():
            raise ValueError("O nome do cliente não pode ser vazio.")
        if not phone.strip():
            raise ValueError("O telefone do cliente não pode ser vazio.")

        client = Client(
            client_id=self._next_client_id,
            name=name.strip(),
            phone=phone.strip(),
            priority=priority,
        )
        self._next_client_id += 1
        self._clients_vector.insert(client)   # Mantém vetor ordenado por ID
        self._active_clients.append(client)   # Adiciona à lista encadeada de ativos
        logger.info("Cliente cadastrado: %s", client)
        return client

    def find_client_by_id(self, client_id: int) -> Optional[Client]:
        """Busca rápida por cliente usando Busca Binária Recursiva. Complexidade: O(log N)."""
        return self._clients_vector.search(client_id)

    def list_clients(self) -> list:
        """Retorna todos os clientes cadastrados (do vetor ordenado). Complexidade: O(N)."""
        return self._clients_vector.to_list()

    def list_active_clients(self) -> list:
        """Retorna clientes ativos da lista encadeada. Complexidade: O(N)."""
        return self._active_clients.to_list()

    def deactivate_client(self, client_id: int) -> Client:
        """Marca cliente como inativo. Não permite remoção com atendimento em aberto.
        Complexidade: O(N) para verificar serviços abertos + O(log N) busca binária.
        """
        client = self.find_client_by_id(client_id)
        if client is None:
            raise ValueError(f"Cliente #{client_id} não encontrado.")

        # Verifica atendimento em aberto
        open_services = [
            s for s in self._history
            if s.client_id == client_id and s.status == ServiceStatus.IN_PROGRESS
        ]
        if open_services:
            raise ValueError(
                f"Cliente #{client_id} possui atendimento em aberto. Finalize antes de remover."
            )

        # Verifica se está na fila
        in_queue = any(
            s.client_id == client_id
            for s in self._priority_queue.to_list() + self._normal_queue.to_list()
        )
        if in_queue:
            raise ValueError(
                f"Cliente #{client_id} está na fila de espera. Não é possível desativá-lo agora."
            )

        client.active = False
        self._clients_vector.update(client)
        logger.info("Cliente desativado: #%d - %s", client_id, client.name)
        return client

    def remove_inactive_clients(self) -> list:
        """Remove da lista encadeada todos os clientes marcados como inativos.
        Complexidade: O(N) - percorre a lista uma única vez.
        """
        removed = self._active_clients.remove_inactive_clients()
        for c in removed:
            logger.info("Cliente inativo removido da lista ativa: #%d - %s", c.client_id, c.name)
        return removed

    # ------------------------------------------------------------------ #
    #  ATENDENTES                                                         #
    # ------------------------------------------------------------------ #

    def register_attendant(self, name: str) -> Attendant:
        """Cadastra um novo atendente no vetor não ordenado. Complexidade: O(1) amortizado."""
        if not name.strip():
            raise ValueError("O nome do atendente não pode ser vazio.")

        attendant = Attendant(
            attendant_id=self._next_attendant_id,
            name=name.strip(),
        )
        self._next_attendant_id += 1
        self._attendants.append(attendant)  # Vetor não ordenado O(1)
        logger.info("Atendente cadastrado: %s", attendant)
        return attendant

    def find_attendant_by_id(self, attendant_id: int) -> Optional[Attendant]:
        """Busca linear de atendente por ID. Complexidade: O(N)."""
        for att in self._attendants:
            if att.attendant_id == attendant_id:
                return att
        return None

    def list_attendants(self) -> list:
        """Retorna todos os atendentes. Complexidade: O(1)."""
        return list(self._attendants)

    def get_free_attendant(self) -> Optional[Attendant]:
        """Retorna o primeiro atendente disponível. Complexidade: O(N)."""
        for att in self._attendants:
            if not att.busy:
                return att
        return None

    # ------------------------------------------------------------------ #
    #  FILAS E ATENDIMENTO                                                #
    # ------------------------------------------------------------------ #

    def open_service(self, client_id: int) -> Service:
        """Coloca o cliente na fila adequada (prioridade ou normal).
        Regra: clientes prioritários entram na fila de prioridade.
        Complexidade: O(log N) busca + O(1) enqueue.
        """
        client = self.find_client_by_id(client_id)
        if client is None:
            raise ValueError(f"Cliente #{client_id} não encontrado.")
        if not client.active:
            raise ValueError(f"Cliente #{client_id} está inativo e não pode entrar na fila.")

        # Verifica se já está em atendimento ou na fila
        already_in = any(
            s.client_id == client_id and s.status in (ServiceStatus.WAITING, ServiceStatus.IN_PROGRESS)
            for s in self._history
        )
        if already_in:
            raise ValueError(f"Cliente #{client_id} já possui um atendimento aberto ou está na fila.")

        service = Service(
            service_id=self._next_service_id,
            client_id=client.client_id,
            client_name=client.name,
        )
        self._next_service_id += 1
        self._history.append(service)

        if client.priority == Priority.PRIORITY:
            self._priority_queue.enqueue(service)
            logger.info("Cliente prioritário adicionado à fila: %s", client.name)
        else:
            self._normal_queue.enqueue(service)
            logger.info("Cliente adicionado à fila normal: %s", client.name)

        return service

    def call_next(self, attendant_id: int) -> Optional[Service]:
        """Chama o próximo cliente da fila respeitando a prioridade.
        Regra: fila prioritária sempre antes da fila normal.
        Não permite chamar se o atendente já está ocupado.
        Complexidade: O(N) busca atendente + O(1) dequeue.
        """
        attendant = self.find_attendant_by_id(attendant_id)
        if attendant is None:
            raise ValueError(f"Atendente #{attendant_id} não encontrado.")
        if attendant.busy:
            raise ValueError(
                f"Atendente #{attendant_id} já está ocupado (serviço #{attendant.current_service_id})."
            )

        # Prioridade sempre antes
        if not self._priority_queue.is_empty():
            service = self._priority_queue.dequeue()
            logger.info("Chamando da fila PRIORITÁRIA: %s", service.client_name)
        elif not self._normal_queue.is_empty():
            service = self._normal_queue.dequeue()
            logger.info("Chamando da fila NORMAL: %s", service.client_name)
        else:
            raise ValueError("Não há clientes aguardando em nenhuma fila.")

        service.start(attendant.attendant_id, attendant.name)
        attendant.busy = True
        attendant.current_service_id = service.service_id
        logger.info(
            "Atendimento iniciado: serviço #%d | %s → %s",
            service.service_id, service.client_name, attendant.name,
        )
        return service

    def finish_service(self, attendant_id: int, notes: str = "") -> Service:
        """Finaliza o atendimento do atendente especificado e registra na pilha de undo.
        Não permite finalizar sem cliente em atendimento.
        Complexidade: O(N) localizar serviço + O(1) push undo.
        """
        attendant = self.find_attendant_by_id(attendant_id)
        if attendant is None:
            raise ValueError(f"Atendente #{attendant_id} não encontrado.")
        if not attendant.busy:
            raise ValueError(f"Atendente #{attendant_id} não está atendendo nenhum cliente.")

        service_id = attendant.current_service_id
        service = next((s for s in self._history if s.service_id == service_id), None)
        if service is None:
            raise ValueError(f"Serviço #{service_id} não encontrado no histórico.")

        service.finish(notes)
        attendant.busy = False
        attendant.current_service_id = None

        # Salva estado para undo
        self._undo_stack.push({
            "service": service,
            "attendant_id": attendant_id,
        })

        logger.info(
            "Atendimento finalizado: serviço #%d | %s | duração: %.1fs",
            service.service_id, service.client_name, service.duration_seconds or 0,
        )
        return service

    def undo_last_finish(self) -> Service:
        """Desfaz a última finalização de atendimento usando a Pilha de Undo.
        Restaura o atendimento para status IN_PROGRESS e o atendente para ocupado.
        Complexidade: O(1) pop da pilha + O(N) para localizar atendente.
        """
        if self._undo_stack.is_empty():
            raise ValueError("Não há ações para desfazer.")

        state = self._undo_stack.pop()
        service: Service = state["service"]
        attendant_id: int = state["attendant_id"]

        attendant = self.find_attendant_by_id(attendant_id)
        if attendant is None:
            raise ValueError(f"Atendente #{attendant_id} não encontrado ao desfazer.")

        if attendant.busy:
            raise ValueError(
                f"Atendente #{attendant_id} já está ocupado. Não é possível desfazer agora."
            )

        # Restaura estado anterior
        service.status = ServiceStatus.IN_PROGRESS
        service.finished_at = None
        service.duration_seconds = None
        service.notes = ""
        attendant.busy = True
        attendant.current_service_id = service.service_id

        logger.info(
            "Undo aplicado: serviço #%d restaurado para IN_PROGRESS | atendente: %s",
            service.service_id, attendant.name,
        )
        return service

    # ------------------------------------------------------------------ #
    #  RELATÓRIOS E ANÁLISES                                              #
    # ------------------------------------------------------------------ #

    def get_queue_status(self) -> Tuple[list, list]:
        """Retorna o estado atual das filas (prioritária, normal)."""
        return self._priority_queue.to_list(), self._normal_queue.to_list()

    def get_wait_alerts(self) -> list:
        """Retorna clientes em espera com tempo acima do limite configurado.
        Complexidade: O(N) onde N é o tamanho total das filas.
        """
        alerts = []
        all_waiting = self._priority_queue.to_list() + self._normal_queue.to_list()
        for service in all_waiting:
            wait = service.wait_seconds()
            if wait >= WAIT_ALERT_THRESHOLD_SECONDS:
                alerts.append((service, wait))
        return alerts

    def get_history(self, client_id: int = None, date_filter: str = None) -> list:
        """Retorna o histórico de atendimentos com filtros opcionais.
        Complexidade: O(N) onde N é o tamanho do histórico.
        """
        results = list(self._history)

        if client_id is not None:
            results = [s for s in results if s.client_id == client_id]

        if date_filter:
            results = [
                s for s in results
                if s.created_at and s.created_at.startswith(date_filter)
            ]
        return results

    def average_service_time(self, date_filter: str = None) -> float:
        """Calcula o tempo médio de atendimento (apenas finalizados).
        Usa recursão para somar os tempos.
        Complexidade: O(N) recursiva.
        """
        finished = [
            s for s in self._history
            if s.status == ServiceStatus.FINISHED and s.duration_seconds is not None
        ]
        if date_filter:
            finished = [s for s in finished if s.created_at and s.created_at.startswith(date_filter)]

        if not finished:
            return 0.0

        return self._recursive_sum_durations(finished, 0) / len(finished)

    def _recursive_sum_durations(self, services: list, index: int) -> float:
        """Soma recursiva das durações dos atendimentos finalizados.
        Caso base: index >= len(services) → retorna 0.
        Caso recursivo: soma o atual + chamada recursiva para próximo índice.
        Complexidade: O(N).
        """
        if index >= len(services):
            return 0.0
        return services[index].duration_seconds + self._recursive_sum_durations(services, index + 1)

    def top_clients(self, n: int = 5) -> list:
        """Retorna os N clientes mais atendidos usando Quicksort recursivo.
        Complexidade: O(K log K) onde K é a quantidade de clientes com atendimentos.
        """
        count: dict = {}
        for s in self._history:
            if s.status == ServiceStatus.FINISHED:
                count[s.client_id] = count.get(s.client_id, {"count": 0, "name": s.client_name})
                count[s.client_id]["count"] += 1

        items = [{"client_id": cid, **info} for cid, info in count.items()]
        return top_n(items, n, key_func=lambda x: x["count"])

    def report_by_attendant(self) -> list:
        """Retorna relatório de atendimentos por atendente, ordenado por quantidade.
        Usa Quicksort recursivo. Complexidade: O(K log K).
        """
        count: dict = {}
        for s in self._history:
            if s.status == ServiceStatus.FINISHED and s.attendant_id is not None:
                if s.attendant_id not in count:
                    count[s.attendant_id] = {"name": s.attendant_name, "count": 0, "total_seconds": 0.0}
                count[s.attendant_id]["count"] += 1
                count[s.attendant_id]["total_seconds"] += s.duration_seconds or 0.0

        items = [{"attendant_id": aid, **info} for aid, info in count.items()]
        return quicksort(items, key_func=lambda x: x["count"], reverse=True)

    # ------------------------------------------------------------------ #
    #  ESTADO (para persistência)                                         #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """Serializa todo o estado do gerenciador para persistência."""
        return {
            "next_client_id": self._next_client_id,
            "next_attendant_id": self._next_attendant_id,
            "next_service_id": self._next_service_id,
            "clients": [c.to_dict() for c in self._clients_vector.to_list()],
            "attendants": [a.to_dict() for a in self._attendants],
            "history": [s.to_dict() for s in self._history],
        }

    def load_from_dict(self, data: dict) -> None:
        """Carrega o estado a partir de dados persistidos."""
        from app.models.client import Client
        from app.models.attendant import Attendant
        from app.models.service import Service

        self._next_client_id = data.get("next_client_id", 1)
        self._next_attendant_id = data.get("next_attendant_id", 1)
        self._next_service_id = data.get("next_service_id", 1)

        # Recarrega clientes no vetor ordenado e lista encadeada
        self._clients_vector = SortedVector()
        self._active_clients = LinkedList()
        for c_data in data.get("clients", []):
            client = Client.from_dict(c_data)
            self._clients_vector.insert(client)
            if client.active:
                self._active_clients.append(client)

        # Recarrega atendentes
        self._attendants = [Attendant.from_dict(a) for a in data.get("attendants", [])]

        # Recarrega histórico e reconstrói filas com os em espera/em andamento
        self._history = []
        self._priority_queue = Queue()
        self._normal_queue = Queue()
        self._undo_stack = Stack()

        for s_data in data.get("history", []):
            service = Service.from_dict(s_data)
            self._history.append(service)
            if service.status == ServiceStatus.WAITING:
                client = self._clients_vector.search(service.client_id)
                if client and client.priority == Priority.PRIORITY:
                    self._priority_queue.enqueue(service)
                else:
                    self._normal_queue.enqueue(service)
