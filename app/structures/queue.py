class QueueNode:
    """Nó individual para a estrutura de dados Fila."""
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    """Implementação customizada de uma Fila (FIFO) baseada em nós encadeados.
    Mantém referências para a cabeça (head) e a cauda (tail) da fila,
    garantindo que inserção e remoção sejam executadas em complexidade constante O(1).
    """
    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def enqueue(self, item) -> None:
        """Adiciona um item ao final da fila (cauda). Complexidade: O(1)."""
        node = QueueNode(item)
        if self.is_empty():
            self._head = node
            self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def dequeue(self):
        """Remove e retorna o item do início da fila (cabeça). Levanta IndexError se vazia. Complexidade: O(1)."""
        if self.is_empty():
            raise IndexError("A fila está vazia. Não é possível remover elementos.")
        
        dequeued_node = self._head
        self._head = dequeued_node.next
        
        if self._head is None:
            self._tail = None
            
        self._size -= 1
        return dequeued_node.data

    def peek(self):
        """Retorna o item no início da fila sem removê-lo. Levanta IndexError se vazia. Complexidade: O(1)."""
        if self.is_empty():
            raise IndexError("A fila está vazia.")
        return self._head.data

    def is_empty(self) -> bool:
        """Retorna se a fila está vazia ou não. Complexidade: O(1)."""
        return self._head is None

    def size(self) -> int:
        """Retorna o número de elementos na fila. Complexidade: O(1)."""
        return self._size

    def to_list(self) -> list:
        """Converte a fila em uma lista Python comum para visualização/processamento. Complexidade: O(N)."""
        items = []
        current = self._head
        while current is not None:
            items.append(current.data)
            current = current.next
        return items

    def __len__(self) -> int:
        return self.size()
