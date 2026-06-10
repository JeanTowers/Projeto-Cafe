# pedidos/views.py
"""
===========================================
VIEWS.PY - Lógica de Negócio do Sistema
===========================================

Este arquivo contém todas as views (funções) que processam as requisições HTTP.
Utiliza SQL puro para operações de banco de dados via classe Database.

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
2. Processa dados (consulta banco via SQL, valida formulários)
3. Retorna resposta HTTP (HTML renderizado ou redirect)

PADRÃO PRG (Post-Redirect-Get):
Após processar POST, sempre redireciona (evita reenvio ao pressionar F5)
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.db import connection
from types import SimpleNamespace
from .models import Comanda, ItemPedido, Mesa, ItemCardapio
from .forms import ComandaForm, ItemPedidoForm, ItemCardapioForm, UsuarioCreateForm
from .decorators import tipo_usuario_required
from .db import Database

# Instância do gerenciador de banco de dados
db = Database()

# ============================================
# VIEW 1: ABRIR NOVA COMANDA (RF1)
# ============================================

@tipo_usuario_required('GARCOM', 'ADMIN')
def abrir_nova_comanda(request):
    """
    RF1: Abrir Nova Comanda para Mesa
    Utiliza SQL puro para todas as operações de banco de dados.
    """
    ItemFormSet = formset_factory(ItemPedidoForm, extra=1, can_delete=True)
    
    # ===== BUSCAR MESAS OCUPADAS VIA SQL =====
    mesas_com_comandas = {}
    comandas_abertas = db.get_comandas_abertas_com_mesas()
    
    for cmd in comandas_abertas:
        mesa_id = cmd['mesa_id']
        if mesa_id not in mesas_com_comandas:
            mesas_com_comandas[mesa_id] = {
                'mesa': SimpleNamespace(id=mesa_id, numero=cmd['numero_mesa'], status=cmd['status_mesa']),
                'clientes': []
            }
        mesas_com_comandas[mesa_id]['clientes'].append(cmd['nome_cliente'])
    
    # ===== PROCESSAMENTO DO FORMULÁRIO (POST) =====
    if request.method == 'POST':
        comanda_form = ComandaForm(request.POST)
        item_formset = ItemFormSet(request.POST)
        
        if comanda_form.is_valid() and item_formset.is_valid():
            mesa = comanda_form.cleaned_data['mesa']
            nome_cliente = comanda_form.cleaned_data['nome_cliente']
            qtde_pessoas = comanda_form.cleaned_data.get('qtde_pessoas', 1)
            
            # Verifica comanda existente via SQL
            comanda_existente = db.get_comanda_aberta_por_mesa_cliente(mesa.id, nome_cliente)
            
            if comanda_existente:
                comanda_id = comanda_existente['id']
                mensagem_tipo = 'adicionado'
                numero_mesa = mesa.numero
                nome_cliente_display = comanda_existente['nome_cliente']
            else:
                # Cria nova comanda via SQL
                comanda_id = db.criar_comanda(mesa.id, request.user.id, nome_cliente, qtde_pessoas)
                mensagem_tipo = 'criado'
                numero_mesa = mesa.numero
                nome_cliente_display = nome_cliente
            
            itens_criados = False
            
            # Salva itens da comanda
            for form in item_formset:
                if form.cleaned_data.get('item_cardapio'):
                    item_cardapio = form.cleaned_data['item_cardapio']
                    quantidade = form.cleaned_data['quantidade']
                    observacao = form.cleaned_data.get('observacao', '')
                    
                    # Busca item do banco via SQL
                    item = db.get_produto_por_id(item_cardapio.id)
                    
                    if not item:
                        messages.error(request, f'⚠️ Item não encontrado no cardápio.')
                        continue
                    
                    if item['disponivel'] != 'S':
                        messages.error(request, f'⚠️ {item["nome"]} não está mais disponível.')
                        continue
                    
                    if item['quantidade_estoque'] <= 0:
                        messages.error(request, f'⚠️ {item["nome"]} está sem estoque.')
                        continue
                    
                    if item['quantidade_estoque'] < quantidade:
                        messages.error(request, f'⚠️ {item["nome"]} tem apenas {item["quantidade_estoque"]} unidade(s) em estoque.')
                        continue
                    
                    # Atualiza estoque via SQL
                    novo_estoque = item['quantidade_estoque'] - quantidade
                    db.update_estoque_produto(item['id'], novo_estoque)
                    
                    # Cria item de pedido via SQL
                    db.criar_item_pedido(comanda_id, item['id'], quantidade, observacao)
                    itens_criados = True

            if itens_criados:
                if mensagem_tipo == 'adicionado':
                    messages.success(request, f'✓ Itens adicionados à comanda de {nome_cliente_display} na Mesa {numero_mesa}!')
                else:
                    messages.success(request, f'✓ Comanda #{comanda_id} criada com sucesso para {nome_cliente_display} na Mesa {numero_mesa}!')
                return redirect('abrir_nova_comanda')
            else:
                messages.error(request, 'É necessário adicionar pelo menos um item ao pedido!')
    else:
        comanda_form = ComandaForm()
        item_formset = ItemFormSet()

    # Busca itens disponíveis via SQL
    itens_cardapio = db.get_produtos_disponiveis()
    itens_info = {item['id']: {'nome': item['nome'], 'estoque': item['quantidade_estoque'], 'disponivel': item['disponivel']} for item in itens_cardapio}

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
    Usa SQL puro para buscar comandas abertas
    """
    mesas_com_comandas = {}
    comandas_abertas = db.get_comandas_abertas_com_mesas()
    
    for cmd in comandas_abertas:
        mesa_id = cmd['mesa_id']
        if mesa_id not in mesas_com_comandas:
            mesas_com_comandas[mesa_id] = {
                'mesa': SimpleNamespace(id=mesa_id, numero=cmd['numero_mesa'], status=cmd['status_mesa']),
                'clientes': []
            }
        mesas_com_comandas[mesa_id]['clientes'].append(cmd['nome_cliente'])
    
    context = {
        'mesas_com_comandas': mesas_com_comandas
    }
    return render(request, 'pedidos/index.html', context)


@tipo_usuario_required('COZINHA', 'ADMIN')
def painel_cozinha(request):
    """
    RF2: Visualização da Fila de Produção da Cozinha
    Usa SQL puro para buscar comandas e itens
    """
    pedidos_pendentes = []
    comandas_abertas = db.get_comandas_abertas()

    for comanda_data in comandas_abertas:
        mesa_data = db.get_mesa_por_id(comanda_data['mesa_id'])
        mesa = SimpleNamespace(**mesa_data) if mesa_data else None
        itens_brutos = db.get_itens_nao_entregues_comanda(comanda_data['id'])
        itens_comanda = []

        for item in itens_brutos:
            itens_comanda.append({
                'id': item['id'],
                'quantidade': item['quantidade'],
                'observacao': item['observacao'],
                'status': item['status'],
                'item': {
                    'nome': item['nome_produto'],
                    'preco': item['preco_produto'],
                },
            })
        
        if itens_comanda:
            todos_prontos = all(item['status'] == 'P' for item in itens_comanda)
            
            pedidos_pendentes.append({
                'comanda': {
                    'id': comanda_data['id'],
                    'mesa': mesa,
                    'mesa_numero': mesa.numero if mesa else None,
                    'nome_cliente': comanda_data['nome_cliente'],
                    'data_abertura': comanda_data['data_abertura'],
                },
                'itens': itens_comanda,
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
    Marca um item específico como pronto (usa SQL puro)
    """
    if request.method == 'POST':
        item = db.get_item_pedido(item_id)
        if not item:
            messages.error(request, 'Item não encontrado.')
            return redirect('painel_cozinha')
        
        db.marcar_item_pronto(item_id)
        messages.success(request, f'✓ Item {item["nome_produto"]} marcado como PRONTO.')
        return redirect('painel_cozinha')
    
    return redirect('painel_cozinha')


@tipo_usuario_required('COZINHA', 'GARCOM', 'ADMIN')
def entregar_comanda(request, comanda_id):
    """
    Marca todos os itens de uma comanda como ENTREGUE (usa SQL puro)
    """
    if request.method == 'POST':
        comanda = db.get_comanda_por_id(comanda_id)
        if not comanda:
            messages.error(request, 'Comanda não encontrada.')
            return redirect('painel_cozinha')
        
        # Verifica se todos os itens estão prontos
        itens_comanda = db.get_itens_nao_entregues_comanda(comanda_id)
        itens_nao_prontos = [i for i in itens_comanda if i['status'] not in ['P', 'E']]
        
        if itens_nao_prontos:
            messages.error(request, f'⚠️ Não é possível entregar. Ainda há {len(itens_nao_prontos)} item(ns) não pronto(s).')
            return redirect('painel_cozinha')
        
        # Marca itens como entregues via SQL
        db.marcar_itens_entregues(comanda_id)
        
        # Busca mesa para exibir na mensagem
        mesa = db.get_mesa_por_id(comanda['mesa_id'])
        messages.success(request, f'✓ Comanda da Mesa {mesa["numero"]} ({comanda["nome_cliente"]}) ENTREGUE!')
        return redirect('painel_cozinha')
    
    return redirect('painel_cozinha')


@login_required
@tipo_usuario_required('GARCOM', 'COZINHA', 'ADMIN')
def gerenciar_mesa(request, mesa_numero):
    """
    Visualiza todas as comandas abertas de uma mesa específica
    Agrupa pedidos por cliente. Usa SQL puro.
    """
    # Verifica se é garçom tentando fechar comanda
    if request.method == 'POST' and request.user.profile.tipo == 'GARCOM':
        messages.error(request, '⚠️ Apenas administradores podem finalizar pagamentos.')
        return redirect('gerenciar_mesa', mesa_numero=mesa_numero)
    
    # Busca mesa via SQL
    mesa = db.get_mesa_por_numero(mesa_numero)
    if not mesa:
        messages.error(request, 'Mesa não encontrada.')
        return redirect('abrir_nova_comanda')
    
    # Busca comandas abertas via SQL
    comandas_abertas = db.get_comandas_aberta_mesa(mesa['id'])
    
    # Agrupa comandas por cliente (case-insensitive)
    clientes_agrupados = {}
    for comanda_data in comandas_abertas:
        nome_cliente_lower = comanda_data['nome_cliente'].lower()
        
        if nome_cliente_lower not in clientes_agrupados:
            clientes_agrupados[nome_cliente_lower] = {
                'nome_original': comanda_data['nome_cliente'],
                'comandas_ids': [],
                'itens': [],
                'primeira_comanda': comanda_data
            }
        
        clientes_agrupados[nome_cliente_lower]['comandas_ids'].append(comanda_data['id'])
        
        # Adiciona itens dessa comanda
        itens_brutos = db.get_itens_comanda(comanda_data['id'])
        for item in itens_brutos:
            item['item'] = {
                'nome': item['nome_produto'],
                'preco': item['preco_produto'],
            }
            clientes_agrupados[nome_cliente_lower]['itens'].append(item)
    
    # Prioridade de status: A (preparando) > P (pronto) > E (entregue)
    _status_prioridade = {'A': 0, 'P': 1, 'E': 2}

    # Prepara dados finais com totais por cliente
    comandas_detalhadas = []
    for cliente_data in clientes_agrupados.values():
        # Agrupa itens do mesmo produto somando quantidades
        grupos = {}
        for item in cliente_data['itens']:
            key = item['produto_id']
            if key not in grupos:
                grupos[key] = {
                    'produto_id': item['produto_id'],
                    'nome_produto': item['nome_produto'],
                    'preco_produto': item['preco_produto'],
                    'quantidade': 0,
                    'subtotal': Decimal('0.00'),
                    'status': item['status'],
                    'observacao': item['observacao'],
                    'item': item['item'],
                }
            grupos[key]['quantidade'] += item['quantidade']
            grupos[key]['subtotal'] += item['preco_produto'] * item['quantidade']
            # Mantém o status mais crítico (A > P > E)
            if _status_prioridade[item['status']] < _status_prioridade[grupos[key]['status']]:
                grupos[key]['status'] = item['status']

        itens_com_subtotal = list(grupos.values())
        total = sum(item['subtotal'] for item in itens_com_subtotal)
        comanda_base = cliente_data['primeira_comanda']
        comanda_obj = SimpleNamespace(
            id=comanda_base['id'],
            mesa=mesa,
            usuario_id=comanda_base['usuario_id'],
            nome_cliente=comanda_base['nome_cliente'],
            data_abertura=comanda_base['data_abertura'],
            qtde_pessoas=comanda_base['qtde_pessoas'],
            status=comanda_base['status'],
        )
        comandas_detalhadas.append({
            'comanda': comanda_obj,
            'comandas_ids': cliente_data['comandas_ids'],
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
    Apenas ADMIN pode finalizar pagamentos (usa SQL puro)
    """
    if request.method == 'POST':
        comanda = db.get_comanda_por_id(comanda_id)
        if not comanda:
            messages.error(request, 'Comanda não encontrada.')
            return redirect('abrir_nova_comanda')
        
        mesa = db.get_mesa_por_id(comanda['mesa_id'])
        nome_cliente = comanda['nome_cliente']
        
        # Fecha TODAS as comandas abertas deste cliente nesta mesa via SQL
        quantidade_fechada = db.fechar_comandas_cliente_mesa(comanda['mesa_id'], nome_cliente)
        
        if quantidade_fechada > 1:
            messages.success(request, f'✓ Todas as comandas de {nome_cliente} foram pagas e fechadas! ({quantidade_fechada} comandas)')
        else:
            messages.success(request, f'✓ Comanda de {nome_cliente} foi paga e fechada!')
        
        # Verifica se ainda há comandas abertas na mesa
        comandas_restantes = db.contar_comandas_abertas_mesa(comanda['mesa_id'])
        if comandas_restantes == 0:
            messages.info(request, f'Mesa {mesa["numero"]} está livre agora.')
        
        return redirect('gerenciar_mesa', mesa_numero=mesa['numero'])
    
    return redirect('abrir_nova_comanda')


@tipo_usuario_required('COZINHA', 'ADMIN')
def adicionar_produto(request):
    """
    Tela para adicionar novos produtos ao cardápio (usa SQL puro)
    """
    if request.method == 'POST':
        form = ItemCardapioForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            descricao = form.cleaned_data.get('descricao', '')
            preco = form.cleaned_data['preco']
            disponivel = form.cleaned_data.get('disponivel', 'S')
            quantidade_estoque = form.cleaned_data.get('quantidade_estoque', 0)
            categoria_id = form.cleaned_data.get('categoria')
            categoria_id = categoria_id.id if categoria_id else None
            
            produto_id = db.criar_produto(nome, descricao, preco, disponivel, quantidade_estoque, categoria_id)
            messages.success(request, f'✓ Produto "{nome}" adicionado com sucesso!')
            return redirect('gerenciar_estoque')
    else:
        form = ItemCardapioForm(initial={'disponivel': 'S'})
    
    return render(request, 'pedidos/adicionar_produto.html', {'form': form})


@tipo_usuario_required('COZINHA', 'ADMIN')
def editar_produto(request, item_id):
    """
    Tela para editar produtos existentes do cardápio (usa SQL puro)
    """
    item = db.get_produto_por_id(item_id)
    if not item:
        messages.error(request, 'Produto não encontrado.')
        return redirect('gerenciar_estoque')

    if request.method == 'POST':
        form = ItemCardapioForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            descricao = form.cleaned_data.get('descricao', '')
            preco = form.cleaned_data['preco']
            disponivel = form.cleaned_data.get('disponivel', 'S')
            quantidade_estoque = form.cleaned_data.get('quantidade_estoque', 0)
            categoria_id = form.cleaned_data.get('categoria')
            categoria_id = categoria_id.id if categoria_id else None
            
            db.atualizar_produto(item_id, nome, descricao, preco, disponivel, quantidade_estoque, categoria_id)
            
            messages.success(request, f'✓ Produto "{nome}" atualizado com sucesso!')
            return redirect('gerenciar_estoque')
    else:
        form = ItemCardapioForm(initial={
            'nome': item['nome'],
            'descricao': item['descricao'],
            'preco': item['preco'],
            'disponivel': item['disponivel'],
            'quantidade_estoque': item['quantidade_estoque']
        })

    return render(request, 'pedidos/adicionar_produto.html', {
        'form': form,
        'modo_edicao': True,
        'item': item
    })


# pedidos/views.py

# ============================================================
# CRUD DE CATEGORIAS
# ============================================================

@tipo_usuario_required('ADMIN')
def listar_categorias(request):
    from .models import Categoria
    categorias = Categoria.objects.all().order_by('descricao')
    return render(request, 'pedidos/listar_categorias.html', {'categorias': categorias})


@tipo_usuario_required('ADMIN')
def criar_categoria(request):
    from .models import Categoria
    if request.method == 'POST':
        descricao = request.POST.get('descricao', '').strip()
        if not descricao:
            messages.error(request, 'A descrição é obrigatória.')
            return redirect('listar_categorias')
        if Categoria.objects.filter(descricao__iexact=descricao).exists():
            messages.error(request, f'Já existe uma categoria com o nome "{descricao}".')
            return redirect('listar_categorias')
        Categoria.objects.create(descricao=descricao)
        messages.success(request, f'Categoria "{descricao}" criada com sucesso!')
    return redirect('listar_categorias')


@tipo_usuario_required('ADMIN')
def editar_categoria(request, categoria_id):
    from .models import Categoria
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        messages.error(request, 'Categoria não encontrada.')
        return redirect('listar_categorias')

    if request.method == 'POST':
        descricao = request.POST.get('descricao', '').strip()
        if not descricao:
            messages.error(request, 'A descrição é obrigatória.')
            return render(request, 'pedidos/editar_categoria.html', {'categoria': categoria})
        if Categoria.objects.filter(descricao__iexact=descricao).exclude(id=categoria_id).exists():
            messages.error(request, f'Já existe outra categoria com o nome "{descricao}".')
            return render(request, 'pedidos/editar_categoria.html', {'categoria': categoria})
        categoria.descricao = descricao
        categoria.save()
        messages.success(request, f'Categoria "{descricao}" atualizada com sucesso!')
        return redirect('listar_categorias')

    return render(request, 'pedidos/editar_categoria.html', {'categoria': categoria})


@tipo_usuario_required('ADMIN')
def deletar_categoria(request, categoria_id):
    from .models import Categoria
    if request.method != 'POST':
        return redirect('listar_categorias')
    try:
        categoria = Categoria.objects.get(id=categoria_id)
    except Categoria.DoesNotExist:
        messages.error(request, 'Categoria não encontrada.')
        return redirect('listar_categorias')

    if categoria.itemcardapio_set.exists():
        messages.error(request, f'A categoria "{categoria.descricao}" possui produtos vinculados e não pode ser excluída.')
        return redirect('listar_categorias')

    nome = categoria.descricao
    categoria.delete()
    messages.success(request, f'Categoria "{nome}" excluída com sucesso!')
    return redirect('listar_categorias')


# ============================================================
# CRUD DE MESAS
# ============================================================

@tipo_usuario_required('ADMIN')
def listar_mesas(request):
    from .models import Mesa
    mesas = Mesa.objects.all().order_by('numero')
    return render(request, 'pedidos/listar_mesas.html', {'mesas': mesas})


@tipo_usuario_required('ADMIN')
def criar_mesa(request):
    from .models import Mesa
    if request.method == 'POST':
        numero_raw = request.POST.get('numero', '').strip()
        status = request.POST.get('status', 'L')

        if not numero_raw:
            messages.error(request, 'O número da mesa é obrigatório.')
            return render(request, 'pedidos/listar_mesas.html', {'mesas': Mesa.objects.all().order_by('numero')})

        try:
            numero = int(numero_raw)
            if numero <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'O número da mesa deve ser um inteiro positivo.')
            return render(request, 'pedidos/listar_mesas.html', {'mesas': Mesa.objects.all().order_by('numero')})

        if Mesa.objects.filter(numero=numero).exists():
            messages.error(request, f'Já existe uma mesa com o número {numero}.')
            return render(request, 'pedidos/listar_mesas.html', {'mesas': Mesa.objects.all().order_by('numero')})

        Mesa.objects.create(numero=numero, status=status)
        messages.success(request, f'Mesa {numero} criada com sucesso!')
        return redirect('listar_mesas')

    return redirect('listar_mesas')


@tipo_usuario_required('ADMIN')
def editar_mesa(request, mesa_id):
    from .models import Mesa
    try:
        mesa = Mesa.objects.get(id=mesa_id)
    except Mesa.DoesNotExist:
        messages.error(request, 'Mesa não encontrada.')
        return redirect('listar_mesas')

    if request.method == 'POST':
        numero_raw = request.POST.get('numero', '').strip()
        status = request.POST.get('status', mesa.status)

        if not numero_raw:
            messages.error(request, 'O número da mesa é obrigatório.')
            return render(request, 'pedidos/editar_mesa.html', {'mesa': mesa})

        try:
            numero = int(numero_raw)
            if numero <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'O número da mesa deve ser um inteiro positivo.')
            return render(request, 'pedidos/editar_mesa.html', {'mesa': mesa})

        if Mesa.objects.filter(numero=numero).exclude(id=mesa_id).exists():
            messages.error(request, f'Já existe outra mesa com o número {numero}.')
            return render(request, 'pedidos/editar_mesa.html', {'mesa': mesa})

        mesa.numero = numero
        mesa.status = status
        mesa.save()
        messages.success(request, f'Mesa {numero} atualizada com sucesso!')
        return redirect('listar_mesas')

    return render(request, 'pedidos/editar_mesa.html', {'mesa': mesa})


@tipo_usuario_required('ADMIN')
def deletar_mesa(request, mesa_id):
    from .models import Mesa, Comanda
    if request.method != 'POST':
        return redirect('listar_mesas')

    try:
        mesa = Mesa.objects.get(id=mesa_id)
    except Mesa.DoesNotExist:
        messages.error(request, 'Mesa não encontrada.')
        return redirect('listar_mesas')

    if Comanda.objects.filter(mesa=mesa, status='A').exists():
        messages.error(request, f'A Mesa {mesa.numero} possui comandas abertas e não pode ser excluída.')
        return redirect('listar_mesas')

    numero = mesa.numero
    mesa.delete()
    messages.success(request, f'Mesa {numero} excluída com sucesso!')
    return redirect('listar_mesas')


@tipo_usuario_required('ADMIN')
def listar_usuarios(request):
    from .models import Usuario
    usuarios = Usuario.objects.all().order_by('first_name', 'username')
    return render(request, 'pedidos/listar_usuarios.html', {'usuarios': usuarios})


@tipo_usuario_required('ADMIN')
def editar_usuario(request, usuario_id):
    from .models import Usuario
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('listar_usuarios')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        tipo = request.POST.get('tipo', '').upper()
        nova_senha = request.POST.get('password1', '')
        confirmar_senha = request.POST.get('password2', '')
        ativo = request.POST.get('is_active') == 'on'

        if not tipo:
            messages.error(request, 'O tipo de usuário é obrigatório.')
            return render(request, 'pedidos/editar_usuario.html', {'usuario': usuario})

        if nova_senha:
            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
                return render(request, 'pedidos/editar_usuario.html', {'usuario': usuario})
            if len(nova_senha) < 6:
                messages.error(request, 'A senha deve ter pelo menos 6 caracteres.')
                return render(request, 'pedidos/editar_usuario.html', {'usuario': usuario})
            usuario.set_password(nova_senha)

        usuario.first_name = first_name
        usuario.email = email
        usuario.tipo = tipo
        usuario.is_active = ativo
        usuario.save()

        messages.success(request, f'Usuário "{usuario.username}" atualizado com sucesso!')
        return redirect('listar_usuarios')

    return render(request, 'pedidos/editar_usuario.html', {'usuario': usuario})


@tipo_usuario_required('ADMIN')
def deletar_usuario(request, usuario_id):
    from .models import Usuario
    if request.method != 'POST':
        return redirect('listar_usuarios')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('listar_usuarios')

    if usuario == request.user:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('listar_usuarios')

    nome = usuario.username
    usuario.delete()
    messages.success(request, f'Usuário "{nome}" excluído com sucesso!')
    return redirect('listar_usuarios')


@tipo_usuario_required('ADMIN')
def criar_usuario(request):
    """
    Cria novos usuários validando os dados manualmente sem o uso de Django Forms.
    """
    # Se a requisição for GET, apenas renderiza a página com o formulário limpo
    if request.method != 'POST':
        return render(request, 'pedidos/criar_usuario.html')

    # 1. Captura os dados brutos do POST
    username = request.POST.get('username', '').strip()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    first_name = request.POST.get('first_name', '').strip()
    tipo_usuario = request.POST.get('tipo', '').upper() # Ex: 'GARCOM', 'COZINHA', 'ADMIN'

    # Dicionário para manter os dados preenchidos e devolver ao HTML em caso de erro
    contexto_erro = {
        'dados_preenchidos': {
            'username': username,
            'first_name': first_name,
            'tipo': tipo_usuario
        }
    }

    # =========================================================================
    # 2. FLUXO DE VALIDAÇÕES MANUAIS
    # =========================================================================

    # Validação: Campos obrigatórios vazios
    if not username or not password1 or not password2 or not tipo_usuario:
        messages.error(request, '⚠️ Todos os campos obrigatórios devem ser preenchidos.')
        return render(request, 'pedidos/criar_usuario.html', contexto_erro)

    # Validação: Confirmação de senha
    if password1 != password2:
        messages.error(request, '⚠️ As senhas informadas não coincidem.')
        return render(request, 'pedidos/criar_usuario.html', contexto_erro)

    # Validação: Complexidade mínima da senha (exemplo: mínimo de 6 caracteres)
    if len(password1) < 6:
        messages.error(request, '⚠️ A senha deve conter pelo menos 6 caracteres.')
        return render(request, 'pedidos/criar_usuario.html', contexto_erro)

    # Validação: Unicidade do Usuário (Consulta direta ao banco)
    # Como seu projeto usa SQL puro/User nativo, verificamos se o username já existe
    from .models import Usuario

    if Usuario.objects.filter(username=username).exists():
        messages.error(request, f'⚠️ O usuário "{username}" já está cadastrado no sistema.')
        return render(request, 'pedidos/criar_usuario.html', contexto_erro)

    try:
        novo_usuario = Usuario(username=username, first_name=first_name, tipo=tipo_usuario)
        novo_usuario.set_password(password1)
        novo_usuario.save()

        messages.success(request, f'✓ Usuário "{username}" criado com sucesso!')
        return redirect('listar_usuarios')

    except Exception as e:
        messages.error(request, f'⚠️ Erro interno ao salvar o usuário: {str(e)}')
        return render(request, 'pedidos/criar_usuario.html', contexto_erro)

@tipo_usuario_required('COZINHA', 'ADMIN')
def gerenciar_estoque(request):
    """
    Painel para gerenciar disponibilidade e estoque dos itens (usa SQL puro)
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        acao = request.POST.get('acao')
        
        item = db.get_produto_por_id(item_id)
        if not item:
            messages.error(request, 'Item não encontrado.')
            return redirect('gerenciar_estoque')
        
        if acao == 'toggle_disponibilidade':
            db.toggle_disponibilidade_produto(item_id)
            status = 'disponível' if item['disponivel'] == 'N' else 'indisponível'
            messages.success(request, f'✓ {item["nome"]} marcado como {status}.')
        
        elif acao == 'atualizar_quantidade':
            nova_quantidade = request.POST.get('quantidade')
            try:
                nova_quantidade = int(nova_quantidade)
                if nova_quantidade < 0:
                    messages.error(request, 'Quantidade não pode ser negativa.')
                else:
                    db.update_estoque_produto(item_id, nova_quantidade)
                    messages.success(request, f'✓ Estoque de {item["nome"]} atualizado para {nova_quantidade} unidades.')
            except ValueError:
                messages.error(request, 'Quantidade inválida.')
        
        elif acao == 'deletar_item':
            try:
                db.deletar_produto(item_id)
                messages.success(request, f'✓ {item["nome"]} removido do cardápio.')
            except Exception as e:
                messages.error(request, f'⚠️ Não foi possível excluir {item["nome"]}. Erro: {str(e)}')
        
        return redirect('gerenciar_estoque')
    
    # Busca todos os itens via SQL
    itens = db.get_todos_produtos()
    
    context = {'itens': itens}
    return render(request, 'pedidos/gerenciar_estoque.html', context)


def login_view(request):
    """
    View de login do sistema
    """
    # 1) Evita mostrar tela de login para quem já possui sessão ativa.
    if request.user.is_authenticated:
        return redirect('index')
    
    # 2) Se o formulário foi enviado, processa credenciais informadas.
    if request.method == 'POST':
        # Captura os campos "username" e "password" enviados no <form> do template.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Valida usuário e senha pelo backend configurado (inclui nosso SQL backend)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.first_name or user.username}!')
            return redirect('index')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    # 6) Requisição GET (ou POST inválido): renderiza a página de login.
    return render(request, 'pedidos/login.html')


def logout_view(request):
    """
    View de logout do sistema
    """
    auth_logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')