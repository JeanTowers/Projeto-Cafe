# pedidos/admin.py
"""
===========================================
ADMIN.PY - Configuração do Painel Admin
===========================================

Este arquivo configura como os modelos aparecem no painel administrativo Django.

ACESSO: http://localhost:8000/admin/

CUSTOMIZAÇÕES:
- list_display: Colunas mostradas na listagem
- list_filter: Filtros laterais
- search_fields: Campos pesquisáveis
- inlines: Edição inline de relacionamentos

RECURSOS DO PAINEL ADMIN:
- Criar, editar e deletar registros
- Filtrar e pesquisar
- Visualizar relacionamentos
- Ações em lote
"""

from django.contrib import admin
from .models import Mesa, ItemCardapio, Comanda, ItemPedido, UserProfile

# ============================================
# INLINE: ITENS DENTRO DA COMANDA
# ============================================

class ItemPedidoInline(admin.TabularInline):
    """
    Permite editar os itens de um pedido diretamente na tela da comanda.
    
    EFEITO:
    Ao abrir uma comanda no admin, mostra tabela com todos os seus itens.
    Pode adicionar/editar/remover itens sem sair da tela da comanda.
    
    CONFIGURAÇÕES:
    - TabularInline: Exibe como tabela
    - model: Modelo relacionado (ItemPedido)
    - extra = 0: Não mostra formulários vazios extras
    """
    model = ItemPedido
    extra = 0  # Não mostra linhas vazias para adicionar itens 

# Registro dos modelos principais
admin.site.register(Mesa)
admin.site.register(ItemCardapio)

# Registro da Comanda com a edição de itens (Inline)
@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'nome_cliente', 'data_abertura', 'fechada')
    list_filter = ('fechada', 'data_abertura')
    inlines = [ItemPedidoInline]

# Registro do UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')