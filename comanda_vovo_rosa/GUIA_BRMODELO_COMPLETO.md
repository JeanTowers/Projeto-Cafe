# Guia Completo no brModelo (Conceitual, Lógico e Físico)
## Projeto: Comanda Vovó Rosa

Este guia está revisado conforme os modelos reais do projeto Django.

---

## 1) DER Conceitual (o que desenhar primeiro)

### Entidades
- MESA
- COMANDA
- ITEM_CARDAPIO
- ITEM_PEDIDO
- USUARIO
- PERFIL_USUARIO

### Atributos por entidade
- MESA: `id_mesa` (identificador), `numero`, `ativa`
- COMANDA: `id_comanda` (identificador), `nome_cliente`, `data_abertura`, `fechada`
- ITEM_CARDAPIO: `id_item_cardapio` (identificador), `nome`, `descricao`, `preco`, `disponivel`, `quantidade_estoque`
- ITEM_PEDIDO: `id_item_pedido` (identificador), `quantidade`, `status`, `observacao`
- USUARIO: `id_usuario` (identificador)
- PERFIL_USUARIO: `id_perfil_usuario` (identificador), `tipo`

### Relacionamentos e cardinalidades (exatamente)
1. MESA — possui — COMANDA
   - MESA (1,1) ; COMANDA (0,N)
2. COMANDA — contém — ITEM_PEDIDO
   - COMANDA (1,1) ; ITEM_PEDIDO (1,N)
3. ITEM_CARDAPIO — compõe — ITEM_PEDIDO
   - ITEM_CARDAPIO (1,1) ; ITEM_PEDIDO (0,N)
4. USUARIO — tem — PERFIL_USUARIO
   - USUARIO (1,1) ; PERFIL_USUARIO (0,1)

### Observações importantes para a defesa
- Estoque está dentro de ITEM_CARDAPIO (`quantidade_estoque` e `disponivel`).
- `status` de ITEM_PEDIDO no projeto: `ABERTO`, `PRONTO`, `ENTREGUE`.

---

## 2) DER Lógico (transformação para tabelas)

Após montar o conceitual no brModelo, transforme para modelo lógico e valide as chaves.

### Tabelas principais
- MESA(`id` PK, `numero`, `ativa`)
- COMANDA(`id` PK, `nome_cliente`, `data_abertura`, `fechada`, `mesa_id` FK -> MESA.id)
- ITEM_CARDAPIO(`id` PK, `nome`, `descricao`, `preco`, `disponivel`, `quantidade_estoque`)
- ITEM_PEDIDO(`id` PK, `quantidade`, `status`, `observacao`, `comanda_id` FK -> COMANDA.id, `item_id` FK -> ITEM_CARDAPIO.id)
- PERFIL_USUARIO(`id` PK, `tipo`, `user_id` FK -> USUARIO.id)

### Regras de modelagem para não errar
- Toda tabela precisa de PK.
- Todo relacionamento 1:N vira FK no lado N.
- Relação USUARIO–PERFIL_USUARIO é 1:0..1 (perfil opcional e no máximo um).
- Evite colocar tabelas técnicas do Django no DER lógico principal do domínio (coloque em anexo, se pedido).

---

## 3) Modelo Físico (tipos reais do banco atual SQLite)

### pedidos_mesa
- `id` INTEGER PK NOT NULL
- `numero` INTEGER NOT NULL
- `ativa` bool NOT NULL

### pedidos_comanda
- `id` INTEGER PK NOT NULL
- `nome_cliente` varchar(100) NOT NULL
- `data_abertura` datetime NOT NULL
- `fechada` bool NOT NULL
- `mesa_id` bigint NOT NULL

### pedidos_itemcardapio
- `id` INTEGER PK NOT NULL
- `nome` varchar(100) NOT NULL
- `descricao` TEXT NOT NULL
- `preco` decimal NOT NULL
- `disponivel` bool NOT NULL
- `quantidade_estoque` INTEGER NOT NULL

### pedidos_itempedido
- `id` INTEGER PK NOT NULL
- `quantidade` INTEGER NOT NULL
- `status` varchar(10) NOT NULL
- `comanda_id` bigint NOT NULL
- `item_id` bigint NOT NULL
- `observacao` TEXT NOT NULL

### pedidos_userprofile
- `id` INTEGER PK NOT NULL
- `tipo` varchar(10) NOT NULL
- `user_id` INTEGER NOT NULL

### auth_user (referência do perfil)
- `id` INTEGER PK NOT NULL
- `password` varchar(128) NOT NULL
- `last_login` datetime
- `is_superuser` bool NOT NULL
- `username` varchar(150) NOT NULL
- `last_name` varchar(150) NOT NULL
- `email` varchar(254) NOT NULL
- `is_staff` bool NOT NULL
- `is_active` bool NOT NULL
- `date_joined` datetime NOT NULL
- `first_name` varchar(150) NOT NULL

---

## 4) Como montar no brModelo sem perder ponto

1. Crie o DER Conceitual primeiro.
2. Marque os identificadores de todas as entidades.
3. Nomeie relacionamentos (`possui`, `contém`, `compõe`, `tem`) e configure cardinalidades.
4. Gere/monte o Modelo Lógico a partir do conceitual.
5. Revise PK/FK no lógico.
6. No Modelo Físico, aplique os tipos reais acima.
7. Entregue com três imagens: Conceitual, Lógico e Físico.

---

## 5) O que anexar para professora exigente

- Imagem DER Conceitual.
- Imagem DER Lógico.
- Imagem Modelo Físico (com tipos).
- Dicionário de dados (campo, tipo, regra, descrição).
- Observação de escopo:
  - DER principal do domínio: `pedidos_*`
  - Tabelas técnicas complementares: `auth_*`, `django_*`

Frase pronta:
"Apresentei o DER conceitual e lógico do domínio do restaurante e, no físico, explicitei os tipos reais do SQLite e as tabelas técnicas do Django como complemento de infraestrutura."