# pedidos/decorators.py
"""
=====================================================
DECORATORS.PY - Decoradores Personalizados
=====================================================

Este arquivo contém decoradores customizados para controle de acesso.

O QUE É UM DECORATOR?
É uma função que "envolve" outra função, adicionando funcionalidades extras.

EXEMPLO PRÁTICO:
Sem decorator:
    def abrir_comanda(request):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.profile.tipo not in ['GARCOM', 'ADMIN']:
            return redirect('index')
        # ... código da função

Com decorator:
    @tipo_usuario_required('GARCOM', 'ADMIN')
    def abrir_comanda(request):
        # ... código da função
        # Verificação automática!

VANTAGENS:
- Código mais limpo e legível
- Reutilizável em múltiplas views
- Fácil manutenção (mudar em um lugar afeta todas as views)
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

# ============================================
# DECORATOR: tipo_usuario_required
# ============================================

def tipo_usuario_required(*tipos_permitidos):
    """
    Decorator para verificar se o usuário tem permissão para acessar uma view.
    
    USO:
    @tipo_usuario_required('GARCOM', 'ADMIN')
    def minha_view(request):
        # Apenas GARCOM e ADMIN podem acessar
        ...
    
    COMO FUNCIONA:
    1. Verifica se o usuário está logado (@login_required)
    2. Verifica se o usuário tem um perfil (profile)
    3. Verifica se o tipo do perfil está na lista de tipos permitidos
    4. Se tudo OK, executa a view
    5. Se não, redireciona com mensagem de erro
    
    PARÂMETROS:
    *tipos_permitidos: Lista de tipos que podem acessar
                      Ex: 'GARCOM', 'COZINHA', 'ADMIN'
    
    RETORNA:
    - Se autorizado: Executa a view normalmente
    - Se não logado: Redireciona para login
    - Se não autorizado: Redireciona para index com erro
    
    EXEMPLOS DE USO:
    
    # Apenas garçom ou admin
    @tipo_usuario_required('GARCOM', 'ADMIN')
    def abrir_nova_comanda(request):
        ...
    
    # Apenas cozinha ou admin
    @tipo_usuario_required('COZINHA', 'ADMIN')
    def painel_cozinha(request):
        ...
    
    # Apenas admin
    @tipo_usuario_required('ADMIN')
    def fechar_comanda(request):
        ...
    """
    def decorator(view_func):
        """
        Decorator interno que será aplicado à view.
        """
        @wraps(view_func)  # Preserva metadados da função original
        @login_required(login_url='login')  # Garante que está logado
        def wrapper(request, *args, **kwargs):
            """
            Função wrapper que faz as verificações.
            
            PARÂMETROS:
            request: Objeto da requisição HTTP (contém user, session, etc.)
            *args: Argumentos posicionais da view
            **kwargs: Argumentos nomeados da view (ex: comanda_id=5)
            """
            
            # VERIFICAÇÃO 1: Usuário tem perfil?
            # Sem perfil = usuário não foi configurado corretamente
            if not hasattr(request.user, 'profile'):
                messages.error(request, 'Seu usuário não tem um perfil configurado. Contate o administrador.')
                return redirect('login')
            
            # VERIFICAÇÃO 2: Tipo do usuário está entre os permitidos?
            # Normaliza maiúsculas/minúsculas e espaços para evitar bloqueio por dado inconsistente.
            tipo_usuario = str(request.user.profile.tipo).strip().upper()
            tipos_permitidos_normalizados = {str(tipo).strip().upper() for tipo in tipos_permitidos}

            if tipo_usuario in tipos_permitidos_normalizados:
                # AUTORIZADO - executa a view normalmente
                return view_func(request, *args, **kwargs)
            else:
                # NÃO AUTORIZADO - mostra erro uma única vez e redireciona
                messages.error(request, 'Você não tem permissão para acessar esta página.')

                return redirect('index')
        
        return wrapper
    return decorator
