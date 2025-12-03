# pedidos/urls.py
"""
===========================================
URLS.PY DO APP - Roteamento do App Pedidos
===========================================

Este arquivo define todas as rotas do app pedidos.

ESTRUTURA DE UMA ROTA:
path('url/', views.funcao, name='nome')
     │       │              │
     │       │              └─ Nome para usar em {% url 'nome' %}
     │       └─ View que processa
     └─ URL que o usuário acessa

EXEMPLO DE FLUXO:
Usuário acessa: /pedidos/nova-comanda/
              ↓
Django procura rota que combina
              ↓
Encontra: path('nova-comanda/', views.abrir_nova_comanda, ...)
              ↓
Chama a view: abrir_nova_comanda(request)
              ↓
View retorna HTML ou redirect

CATEGORIAS DE ROTAS:
- Autenticação: login, logout
- Comandas: nova-comanda, gerenciar-mesa, fechar-comanda
- Cozinha: painel-cozinha, marcar-pronto, entregar-comanda
- Estoque: gerenciar-estoque, adicionar-produto
"""

from django.urls import path
from . import views

# ============================================
# MAPEAMENTO DE URLS
# ============================================

urlpatterns = [
    # Página inicial
    path('', views.index, name='index'),
    
    # RF1: Abrir Nova Comanda para a Mesa
    path('nova-comanda/', views.abrir_nova_comanda, name='abrir_nova_comanda'),
    
    # RF2: Visualização da Fila de Produção da Cozinha
    path('painel-cozinha/', views.painel_cozinha, name='painel_cozinha'),
    
    # RF3: Sinalização de Itens Concluídos
    path('marcar-pronto/<int:item_id>/', views.marcar_item_pronto, name='marcar_item_pronto'),
    path('entregar-comanda/<int:comanda_id>/', views.entregar_comanda, name='entregar_comanda'),
    
    # Gerenciamento de Mesa e Comandas
    path('mesa/<int:mesa_numero>/', views.gerenciar_mesa, name='gerenciar_mesa'),
    path('fechar-comanda/<int:comanda_id>/', views.fechar_comanda, name='fechar_comanda'),
    
    # Gerenciamento de Estoque
    path('gerenciar-estoque/', views.gerenciar_estoque, name='gerenciar_estoque'),
    path('adicionar-produto/', views.adicionar_produto, name='adicionar_produto'),
    
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]