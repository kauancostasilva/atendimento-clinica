"""Interface de usuário por terminal - Menu interativo da Clínica."""
import os
import sys
from datetime import datetime
from typing import Optional

from app.models.client import Priority
from app.services.clinic_manager import ClinicManager
from app.services.persistence import (
    save_state, load_state,
    export_history_csv, export_performance_csv, export_top_clients_csv,
)

# ────────────────────────────────────────────────────────────────────────────── #
#  CORES ANSI                                                                   #
# ────────────────────────────────────────────────────────────────────────────── #
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
BG_BLUE = "\033[44m"


def _supports_color() -> bool:
    """Detecta se o terminal suporta cores ANSI."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


USE_COLOR = _supports_color()


def c(text: str, color: str) -> str:
    """Aplica cor ANSI ao texto apenas se suportado pelo terminal."""
    return f"{color}{text}{RESET}" if USE_COLOR else text


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _line(char: str = "─", width: int = 64) -> str:
    return char * width


def _header(title: str) -> None:
    print()
    print(c(_line("═"), CYAN))
    print(c(f"  🏥  {title}", BOLD + CYAN))
    print(c(_line("═"), CYAN))
    print()


def _section(title: str) -> None:
    print()
    print(c(f"  ── {title} " + "─" * max(0, 52 - len(title)), BLUE))


def _ok(msg: str) -> None:
    print(c(f"  ✔  {msg}", GREEN))


def _err(msg: str) -> None:
    print(c(f"  ✘  {msg}", RED))


def _warn(msg: str) -> None:
    print(c(f"  ⚠  {msg}", YELLOW))


def _info(msg: str) -> None:
    print(c(f"  ℹ  {msg}", CYAN))


def _pause() -> None:
    input(c("\n  Pressione ENTER para continuar...", DIM))


# ────────────────────────────────────────────────────────────────────────────── #
#  HELPERS DE ENTRADA                                                           #
# ────────────────────────────────────────────────────────────────────────────── #

def _read_str(prompt: str, allow_empty: bool = False) -> str:
    """Lê string do usuário com tratamento de entrada vazia."""
    while True:
        value = input(c(f"  › {prompt}: ", WHITE)).strip()
        if value or allow_empty:
            return value
        _err("Este campo não pode ser vazio.")


def _read_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Lê inteiro com validação de range e tratamento de erro de tipo."""
    while True:
        raw = input(c(f"  › {prompt}: ", WHITE)).strip()
        if not raw.lstrip("-").isdigit():
            _err("Por favor, informe um número inteiro válido.")
            continue
        value = int(raw)
        if min_val is not None and value < min_val:
            _err(f"O valor mínimo é {min_val}.")
            continue
        if max_val is not None and value > max_val:
            _err(f"O valor máximo é {max_val}.")
            continue
        return value


def _read_option(options: list) -> str:
    """Lê uma opção de menu válida."""
    while True:
        choice = input(c("  › Opção: ", YELLOW + BOLD)).strip().lower()
        if choice in options:
            return choice
        _err(f"Opção inválida. Escolha entre: {', '.join(options)}")


def _read_priority() -> Priority:
    """Lê a prioridade do cliente."""
    print(c("  › Prioridade:", WHITE))
    print(c("    [1] Normal", WHITE))
    print(c("    [2] Prioritário (urgente)", YELLOW))
    choice = _read_option(["1", "2"])
    return Priority.PRIORITY if choice == "2" else Priority.NORMAL


def _read_date_filter() -> Optional[str]:
    """Lê um filtro de data no formato YYYY-MM-DD (opcional)."""
    raw = input(c("  › Data (YYYY-MM-DD) ou ENTER para todas: ", WHITE)).strip()
    if not raw:
        return None
    try:
        datetime.strptime(raw, "%Y-%m-%d")
        return raw
    except ValueError:
        _err("Formato de data inválido. Ignorando filtro.")
        return None


# ────────────────────────────────────────────────────────────────────────────── #
#  TELAS DE MENU                                                                #
# ────────────────────────────────────────────────────────────────────────────── #

def _print_main_menu() -> None:
    _header("SISTEMA DE GERENCIAMENTO DE ATENDIMENTOS")
    print(c("  CADASTROS", BOLD))
    print("  [1]  Cadastrar cliente")
    print("  [2]  Cadastrar atendente")
    print("  [3]  Listar clientes")
    print("  [4]  Listar atendentes")
    print("  [5]  Buscar cliente por ID")
    print()
    print(c("  ATENDIMENTO", BOLD))
    print("  [6]  Colocar cliente na fila")
    print("  [7]  Chamar próximo (por atendente)")
    print("  [8]  Finalizar atendimento")
    print("  [9]  Ver estado das filas")
    print("  [10] Desfazer última finalização")
    print()
    print(c("  CLIENTES ATIVOS", BOLD))
    print("  [11] Ver clientes ativos")
    print("  [12] Desativar cliente")
    print("  [13] Remover clientes inativos da lista")
    print()
    print(c("  RELATÓRIOS", BOLD))
    print("  [14] Histórico de atendimentos")
    print("  [15] Tempo médio de atendimento")
    print("  [16] Top 5 clientes mais atendidos")
    print("  [17] Alertas de tempo de espera alto")
    print("  [18] Relatório por atendente")
    print()
    print(c("  EXPORTAÇÃO", BOLD))
    print("  [19] Exportar histórico (CSV)")
    print("  [20] Exportar desempenho (CSV)")
    print("  [21] Exportar top clientes (CSV)")
    print()
    print(c("  [s]  Salvar dados manualmente", DIM))
    print(c("  [0]  Sair", RED))
    print()
    print(c(_line(), CYAN))


# ────────────────────────────────────────────────────────────────────────────── #
#  AÇÕES                                                                        #
# ────────────────────────────────────────────────────────────────────────────── #

def _action_register_client(manager: ClinicManager) -> None:
    _section("CADASTRAR CLIENTE")
    name = _read_str("Nome completo")
    phone = _read_str("Telefone")
    priority = _read_priority()
    try:
        client = manager.register_client(name, phone, priority)
        _ok(f"Cliente cadastrado com sucesso! ID: #{client.client_id}")
        print(c(f"     {client}", WHITE))
    except ValueError as e:
        _err(str(e))


def _action_register_attendant(manager: ClinicManager) -> None:
    _section("CADASTRAR ATENDENTE")
    name = _read_str("Nome do atendente")
    try:
        attendant = manager.register_attendant(name)
        _ok(f"Atendente cadastrado! ID: #{attendant.attendant_id}")
        print(c(f"     {attendant}", WHITE))
    except ValueError as e:
        _err(str(e))


def _action_list_clients(manager: ClinicManager) -> None:
    _section("CLIENTES CADASTRADOS")
    clients = manager.list_clients()
    if not clients:
        _info("Nenhum cliente cadastrado.")
        return
    print(c(f"  {'ID':<6} {'NOME':<30} {'TELEFONE':<15} {'PRIORIDADE':<12} {'STATUS'}", DIM))
    print(c("  " + _line("·", 62), DIM))
    for cl in clients:
        prio = c("[PRIO]", YELLOW) if cl.priority == Priority.PRIORITY else "[NORM]"
        status = c("Ativo", GREEN) if cl.active else c("Inativo", RED)
        print(f"  #{cl.client_id:<5} {cl.name:<30} {cl.phone:<15} {prio:<12} {status}")
    print(c(f"\n  Total: {len(clients)} cliente(s).", DIM))


def _action_list_attendants(manager: ClinicManager) -> None:
    _section("ATENDENTES CADASTRADOS")
    attendants = manager.list_attendants()
    if not attendants:
        _info("Nenhum atendente cadastrado.")
        return
    print(c(f"  {'ID':<6} {'NOME':<30} {'STATUS'}", DIM))
    print(c("  " + _line("·", 50), DIM))
    for att in attendants:
        status = c(f"Atendendo #{att.current_service_id}", YELLOW) if att.busy else c("Disponível", GREEN)
        print(f"  #{att.attendant_id:<5} {att.name:<30} {status}")


def _action_search_client(manager: ClinicManager) -> None:
    _section("BUSCAR CLIENTE POR ID (Busca Binária)")
    client_id = _read_int("ID do cliente", min_val=1)
    client = manager.find_client_by_id(client_id)
    if client:
        _ok("Cliente encontrado:")
        print(c(f"     {client}", WHITE))
    else:
        _err(f"Cliente #{client_id} não encontrado.")


def _action_open_service(manager: ClinicManager) -> None:
    _section("COLOCAR CLIENTE NA FILA")
    client_id = _read_int("ID do cliente", min_val=1)
    try:
        service = manager.open_service(client_id)
        queue_name = c("PRIORITÁRIA", YELLOW) if service.client_id and \
            manager.find_client_by_id(service.client_id) and \
            manager.find_client_by_id(service.client_id).priority == Priority.PRIORITY \
            else c("NORMAL", CYAN)
        _ok(f"Cliente adicionado à fila {queue_name}. Atendimento #{service.service_id} aberto.")
    except ValueError as e:
        _err(str(e))


def _action_call_next(manager: ClinicManager) -> None:
    _section("CHAMAR PRÓXIMO CLIENTE")
    attendants = manager.list_attendants()
    free = [a for a in attendants if not a.busy]
    if not free:
        _warn("Todos os atendentes estão ocupados no momento.")
        _pause()
        return
    print(c("  Atendentes disponíveis:", WHITE))
    for a in free:
        print(f"    #{a.attendant_id} - {a.name}")
    attendant_id = _read_int("ID do atendente", min_val=1)
    try:
        service = manager.call_next(attendant_id)
        _ok(f"Atendimento iniciado!")
        print(c(f"     {service}", WHITE))
    except ValueError as e:
        _err(str(e))


def _action_finish_service(manager: ClinicManager) -> None:
    _section("FINALIZAR ATENDIMENTO")
    busy = [a for a in manager.list_attendants() if a.busy]
    if not busy:
        _warn("Nenhum atendente está em atendimento.")
        _pause()
        return
    print(c("  Atendentes em atendimento:", WHITE))
    for a in busy:
        print(f"    #{a.attendant_id} - {a.name} (serviço #{a.current_service_id})")
    attendant_id = _read_int("ID do atendente", min_val=1)
    notes = _read_str("Observações (opcional, ENTER para pular)", allow_empty=True)
    try:
        service = manager.finish_service(attendant_id, notes)
        dur = f"{service.duration_seconds:.1f}s" if service.duration_seconds else "—"
        _ok(f"Atendimento #{service.service_id} finalizado! Duração: {dur}")
    except ValueError as e:
        _err(str(e))


def _action_show_queues(manager: ClinicManager) -> None:
    _section("ESTADO DAS FILAS")
    pq, nq = manager.get_queue_status()

    print(c(f"\n  🔴 Fila Prioritária ({len(pq)} cliente(s)):", YELLOW + BOLD))
    if pq:
        for i, s in enumerate(pq, 1):
            wait = s.wait_seconds()
            print(f"    {i}. {s.client_name:<30} Espera: {wait:.0f}s")
    else:
        print(c("     (vazia)", DIM))

    print(c(f"\n  🔵 Fila Normal ({len(nq)} cliente(s)):", CYAN + BOLD))
    if nq:
        for i, s in enumerate(nq, 1):
            wait = s.wait_seconds()
            print(f"    {i}. {s.client_name:<30} Espera: {wait:.0f}s")
    else:
        print(c("     (vazia)", DIM))


def _action_undo(manager: ClinicManager) -> None:
    _section("DESFAZER ÚLTIMA FINALIZAÇÃO")
    try:
        service = manager.undo_last_finish()
        _ok(f"Undo realizado! Atendimento #{service.service_id} ({service.client_name}) restaurado para EM ATENDIMENTO.")
    except ValueError as e:
        _err(str(e))


def _action_list_active(manager: ClinicManager) -> None:
    _section("CLIENTES ATIVOS (Lista Encadeada)")
    active = manager.list_active_clients()
    if not active:
        _info("Nenhum cliente ativo na lista encadeada.")
        return
    for cl in active:
        prio = c("[PRIO]", YELLOW) if cl.priority == Priority.PRIORITY else "[NORM]"
        print(f"  #{cl.client_id:<5} {cl.name:<30} {prio}")
    print(c(f"\n  Total: {len(active)} cliente(s) ativo(s).", DIM))


def _action_deactivate_client(manager: ClinicManager) -> None:
    _section("DESATIVAR CLIENTE")
    client_id = _read_int("ID do cliente", min_val=1)
    try:
        client = manager.deactivate_client(client_id)
        _ok(f"Cliente #{client.client_id} - {client.name} desativado.")
    except ValueError as e:
        _err(str(e))


def _action_remove_inactive(manager: ClinicManager) -> None:
    _section("REMOVER CLIENTES INATIVOS")
    removed = manager.remove_inactive_clients()
    if not removed:
        _info("Nenhum cliente inativo encontrado na lista encadeada.")
    else:
        _ok(f"{len(removed)} cliente(s) inativo(s) removido(s):")
        for cl in removed:
            print(c(f"     #{cl.client_id} - {cl.name}", DIM))


def _action_history(manager: ClinicManager) -> None:
    _section("HISTÓRICO DE ATENDIMENTOS")
    client_id_raw = input(c("  › ID do cliente (ENTER para todos): ", WHITE)).strip()
    client_id = int(client_id_raw) if client_id_raw.isdigit() else None
    date_filter = _read_date_filter()
    history = manager.get_history(client_id=client_id, date_filter=date_filter)
    if not history:
        _info("Nenhum atendimento encontrado.")
        return
    print(c(f"\n  {'#SRV':<6} {'CLIENTE':<25} {'ATENDENTE':<20} {'STATUS':<14} {'DURAÇÃO'}", DIM))
    print(c("  " + _line("·", 62), DIM))
    for s in history:
        status_colors = {
            "waiting": CYAN, "in_progress": YELLOW, "finished": GREEN,
        }
        status_label = s.status.value
        col = status_colors.get(status_label, WHITE)
        dur = f"{s.duration_seconds:.0f}s" if s.duration_seconds else "—"
        att = s.attendant_name or "—"
        print(f"  #{s.service_id:<5} {s.client_name:<25} {att:<20} {c(status_label, col):<24} {dur}")
    print(c(f"\n  Total: {len(history)} registro(s).", DIM))


def _action_avg_time(manager: ClinicManager) -> None:
    _section("TEMPO MÉDIO DE ATENDIMENTO")
    date_filter = _read_date_filter()
    avg = manager.average_service_time(date_filter=date_filter)
    if avg == 0:
        _info("Nenhum atendimento finalizado encontrado.")
    else:
        mins = avg // 60
        secs = avg % 60
        _ok(f"Tempo médio: {avg:.1f} segundos ({int(mins)}m {secs:.0f}s)")


def _action_top_clients(manager: ClinicManager) -> None:
    _section("TOP 5 CLIENTES MAIS ATENDIDOS")
    top = manager.top_clients(5)
    if not top:
        _info("Nenhum atendimento finalizado encontrado.")
        return
    print(c(f"\n  {'Pos':<5} {'Cliente':<30} {'Atendimentos'}", DIM))
    print(c("  " + _line("·", 50), DIM))
    medals = ["🥇", "🥈", "🥉", "  4.", "  5."]
    for i, item in enumerate(top):
        medal = medals[i] if i < len(medals) else f"  {i+1}."
        print(f"  {medal}  #{item['client_id']:<5} {item['name']:<28} {c(str(item['count']), YELLOW)} atend.")


def _action_wait_alerts(manager: ClinicManager) -> None:
    _section("ALERTAS DE TEMPO DE ESPERA ALTO")
    alerts = manager.get_wait_alerts()
    if not alerts:
        _ok("Nenhum cliente com tempo de espera elevado.")
        return
    for service, wait_secs in alerts:
        mins = int(wait_secs // 60)
        secs = int(wait_secs % 60)
        _warn(f"⚠  {service.client_name} | Esperando há {mins}m {secs}s (serviço #{service.service_id})")


def _action_report_attendant(manager: ClinicManager) -> None:
    _section("RELATÓRIO POR ATENDENTE")
    report = manager.report_by_attendant()
    if not report:
        _info("Nenhum dado de atendimento disponível.")
        return
    print(c(f"\n  {'ID':<6} {'NOME':<25} {'Atend.':<8} {'Total(s)':<12} {'Média(s)'}", DIM))
    print(c("  " + _line("·", 60), DIM))
    for row in report:
        avg = row["total_seconds"] / row["count"] if row["count"] > 0 else 0
        print(f"  #{row['attendant_id']:<5} {row['name']:<25} {row['count']:<8} {row['total_seconds']:<12.1f} {avg:.1f}")


def _action_export(manager: ClinicManager, kind: str) -> None:
    _section(f"EXPORTAR {kind.upper()} EM CSV")
    try:
        if kind == "historico":
            path = export_history_csv(manager)
        elif kind == "desempenho":
            path = export_performance_csv(manager)
        else:
            path = export_top_clients_csv(manager, n=5)
        _ok(f"Arquivo gerado: {path}")
    except Exception as e:
        _err(f"Erro ao exportar: {e}")


# ────────────────────────────────────────────────────────────────────────────── #
#  LOOP PRINCIPAL                                                                #
# ────────────────────────────────────────────────────────────────────────────── #

VALID_OPTIONS = [str(i) for i in range(22)] + ["s"]


def run() -> None:
    """Ponto de entrada da interface CLI. Carrega dados e mantém o loop principal."""
    manager = ClinicManager()

    # Carrega dados salvos
    try:
        loaded = load_state(manager)
        if loaded:
            _ok("Dados carregados com sucesso.")
    except ValueError as e:
        _warn(f"Não foi possível carregar dados: {e}. Iniciando do zero.")

    while True:
        clear_screen()
        _print_main_menu()

        # Alertas automáticos de espera
        alerts = manager.get_wait_alerts()
        if alerts:
            _warn(f"⚠  {len(alerts)} cliente(s) com tempo de espera elevado! (opção 17 para ver)")
            print()

        choice = _read_option(VALID_OPTIONS)

        clear_screen()

        actions = {
            "1":  lambda: _action_register_client(manager),
            "2":  lambda: _action_register_attendant(manager),
            "3":  lambda: _action_list_clients(manager),
            "4":  lambda: _action_list_attendants(manager),
            "5":  lambda: _action_search_client(manager),
            "6":  lambda: _action_open_service(manager),
            "7":  lambda: _action_call_next(manager),
            "8":  lambda: _action_finish_service(manager),
            "9":  lambda: _action_show_queues(manager),
            "10": lambda: _action_undo(manager),
            "11": lambda: _action_list_active(manager),
            "12": lambda: _action_deactivate_client(manager),
            "13": lambda: _action_remove_inactive(manager),
            "14": lambda: _action_history(manager),
            "15": lambda: _action_avg_time(manager),
            "16": lambda: _action_top_clients(manager),
            "17": lambda: _action_wait_alerts(manager),
            "18": lambda: _action_report_attendant(manager),
            "19": lambda: _action_export(manager, "historico"),
            "20": lambda: _action_export(manager, "desempenho"),
            "21": lambda: _action_export(manager, "top_clientes"),
            "s":  lambda: (save_state(manager), _ok("Dados salvos com sucesso!")),
            "0":  None,
        }

        if choice == "0":
            _section("ENCERRANDO")
            try:
                save_state(manager)
                _ok("Dados salvos automaticamente. Até logo!")
            except Exception as e:
                _err(f"Erro ao salvar dados: {e}")
            print()
            sys.exit(0)

        action = actions.get(choice)
        if action:
            action()

        _pause()
