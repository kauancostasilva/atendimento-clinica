class SortedVector:
    """Vetor ordenado que mantém os clientes ordenados crescentemente por client_id.
    Permite busca rápida por ID utilizando Busca Binária Recursiva.

    Complexidade:
        - Inserção ordenada: O(N)  - necessita shift dos elementos
        - Busca Binária: O(log N)  - grande vantagem sobre busca linear para grandes N
        - Remoção: O(N)            - necessita shift dos elementos
        - Acesso por índice: O(1)
    """
    def __init__(self):
        self._data: list = []

    def insert(self, client) -> None:
        """Insere um cliente mantendo o vetor ordenado por client_id.
        Complexidade: O(N) devido ao shift de elementos.
        """
        pos = 0
        while pos < len(self._data) and self._data[pos].client_id < client.client_id:
            pos += 1
        self._data.insert(pos, client)  # O(N)

    def search(self, client_id: int):
        """Busca um cliente pelo ID utilizando Busca Binária Recursiva.
        Complexidade: O(log N).
        Retorna o objeto Client se encontrado, None caso contrário.
        """
        return self._binary_search_recursive(client_id, 0, len(self._data) - 1)

    def _binary_search_recursive(self, client_id: int, low: int, high: int):
        """Implementação recursiva da Busca Binária.
        Caso base: low > high (não encontrado) ou elemento encontrado.
        Caso recursivo: busca na metade esquerda ou direita dependendo da comparação.
        Complexidade: O(log N).
        """
        if low > high:
            return None  # Caso base: elemento não encontrado

        mid = (low + high) // 2
        mid_id = self._data[mid].client_id

        if mid_id == client_id:
            return self._data[mid]  # Caso base: elemento encontrado
        elif mid_id < client_id:
            return self._binary_search_recursive(client_id, mid + 1, high)  # Recursão direita
        else:
            return self._binary_search_recursive(client_id, low, mid - 1)  # Recursão esquerda

    def remove(self, client_id: int) -> bool:
        """Remove um cliente pelo ID. Complexidade: O(N)."""
        for i, client in enumerate(self._data):
            if client.client_id == client_id:
                self._data.pop(i)
                return True
        return False

    def update(self, updated_client) -> bool:
        """Atualiza os dados de um cliente já existente no vetor. Complexidade: O(log N) busca + O(1) update.
        Retorna True se o cliente foi encontrado e atualizado.
        """
        for i, client in enumerate(self._data):
            if client.client_id == updated_client.client_id:
                self._data[i] = updated_client
                return True
        return False

    def to_list(self) -> list:
        """Retorna uma cópia da lista interna. Complexidade: O(N)."""
        return list(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]
