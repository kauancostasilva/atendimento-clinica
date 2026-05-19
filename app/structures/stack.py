class StackNode:
    """Nó individual para a estrutura de dados Pilha."""
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    """Implementação customizada de uma Pilha (LIFO) baseada em nós encadeados."""
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, item) -> None:
        """Adiciona um item ao topo da pilha. Complexidade: O(1)."""
        node = StackNode(item)
        node.next = self._top
        self._top = node
        self._size += 1

    def pop(self):
        """Remove e retorna o item do topo da pilha. Levanta IndexError se vazia. Complexidade: O(1)."""
        if self.is_empty():
            raise IndexError("A pilha está vazia. Não é possível remover elementos.")
        
        popped_node = self._top
        self._top = popped_node.next
        self._size -= 1
        return popped_node.data

    def peek(self):
        """Retorna o item no topo da pilha sem removê-lo. Levanta IndexError se vazia. Complexidade: O(1)."""
        if self.is_empty():
            raise IndexError("A pilha está vazia.")
        return self._top.data

    def is_empty(self) -> bool:
        """Retorna se a pilha está vazia ou não. Complexidade: O(1)."""
        return self._top is None

    def size(self) -> int:
        """Retorna o número de elementos na pilha. Complexidade: O(1)."""
        return self._size

    def clear(self) -> None:
        """Limpa a pilha por completo. Complexidade: O(1)."""
        self._top = None
        self._size = 0

    def __len__(self) -> int:
        return self.size()
