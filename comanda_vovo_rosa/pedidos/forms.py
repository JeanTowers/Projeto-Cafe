# pedidos/forms.py
"""
===========================================
FORMS.PY - Formulários de Entrada de Dados
===========================================

Este arquivo define os formulários usados nas views.

FORMULÁRIOS CRIADOS:
1. ItemCardapioForm - Adicionar produto ao cardápio
2. ComandaForm - Selecionar mesa e digitar nome do cliente
3. ItemPedidoForm - Selecionar item, quantidade e observações

COMO FUNCIONA:
- ModelForm: Cria formulário baseado em um Model
- Form: Formulário customizado (não vinculado diretamente a um Model)
- widgets: Define como os campos são renderizados (input, select, radio, etc.)
- clean_*: Métodos de validação customizada

FLUXO DE VALIDAÇÃO:
1. is_valid() - Valida todos os campos
2. clean_campo() - Validação específica de um campo
3. clean() - Validação geral (múltiplos campos)
"""

from django import forms
from .models import Comanda, ItemPedido, Mesa, ItemCardapio

# ============================================
# FORMULÁRIO 1: ITEM DO CARDÁPIO
# ============================================

class ItemCardapioForm(forms.ModelForm):
    """
    Formulário para adicionar/editar produtos do cardápio.
    
    CAMPOS:
    - nome: Nome do produto
    - descricao: Descrição opcional
    - preco: Preço em R$
    - quantidade_estoque: Quantidade inicial
    - disponivel: Se está disponível para pedidos
    
    USO:
    Usado na view adicionar_produto() pela COZINHA ou ADMIN
    """
    
    class Meta:
        model = ItemCardapio
        fields = ['nome', 'descricao', 'preco', 'quantidade_estoque', 'disponivel']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Ex: Café Expresso',
                'class': 'form-control'
            }),
            'descricao': forms.Textarea(attrs={
                'placeholder': 'Descrição do produto',
                'class': 'form-control',
                'rows': 3
            }),
            'preco': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'class': 'form-control'
            }),
            'quantidade_estoque': forms.NumberInput(attrs={
                'placeholder': '0',
                'class': 'form-control'
            }),
        }

# 1. Formulário para o cabeçalho da Comanda (Mesa e Cliente)
class ComandaForm(forms.ModelForm):
    # Usa RadioSelect com widget customizado para renderizar como botões
    mesa = forms.ModelChoiceField(
        queryset=Mesa.objects.filter(ativa=True),
        label="Mesa",
        widget=forms.RadioSelect,
        empty_label=None
    )
    
    class Meta:
        model = Comanda
        fields = ['mesa', 'nome_cliente']
        widgets = {
            'nome_cliente': forms.TextInput(attrs={
                'placeholder': 'Digite o nome do cliente',
                'class': 'input-cliente'
            })
        }

# 2. Formulário para um Item dentro do Pedido (Cardápio e Quantidade)
class ItemPedidoForm(forms.Form):
    item_cardapio = forms.ModelChoiceField(
        queryset=ItemCardapio.objects.filter(disponivel=True, quantidade_estoque__gt=0).order_by('nome'),
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
    
    def clean_item_cardapio(self):
        item = self.cleaned_data.get('item_cardapio')
        
        if item:
            # Recarrega o item do banco para ter os dados mais atuais
            try:
                item = ItemCardapio.objects.get(pk=item.pk)
            except ItemCardapio.DoesNotExist:
                raise forms.ValidationError('⚠️ Este item não existe mais no cardápio.')
            
            if not item.disponivel:
                raise forms.ValidationError(f'⚠️ {item.nome} não está mais disponível no momento.')
            
            if item.quantidade_estoque <= 0:
                raise forms.ValidationError(f'⚠️ {item.nome} está sem estoque no momento.')
        
        return item
    
    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item_cardapio')
        quantidade = cleaned_data.get('quantidade')
        
        if item and quantidade:
            # Recarrega novamente para garantir dados atualizados
            try:
                item_atualizado = ItemCardapio.objects.get(pk=item.pk)
            except ItemCardapio.DoesNotExist:
                raise forms.ValidationError('⚠️ Este item não existe mais no cardápio.')
            
            if item_atualizado.quantidade_estoque < quantidade:
                raise forms.ValidationError(
                    f'⚠️ {item_atualizado.nome} tem apenas {item_atualizado.quantidade_estoque} unidade(s) em estoque.'
                )
        
        return cleaned_data