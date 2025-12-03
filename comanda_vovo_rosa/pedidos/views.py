# pedidos/views.py
"""
===========================================
VIEWS.PY - Lógica de Negócio do Sistema
===========================================

Este arquivo contém todas as views (funções) que processam as requisições HTTP.

VIEWS IMPLEMENTADAS:
1. abrir_nova_comanda - RF1: Criar nova comanda
2. index - Página inicial com menu
3. painel_cozinha - RF2: Fila de produção da cozinha
4. marcar_item_pronto - RF3: Marcar item como pronto
5. entregar_comanda - Marcar comanda como entregue
6. gerenciar_mesa - Visualizar e gerenciar comandas de uma mesa
7. fechar_comanda - Fechar e pagar comanda (apenas ADMIN)
8. gerenciar_estoque - Controlar disponibilidade e estoque
9. adicionar_produto - Adicionar novo item ao cardápio
10. login_view - Autenticação de usuário
11. logout_view - Deslogar usuário

COMO FUNCIONA UMA VIEW:
1. Recebe requisição HTTP (request)
2. Processa dados (consulta banco, valida formulários)
3. Retorna resposta HTTP (HTML renderizado ou redirect)

PADRÃO PRG (Post-Redirect-Get):
Após processar POST, sempre redireciona (evita reenvio ao pressionar F5)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import Comanda, ItemPedido, Mesa
from .forms import ComandaForm, ItemPedidoForm
from .decorators import tipo_usuario_required

# ============================================
# VIEW 1: ABRIR NOVA COMANDA (RF1)
# ============================================

@tipo_usuario_required('GARCOM', 'ADMIN')  # Apenas garçom ou admin podem criar comandas
def abrir_nova_comanda(request):
    """
    RF1: Abrir Nova Comanda para Mesa
    
    Permite criar uma nova comanda ou adicionar itens a comanda existente.
    
    FUNCIONALIDADES:
    - Selecionar mesa
    - Digitar nome do cliente
    - Adicionar múltiplos itens com quantidade e observações
    - Controle automático de estoque
    - Detecção de comandas duplicadas (mesmo cliente, mesma mesa)
    
    FLUXO:
    GET: Mostra formulário vazio
    POST: Processa pedido, valida estoque, cria comanda/itens
    """
    
    # ===== PREPARAÇÃO: Criar Formset para Múltiplos Itens =====
    # Formset: Gerenciador que permite adicionar/remover formulários dinamicamente
    # extra=1: Começa com 1 formulário vazio
    # can_delete=True: Permite remover formulários via JavaScript
    ItemFormSet = formset_factory(ItemPedidoForm, extra=1, can_delete=True)
    
    # ===== BUSCAR MESAS OCUPADAS =====
    # Para mostrar quais mesas têm comandas abertas e quem está nelas
    mesas_com_comandas = {}
    
    # Busca todas as comandas não fechadas (ainda não foram pagas)
    # select_related('mesa'): Otimização - carrega mesa junto (1 query ao invés de N+1)
    # order_by: Ordena por número da mesa e nome do cliente
    comandas_abertas = Comanda.objects.filter(fechada=False).select_related('mesa').order_by('mesa__numero', 'nome_cliente')
    
    for comanda in comandas_abertas:
        mesa_id = comanda.mesa.id
        if mesa_id not in mesas_com_comandas:
            mesas_com_comandas[mesa_id] = {
                'mesa': comanda.mesa,
                'clientes': []
            }
        mesas_com_comandas[mesa_id]['clientes'].append(comanda.nome_cliente)
    
    # ===== PROCESSAMENTO DO FORMULÁRIO (POST) =====
    if request.method == 'POST':
        # Cria formulários com os dados enviados
        comanda_form = ComandaForm(request.POST)
        item_formset = ItemFormSet(request.POST)
        
        # ===== ETAPA 1: VALIDAÇÃO =====
        # Valida se todos os campos foram preenchidos corretamente
        # - Mesa foi selecionada?
        # - Nome do cliente foi digitado?
        # - Itens selecionados são válidos?
        # - Quantidades são números positivos?
        if comanda_form.is_valid() and item_formset.is_valid():
            
            mesa = comanda_form.cleaned_data['mesa']
            nome_cliente = comanda_form.cleaned_data['nome_cliente']
            
            # Verifica se já existe uma comanda aberta para este cliente nesta mesa
            comanda_existente = Comanda.objects.filter(
                mesa=mesa,
                nome_cliente__iexact=nome_cliente,  # Ignora maiúsculas/minúsculas
                fechada=False
            ).first()
            
            if comanda_existente:
                # Usa a comanda existente
                comanda = comanda_existente
                mensagem_tipo = 'adicionado'
            else:
                # 2. Cria nova comanda
                comanda = comanda_form.save(commit=False)
                comanda.save()
                mensagem_tipo = 'criado'
            
            itens_criados = False
            
            # 3. Salva os Itens do Pedido associados à Comanda (nova ou existente)
            for form in item_formset:
                # Usa os dados do formulário apenas se o item_cardapio foi selecionado
                if form.cleaned_data.get('item_cardapio'):
                    item_cardapio = form.cleaned_data['item_cardapio']
                    quantidade = form.cleaned_data['quantidade']
                    observacao = form.cleaned_data.get('observacao', '')
                    
                    # Recarrega o item do banco para garantir dados atualizados
                    from .models import ItemCardapio
                    try:
                        item_cardapio = ItemCardapio.objects.get(pk=item_cardapio.pk)
                    except ItemCardapio.DoesNotExist:
                        messages.error(request, f'⚠️ Item não encontrado no cardápio.')
                        continue
                    
                    # Valida estoque novamente antes de salvar
                    if not item_cardapio.disponivel:
                        messages.error(request, f'⚠️ {item_cardapio.nome} não está mais disponível.')
                        continue
                    
                    if item_cardapio.quantidade_estoque <= 0:
                        messages.error(request, f'⚠️ {item_cardapio.nome} está sem estoque.')
                        continue
                    
                    if item_cardapio.quantidade_estoque < quantidade:
                        messages.error(request, f'⚠️ {item_cardapio.nome} tem apenas {item_cardapio.quantidade_estoque} unidade(s) em estoque.')
                        continue
                    
                    # Decrementa o estoque
                    item_cardapio.quantidade_estoque -= quantidade
                    if item_cardapio.quantidade_estoque <= 0:
                        item_cardapio.quantidade_estoque = 0
                        item_cardapio.disponivel = False  # Desabilita item se estoque zerou
                    item_cardapio.save()
                    
                    ItemPedido.objects.create(
                        comanda=comanda,
                        item=item_cardapio,
                        quantidade=quantidade,
                        observacao=observacao,
                        status='ABERTO' # Status inicial para Cozinha
                    )
                    itens_criados = True

            # 4. Pós-Condição: Notificação ao Painel da Cozinha (Lógica Futura)

            if itens_criados:
                # Redireciona para uma página de sucesso
                if mensagem_tipo == 'adicionado':
                    messages.success(request, f'✓ Itens adicionados à comanda de {comanda.nome_cliente} na Mesa {comanda.mesa.numero}!')
                else:
                    messages.success(request, f'✓ Comanda #{comanda.id} criada com sucesso para {comanda.nome_cliente} na Mesa {comanda.mesa.numero}!')
                return redirect('abrir_nova_comanda')
            else:
                # Se nenhuma linha de item foi preenchida
                if mensagem_tipo == 'criado':
                    comanda.delete()
                messages.error(request, 'É necessário adicionar pelo menos um item ao pedido!')


    else: # GET
        comanda_form = ComandaForm()
        item_formset = ItemFormSet()

    # Busca todos os itens do cardápio para mostrar informações de estoque
    # Filtra apenas itens disponíveis e com estoque
    from .models import ItemCardapio
    itens_cardapio = ItemCardapio.objects.filter(disponivel=True, quantidade_estoque__gt=0)
    itens_info = {item.id: {'nome': item.nome, 'estoque': item.quantidade_estoque, 'disponivel': item.disponivel} for item in itens_cardapio}

    context = {
        'comanda_form': comanda_form,
        'item_formset': item_formset,
        'mesas_com_comandas': mesas_com_comandas,
        'itens_info': itens_info
    }
    return render(request, 'pedidos/nova_comanda.html', context)


@login_required
def index(request):
    """
    Página inicial com menu de navegação
    """
    # Busca comandas abertas agrupadas por mesa
    mesas_com_comandas = {}
    comandas_abertas = Comanda.objects.filter(fechada=False).select_related('mesa').order_by('mesa__numero', 'nome_cliente')
    
    for comanda in comandas_abertas:
        mesa_id = comanda.mesa.id
        if mesa_id not in mesas_com_comandas:
            mesas_com_comandas[mesa_id] = {
                'mesa': comanda.mesa,
                'clientes': []
            }
        mesas_com_comandas[mesa_id]['clientes'].append(comanda.nome_cliente)
    
    context = {
        'mesas_com_comandas': mesas_com_comandas
    }
    return render(request, 'pedidos/index.html', context)


@tipo_usuario_required('COZINHA', 'ADMIN')
def painel_cozinha(request):
    """
    RF2: Visualização da Fila de Produção da Cozinha
    Exibe todos os pedidos que não foram entregues (ABERTO ou PRONTO)
    """
    # Busca todas as comandas abertas (não fechadas)
    comandas_ativas = Comanda.objects.filter(fechada=False).order_by('data_abertura')
    
    # Para cada comanda, busca os itens que ainda não foram entregues
    pedidos_pendentes = []
    for comanda in comandas_ativas:
        itens_nao_entregues = ItemPedido.objects.filter(
            comanda=comanda
        ).exclude(status='ENTREGUE')
        
        if itens_nao_entregues.exists():
            # Verifica se todos os itens estão prontos
            itens_abertos = itens_nao_entregues.filter(status='ABERTO')
            todos_prontos = not itens_abertos.exists()
            
            pedidos_pendentes.append({
                'comanda': comanda,
                'itens': itens_nao_entregues,
                'todos_prontos': todos_prontos
            })
    
    context = {
        'pedidos_pendentes': pedidos_pendentes
    }
    return render(request, 'pedidos/painel_cozinha.html', context)


@tipo_usuario_required('COZINHA', 'ADMIN')
def marcar_item_pronto(request, item_id):
    """
    RF3: Sinalização de Itens Concluídos
    Marca um item específico como pronto
    """
    if request.method == 'POST':
        item = get_object_or_404(ItemPedido, id=item_id)
        item.status = 'PRONTO'
        item.save()
        
        messages.success(request, f'✓ Item {item.item.nome} marcado como PRONTO.')
        
        return redirect('painel_cozinha')
    
    return redirect('painel_cozinha')

@tipo_usuario_required('COZINHA', 'GARCOM', 'ADMIN')
def entregar_comanda(request, comanda_id):
    """
    Marca todos os itens de uma comanda como ENTREGUE
    Remove a comanda do painel da cozinha
    """
    if request.method == 'POST':
        comanda = get_object_or_404(Comanda, id=comanda_id)
        
        # Verifica se todos os itens estão prontos
        itens_nao_prontos = ItemPedido.objects.filter(comanda=comanda).exclude(status='PRONTO').exclude(status='ENTREGUE')
        
        if itens_nao_prontos.exists():
            messages.error(request, f'⚠️ Não é possível entregar. Ainda há {itens_nao_prontos.count()} item(ns) não pronto(s).')
            return redirect('painel_cozinha')
        
        # Marca todos os itens como entregue
        ItemPedido.objects.filter(comanda=comanda, status='PRONTO').update(status='ENTREGUE')
        
        messages.success(request, f'✓ Comanda da Mesa {comanda.mesa.numero} ({comanda.nome_cliente}) ENTREGUE!')
        
        return redirect('painel_cozinha')
    
    return redirect('painel_cozinha')


@login_required
@tipo_usuario_required('GARCOM', 'ADMIN')
def gerenciar_mesa(request, mesa_numero):
    """
    Visualiza todas as comandas abertas de uma mesa específica
    Agora agrupa todos os pedidos por cliente (mesmo se houver múltiplas comandas)
    GARCOM: apenas visualização
    ADMIN: pode finalizar pagamentos
    """
    from django.db.models import Sum, Q
    
    # Verifica se é garçom tentando fechar comanda
    if request.method == 'POST' and request.user.profile.tipo == 'GARCOM':
        messages.error(request, '⚠️ Apenas administradores podem finalizar pagamentos.')
        return redirect('gerenciar_mesa', mesa_numero=mesa_numero)
    
    mesa = get_object_or_404(Mesa, numero=mesa_numero)
    
    # Busca todas as comandas abertas da mesa
    comandas_abertas = Comanda.objects.filter(
        mesa=mesa, 
        fechada=False
    ).prefetch_related('itempedido_set__item')
    
    # Agrupa comandas por nome do cliente (case-insensitive)
    clientes_agrupados = {}
    for comanda in comandas_abertas:
        nome_cliente_lower = comanda.nome_cliente.lower()
        
        if nome_cliente_lower not in clientes_agrupados:
            clientes_agrupados[nome_cliente_lower] = {
                'nome_original': comanda.nome_cliente,
                'comandas_ids': [],
                'itens': [],
                'primeira_comanda': comanda
            }
        
        clientes_agrupados[nome_cliente_lower]['comandas_ids'].append(comanda.id)
        
        # Adiciona todos os itens desta comanda
        itens_comanda = ItemPedido.objects.filter(comanda=comanda).select_related('item')
        clientes_agrupados[nome_cliente_lower]['itens'].extend(itens_comanda)
    
    # Prepara dados finais com totais por cliente
    comandas_detalhadas = []
    for cliente_data in clientes_agrupados.values():
        # Adiciona subtotal calculado para cada item
        itens_com_subtotal = []
        for item in cliente_data['itens']:
            item.subtotal = item.item.preco * item.quantidade
            itens_com_subtotal.append(item)
        
        total = sum(item.subtotal for item in itens_com_subtotal)
        comandas_detalhadas.append({
            'comanda': cliente_data['primeira_comanda'],  # Usa a primeira comanda para referência
            'comandas_ids': cliente_data['comandas_ids'],  # Lista de IDs de todas as comandas deste cliente
            'itens': itens_com_subtotal,
            'total': total,
            'nome_cliente': cliente_data['nome_original']
        })
    
    context = {
        'mesa': mesa,
        'comandas_detalhadas': comandas_detalhadas,
        'usuario_tipo': request.user.profile.tipo
    }
    return render(request, 'pedidos/gerenciar_mesa.html', context)


@tipo_usuario_required('ADMIN')
def fechar_comanda(request, comanda_id):
    """
    Fecha/paga todas as comandas de um cliente na mesa
    Apenas ADMIN pode finalizar pagamentos
    """
    if request.method == 'POST':
        comanda = get_object_or_404(Comanda, id=comanda_id)
        mesa = comanda.mesa
        nome_cliente = comanda.nome_cliente
        
        # Fecha TODAS as comandas abertas deste cliente nesta mesa
        comandas_cliente = Comanda.objects.filter(
            mesa=mesa,
            nome_cliente__iexact=nome_cliente,
            fechada=False
        )
        
        quantidade_fechada = comandas_cliente.count()
        comandas_cliente.update(fechada=True)
        
        if quantidade_fechada > 1:
            messages.success(request, f'✓ Todas as comandas de {nome_cliente} foram pagas e fechadas! ({quantidade_fechada} comandas)')
        else:
            messages.success(request, f'✓ Comanda de {nome_cliente} foi paga e fechada!')
        
        # Verifica se ainda há comandas abertas na mesa
        comandas_restantes = Comanda.objects.filter(mesa=mesa, fechada=False).count()
        if comandas_restantes == 0:
            messages.info(request, f'Mesa {mesa.numero} está livre agora.')
        
        return redirect('gerenciar_mesa', mesa_numero=mesa.numero)
    
    return redirect('abrir_nova_comanda')


@tipo_usuario_required('COZINHA', 'ADMIN')
@tipo_usuario_required('COZINHA', 'ADMIN')
def adicionar_produto(request):
    """
    Tela para adicionar novos produtos ao cardápio
    """
    from .models import ItemCardapio
    from .forms import ItemCardapioForm
    
    if request.method == 'POST':
        form = ItemCardapioForm(request.POST)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f'✓ Produto "{produto.nome}" adicionado com sucesso!')
            return redirect('gerenciar_estoque')
    else:
        form = ItemCardapioForm(initial={'disponivel': True})
    
    return render(request, 'pedidos/adicionar_produto.html', {
        'form': form
    })

@tipo_usuario_required('COZINHA', 'ADMIN')
def gerenciar_estoque(request):
    """
    Painel da cozinha para gerenciar disponibilidade e estoque dos itens
    """
    from .models import ItemCardapio
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        acao = request.POST.get('acao')
        
        item = get_object_or_404(ItemCardapio, id=item_id)
        
        if acao == 'toggle_disponibilidade':
            item.disponivel = not item.disponivel
            item.save()
            status = 'disponível' if item.disponivel else 'indisponível'
            messages.success(request, f'✓ {item.nome} marcado como {status}.')
        
        elif acao == 'atualizar_quantidade':
            nova_quantidade = request.POST.get('quantidade')
            try:
                nova_quantidade = int(nova_quantidade)
                if nova_quantidade < 0:
                    messages.error(request, 'Quantidade não pode ser negativa.')
                else:
                    item.quantidade_estoque = nova_quantidade
                    # Se adicionar estoque, reativa o item
                    if nova_quantidade > 0 and not item.disponivel:
                        item.disponivel = True
                    item.save()
                    messages.success(request, f'✓ Estoque de {item.nome} atualizado para {nova_quantidade} unidades.')
            except ValueError:
                messages.error(request, 'Quantidade inválida.')
        
        return redirect('gerenciar_estoque')
    
    # Busca todos os itens do cardápio ordenados
    itens = ItemCardapio.objects.all().order_by('nome')
    
    context = {
        'itens': itens
    }
    return render(request, 'pedidos/gerenciar_estoque.html', context)


def login_view(request):
    """
    View de login do sistema
    """
    # Se já está logado, redireciona para index
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.first_name or user.username}!')
            return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'pedidos/login.html')


def logout_view(request):
    """
    View de logout do sistema
    """
    auth_logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')