class LinkedListNode:
    """Nó individual para a Lista Encadeada de clientes ativos."""
    def __init__(self, client):
        self.client = client
        self.next = None


class LinkedList:
    """Implementação customizada de Lista Encadeada Simples para armazenar
    clientes ativos. Permite remoção eficiente de clientes inativos.

    Complexidade:
        - Inserção (head): O(1)
        - Busca por ID: O(N)
        - Remoção por ID: O(N) - necessita percorrer para encontrar o nó anterior
        - Remoção de todos inativos: O(N)
    """
    def __init__(self):
        self._head = None
        self._size = 0

    def append(self, client) -> None:
        """Adiciona um cliente ao final da lista. Complexidade: O(N)."""
        node = LinkedListNode(client)
        if self._head is None:
            self._head = node
        else:
            current = self._head
            while current.next is not None:
                current = current.next
            current.next = node
        self._size += 1

    def remove_by_id(self, client_id: int) -> bool:
        """Remove o cliente com o ID especificado. Complexidade: O(N).
        Retorna True se removido com sucesso, False se não encontrado.
        """
        if self._head is None:
            return False

        if self._head.client.client_id == client_id:
            self._head = self._head.next
            self._size -= 1
            return True

        current = self._head
        while current.next is not None:
            if current.next.client.client_id == client_id:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        return False

    def remove_inactive_clients(self) -> list:
        """Remove todos os clientes marcados como inativos (active=False).
        Percorre a lista uma única vez. Complexidade: O(N).
        Retorna a lista de clientes removidos.
        """
        removed = []
        while self._head is not None and not self._head.client.active:
            removed.append(self._head.client)
            self._head = self._head.next
            self._size -= 1

        current = self._head
        while current is not None and current.next is not None:
            if not current.next.client.active:
                removed.append(current.next.client)
                current.next = current.next.next
                self._size -= 1
            else:
                current = current.next
        return removed

    def find_by_id(self, client_id: int):
        """Busca um cliente pelo ID. Complexidade: O(N).
        Retorna o objeto Client se encontrado, None caso contrário.
        """
        current = self._head
        while current is not None:
            if current.client.client_id == client_id:
                return current.client
            current = current.next
        return None

    def to_list(self) -> list:
        """Converte a lista encadeada para lista Python. Complexidade: O(N)."""
        items = []
        current = self._head
        while current is not None:
            items.append(current.client)
            current = current.next
        return items

    def is_empty(self) -> bool:
        return self._head is None

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size
