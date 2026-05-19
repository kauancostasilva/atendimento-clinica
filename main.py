#!/usr/bin/env python3
"""Ponto de entrada principal do Sistema de Gerenciamento de Atendimentos."""
import sys
import os

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.terminal_menu import run


def main() -> None:
    """Inicia o sistema de gerenciamento de atendimentos da clínica."""
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n  Sistema encerrado pelo usuário. Até logo!")
        sys.exit(0)


if __name__ == "__main__":
    main()
