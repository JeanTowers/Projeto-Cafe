# Sistema de Comanda Digital - Café da Vovó Rosa

Sistema web completo para gerenciamento de pedidos e comandas em estabelecimentos de alimentação, desenvolvido com Django. Oferece controle total desde o pedido até o pagamento, com gestão de estoque integrada e diferentes níveis de acesso para usuários (Garçom, Cozinha e Administrador).

## 🎯 Objetivo do Sistema

Digitalizar e otimizar o fluxo completo de atendimento em cafés e restaurantes, eliminando cartelas de papel e proporcionando:
- **Agilidade** no registro de pedidos
- **Organização** da produção na cozinha
- **Controle** de estoque em tempo real
- **Gestão** de pagamentos e comandas
- **Segurança** com diferentes níveis de acesso por tipo de usuário

## 👥 Sistema de Usuários e Permissões

O sistema possui três tipos de usuários, cada um com acesso específico:

### 🍽️ Garçom/Atendente
**Responsabilidades:**
- Abrir novas comandas
- Adicionar pedidos para clientes
- Visualizar status dos pedidos nas mesas
- **NÃO pode:** Gerenciar estoque, acessar painel da cozinha ou finalizar pagamentos

### 👨‍🍳 Cozinha
**Responsabilidades:**
- Visualizar fila de produção
- Marcar itens como prontos
- Gerenciar estoque de produtos
- Adicionar novos produtos ao cardápio
- Marcar comandas como entregues
- **NÃO pode:** Abrir comandas ou finalizar pagamentos

### 👔 Administrador
**Responsabilidades:**
- Acesso total ao sistema
- Gerenciar comandas e pagamentos
- Visualizar e gerenciar todas as mesas
- Acesso ao painel administrativo Django
- Criar e gerenciar usuários

**Usuários de Teste:**
- Garçom: `garcom` / senha: `senha123`
- Cozinha: `cozinha` / senha: `senha123`
- Admin: `admin` / senha: `admin123`

## 📋 Funcionalidades Principais

### 1️⃣ Gestão de Pedidos (Garçom/Admin)
✅ **Abrir Nova Comanda**
- Seleção de mesa com botões visuais
- Nome do cliente obrigatório
- Múltiplos clientes por mesa (cada um com sua comanda individual)
- Adição de vários itens com quantidades personalizadas
- Campo de observações para pedidos especiais (ex: "sem cebola")
- **Sistema inteligente:** Se o cliente já tem comanda aberta na mesa, os novos itens são adicionados à comanda existente
- Exibição do estoque disponível em tempo real
- Validação automática: produtos sem estoque não aparecem para pedido
- Decremento automático do estoque ao confirmar pedido

✅ **Visualização de Mesas**
- Lista de todas as mesas com comandas abertas
- Identificação dos clientes em cada mesa
- Acesso rápido aos detalhes da comanda

### 2️⃣ Produção na Cozinha (Cozinha/Admin)
✅ **Painel de Produção em Tempo Real**
- Visualização de todos os pedidos não entregues
- Organização por ordem de chegada (FIFO)
- Exibição clara: Mesa, Cliente, Itens e Observações
- Status de cada item: 🔴 Em Preparo, ✅ Pronto, 🚀 Entregue
- Atualização automática a cada 30 segundos

✅ **Controle de Status**
- **Fase 1 - Preparando (ABERTO):** Item sendo produzido, com botão "Marcar Pronto"
- **Fase 2 - Pronto:** Todos os itens prontos, aguardando entrega
- **Fase 3 - Entregue:** Comanda sai do painel após confirmação de entrega
- Botão "Entregar Comanda" só aparece quando TODOS os itens estão prontos

### 3️⃣ Controle de Estoque (Cozinha/Admin)
✅ **Gerenciamento Completo**
- Visualização de todos os produtos com quantidade em estoque
- Marcação de disponibilidade (disponível/indisponível)
- Atualização manual de quantidade
- Alertas visuais para produtos com estoque baixo (≤5 unidades)
- Decremento automático ao confirmar pedidos
- Produtos com estoque zero são automaticamente marcados como indisponíveis

✅ **Cadastro de Produtos**
- Adicionar novos itens ao cardápio
- Definir nome, descrição, preço e estoque inicial
- Controle de disponibilidade

### 4️⃣ Gestão de Pagamentos (Admin)
✅ **Gerenciamento de Comandas**
- Visualização detalhada de todos os pedidos por cliente
- Agrupamento automático de múltiplas comandas do mesmo cliente
- Exibição de status de cada item (Preparando/Pronto/Entregue)
- Cálculo automático: quantidade × preço unitário = subtotal
- Total consolidado por cliente
- Finalização de pagamento (fecha todas as comandas do cliente)

### 5️⃣ Sistema de Autenticação
✅ **Login Seguro**
- Página de login moderna com toggle de senha
- Redirecionamento automático baseado no tipo de usuário
- Sessões persistentes
- Botão de logout em todas as telas
- Proteção de rotas por tipo de usuário

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- Python 3.13+ instalado
- Navegador web moderno

### 2. Instalação

O projeto já está configurado com:
- Django instalado
- Banco de dados SQLite configurado
- Migrações aplicadas

### 3. Popular Dados Iniciais

Execute o comando para criar mesas (1-10) e itens do cardápio:

```powershell
python manage.py popular_dados
```

### 4. Iniciar o Servidor

```powershell
python manage.py runserver
```

O servidor iniciará em: **http://127.0.0.1:8000/**

### 5. Acessar o Sistema

- **Página Inicial:** http://127.0.0.1:8000/
- **Nova Comanda (Garçom):** http://127.0.0.1:8000/pedidos/nova-comanda/
- **Painel da Cozinha:** http://127.0.0.1:8000/pedidos/painel-cozinha/
- **Gerenciar Estoque:** http://127.0.0.1:8000/pedidos/gerenciar-estoque/
- **Admin:** http://127.0.0.1:8000/admin/

## 🔄 Fluxo Completo do Sistema (Passo a Passo)

### 📍 Cenário: Cliente chega e faz um pedido

**1. Login no Sistema**
- Garçom faz login com suas credenciais
- Sistema redireciona para a página inicial com menu personalizado

**2. Abertura da Comanda (Garçom)**
- Clica em "Nova Comanda"
- Seleciona a mesa do cliente (ex: Mesa 5)
- Digita o nome do cliente (ex: "João Silva")
- Escolhe os itens desejados (apenas produtos com estoque aparecem)
  - Ex: 2x Café Expresso, 3x Pão de Queijo
- Adiciona observações se necessário (ex: "Café sem açúcar")
- Clica em "Confirmar Pedido"
- **Sistema automaticamente:**
  - Cria a comanda ou adiciona itens à comanda existente do cliente
  - Decrementa o estoque (2 cafés e 3 pães)
  - Envia pedido para o Painel da Cozinha
  - Marca itens como "ABERTO" (Em Preparo)

**3. Produção na Cozinha (Cozinha)**
- Acessa "Painel da Cozinha"
- Visualiza o pedido da Mesa 5 - João Silva
- Vê todos os itens: 2x Café Expresso, 3x Pão de Queijo
- Lê a observação: "Café sem açúcar"
- **Ao preparar cada item:**
  - Prepara o Café Expresso → Clica "Marcar Pronto"
  - Item fica verde com ✅ Pronto
  - Prepara o Pão de Queijo → Clica "Marcar Pronto"
  - Item fica verde com ✅ Pronto
- **Quando todos os itens estão prontos:**
  - Aparece botão "🚀 Entregar Comanda"
  - Cozinha clica neste botão
  - Comanda sai do painel (status = ENTREGUE)

**4. Visualização para Garçom (Garçom/Admin)**
- Garçom pode acessar "Mesas com Comandas Abertas"
- Clica na Mesa 5
- Vê todos os pedidos de João Silva com status:
  - Café Expresso: 🚀 Entregue
  - Pão de Queijo: 🚀 Entregue
- Vê o total a pagar: R$ 28,50

**5. Pagamento (Admin)**
- Admin acessa "Gerenciar Mesa 5"
- Vê detalhamento completo:
  - 2x R$ 5,00 = **R$ 10,00** (Café Expresso)
  - 3x R$ 9,50 = **R$ 28,50** (Pão de Queijo)
  - **Total: R$ 38,50**
- Confirma pagamento
- Sistema fecha todas as comandas de João Silva
- Mesa fica disponível para novo cliente

### 🔁 Casos Especiais

**Múltiplos Clientes na Mesma Mesa:**
- Maria e Pedro sentam na Mesa 5
- Garçom cria comanda para "Maria" → 1x Café
- Garçom cria comanda para "Pedro" → 2x Pão de Queijo
- Sistema mantém comandas separadas
- No pagamento, mostra duas comandas distintas
- Podem pagar separadamente ou juntos

**Cliente Adiciona Mais Itens:**
- João já tem comanda aberta na Mesa 5
- Garçom abre "Nova Comanda" novamente
- Seleciona Mesa 5 e digita "João Silva"
- **Sistema detecta comanda existente**
- Novos itens são adicionados à mesma comanda
- Total é atualizado automaticamente

**Item Sem Estoque:**
- Cliente pede Bolo de Cenoura (estoque = 0)
- Item **não aparece** na lista de pedidos
- Se garçom tentar forçar (URL direta), recebe erro:
  - "⚠️ Bolo de Cenoura está sem estoque no momento"
- Pedido não é criado

## 🗄️ Arquitetura e Banco de Dados

### Estrutura do Projeto Django

```
comanda_vovo_rosa/
├── comanda_vovo_rosa/          # Configurações do projeto
│   ├── settings.py             # Configurações gerais
│   ├── urls.py                 # URLs principais
│   └── wsgi.py                 # Servidor WSGI
├── pedidos/                    # App principal
│   ├── models.py               # Modelos do banco de dados
│   ├── views.py                # Lógica de negócio
│   ├── forms.py                # Formulários Django
│   ├── urls.py                 # URLs do app
│   ├── decorators.py           # Decoradores de permissão
│   ├── admin.py                # Painel administrativo
│   ├── templates/              # Templates HTML
│   │   └── pedidos/
│   │       ├── login.html
│   │       ├── index.html
│   │       ├── nova_comanda.html
│   │       ├── painel_cozinha.html
│   │       ├── gerenciar_mesa.html
│   │       ├── gerenciar_estoque.html
│   │       └── adicionar_produto.html
│   └── management/commands/    # Comandos customizados
│       ├── popular_dados.py
│       ├── resetar_banco.py
│       └── criar_usuarios.py
├── db.sqlite3                  # Banco de dados SQLite
└── manage.py                   # CLI do Django
```

### Modelos do Banco de Dados

**UserProfile** (Perfil de Usuário)
- `user` - Relacionamento OneToOne com User do Django
- `tipo` - CharField com choices: GARCOM, COZINHA, ADMIN
- **Função:** Estende o modelo User padrão do Django para adicionar tipo de usuário

**Mesa**
- `numero` - IntegerField único (1-10)
- `ativa` - BooleanField (controla se a mesa está disponível)
- **Função:** Representa as mesas físicas do estabelecimento

**ItemCardapio**
- `nome` - CharField (ex: "Café Expresso")
- `descricao` - TextField opcional
- `preco` - DecimalField (5 dígitos, 2 decimais)
- `disponivel` - BooleanField (controla se pode ser pedido)
- `quantidade_estoque` - IntegerField (unidades disponíveis)
- **Função:** Catálogo de produtos vendidos
- **Regra:** Se quantidade_estoque = 0, automaticamente disponivel = False

**Comanda**
- `mesa` - ForeignKey(Mesa) com PROTECT
- `nome_cliente` - CharField obrigatório
- `data_abertura` - DateTimeField automático
- `fechada` - BooleanField (False = aberta, True = paga)
- **Função:** Representa um pedido de um cliente específico em uma mesa
- **Regra:** Pode haver múltiplas comandas abertas na mesma mesa (clientes diferentes)

**ItemPedido**
- `comanda` - ForeignKey(Comanda) com CASCADE
- `item` - ForeignKey(ItemCardapio) com PROTECT
- `quantidade` - IntegerField
- `observacao` - TextField opcional (ex: "sem cebola")
- `status` - CharField com choices: ABERTO, PRONTO, ENTREGUE
- **Função:** Representa cada item individual dentro de uma comanda
- **Regra:** Ao criar, decrementa estoque; status inicial = ABERTO

### Relacionamentos

```
Mesa (1) ──────< (N) Comanda
                        │
                        │ (1 comanda tem N itens)
                        │
                        └──< ItemPedido >── ItemCardapio
                                │
                                └── quantidade, observacao, status

User (1) ─────< (1) UserProfile
                    └── tipo (GARCOM/COZINHA/ADMIN)
```

## 🎨 Tecnologias e Recursos Técnicos

### Stack Tecnológico
- **Backend:** Django 5.2.8 (Python 3.13.3)
- **Banco de Dados:** SQLite (desenvolvimento)
- **Frontend:** HTML5, CSS3 puro (sem frameworks)
- **Autenticação:** Django Authentication System
- **Formulários:** Django Forms com validação server-side

### Recursos Implementados

**Segurança:**
- Sistema de login obrigatório
- Decorador customizado `@tipo_usuario_required` para controle de acesso
- Proteção CSRF em todos os formulários
- Validação de permissões em cada view

**Interface do Usuário:**
- Design responsivo com gradientes modernos
- Botões visuais em vez de dropdowns
- Feedback visual imediato (mensagens de sucesso/erro)
- Auto-refresh de 30 segundos no painel da cozinha
- Cores semânticas (verde=disponível, vermelho=indisponível, amarelo=baixo estoque)

**Lógica de Negócio:**
- Validação em múltiplas camadas (formulário → view → banco)
- Controle de estoque com validação em tempo real
- Agrupamento inteligente de comandas por cliente
- Cálculo automático de subtotais e totais
- Case-insensitive na busca de clientes (João = joão = JOÃO)

**Otimizações:**
- `select_related()` e `prefetch_related()` para reduzir queries
- Índices automáticos em ForeignKeys
- Queries otimizadas com agregações do Django ORM

## 📊 Painel Administrativo

Acesse `/admin/` para:
- Gerenciar mesas
- Adicionar/editar itens do cardápio
- Visualizar histórico de comandas
- Gerenciar usuários do sistema

## 🔧 Comandos Customizados

O sistema possui comandos Django customizados para facilitar o gerenciamento:

### 1. Popular Dados Iniciais
```powershell
python manage.py popular_dados
```
**O que faz:**
- Cria 10 mesas (numeradas de 1 a 10)
- Adiciona itens ao cardápio:
  - Café Expresso - R$ 5,00 (50 un.)
  - Café com Leite - R$ 6,00 (50 un.)
  - Cappuccino - R$ 8,00 (30 un.)
  - Pão de Queijo - R$ 9,50 (100 un.)
  - Croissant - R$ 7,00 (50 un.)
  - Bolo de Cenoura - R$ 6,50 (20 un.)
  - Sanduíche Natural - R$ 12,00 (30 un.)
  - Suco de Laranja - R$ 7,50 (40 un.)

### 2. Criar Usuários de Teste
```powershell
python manage.py criar_usuarios
```
**O que faz:**
- Cria usuário "garcom" (senha: senha123) - Tipo: GARCOM
- Cria usuário "cozinha" (senha: senha123) - Tipo: COZINHA
- Cria usuário "admin" (senha: admin123) - Tipo: ADMIN (superuser)

### 3. Resetar Banco de Dados
```powershell
python manage.py resetar_banco
```
**⚠️ CUIDADO:** Este comando apaga TODO o banco de dados e recria do zero.
**Útil para:** Começar com dados limpos durante desenvolvimento.

### Outros Comandos Django Úteis

```powershell
# Criar migrações (após alterar models.py)
python manage.py makemigrations

# Aplicar migrações ao banco
python manage.py migrate

# Criar superusuário manualmente
python manage.py createsuperuser

# Abrir shell interativo do Django
python manage.py shell

# Coletar arquivos estáticos (produção)
python manage.py collectstatic

# Verificar problemas no projeto
python manage.py check
```

## 📝 Autor

**Jean Torres**  
Projeto Acadêmico - Sistema de Comanda Digital

## 📄 Licença

Projeto educacional desenvolvido para o Café da Vovó Rosa.
