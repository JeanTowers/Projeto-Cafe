# DER Conceitual para montar no brModelo
## Projeto: Comanda Vovó Rosa

Use este roteiro no brModelo para criar o DER conceitual rapidamente.

---

## 1) Entidades e atributos

### MESA
- id_mesa (identificador)
- numero
- ativa

### COMANDA
- id_comanda (identificador)
- nome_cliente
- data_abertura
- fechada

### ITEM_CARDAPIO
- id_item_cardapio (identificador)
- nome
- descricao
- preco
- disponivel
- quantidade_estoque

### ITEM_PEDIDO
- id_item_pedido (identificador)
- quantidade
- status
- observacao

### USUARIO
- id_usuario (identificador)

### PERFIL_USUARIO
- id_perfil_usuario (identificador)
- tipo

---

## 2) Relacionamentos (com cardinalidade)

1. **MESA possui COMANDA**
- MESA (1,1) —— (0,N) COMANDA

2. **COMANDA contém ITEM_PEDIDO**
- COMANDA (1,1) —— (1,N) ITEM_PEDIDO

3. **ITEM_CARDAPIO compõe ITEM_PEDIDO**
- ITEM_CARDAPIO (1,1) —— (0,N) ITEM_PEDIDO

4. **USUARIO tem PERFIL_USUARIO**
- USUARIO (1,1) —— (0,1) PERFIL_USUARIO

---

## 3) Como desenhar no brModelo (ordem sugerida)

1. Crie as 6 entidades.
2. Marque o atributo identificador (chave) em cada entidade.
3. Crie os 4 relacionamentos com os nomes: `possui`, `contém`, `compõe`, `tem`.
4. Ajuste as cardinalidades exatamente como na seção 2.
5. Organize visualmente em cadeia:
   - MESA -> COMANDA -> ITEM_PEDIDO <- ITEM_CARDAPIO
   - USUARIO -> PERFIL_USUARIO

---

## 4) Observação para apresentação

No banco físico atual, o estoque está modelado dentro de ITEM_CARDAPIO (`quantidade_estoque` e `disponivel`), por isso não há entidade separada de estoque no DER conceitual principal.

---

## 5) Tipos de cada coluna (banco físico atual)

### pedidos_mesa
- id: INTEGER (PK, NOT NULL)
- numero: INTEGER (NOT NULL)
- ativa: bool (NOT NULL)

### pedidos_comanda
- id: INTEGER (PK, NOT NULL)
- nome_cliente: varchar(100) (NOT NULL)
- data_abertura: datetime (NOT NULL)
- fechada: bool (NOT NULL)
- mesa_id: bigint (NOT NULL)

### pedidos_itemcardapio
- id: INTEGER (PK, NOT NULL)
- nome: varchar(100) (NOT NULL)
- descricao: TEXT (NOT NULL)
- preco: decimal (NOT NULL)
- disponivel: bool (NOT NULL)
- quantidade_estoque: INTEGER (NOT NULL)

### pedidos_itempedido
- id: INTEGER (PK, NOT NULL)
- quantidade: INTEGER (NOT NULL)
- status: varchar(10) (NOT NULL)
- comanda_id: bigint (NOT NULL)
- item_id: bigint (NOT NULL)
- observacao: TEXT (NOT NULL)

### pedidos_userprofile
- id: INTEGER (PK, NOT NULL)
- tipo: varchar(10) (NOT NULL)
- user_id: INTEGER (NOT NULL)

### auth_user (referenciada por pedidos_userprofile)
- id: INTEGER (PK, NOT NULL)
- password: varchar(128) (NOT NULL)
- last_login: datetime
- is_superuser: bool (NOT NULL)
- username: varchar(150) (NOT NULL)
- last_name: varchar(150) (NOT NULL)
- email: varchar(254) (NOT NULL)
- is_staff: bool (NOT NULL)
- is_active: bool (NOT NULL)
- date_joined: datetime (NOT NULL)
- first_name: varchar(150) (NOT NULL)

---

## 6) Checklist de entrega (professora exigente)

Use esta lista antes de entregar:

- [ ] DER conceitual com entidades, relacionamentos e cardinalidades visíveis.
- [ ] Identificadores (chaves) marcados em todas as entidades.
- [ ] Status de ITEM_PEDIDO coerente com o projeto: `ABERTO`, `PRONTO`, `ENTREGUE`.
- [ ] Explicação de estoque: modelado em ITEM_CARDAPIO (`quantidade_estoque` e `disponivel`).
- [ ] DER lógico com PK/FK e tipos das colunas principais (`pedidos_*`).
- [ ] Dicionário de dados (campo, tipo, regra e descrição).
- [ ] Observação explícita de escopo: domínio do sistema vs banco físico completo.

---

## 7) Escopo completo do banco físico (para não "deixar nada de fora")

Além das tabelas de domínio (`pedidos_*`), o projeto também usa tabelas internas do Django.

### Tabelas de domínio (app pedidos)
- pedidos_mesa
- pedidos_comanda
- pedidos_itemcardapio
- pedidos_itempedido
- pedidos_userprofile

### Tabelas técnicas do Django
- auth_user
- auth_group
- auth_permission
- auth_group_permissions
- auth_user_groups
- auth_user_user_permissions
- django_session
- django_migrations
- django_content_type
- django_admin_log

### Frase pronta para a apresentação
"O DER conceitual e o lógico principal foram feitos sobre o domínio do restaurante (tabelas `pedidos_*`). Como complemento técnico, o banco físico inclui tabelas nativas do Django para autenticação, permissão, sessão e migrações."