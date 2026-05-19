# 🏥 Sistema de Gerenciamento de Atendimentos — Clínica

> Sistema completo de gerenciamento de atendimentos desenvolvido em Python, integrando estruturas de dados clássicas, algoritmos avançados e boas práticas de engenharia de software.

---

## 📋 Objetivo

Construir um software completo de gerenciamento de atendimentos com:
- Cadastro de clientes e atendentes
- Filas de atendimento (comum e prioritária)
- Histórico, relatórios e análise de desempenho
- Uso prático e didático de: Pilhas, Filas, Listas Encadeadas, Vetores Ordenados, Busca Binária Recursiva, Quicksort Recursivo

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior

### Instalação de Dependências
```bash
pip install -r requirements.txt
```

### Executar o Sistema
```bash
python3 main.py
```

### Carregar Dados de Exemplo
```bash
python3 seed_data.py
python3 main.py
```

### Executar Testes Unitários
```bash
python3 -m pytest tests/ -v
```

---

## 🗂️ Estrutura do Projeto

```
atendimento-clinica/
├── main.py                         # Ponto de entrada
├── seed_data.py                    # Script de dados de exemplo
├── requirements.txt                # Dependências (pytest)
├── clinic_data.json                # Persistência (gerado em runtime)
├── clinic.log                      # Log de operações (gerado em runtime)
├── app/
│   ├── models/
│   │   ├── client.py               # Entidade Cliente (id, nome, telefone, prioridade)
│   │   ├── attendant.py            # Entidade Atendente (id, nome, ocupado)
│   │   └── service.py              # Entidade Atendimento (ciclo de vida completo)
│   ├── structures/
│   │   ├── stack.py                # Pilha customizada - LIFO - Undo
│   │   ├── queue.py                # Fila customizada - FIFO - O(1) enq/deq
│   │   ├── linked_list.py          # Lista Encadeada - Clientes Ativos
│   │   └── sorted_vector.py        # Vetor Ordenado + Busca Binária Recursiva
│   ├── services/
│   │   ├── clinic_manager.py       # Regras de negócio centrais
│   │   ├── persistence.py          # Persistência JSON + exportação CSV
│   │   └── algorithms.py           # Quicksort / MergeSort / InsertionSort recursivos
│   └── ui/
│       └── terminal_menu.py        # Interface CLI com cores ANSI e validações
└── tests/
    ├── test_structures.py           # Testes das estruturas de dados
    └── test_services.py             # Testes das regras de negócio
```

---

## ✅ Funcionalidades Implementadas

### Obrigatórias
| # | Funcionalidade | Status |
|---|---|---|
| 1 | Cadastro de clientes (id, nome, telefone, prioridade) | ✅ |
| 2 | Cadastro de atendentes (id, nome) | ✅ |
| 3 | Abertura de atendimento (cliente entra em fila) | ✅ |
| 4 | Fila comum e fila de prioridade | ✅ |
| 5 | Chamada do próximo considerando prioridade | ✅ |
| 6 | Finalização com registro (data, duração, atendente) | ✅ |
| 7 | Histórico de atendimentos por cliente | ✅ |
| 8 | Desfazer última finalização (pilha) | ✅ |
| 9 | Remover clientes inativos (lista encadeada) | ✅ |
| 10 | Relatório de tempo médio de atendimento | ✅ |
| 11 | Exportar relatórios em CSV | ✅ |
| 12 | Busca rápida por cliente (vetor ordenado + busca binária) | ✅ |

### Extras
| Funcionalidade | Status |
|---|---|
| Filtro de histórico por data | ✅ |
| Top 5 clientes mais atendidos | ✅ |
| Alertas para tempo de espera alto (> 15 min) | ✅ |

---

## 🏗️ Estruturas de Dados e Análise Big-O

### 1. `SortedVector` — Vetor Ordenado com Busca Binária Recursiva
**Arquivo:** `app/structures/sorted_vector.py`

Mantém clientes ordenados por `client_id`. A inserção faz shift dos elementos para preservar a ordem.

| Operação | Complexidade | Justificativa |
|---|---|---|
| `insert()` | O(N) | Shift de elementos para inserção ordenada |
| `search()` (busca binária) | **O(log N)** | Divide o espaço de busca pela metade a cada chamada recursiva |
| `remove()` | O(N) | Shift de elementos |
| `update()` | O(N) | Busca linear para encontrar o índice |

**Recursão implementada em `_binary_search_recursive(id, low, high)`:**
- Caso base 1: `low > high` → elemento não encontrado, retorna `None`
- Caso base 2: `data[mid].id == id` → elemento encontrado
- Caso recursivo: busca na metade esquerda (`high = mid - 1`) ou direita (`low = mid + 1`)

---

### 2. `Queue` — Fila Customizada FIFO com Ponteiros head/tail
**Arquivo:** `app/structures/queue.py`

Usada para a **fila comum** e a **fila prioritária**. Mantém ponteiros `head` e `tail` para garantir O(1) em ambas as operações principais, evitando o O(N) do `list.pop(0)` nativo do Python.

| Operação | Complexidade | Justificativa |
|---|---|---|
| `enqueue()` | **O(1)** | Inserção no tail com ponteiro direto |
| `dequeue()` | **O(1)** | Remoção do head com ponteiro direto |
| `to_list()` | O(N) | Percorre todos os nós |

**Regra de prioridade:** O `ClinicManager` mantém **duas filas separadas** (`_priority_queue` e `_normal_queue`). Ao chamar o próximo, verifica a fila prioritária primeiro. Isso preserva a ordem de chegada dentro de cada nível de prioridade (FIFO justo).

---

### 3. `Stack` — Pilha Customizada LIFO para Undo
**Arquivo:** `app/structures/stack.py`

Usada para desfazer a última finalização de atendimento.

| Operação | Complexidade | Justificativa |
|---|---|---|
| `push()` | **O(1)** | Inserção no topo com ponteiro |
| `pop()` | **O(1)** | Remoção do topo com ponteiro |
| `peek()` | **O(1)** | Leitura do topo sem remoção |

---

### 4. `LinkedList` — Lista Encadeada de Clientes Ativos
**Arquivo:** `app/structures/linked_list.py`

Mantém a lista de clientes ativos no sistema. Ideal para remoção eficiente de nós sem necessidade de realocação de memória (como ocorre em arrays).

| Operação | Complexidade | Justificativa |
|---|---|---|
| `append()` | O(N) | Percorre até o fim para inserir |
| `remove_by_id()` | O(N) | Percorre até encontrar o nó anterior |
| `remove_inactive_clients()` | **O(N)** | **Uma única passagem pela lista inteira** |
| `find_by_id()` | O(N) | Busca linear |

---

### 5. `Quicksort Recursivo` — Algoritmo de Ordenação para Relatórios
**Arquivo:** `app/services/algorithms.py`

Usado para ordenar relatórios de Top 5 clientes, relatórios por atendente e filtros de histórico.

| Operação | Complexidade | Justificativa |
|---|---|---|
| `quicksort()` | **O(N log N)** médio | Divisão e conquista recursiva |
| `quicksort()` | O(N²) pior caso | Evitado com estratégia **mediana de três** |
| Espaço (pilha de chamadas) | O(log N) | Recursão balanceada |

**Recursão implementada em `quicksort(items, key_func, reverse)`:**
- Caso base: `len(items) <= 1` → retorna a lista diretamente
- Caso recursivo: particiona em `smaller + equal + greater` e aplica `quicksort` em cada parte

Implementamos também `merge_sort()` (O(N log N) garantido) e `insertion_sort()` (O(N²), eficiente para pequenas listas).

---

### 6. `_recursive_sum_durations` — Recursão em Relatório
**Arquivo:** `app/services/clinic_manager.py`

Soma as durações dos atendimentos finalizados de forma recursiva para calcular a média:
- Caso base: `index >= len(services)` → retorna 0
- Caso recursivo: `durations[index] + _recursive_sum_durations(services, index + 1)`

---

## 🔒 Regras de Negócio

- **Prioridade sempre na frente**, mas a ordem de chegada é preservada dentro de cada nível (FIFO justo por fila separada).
- **Atendente só atende um cliente por vez** — bloqueio verificado antes de qualquer chamada.
- **Não é possível finalizar sem atendimento em aberto** — verificação de estado antes da finalização.
- **Não é possível desativar cliente com atendimento em aberto ou na fila** — proteção de integridade.
- **Alerta automático** se cliente espera mais de 15 minutos na fila.

---

## 📦 Separação de Camadas

| Camada | Pasta | Responsabilidade |
|---|---|---|
| **Dados** | `app/models/` | Entidades e serialização |
| **Estruturas** | `app/structures/` | Implementações puras das estruturas de dados |
| **Negócio** | `app/services/` | Regras de negócio, algoritmos, persistência |
| **Interface** | `app/ui/` | Menu CLI, validação de entrada, exibição |

---

## 🧪 Testes

```bash
# Rodar todos os testes
python3 -m pytest tests/ -v

# Apenas testes de estruturas
python3 -m pytest tests/test_structures.py -v

# Apenas testes de regras de negócio
python3 -m pytest tests/test_services.py -v
```

Cobertura de testes:
- **Stack**: push, pop, peek, LIFO, clear, IndexError
- **Queue**: enqueue, dequeue, FIFO, peek, IndexError, to_list
- **LinkedList**: append, find, remove, remove_inactive
- **SortedVector**: insert ordenado, busca binária (incluindo N=1000), update, remove
- **Algorithms**: quicksort, merge_sort, insertion_sort, top_n
- **ClinicManager**: cadastro, filas, prioridade, finalização, undo, relatórios, recursão

---

## 👤 Autor

Projeto desenvolvido como trabalho acadêmico de Estruturas de Dados em Python.
