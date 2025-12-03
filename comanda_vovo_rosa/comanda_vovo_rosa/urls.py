"""
=========================================
URLS.PY PRINCIPAL - Roteamento de URLs
=========================================

Este arquivo define as rotas principais do projeto.

COMO FUNCIONA:
Quando você acessa uma URL (ex: http://localhost:8000/pedidos/nova-comanda/)
O Django segue este caminho:
1. Procura a rota que combina com a URL
2. Se encontrar 'pedidos/', delega para pedidos/urls.py
3. Se encontrar 'admin/', abre o painel administrativo
4. Se for a raiz '/', redireciona para 'index'

EXEMPLO DE FLUXO:
URL digitada: http://localhost:8000/pedidos/nova-comanda/
↓
Django vê 'pedidos/' e delega para pedidos/urls.py
↓
pedidos/urls.py procura por 'nova-comanda/'
↓
Encontra e chama a view abrir_nova_comanda()
↓
View processa e retorna o HTML
"""

from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

# ============================================
# MAPEAMENTO DE URLS PRINCIPAIS
# ============================================

urlpatterns = [
    # Painel administrativo do Django
    # Acesso: http://localhost:8000/admin/
    # Permite gerenciar: usuários, mesas, cardápio, comandas
    path('admin/', admin.site.urls),
    
    # Delega todas as URLs que começam com 'pedidos/' para o app pedidos
    # Exemplo: 'pedidos/nova-comanda/' → pedidos/urls.py
    path('pedidos/', include('pedidos.urls')),
    
    # Página raiz - redireciona para a página inicial (index)
    # Acesso: http://localhost:8000/ → redireciona para /pedidos/
    path('', lambda request: redirect('index')),
]
