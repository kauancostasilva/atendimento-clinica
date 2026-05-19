"""Módulo de algoritmos de ordenação recursiva para relatórios.

Implementa Quicksort recursivo para ordenar listas de atendimentos
e clientes por diferentes critérios.

Complexidade do Quicksort:
    - Caso médio: O(N log N)
    - Pior caso: O(N²) - evitado com escolha inteligente de pivô
    - Espaço: O(log N) na pilha de chamadas recursivas
"""


def quicksort(items: list, key_func=None, reverse: bool = False) -> list:
    """Ordena uma lista usando Quicksort recursivo.

    Args:
        items: Lista de itens a ordenar.
        key_func: Função que extrai o valor de comparação de cada item.
                  Se None, compara os itens diretamente.
        reverse: Se True, ordena em ordem decrescente.

    Returns:
        Nova lista ordenada (não modifica a original).

    Complexidade: O(N log N) caso médio, O(N²) pior caso.
    """
    if len(items) <= 1:
        return list(items)  # Caso base: lista vazia ou com 1 elemento

    # Escolha de pivô: mediana entre primeiro, meio e último (evita pior caso)
    pivot_index = _median_of_three_index(items, key_func)
    pivot = items[pivot_index]
    pivot_key = key_func(pivot) if key_func else pivot

    # Particionar: menores, iguais, maiores
    smaller = [x for x in items if (key_func(x) if key_func else x) < pivot_key]
    equal = [x for x in items if (key_func(x) if key_func else x) == pivot_key]
    greater = [x for x in items if (key_func(x) if key_func else x) > pivot_key]

    # Recursão nas sub-listas
    if not reverse:
        return quicksort(smaller, key_func, reverse) + equal + quicksort(greater, key_func, reverse)
    else:
        return quicksort(greater, key_func, reverse) + equal + quicksort(smaller, key_func, reverse)


def _median_of_three_index(items: list, key_func) -> int:
    """Retorna o índice do pivô usando a estratégia mediana de três.
    Reduz a probabilidade do pior caso O(N²) em listas já ordenadas.
    """
    n = len(items)
    indices = [0, n // 2, n - 1]
    keys = [(key_func(items[i]) if key_func else items[i], i) for i in indices]
    keys.sort()
    return keys[1][1]  # Índice do elemento do meio (mediana)


def insertion_sort(items: list, key_func=None, reverse: bool = False) -> list:
    """Ordena uma lista pequena usando Insertion Sort.
    Eficiente para listas pequenas (N < 20) ou quase ordenadas.

    Complexidade: O(N²) pior caso, O(N) para listas quase ordenadas.
    """
    result = list(items)
    for i in range(1, len(result)):
        current = result[i]
        current_key = key_func(current) if key_func else current
        j = i - 1
        while j >= 0:
            compare_key = key_func(result[j]) if key_func else result[j]
            if (not reverse and compare_key > current_key) or (reverse and compare_key < current_key):
                result[j + 1] = result[j]
                j -= 1
            else:
                break
        result[j + 1] = current
    return result


def merge_sort(items: list, key_func=None, reverse: bool = False) -> list:
    """Ordena uma lista usando Merge Sort recursivo.
    Garante O(N log N) em todos os casos (inclusive pior caso).

    Complexidade: O(N log N) sempre. Espaço: O(N).
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = merge_sort(items[:mid], key_func, reverse)
    right = merge_sort(items[mid:], key_func, reverse)
    return _merge(left, right, key_func, reverse)


def _merge(left: list, right: list, key_func, reverse: bool) -> list:
    """Mescla duas listas ordenadas em uma única lista ordenada. Complexidade: O(N)."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        lk = key_func(left[i]) if key_func else left[i]
        rk = key_func(right[j]) if key_func else right[j]
        if (not reverse and lk <= rk) or (reverse and lk >= rk):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def top_n(items: list, n: int, key_func=None) -> list:
    """Retorna os N maiores elementos de uma lista usando Quicksort recursivo.
    Complexidade: O(K log K) onde K = len(items).
    """
    sorted_items = quicksort(items, key_func=key_func, reverse=True)
    return sorted_items[:n]
