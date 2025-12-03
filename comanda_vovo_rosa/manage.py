#!/usr/bin/env python
"""
========================================
MANAGE.PY - Ponto de Entrada do Sistema
========================================

Este é o arquivo principal para executar comandos Django.

O QUE ELE FAZ:
- Permite rodar o servidor: python manage.py runserver
- Criar migrações de banco: python manage.py makemigrations
- Aplicar migrações: python manage.py migrate
- Criar superusuário: python manage.py createsuperuser
- Executar comandos customizados (popular_dados, criar_usuarios, etc.)

COMO FUNCIONA:
1. Define a variável de ambiente que aponta para o arquivo de configuração (settings.py)
2. Importa o gerenciador de comandos do Django
3. Executa o comando que você digitou no terminal
"""

import os
import sys


def main():
    """
    Função principal que executa as tarefas administrativas.
    
    Esta função:
    - Define qual arquivo de configuração usar (comanda_vovo_rosa.settings)
    - Tenta importar o Django
    - Se o Django não estiver instalado, mostra erro
    - Executa o comando que você digitou (runserver, migrate, etc.)
    """
    # Define o módulo de configurações do projeto
    # Isso diz ao Django onde encontrar as configurações (settings.py)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comanda_vovo_rosa.settings')
    
    try:
        # Importa o executor de comandos do Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Se não conseguir importar, significa que o Django não está instalado
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Executa o comando que foi passado via terminal
    # sys.argv contém os argumentos: ['manage.py', 'runserver', '8000']
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Só executa main() se este arquivo for executado diretamente
    # Não executa se for importado como módulo
    main()
