# pedidos/management/commands/criar_usuarios.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pedidos.models import UserProfile

class Command(BaseCommand):
    help = 'Cria usuários de teste para o sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando usuários de teste...')
        
        usuarios = [
            {
                'username': 'garcom',
                'password': 'senha123',
                'first_name': 'João',
                'last_name': 'Silva',
                'tipo': 'GARCOM'
            },
            {
                'username': 'cozinha',
                'password': 'senha123',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'tipo': 'COZINHA'
            },
            {
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'Sistema',
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
            
            if created:
                user.set_password(password)
                user.is_staff = is_staff
                user.is_superuser = is_superuser
                user.save()
                criados += 1
                self.stdout.write(f"  ✓ Usuário '{user.username}' criado")
            else:
                # Atualiza senha se o usuário já existe
                user.set_password(password)
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.is_staff = is_staff
                user.is_superuser = is_superuser
                user.save()
                atualizados += 1
                self.stdout.write(f"  → Usuário '{user.username}' atualizado")
            
            # Cria ou atualiza o perfil
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'tipo': tipo}
            )
            
            if not profile_created:
                profile.tipo = tipo
                profile.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {criados} usuários criados!'))
        if atualizados > 0:
            self.stdout.write(self.style.SUCCESS(f'✓ {atualizados} usuários atualizados!'))
        
        self.stdout.write(self.style.SUCCESS('\nUsuários disponíveis:'))
        self.stdout.write('  - garcom / senha123 (Garçom/Atendente)')
        self.stdout.write('  - cozinha / senha123 (Cozinha)')
        self.stdout.write('  - admin / admin123 (Administrador)')
