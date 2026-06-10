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
from .models import Categoria, Mesa, ItemCardapio, Comanda, ItemPedido, Usuario

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
admin.site.register(Categoria)

# Registro da Comanda com a edição de itens (Inline)
@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'nome_cliente', 'data_abertura', 'status')
    list_filter = ('status', 'data_abertura')
    inlines = [ItemPedidoInline]

# Registro do Usuario
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'email', 'tipo', 'is_active')
    list_filter = ('tipo',)
    search_fields = ('username', 'first_name', 'email')