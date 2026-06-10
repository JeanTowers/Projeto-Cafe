# pedidos/management/commands/criar_usuarios.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuários de teste para o sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando usuários de teste...')
        
        usuarios = [
            {
                'username': 'garcom',
                'password': 'senha123',
                'first_name': 'João',
                'tipo': 'GARCOM'
            },
            {
                'username': 'cozinha',
                'password': 'senha123',
                'first_name': 'Maria',
                'tipo': 'COZINHA'
            },
            {
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Admin',
                'tipo': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            },
        ]
        
        criados = 0
        atualizados = 0
        
        for user_data in usuarios:
            tipo = user_data.pop('tipo')
            is_staff = user_data.pop('is_staff', False)
            is_superuser = user_data.pop('is_superuser', False)
            password = user_data.pop('password')
            
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )

            user.first_name = user_data.get('first_name', '')
            user.tipo = tipo
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.set_password(password)
            user.save()

            if created:
                criados += 1
                self.stdout.write(f"  ✓ Usuário '{user.username}' criado")
            else:
                atualizados += 1
                self.stdout.write(f"  → Usuário '{user.username}' atualizado")
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {criados} usuários criados!'))
        if atualizados > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ {atualizados} usuários atualizados!'))
        
        self.stdout.write(self.style.SUCCESS('\nUsuários disponíveis:'))
        self.stdout.write('  - garcom / senha123 (Garçom/Atendente)')
        self.stdout.write('  - cozinha / senha123 (Cozinha)')
        self.stdout.write('  - admin / admin123 (Administrador)')
