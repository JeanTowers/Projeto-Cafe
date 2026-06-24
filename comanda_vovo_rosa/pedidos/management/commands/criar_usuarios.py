# pedidos/management/commands/criar_usuarios.py
from django.core.management.base import BaseCommand

from pedidos.db import Database


class Command(BaseCommand):
    help = 'Cria usuários de teste para o sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando usuários de teste...')

        usuarios = [
            {
                'login': 'garcom',
                'senha': 'senha123',
                'email': '',
                'nome': 'João',
                'tipo': 'GARCOM',
            },
            {
                'login': 'cozinha',
                'senha': 'senha123',
                'email': '',
                'nome': 'Maria',
                'tipo': 'COZINHA',
            },
            {
                'login': 'admin',
                'senha': 'admin123',
                'email': '',
                'nome': 'Admin',
                'tipo': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        criados = 0

        for u in usuarios:
            existing = Database.get_usuario_por_login(u['login'])
            if existing:
                self.stdout.write(f"  → Usuário '{u['login']}' já existe, pulando")
                continue

            Database.criar_usuario(
                login=u['login'],
                senha=u['senha'],
                email=u.get('email', ''),
                nome=u['nome'],
                tipo=u['tipo'],
                is_staff=u.get('is_staff', False),
                is_superuser=u.get('is_superuser', False),
            )
            criados += 1
            self.stdout.write(f"  ✓ Usuário '{u['login']}' criado")

        self.stdout.write(self.style.SUCCESS(f'\n✓ {criados} usuários criados!'))
        self.stdout.write(self.style.SUCCESS('\nUsuários disponíveis:'))
        self.stdout.write('  - garcom / senha123 (Garçom/Atendente)')
        self.stdout.write('  - cozinha / senha123 (Cozinha)')
        self.stdout.write('  - admin / admin123 (Administrador)')
