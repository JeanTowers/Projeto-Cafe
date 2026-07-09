from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comanda, ItemCardapio, ItemPedido, Mesa


User = get_user_model()


class GerenciarEstoqueDeleteTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='admin_teste', password='senha123', first_name='Admin Teste', tipo='ADMIN')
		self.client.force_login(self.user)

	def test_deletar_item_sem_pedidos(self):
		item = ItemCardapio.objects.create(
			nome='Bolo de Chocolate',
			descricao='Fatias',
			preco='8.50',
			disponivel='S',
			quantidade_estoque=12,
		)

		response = self.client.post(
			reverse('gerenciar_estoque'),
			{'item_id': item.id, 'acao': 'deletar_item'},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(ItemCardapio.objects.filter(id=item.id).exists())
		self.assertContains(response, 'removido do cardápio')

	def test_deletar_item_com_pedidos_e_bloqueado(self):
		mesa = Mesa.objects.create(numero=1)
		item = ItemCardapio.objects.create(
			nome='Café Expresso',
			descricao='Quente',
			preco=Decimal('5.00'),
			disponivel='S',
			quantidade_estoque=20,
		)
		comanda = Comanda.objects.create(mesa=mesa, usuario=self.user, nome_cliente='João', status='A')
		ItemPedido.objects.create(
			comanda=comanda,
			item=item,
			quantidade=1,
			observacao='',
			status='A',
		)

		response = self.client.post(
			reverse('gerenciar_estoque'),
			{'item_id': item.id, 'acao': 'deletar_item'},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(ItemCardapio.objects.filter(id=item.id).exists())
		self.assertContains(response, 'Não foi possível excluir')


class EditarProdutoTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='admin_edicao', password='senha123', first_name='Admin Edição', tipo='ADMIN')
		self.client.force_login(self.user)

	def test_carregar_formulario_de_edicao_preenchido(self):
		item = ItemCardapio.objects.create(
			nome='Pão de Queijo',
			descricao='Tradicional',
			preco='9.50',
			disponivel='S',
			quantidade_estoque=25,
		)

		response = self.client.get(reverse('editar_produto', args=[item.id]))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Editar Produto')
		self.assertContains(response, 'value="Pão de Queijo"', html=False)

	def test_salvar_alteracoes_do_produto(self):
		item = ItemCardapio.objects.create(
			nome='Café com Leite',
			descricao='Quente',
			preco='6.50',
			disponivel='S',
			quantidade_estoque=30,
		)

		response = self.client.post(
			reverse('editar_produto', args=[item.id]),
			{
				'nome': 'Café com Leite Cremoso',
				'descricao': 'Quente e mais cremoso',
				'preco': '7.00',
				'quantidade_estoque': 18,
				'disponivel': 'S',
			},
			follow=True,
		)

		item.refresh_from_db()

		self.assertEqual(response.status_code, 200)
		self.assertEqual(item.nome, 'Café com Leite Cremoso')
		self.assertEqual(str(item.preco), '7.00')
		self.assertEqual(item.quantidade_estoque, 18)
		self.assertContains(response, 'atualizado com sucesso')
