# pedidos/models.py
"""
===========================================
MODELS.PY - Estrutura do Banco de Dados
===========================================

Este arquivo define TODOS os modelos (tabelas) do banco de dados.

MODELOS CRIADOS:
1. UserProfile - Perfil de usuário (tipo: GARCOM, COZINHA, ADMIN)
2. Mesa - Mesas do restaurante (número e status)
3. ItemCardapio - Produtos disponíveis (nome, preço, estoque)
4. Comanda - Pedidos das mesas (mesa, cliente, data)
5. ItemPedido - Itens dentro de cada comanda (quantidade, status)

RELACIONAMENTOS:
User (Django) ←→ UserProfile (nosso)
Mesa → Comanda (uma mesa pode ter várias comandas)
Comanda → ItemPedido (uma comanda tem vários itens)
ItemCardapio → ItemPedido (um item do cardápio pode estar em vários pedidos)

COMO FUNCIONA:
Quando você define um modelo aqui, o Django:
1. Cria a tabela no banco (python manage.py migrate)
2. Gera métodos para criar, ler, atualizar e deletar (CRUD)
3. Permite fazer consultas (Ex: Comanda.objects.filter(fechada=False))
"""

from django.db import models
from django.contrib.auth.models import User

# ============================================
# CONSTANTES - OPÇÕES DE ESCOLHA
# ============================================

# STATUS_CHOICES: Define os 3 estados possíveis de um item
# ABERTO → Item está sendo preparado na cozinha (🔴)
# PRONTO → Item foi finalizado mas ainda não foi entregue (✅)
# ENTREGUE → Item foi entregue ao cliente (🚀)
STATUS_CHOICES = [
    ('ABERTO', 'Aberto'),        # Cozinha está preparando
    ('PRONTO', 'Pronto'),        # Pronto para entregar
    ('ENTREGUE', 'Entregue'),    # Já foi entregue
]

# TIPO_USUARIO_CHOICES: Define os 3 tipos de usuário do sistema
# GARCOM → Pode criar comandas e visualizar pedidos
# COZINHA → Pode ver painel de produção e gerenciar estoque
# ADMIN → Acesso completo (tudo que garçom e cozinha podem + pagamentos)
TIPO_USUARIO_CHOICES = [
    ('GARCOM', 'Garçom/Atendente'),   # Atendimento ao cliente
    ('COZINHA', 'Cozinha'),           # Produção de pedidos
    ('ADMIN', 'Administrador'),       # Gestão completa
]

# ============================================
# MODELO 1: USERPROFILE - Perfil de Usuário
# ============================================
# Estende o modelo User padrão do Django
# Adiciona o campo 'tipo' para definir permissões

class UserProfile(models.Model):
    """
    Perfil estendido do usuário.
    
    CAMPOS:
    - user: Relacionamento 1-para-1 com User do Django
    - tipo: Tipo de usuário (GARCOM, COZINHA ou ADMIN)
    
    RELACIONAMENTO:
    User (Django) ←→ UserProfile (nosso)
    OneToOne = Cada User tem APENAS UM perfil
    
    USO:
    user = request.user                    # Pega usuário logado
    tipo = user.profile.tipo               # Acessa o tipo (GARCOM, etc.)
    if tipo == 'ADMIN':                    # Verifica se é admin
        # Permite acessar funcionalidade
    
    EXEMPLO DE DADOS:
    user: garcom (User object)
    tipo: 'GARCOM'
    """
    
    # OneToOneField: Cada User só pode ter 1 perfil
    # on_delete=CASCADE: Se o User for deletado, o perfil também é
    # related_name='profile': Permite acessar como user.profile
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Tipo de usuário (escolha entre GARCOM, COZINHA, ADMIN)
    # max_length=10: Tamanho máximo da string
    # choices: Limita as opções possíveis
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    
    def __str__(self):
        """Representação em texto do perfil (usado no admin e logs)"""
        return f"{self.user.username} - {self.get_tipo_display()}"
    
    class Meta:
        """Metadados do modelo"""
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

# ============================================
# MODELO 2: MESA - Mesas do Restaurante
# ============================================

class Mesa(models.Model):
    """
    Representa uma mesa física do restaurante.
    
    CAMPOS:
    - numero: Número identificador da mesa (1, 2, 3...)
    - ativa: Se a mesa está disponível para uso
    
    REGRAS:
    - Número deve ser único (não pode ter duas "Mesa 5")
    - Por padrão, mesas são ativas (ativa=True)
    
    EXEMPLO DE DADOS:
    numero: 5
    ativa: True
    
    USO:
    Mesa.objects.filter(ativa=True)  # Lista todas as mesas ativas
    """
    
    # Número da mesa (unique=True garante que não tenha duplicata)
    numero = models.IntegerField(unique=True)
    
    # Se a mesa está ativa (disponível para uso)
    ativa = models.BooleanField(default=True)
    
    def __str__(self):
        """Representação em texto (usado em formulários e admin)"""
        return f"Mesa {self.numero}"


# ============================================
# MODELO 3: ITEMCARDAPIO - Produtos/Cardápio
# ============================================

class ItemCardapio(models.Model):
    """
    Representa um item disponível no cardápio.
    
    CAMPOS:
    - nome: Nome do produto (ex: "Café Expresso")
    - descricao: Descrição detalhada (opcional)
    - preco: Preço em R$ (ex: 5.50)
    - disponivel: Se está disponível para pedidos
    - quantidade_estoque: Quantidade disponível
    
    LÓGICA DE ESTOQUE:
    - Quando um pedido é feito, quantidade_estoque é decrementada
    - Se quantidade_estoque chega a 0, disponivel é marcado como False
    - Item com disponivel=False não aparece no formulário de pedidos
    
    EXEMPLO DE DADOS:
    nome: "Café Expresso"
    descricao: "Café forte e aromático"
    preco: 5.50
    disponivel: True
    quantidade_estoque: 48
    
    ALERTAS VISUAIS:
    - Estoque > 5: Verde (OK)
    - Estoque ≤ 5: Amarelo piscando (ALERTA)
    - Estoque = 0: Vermelho (INDISPONÍVEL)
    """
    
    # Nome do item (máximo 100 caracteres)
    nome = models.CharField(max_length=100)
    
    # Descrição opcional do item (blank=True permite vazio)
    descricao = models.TextField(blank=True)
    
    # Preço com 2 casas decimais (ex: 99.99)
    # max_digits=5: Máximo 999.99
    # decimal_places=2: Duas casas decimais
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    
    # CONTROLE DE ESTOQUE
    # disponivel: Se o item pode ser pedido neste momento
    disponivel = models.BooleanField(default=True, help_text="Item disponível para pedidos")
    
    # Quantidade em estoque (decrementada automaticamente ao criar pedido)
    quantidade_estoque = models.IntegerField(default=0, help_text="Quantidade disponível em estoque")
    
    def __str__(self):
        """Representação em texto"""
        return self.nome

# ============================================
# MODELO 4: COMANDA - Pedido de uma Mesa
# ============================================

class Comanda(models.Model):
    """
    Representa um pedido de um cliente em uma mesa.
    
    CAMPOS:
    - mesa: Qual mesa fez o pedido (FK para Mesa)
    - nome_cliente: Nome do cliente que fez o pedido
    - data_abertura: Quando a comanda foi criada (automático)
    - fechada: Se a comanda foi paga e fechada
    
    RELACIONAMENTO:
    Mesa → Comanda (Uma mesa pode ter várias comandas)
    ForeignKey: Relacionamento Muitos-para-Um
    
    REGRAS DE NEGÓCIO:
    - Múltiplos clientes podem ter comandas na mesma mesa
    - Comandas com mesmo nome_cliente na mesma mesa são agrupadas no pagamento
    - Comando fechada=True significa que foi paga
    - PROTECT: Não permite deletar mesa se tiver comandas
    
    EXEMPLO DE DADOS:
    id: 1
    mesa: Mesa 5 (objeto)
    nome_cliente: "João Silva"
    data_abertura: 2025-12-03 14:30:00
    fechada: False
    
    FLUXO:
    1. Garçom cria comanda (fechada=False)
    2. Itens são adicionados à comanda
    3. Cozinha prepara os itens
    4. Admin fecha a comanda (fechada=True) após pagamento
    """
    
    # ForeignKey: Relacionamento com Mesa
    # on_delete=PROTECT: Não permite deletar mesa se tiver comandas
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT)
    
    # Nome do cliente (máximo 100 caracteres)
    nome_cliente = models.CharField(max_length=100)
    
    # Data e hora de abertura (auto_now_add=True define automaticamente)
    data_abertura = models.DateTimeField(auto_now_add=True)
    
    # Se a comanda foi paga e fechada
    fechada = models.BooleanField(default=False)
    
    def __str__(self):
        """Representação em texto"""
        return f"Comanda {self.id} - Mesa {self.mesa.numero}"


# ============================================
# MODELO 5: ITEMPEDIDO - Item dentro do Pedido
# ============================================

class ItemPedido(models.Model):
    """
    Representa um item específico dentro de uma comanda.
    
    CAMPOS:
    - comanda: A qual comanda este item pertence (FK)
    - item: Qual produto do cardápio foi pedido (FK)
    - quantidade: Quantas unidades foram pedidas
    - observacao: Pedidos especiais (ex: "sem cebola")
    - status: Estado do item (ABERTO/PRONTO/ENTREGUE)
    
    RELACIONAMENTOS:
    Comanda → ItemPedido (Uma comanda tem vários itens)
    ItemCardapio → ItemPedido (Um item do cardápio pode estar em vários pedidos)
    
    FLUXO DE STATUS:
    ABERTO (inicial) → Cozinha está preparando (🔴)
    ↓
    PRONTO → Item finalizado, aguardando entrega (✅)
    ↓
    ENTREGUE → Item foi entregue ao cliente (🚀)
    
    REGRAS:
    - Status inicial sempre é 'ABERTO'
    - CASCADE: Se comanda for deletada, seus itens também são
    - PROTECT: Não permite deletar item do cardápio se estiver em pedidos
    - Ao criar ItemPedido, o estoque do ItemCardapio é decrementado
    
    EXEMPLO DE DADOS:
    comanda: Comanda #1 (objeto)
    item: Café Expresso (objeto)
    quantidade: 2
    observacao: "Sem açúcar"
    status: 'ABERTO'
    
    CÁLCULOS:
    subtotal = quantidade × item.preco
    Exemplo: 2 × R$ 5,00 = R$ 10,00
    """
    
    # ForeignKey: Relacionamento com Comanda
    # on_delete=CASCADE: Se comanda for deletada, os itens também são
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE)
    
    # ForeignKey: Relacionamento com ItemCardapio
    # on_delete=PROTECT: Não permite deletar item se estiver em pedidos
    item = models.ForeignKey(ItemCardapio, on_delete=models.PROTECT)
    
    # Quantidade pedida
    quantidade = models.IntegerField()
    
    # Observações opcionais (blank=True permite vazio)
    observacao = models.TextField(blank=True, help_text="Observações ou pedidos especiais (ex: sem cebola)")
    
    # Status do item (ABERTO, PRONTO ou ENTREGUE)
    # default='ABERTO': Todos os itens começam como ABERTO
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTO')
    
    def __str__(self):
        """Representação em texto"""
        return f"{self.quantidade}x {self.item.nome} ({self.status})"