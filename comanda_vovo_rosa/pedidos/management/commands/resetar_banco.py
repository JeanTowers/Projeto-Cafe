# pedidos/management/commands/resetar_banco.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Reseta o banco de dados completamente'

    def handle(self, *args, **kwargs):
        self.stdout.write('Limpando tabelas do banco...')
        call_command('flush', verbosity=0, interactive=False)

        self.stdout.write('Aplicando migrações...')
        call_command('migrate', verbosity=0)

        self.stdout.write('Populando dados iniciais...')
        call_command('popular_dados', verbosity=0)

        self.stdout.write(self.style.SUCCESS('\n✓ Banco de dados resetado com sucesso!'))
        self.stdout.write('Banco limpo com mesas e cardápio prontos para uso.')
