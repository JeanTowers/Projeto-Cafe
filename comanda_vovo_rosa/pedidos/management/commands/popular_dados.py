# pedidos/management/commands/popular_dados.py
from django.core.management.base import BaseCommand

from pedidos.models import ItemCardapio, Mesa

class Command(BaseCommand):
    help = 'Popula o banco de dados com Mesas e Itens do Cardápio iniciais'

    def handle(self, *args, **kwargs):
        # Criar Mesas (1 a 10)
        self.stdout.write('Criando mesas...')
        mesas_criadas = 0
        for i in range(1, 11):
            mesa, created = Mesa.objects.get_or_create(numero=i, defaults={'status': 'L'})
            if created:
                mesas_criadas += 1
        self.stdout.write(self.style.SUCCESS(f'{mesas_criadas} mesas criadas!'))

        # Criar Itens do Cardápio (Café da Manhã)
        self.stdout.write('Criando itens do cardápio...')
        itens = [
            {'nome': 'Café Preto', 'descricao': 'Café coado tradicional', 'preco': 5.00, 'estoque': 50},
            {'nome': 'Café com Leite', 'descricao': 'Café com leite quente', 'preco': 6.50, 'estoque': 40},
            {'nome': 'Cappuccino', 'descricao': 'Cappuccino cremoso', 'preco': 8.00, 'estoque': 30},
            {'nome': 'Pão na Chapa', 'descricao': 'Pão francês tostado na manteiga', 'preco': 7.00, 'estoque': 25},
            {'nome': 'Misto Quente', 'descricao': 'Pão com queijo e presunto', 'preco': 10.00, 'estoque': 20},
            {'nome': 'Tapioca', 'descricao': 'Tapioca com recheio a escolher', 'preco': 12.00, 'estoque': 15},
            {'nome': 'Bolo Caseiro', 'descricao': 'Fatia de bolo da casa', 'preco': 8.50, 'estoque': 12},
            {'nome': 'Suco Natural', 'descricao': 'Suco de frutas frescas', 'preco': 9.00, 'estoque': 35},
            {'nome': 'Vitamina', 'descricao': 'Vitamina de frutas com leite', 'preco': 11.00, 'estoque': 25},
            {'nome': 'Pão de Queijo', 'descricao': 'Porção com 4 unidades', 'preco': 9.50, 'estoque': 18},
        ]
        
        itens_criados = 0
        itens_atualizados = 0
        for item_data in itens:
            item, created = ItemCardapio.objects.get_or_create(
                nome=item_data['nome'],
                defaults={
                    'descricao': item_data['descricao'],
                    'preco': item_data['preco'],
                    'quantidade_estoque': item_data['estoque'],
                    'disponivel': 'S'
                }
            )
            if created:
                itens_criados += 1
            else:
                # Atualiza estoque se o item já existia
                item.quantidade_estoque = item_data['estoque']
                item.disponivel = 'S'
                item.save()
                itens_atualizados += 1
        
        self.stdout.write(self.style.SUCCESS(f'{itens_criados} itens do cardápio criados!'))
        if itens_atualizados > 0:
            self.stdout.write(self.style.SUCCESS(f'{itens_atualizados} itens do cardápio atualizados com estoque!'))
        self.stdout.write(self.style.SUCCESS('✓ Dados populados com sucesso!'))
