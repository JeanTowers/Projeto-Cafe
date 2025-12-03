# pedidos/management/commands/resetar_banco.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Reseta o banco de dados completamente'

    def handle(self, *args, **kwargs):
        # Caminho do banco de dados
        db_path = 'db.sqlite3'
        
        # Remove o banco de dados se existir
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS('✓ Banco de dados deletado!'))
        
        # Recria o banco de dados
        self.stdout.write('Criando novo banco de dados...')
        call_command('migrate', verbosity=0)
        self.stdout.write(self.style.SUCCESS('✓ Banco de dados recriado!'))
        
        # Popula dados iniciais
        self.stdout.write('Populando dados iniciais...')
        call_command('popular_dados', verbosity=0)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Banco de dados resetado com sucesso!'))
        self.stdout.write('Banco limpo com mesas e cardápio prontos para uso.')
