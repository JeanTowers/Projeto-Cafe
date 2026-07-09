# pedidos/forms.py
"""
===========================================
FORMS.PY - Formulários de Entrada de Dados
===========================================

Este arquivo define os formulários usados nas views.

As opções dos campos (mesas, produtos, categorias) são carregadas
com as queries do db.py no __init__ de cada form, e as validações
consultam o banco do mesmo jeito.

FORMULÁRIOS CRIADOS:
1. ItemCardapioForm - Adicionar/editar produto do cardápio
2. ComandaForm - Selecionar mesa e digitar nome do cliente
3. ItemPedidoForm - Selecionar item, quantidade e observações

FLUXO DE VALIDAÇÃO:
1. is_valid() - Valida todos os campos
2. clean_campo() - Validação específica de um campo
3. clean() - Validação geral (múltiplos campos)
"""

from django import forms

from .db import Database

# ============================================
# FORMULÁRIO 1: ITEM DO CARDÁPIO
# ============================================

class ItemCardapioForm(forms.Form):
    """
    Formulário para adicionar/editar produtos do cardápio.
    Usado na view adicionar_produto()/editar_produto() pela COZINHA ou ADMIN.
    """

    nome = forms.CharField(
        label='Nome',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Café Expresso',
            'class': 'form-control'
        })
    )
    descricao = forms.CharField(
        label='Descrição',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Descrição do produto',
            'class': 'form-control',
            'rows': 3
        })
    )
    preco = forms.DecimalField(
        label='Preço',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.00',
            'step': '0.01',
            'class': 'form-control'
        })
    )
    quantidade_estoque = forms.IntegerField(
        label='Quantidade em estoque',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        })
    )
    disponivel = forms.ChoiceField(
        choices=[('S', 'Sim'), ('N', 'Não')],
        label="Disponível para venda",
        widget=forms.RadioSelect(attrs={
            'class': 'disponivel-radio'
        })
    )
    categoria = forms.ChoiceField(
        label='Categoria',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Carrega as categorias via SQL puro
        categorias = Database.get_todas_categorias()
        self.fields['categoria'].choices = [('', '— Sem categoria')] + [
            (str(c['id']), c['descricao']) for c in categorias
        ]
        # Lista usada pelo template para renderizar os chips de categoria
        self.categorias_disponiveis = categorias

    def clean_categoria(self):
        valor = self.cleaned_data.get('categoria')
        return int(valor) if valor else None


# 1. Formulário para o cabeçalho da Comanda (Mesa e Cliente)
class ComandaForm(forms.Form):
    mesa = forms.ChoiceField(
        label="Mesa",
        widget=forms.RadioSelect,
    )
    nome_cliente = forms.CharField(
        label='Nome do cliente',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite o nome do cliente',
            'class': 'input-cliente'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apenas mesas livres, buscadas via SQL puro
        mesas = [m for m in Database.get_todas_mesas() if m['status'] == 'L']
        self.fields['mesa'].choices = [(str(m['id']), f"Mesa {m['numero']}") for m in mesas]

    def clean_mesa(self):
        mesa_id = self.cleaned_data.get('mesa')
        mesa = Database.get_mesa_por_id(mesa_id)
        if not mesa:
            raise forms.ValidationError('⚠️ Mesa não encontrada.')
        return mesa  # dicionário {'id', 'numero', 'status'}


# 2. Formulário para um Item dentro do Pedido (Cardápio e Quantidade)
class ItemPedidoForm(forms.Form):
    item_cardapio = forms.ChoiceField(
        label="Item do Cardápio",
        widget=forms.RadioSelect,
        required=False
    )
    quantidade = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Quantidade",
        widget=forms.NumberInput(attrs={'class': 'input-quantidade'})
    )
    observacao = forms.CharField(
        required=False,
        label="Observações",
        widget=forms.Textarea(attrs={
            'class': 'input-observacao',
            'placeholder': 'Ex: sem cebola, bem passado, etc.',
            'rows': 2
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apenas produtos disponíveis e com estoque, via SQL puro
        produtos = Database.get_produtos_disponiveis()
        self.fields['item_cardapio'].choices = [(str(p['id']), p['nome']) for p in produtos]

    def clean_item_cardapio(self):
        item_id = self.cleaned_data.get('item_cardapio')

        if not item_id:
            return None

        # Recarrega o item do banco (SQL) para ter os dados mais atuais
        item = Database.get_produto_por_id(item_id)
        if not item:
            raise forms.ValidationError('⚠️ Este item não existe mais no cardápio.')

        if item['disponivel'] != 'S':
            raise forms.ValidationError(f"⚠️ {item['nome']} não está mais disponível no momento.")

        if item['quantidade_estoque'] <= 0:
            raise forms.ValidationError(f"⚠️ {item['nome']} está sem estoque no momento.")

        return item  # dicionário do produto

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item_cardapio')
        quantidade = cleaned_data.get('quantidade')

        if item and quantidade:
            # Recarrega novamente para garantir dados atualizados
            item_atualizado = Database.get_produto_por_id(item['id'])
            if not item_atualizado:
                raise forms.ValidationError('⚠️ Este item não existe mais no cardápio.')

            if item_atualizado['quantidade_estoque'] < quantidade:
                raise forms.ValidationError(
                    f"⚠️ {item_atualizado['nome']} tem apenas {item_atualizado['quantidade_estoque']} unidade(s) em estoque."
                )

        return cleaned_data
