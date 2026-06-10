from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


TIPO_USUARIO_CHOICES = [
    ('GARCOM', 'Garçom/Atendente'),
    ('COZINHA', 'Cozinha'),
    ('ADMIN', 'Administrador'),
]

STATUS_MESA_CHOICES = [
    ('L', 'Livre'),
    ('O', 'Ocupada'),
    ('I', 'Inativa'),
]

STATUS_DISPONIVEL_CHOICES = [
    ('S', 'Sim'),
    ('N', 'Não'),
]

STATUS_PEDIDO_CHOICES = [
    ('A', 'Aberto'),
    ('F', 'Fechado'),
]

STATUS_ITEM_PEDIDO_CHOICES = [
    ('A', 'Aberto'),
    ('P', 'Pronto'),
    ('E', 'Entregue'),
]


class Usuario(AbstractUser):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, default='GARCOM')

    username = models.CharField('Login', max_length=150, unique=True, db_column='Login')
    password = models.CharField('Senha', max_length=128, db_column='Senha')
    email = models.EmailField('Email', blank=True, db_column='Email')
    first_name = models.CharField('Nome', max_length=150, blank=True, db_column='Nome')
    is_active = models.BooleanField('Ativo', default=True, db_column='Ativo')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'Usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.first_name or self.username

    @property
    def login(self):
        return self.username

    @property
    def nome(self):
        return self.first_name

    @property
    def profile(self):
        return self


class Mesa(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Mesa')
    numero = models.IntegerField(unique=True, db_column='Numero')
    status = models.CharField(max_length=1, choices=STATUS_MESA_CHOICES, default='L', db_column='Status')

    class Meta:
        db_table = 'Mesa'
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering = ['numero']

    def __str__(self):
        return f'Mesa {self.numero}'

    @property
    def ativa(self):
        return self.status == 'L'

    @ativa.setter
    def ativa(self, value):
        self.status = 'L' if value else 'I'


class Categoria(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id_Categoria')
    descricao = models.CharField(max_length=50, db_column='Descricao')

    class Meta:
        db_table = 'Categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['descricao']

    def __str__(self):
        return self.descricao


class ItemCardapio(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Produto')
    nome = models.CharField(max_length=100, db_column='Nome')
    descricao = models.TextField(blank=True, default='', db_column='Descricao')
    preco = models.DecimalField(max_digits=10, decimal_places=2, db_column='Vlr_Produto')
    disponivel = models.CharField(max_length=1, choices=STATUS_DISPONIVEL_CHOICES, default='S', db_column='Disponivel')
    quantidade_estoque = models.IntegerField(default=0, db_column='Qtde_Estoque')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Id_Categoria',
    )

    class Meta:
        db_table = 'Produto'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def disponivel_bool(self):
        return self.disponivel == 'S'


class Comanda(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Pedido')
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, db_column='ID_Mesa')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='ID_Usuario')
    nome_cliente = models.CharField(max_length=100, db_column='Cliente')
    data_abertura = models.DateTimeField(default=timezone.now, db_column='DT_Pedido')
    qtde_pessoas = models.IntegerField(default=1, db_column='Qtde_Pessoas')
    status = models.CharField(max_length=1, choices=STATUS_PEDIDO_CHOICES, default='A', db_column='Status')

    class Meta:
        db_table = 'Pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_abertura', '-id']

    def __str__(self):
        return f'Pedido {self.id} - Mesa {self.mesa.numero}'

    @property
    def fechado(self):
        return self.status == 'F'

    @fechado.setter
    def fechado(self, value):
        self.status = 'F' if value else 'A'


class ItemPedido(models.Model):
    id = models.AutoField(primary_key=True)
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, db_column='ID_Pedido')
    item = models.ForeignKey(ItemCardapio, on_delete=models.PROTECT, db_column='ID_Produto')
    quantidade = models.IntegerField(db_column='Qtde_Pedido')
    vlr_total_pedido_produto = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        db_column='Vlr_Total_Pedido_Produto',
    )
    observacao = models.CharField(max_length=100, blank=True, default='', db_column='Observacao')
    status = models.CharField(max_length=1, choices=STATUS_ITEM_PEDIDO_CHOICES, default='A', db_column='Status')

    class Meta:
        db_table = 'Pedido_Produto'
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['comanda', 'item'], name='pedido_produto_unico_por_pedido_e_item'),
        ]

    def save(self, *args, **kwargs):
        if self.item_id and self.quantidade is not None:
            self.vlr_total_pedido_produto = (self.item.preco * self.quantidade).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.quantidade}x {self.item.nome} ({self.get_status_display()})'


UserProfile = Usuario
Produto = ItemCardapio
Pedido = Comanda
PedidoProduto = ItemPedido