"""Testes unitários das estruturas de dados customizadas."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.structures.stack import Stack
from app.structures.queue import Queue
from app.structures.linked_list import LinkedList
from app.structures.sorted_vector import SortedVector
from app.models.client import Client, Priority
from app.services.algorithms import quicksort, merge_sort, insertion_sort, top_n


# ────────────────────────────────────────────────────────────────────────────── #
#  PILHA (Stack)                                                                #
# ────────────────────────────────────────────────────────────────────────────── #

class TestStack:
    def test_push_and_peek(self):
        s = Stack()
        s.push(10)
        s.push(20)
        assert s.peek() == 20

    def test_pop_returns_last_pushed(self):
        s = Stack()
        s.push("a")
        s.push("b")
        assert s.pop() == "b"
        assert s.pop() == "a"

    def test_pop_empty_raises(self):
        s = Stack()
        with pytest.raises(IndexError):
            s.pop()

    def test_peek_empty_raises(self):
        s = Stack()
        with pytest.raises(IndexError):
            s.peek()

    def test_is_empty(self):
        s = Stack()
        assert s.is_empty()
        s.push(1)
        assert not s.is_empty()

    def test_size(self):
        s = Stack()
        assert s.size() == 0
        s.push(1)
        s.push(2)
        assert s.size() == 2
        s.pop()
        assert s.size() == 1

    def test_len_dunder(self):
        s = Stack()
        s.push("x")
        assert len(s) == 1

    def test_clear(self):
        s = Stack()
        s.push(1)
        s.push(2)
        s.clear()
        assert s.is_empty()
        assert s.size() == 0

    def test_lifo_order(self):
        s = Stack()
        for i in range(5):
            s.push(i)
        result = []
        while not s.is_empty():
            result.append(s.pop())
        assert result == [4, 3, 2, 1, 0]


# ────────────────────────────────────────────────────────────────────────────── #
#  FILA (Queue)                                                                 #
# ────────────────────────────────────────────────────────────────────────────── #

class TestQueue:
    def test_enqueue_and_peek(self):
        q = Queue()
        q.enqueue("primeiro")
        q.enqueue("segundo")
        assert q.peek() == "primeiro"

    def test_dequeue_fifo_order(self):
        q = Queue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        assert q.dequeue() == 1
        assert q.dequeue() == 2
        assert q.dequeue() == 3

    def test_dequeue_empty_raises(self):
        q = Queue()
        with pytest.raises(IndexError):
            q.dequeue()

    def test_peek_empty_raises(self):
        q = Queue()
        with pytest.raises(IndexError):
            q.peek()

    def test_is_empty(self):
        q = Queue()
        assert q.is_empty()
        q.enqueue("x")
        assert not q.is_empty()

    def test_size(self):
        q = Queue()
        assert q.size() == 0
        q.enqueue("a")
        q.enqueue("b")
        assert q.size() == 2
        q.dequeue()
        assert q.size() == 1

    def test_to_list(self):
        q = Queue()
        q.enqueue(10)
        q.enqueue(20)
        q.enqueue(30)
        assert q.to_list() == [10, 20, 30]

    def test_enqueue_after_empty(self):
        q = Queue()
        q.enqueue(1)
        q.dequeue()
        q.enqueue(2)
        assert q.peek() == 2
        assert q.size() == 1


# ────────────────────────────────────────────────────────────────────────────── #
#  LISTA ENCADEADA (LinkedList)                                                 #
# ────────────────────────────────────────────────────────────────────────────── #

def _make_client(cid: int, active: bool = True) -> Client:
    return Client(client_id=cid, name=f"Cliente {cid}", phone="99999-9999", active=active)


class TestLinkedList:
    def test_append_and_to_list(self):
        ll = LinkedList()
        c1 = _make_client(1)
        c2 = _make_client(2)
        ll.append(c1)
        ll.append(c2)
        assert ll.to_list() == [c1, c2]

    def test_size(self):
        ll = LinkedList()
        assert ll.size() == 0
        ll.append(_make_client(1))
        assert ll.size() == 1

    def test_is_empty(self):
        ll = LinkedList()
        assert ll.is_empty()
        ll.append(_make_client(1))
        assert not ll.is_empty()

    def test_find_by_id(self):
        ll = LinkedList()
        ll.append(_make_client(5))
        ll.append(_make_client(10))
        found = ll.find_by_id(10)
        assert found is not None
        assert found.client_id == 10

    def test_find_by_id_not_found(self):
        ll = LinkedList()
        ll.append(_make_client(1))
        assert ll.find_by_id(999) is None

    def test_remove_by_id_head(self):
        ll = LinkedList()
        ll.append(_make_client(1))
        ll.append(_make_client(2))
        result = ll.remove_by_id(1)
        assert result is True
        assert ll.size() == 1
        assert ll.find_by_id(1) is None

    def test_remove_by_id_middle(self):
        ll = LinkedList()
        ll.append(_make_client(1))
        ll.append(_make_client(2))
        ll.append(_make_client(3))
        ll.remove_by_id(2)
        assert ll.size() == 2
        assert ll.find_by_id(2) is None

    def test_remove_by_id_not_found(self):
        ll = LinkedList()
        ll.append(_make_client(1))
        result = ll.remove_by_id(999)
        assert result is False

    def test_remove_inactive_clients(self):
        ll = LinkedList()
        ll.append(_make_client(1, active=True))
        ll.append(_make_client(2, active=False))
        ll.append(_make_client(3, active=True))
        ll.append(_make_client(4, active=False))
        removed = ll.remove_inactive_clients()
        assert len(removed) == 2
        assert ll.size() == 2
        ids_remaining = [c.client_id for c in ll.to_list()]
        assert 1 in ids_remaining
        assert 3 in ids_remaining

    def test_remove_inactive_all_active(self):
        ll = LinkedList()
        ll.append(_make_client(1))
        ll.append(_make_client(2))
        removed = ll.remove_inactive_clients()
        assert removed == []
        assert ll.size() == 2


# ────────────────────────────────────────────────────────────────────────────── #
#  VETOR ORDENADO + BUSCA BINÁRIA (SortedVector)                                #
# ────────────────────────────────────────────────────────────────────────────── #

class TestSortedVector:
    def test_insert_maintains_order(self):
        sv = SortedVector()
        sv.insert(_make_client(5))
        sv.insert(_make_client(1))
        sv.insert(_make_client(3))
        ids = [c.client_id for c in sv.to_list()]
        assert ids == [1, 3, 5]

    def test_search_found(self):
        sv = SortedVector()
        for cid in [10, 5, 20, 15]:
            sv.insert(_make_client(cid))
        found = sv.search(15)
        assert found is not None
        assert found.client_id == 15

    def test_search_not_found(self):
        sv = SortedVector()
        sv.insert(_make_client(1))
        sv.insert(_make_client(2))
        assert sv.search(999) is None

    def test_search_empty(self):
        sv = SortedVector()
        assert sv.search(1) is None

    def test_remove(self):
        sv = SortedVector()
        sv.insert(_make_client(7))
        sv.insert(_make_client(3))
        result = sv.remove(7)
        assert result is True
        assert sv.search(7) is None
        assert sv.size() == 1

    def test_remove_not_found(self):
        sv = SortedVector()
        sv.insert(_make_client(1))
        assert sv.remove(999) is False

    def test_update(self):
        sv = SortedVector()
        cl = _make_client(1)
        sv.insert(cl)
        updated = Client(client_id=1, name="Novo Nome", phone="88888-8888")
        sv.update(updated)
        found = sv.search(1)
        assert found.name == "Novo Nome"

    def test_size_and_len(self):
        sv = SortedVector()
        assert sv.size() == 0
        sv.insert(_make_client(1))
        sv.insert(_make_client(2))
        assert sv.size() == 2
        assert len(sv) == 2

    def test_binary_search_large(self):
        """Testa busca binária com N=1000 clientes."""
        sv = SortedVector()
        for i in range(1, 1001):
            sv.insert(_make_client(i))
        assert sv.search(1).client_id == 1
        assert sv.search(500).client_id == 500
        assert sv.search(1000).client_id == 1000
        assert sv.search(1001) is None


# ────────────────────────────────────────────────────────────────────────────── #
#  ALGORITMOS DE ORDENAÇÃO                                                      #
# ────────────────────────────────────────────────────────────────────────────── #

class TestAlgorithms:
    def _items(self, values):
        return [{"val": v} for v in values]

    def test_quicksort_ascending(self):
        data = [5, 3, 8, 1, 9, 2]
        result = quicksort(data)
        assert result == sorted(data)

    def test_quicksort_descending(self):
        data = [5, 3, 8, 1, 9, 2]
        result = quicksort(data, reverse=True)
        assert result == sorted(data, reverse=True)

    def test_quicksort_with_key(self):
        items = self._items([5, 1, 3, 2, 4])
        result = quicksort(items, key_func=lambda x: x["val"])
        assert [r["val"] for r in result] == [1, 2, 3, 4, 5]

    def test_quicksort_empty(self):
        assert quicksort([]) == []

    def test_quicksort_single(self):
        assert quicksort([42]) == [42]

    def test_quicksort_does_not_modify_original(self):
        data = [3, 1, 2]
        _ = quicksort(data)
        assert data == [3, 1, 2]

    def test_merge_sort_ascending(self):
        data = [7, 2, 5, 1, 8]
        assert merge_sort(data) == sorted(data)

    def test_merge_sort_descending(self):
        data = [7, 2, 5, 1, 8]
        assert merge_sort(data, reverse=True) == sorted(data, reverse=True)

    def test_insertion_sort_ascending(self):
        data = [4, 2, 7, 1, 3]
        assert insertion_sort(data) == sorted(data)

    def test_insertion_sort_already_sorted(self):
        data = [1, 2, 3, 4, 5]
        assert insertion_sort(data) == data

    def test_top_n(self):
        items = [{"name": "A", "count": 3}, {"name": "B", "count": 7},
                 {"name": "C", "count": 1}, {"name": "D", "count": 5}]
        result = top_n(items, 2, key_func=lambda x: x["count"])
        assert result[0]["name"] == "B"
        assert result[1]["name"] == "D"

    def test_top_n_less_than_n(self):
        data = [1, 2]
        result = top_n(data, 5)
        assert result == [2, 1]
