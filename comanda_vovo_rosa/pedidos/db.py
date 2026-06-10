"""
===========================================
DB.PY - Acesso ao Banco via SQL Puro
===========================================

Este módulo encapsula todas as operações de banco de dados em SQL raw.
Substitui o uso do ORM Django por queries SQL diretas.

USO:
    from pedidos.db import Database
    db = Database()
    usuarios = db.get_usuarios()
    comanda = db.create_comanda(mesa_id, usuario_id, nome_cliente, qtde_pessoas)
"""

from datetime import datetime
from decimal import Decimal

from django.db import connection


class Database:
    """Gerenciador de banco de dados com queries SQL puras."""

    @staticmethod
    def get_usuario_por_login(username):
        # Busca um usuário pelo login para autenticação.
        # Retorna os campos necessários para validar senha e carregar a sessão.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "id", "Login", "Senha", "Email", "Nome", "Ativo", "tipo" FROM "Usuario" WHERE "Login" = %s',
                [username],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'first_name': row[4],
                'is_active': row[5],
                'tipo': row[6],
            }

    @staticmethod
    def get_usuario_por_id(usuario_id):
        # Busca um usuário pelo ID primário.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "id", "Login", "Senha", "Email", "Nome", "Ativo", "tipo" FROM "Usuario" WHERE "id" = %s',
                [usuario_id],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'email': row[3],
                'first_name': row[4],
                'is_active': row[5],
                'tipo': row[6],
            }

    @staticmethod
    def get_todos_usuarios():
        # Lista todos os usuários ordenados pelo nome.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "id", "Login", "Email", "Nome", "Ativo", "tipo" FROM "Usuario" ORDER BY "Nome"'
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'first_name': row[3],
                    'is_active': row[4],
                    'tipo': row[5],
                }
                for row in rows
            ]

    @staticmethod
    def get_todas_mesas():
        # Consulta todas as mesas para seleção nos formulários.
        with connection.cursor() as cursor:
            cursor.execute('SELECT "ID_Mesa", "Numero", "Status" FROM "Mesa" ORDER BY "Numero"')
            rows = cursor.fetchall()
            return [{'id': row[0], 'numero': row[1], 'status': row[2]} for row in rows]

    @staticmethod
    def get_mesa_por_id(mesa_id):
        # Busca uma mesa específica para montar telas de detalhe.
        with connection.cursor() as cursor:
            cursor.execute('SELECT "ID_Mesa", "Numero", "Status" FROM "Mesa" WHERE "ID_Mesa" = %s', [mesa_id])
            row = cursor.fetchone()
            if not row:
                return None
            return {'id': row[0], 'numero': row[1], 'status': row[2]}

    @staticmethod
    def get_mesa_por_numero(numero):
        # Busca uma mesa pelo número exibido ao usuário.
        with connection.cursor() as cursor:
            cursor.execute('SELECT "ID_Mesa", "Numero", "Status" FROM "Mesa" WHERE "Numero" = %s', [numero])
            row = cursor.fetchone()
            if not row:
                return None
            return {'id': row[0], 'numero': row[1], 'status': row[2]}

    @staticmethod
    def get_todas_categorias():
        # Lista categorias do cardápio para relacionar produtos.
        with connection.cursor() as cursor:
            cursor.execute('SELECT "Id_Categoria", "Descricao" FROM "Categoria" ORDER BY "Descricao"')
            rows = cursor.fetchall()
            return [{'id': row[0], 'descricao': row[1]} for row in rows]

    @staticmethod
    def get_todos_produtos():
        # Busca o catálogo completo de produtos para o painel de estoque.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Produto", "Nome", "Descricao", "Vlr_Produto", "Disponivel", "Qtde_Estoque", "Id_Categoria" FROM "Produto" ORDER BY "Nome"'
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'nome': row[1],
                    'descricao': row[2],
                    'preco': Decimal(str(row[3])),
                    'disponivel': row[4],
                    'quantidade_estoque': row[5],
                    'categoria_id': row[6],
                }
                for row in rows
            ]

    @staticmethod
    def get_produtos_disponiveis():
        # Busca apenas produtos disponíveis e com estoque para montar pedidos.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Produto", "Nome", "Descricao", "Vlr_Produto", "Disponivel", "Qtde_Estoque", "Id_Categoria" FROM "Produto" WHERE "Disponivel" = %s AND "Qtde_Estoque" > 0 ORDER BY "Nome"',
                ['S'],
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'nome': row[1],
                    'descricao': row[2],
                    'preco': Decimal(str(row[3])),
                    'disponivel': row[4],
                    'quantidade_estoque': row[5],
                    'categoria_id': row[6],
                }
                for row in rows
            ]

    @staticmethod
    def get_produto_por_id(produto_id):
        # Busca um produto específico para validar estoque e disponibilidade.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Produto", "Nome", "Descricao", "Vlr_Produto", "Disponivel", "Qtde_Estoque", "Id_Categoria" FROM "Produto" WHERE "ID_Produto" = %s',
                [produto_id],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'nome': row[1],
                'descricao': row[2],
                'preco': Decimal(str(row[3])),
                'disponivel': row[4],
                'quantidade_estoque': row[5],
                'categoria_id': row[6],
            }

    @staticmethod
    def update_estoque_produto(produto_id, nova_quantidade):
        # Atualiza estoque e já ajusta a disponibilidade quando o estoque zera.
        novo_disponivel = 'S' if nova_quantidade > 0 else 'N'
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE "Produto" SET "Qtde_Estoque" = %s, "Disponivel" = %s WHERE "ID_Produto" = %s',
                [nova_quantidade, novo_disponivel, produto_id],
            )

    @staticmethod
    def toggle_disponibilidade_produto(produto_id):
        # Alterna manualmente a disponibilidade do produto (S <-> N).
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE "Produto" SET "Disponivel" = CASE WHEN "Disponivel" = %s THEN %s ELSE %s END WHERE "ID_Produto" = %s',
                ['S', 'N', 'S', produto_id],
            )

    @staticmethod
    def criar_produto(nome, descricao, preco, disponivel, qtde_estoque, categoria_id=None):
        # Insere um novo produto no cardápio e retorna o ID gerado.
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "Produto" ("Nome", "Descricao", "Vlr_Produto", "Disponivel", "Qtde_Estoque", "Id_Categoria") VALUES (%s, %s, %s, %s, %s, %s) RETURNING "ID_Produto"',
                [nome, descricao, preco, disponivel, qtde_estoque, categoria_id],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def atualizar_produto(produto_id, nome, descricao, preco, disponivel, qtde_estoque, categoria_id=None):
        # Atualiza todos os campos principais do produto no banco.
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE "Produto" SET "Nome" = %s, "Descricao" = %s, "Vlr_Produto" = %s, "Disponivel" = %s, "Qtde_Estoque" = %s, "Id_Categoria" = %s WHERE "ID_Produto" = %s',
                [nome, descricao, preco, disponivel, qtde_estoque, categoria_id, produto_id],
            )

    @staticmethod
    def deletar_produto(produto_id):
        # Remove o produto do cardápio, se não houver dependências bloqueando.
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM "Produto" WHERE "ID_Produto" = %s', [produto_id])

    @staticmethod
    def get_comandas_abertas():
        # Lista todas as comandas com status aberto para o painel geral.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Pedido", "ID_Mesa", "ID_Usuario", "Cliente", "DT_Pedido", "Qtde_Pessoas", "Status" FROM "Pedido" WHERE "Status" = %s ORDER BY "DT_Pedido" DESC, "ID_Pedido" DESC',
                ['A'],
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'mesa_id': row[1],
                    'usuario_id': row[2],
                    'nome_cliente': row[3],
                    'data_abertura': row[4],
                    'qtde_pessoas': row[5],
                    'status': row[6],
                }
                for row in rows
            ]

    @staticmethod
    def get_comanda_por_id(comanda_id):
        # Busca uma comanda específica para fechar, entregar ou detalhar.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Pedido", "ID_Mesa", "ID_Usuario", "Cliente", "DT_Pedido", "Qtde_Pessoas", "Status" FROM "Pedido" WHERE "ID_Pedido" = %s',
                [comanda_id],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'mesa_id': row[1],
                'usuario_id': row[2],
                'nome_cliente': row[3],
                'data_abertura': row[4],
                'qtde_pessoas': row[5],
                'status': row[6],
            }

    @staticmethod
    def get_comandas_aberta_mesa(mesa_id):
        # Lista todas as comandas abertas de uma mesa para a tela de gerenciamento.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Pedido", "ID_Mesa", "ID_Usuario", "Cliente", "DT_Pedido", "Qtde_Pessoas", "Status" FROM "Pedido" WHERE "ID_Mesa" = %s AND "Status" = %s ORDER BY "Cliente", "DT_Pedido"',
                [mesa_id, 'A'],
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'mesa_id': row[1],
                    'usuario_id': row[2],
                    'nome_cliente': row[3],
                    'data_abertura': row[4],
                    'qtde_pessoas': row[5],
                    'status': row[6],
                }
                for row in rows
            ]

    @staticmethod
    def get_comanda_aberta_por_mesa_cliente(mesa_id, nome_cliente):
        # Evita duplicar comanda aberta para o mesmo cliente na mesma mesa.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "ID_Pedido", "ID_Mesa", "ID_Usuario", "Cliente", "DT_Pedido", "Qtde_Pessoas", "Status" FROM "Pedido" WHERE "ID_Mesa" = %s AND LOWER("Cliente") = LOWER(%s) AND "Status" = %s LIMIT 1',
                [mesa_id, nome_cliente, 'A'],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'mesa_id': row[1],
                'usuario_id': row[2],
                'nome_cliente': row[3],
                'data_abertura': row[4],
                'qtde_pessoas': row[5],
                'status': row[6],
            }

    @staticmethod
    def criar_comanda(mesa_id, usuario_id, nome_cliente, qtde_pessoas=1):
        # Insere uma nova comanda aberta e retorna o ID criado.
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO "Pedido" ("ID_Mesa", "ID_Usuario", "Cliente", "DT_Pedido", "Qtde_Pessoas", "Status") VALUES (%s, %s, %s, %s, %s, %s) RETURNING "ID_Pedido"',
                [mesa_id, usuario_id, nome_cliente, datetime.now(), qtde_pessoas, 'A'],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def fechar_comanda(comanda_id):
        # Marca uma comanda como fechada/paga.
        with connection.cursor() as cursor:
            cursor.execute('UPDATE "Pedido" SET "Status" = %s WHERE "ID_Pedido" = %s', ['F', comanda_id])

    @staticmethod
    def fechar_comandas_cliente_mesa(mesa_id, nome_cliente):
        # Fecha todas as comandas abertas daquele cliente na mesma mesa.
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE "Pedido" SET "Status" = %s WHERE "ID_Mesa" = %s AND LOWER("Cliente") = LOWER(%s) AND "Status" = %s',
                ['F', mesa_id, nome_cliente, 'A'],
            )
            return cursor.rowcount

    @staticmethod
    def get_itens_comanda(comanda_id):
        # Busca itens da comanda com nome e preço do produto para montar a tela de detalhe.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT pp.id, pp."ID_Pedido", pp."ID_Produto", pp."Qtde_Pedido", pp."Vlr_Total_Pedido_Produto", pp."Observacao", pp."Status", p."Nome", p."Vlr_Produto" FROM "Pedido_Produto" pp JOIN "Produto" p ON pp."ID_Produto" = p."ID_Produto" WHERE pp."ID_Pedido" = %s ORDER BY pp.id',
                [comanda_id],
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'comanda_id': row[1],
                    'produto_id': row[2],
                    'quantidade': row[3],
                    'vlr_total': Decimal(str(row[4])),
                    'observacao': row[5],
                    'status': row[6],
                    'nome_produto': row[7],
                    'preco_produto': Decimal(str(row[8])),
                }
                for row in rows
            ]

    @staticmethod
    def get_itens_nao_entregues_comanda(comanda_id):
        # Busca itens ainda não entregues para o painel da cozinha.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT pp.id, pp."ID_Pedido", pp."ID_Produto", pp."Qtde_Pedido", pp."Vlr_Total_Pedido_Produto", pp."Observacao", pp."Status", p."Nome", p."Vlr_Produto" FROM "Pedido_Produto" pp JOIN "Produto" p ON pp."ID_Produto" = p."ID_Produto" WHERE pp."ID_Pedido" = %s AND pp."Status" <> %s ORDER BY pp.id',
                [comanda_id, 'E'],
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'comanda_id': row[1],
                    'produto_id': row[2],
                    'quantidade': row[3],
                    'vlr_total': Decimal(str(row[4])),
                    'observacao': row[5],
                    'status': row[6],
                    'nome_produto': row[7],
                    'preco_produto': Decimal(str(row[8])),
                }
                for row in rows
            ]

    @staticmethod
    def criar_item_pedido(comanda_id, produto_id, quantidade, observacao=''):
        # Insere o item. Se já existir na comanda, soma a quantidade e recalcula o total.
        with connection.cursor() as cursor:
            cursor.execute('SELECT "Vlr_Produto" FROM "Produto" WHERE "ID_Produto" = %s', [produto_id])
            row = cursor.fetchone()
            if row is None:
                return None
            preco = Decimal(str(row[0]))
            vlr_total = preco * quantidade
            cursor.execute(
                'INSERT INTO "Pedido_Produto" ("ID_Pedido", "ID_Produto", "Qtde_Pedido", "Vlr_Total_Pedido_Produto", "Observacao", "Status") VALUES (%s, %s, %s, %s, %s, %s) RETURNING id',
                [comanda_id, produto_id, quantidade, vlr_total, observacao, 'A'],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def marcar_item_pronto(item_id):
        # Atualiza o status do item para pronto.
        with connection.cursor() as cursor:
            cursor.execute('UPDATE "Pedido_Produto" SET "Status" = %s WHERE id = %s', ['P', item_id])

    @staticmethod
    def marcar_itens_entregues(comanda_id):
        # Marca todos os itens prontos de uma comanda como entregues.
        with connection.cursor() as cursor:
            cursor.execute('UPDATE "Pedido_Produto" SET "Status" = %s WHERE "ID_Pedido" = %s AND "Status" = %s', ['E', comanda_id, 'P'])

    @staticmethod
    def get_item_pedido(item_id):
        # Busca um item específico com nome do produto para exibição na cozinha.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT pp.id, pp."ID_Pedido", pp."ID_Produto", pp."Qtde_Pedido", pp."Vlr_Total_Pedido_Produto", pp."Observacao", pp."Status", p."Nome", p."Vlr_Produto" FROM "Pedido_Produto" pp JOIN "Produto" p ON pp."ID_Produto" = p."ID_Produto" WHERE pp.id = %s',
                [item_id],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'comanda_id': row[1],
                'produto_id': row[2],
                'quantidade': row[3],
                'vlr_total': Decimal(str(row[4])),
                'observacao': row[5],
                'status': row[6],
                'nome_produto': row[7],
                'preco_produto': Decimal(str(row[8])),
            }

    @staticmethod
    def get_comandas_abertas_com_mesas():
        # Busca comandas abertas já com o número da mesa para mostrar na home.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT p."ID_Pedido", p."ID_Mesa", p."Cliente", m."Numero", m."Status" FROM "Pedido" p JOIN "Mesa" m ON p."ID_Mesa" = m."ID_Mesa" WHERE p."Status" = %s ORDER BY m."Numero", p."Cliente"',
                ['A'],
            )
            rows = cursor.fetchall()
            return [
                {
                    'comanda_id': row[0],
                    'mesa_id': row[1],
                    'nome_cliente': row[2],
                    'numero_mesa': row[3],
                    'status_mesa': row[4],
                }
                for row in rows
            ]

    @staticmethod
    def contar_comandas_abertas_mesa(mesa_id):
        # Conta quantas comandas abertas ainda existem para uma mesa.
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM "Pedido" WHERE "ID_Mesa" = %s AND "Status" = %s', [mesa_id, 'A'])
            return cursor.fetchone()[0]

    @staticmethod
    def get_painel_cozinha():
        # Query agregada para o painel da cozinha.
        # Retorna comanda, mesa, cliente, data, total de itens e contagem por status.
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT p."ID_Pedido", p."ID_Mesa", p."Cliente", p."DT_Pedido", m."Numero", COUNT(DISTINCT pp.id) AS total_itens, SUM(CASE WHEN pp."Status" = %s THEN 1 ELSE 0 END) AS itens_abertos, SUM(CASE WHEN pp."Status" = %s THEN 1 ELSE 0 END) AS itens_prontos FROM "Pedido" p JOIN "Mesa" m ON p."ID_Mesa" = m."ID_Mesa" LEFT JOIN "Pedido_Produto" pp ON p."ID_Pedido" = pp."ID_Pedido" AND pp."Status" <> %s WHERE p."Status" = %s GROUP BY p."ID_Pedido", p."ID_Mesa", p."Cliente", p."DT_Pedido", m."Numero" ORDER BY p."DT_Pedido" ASC',
                ['A', 'P', 'E', 'A'],
            )
            rows = cursor.fetchall()
            return [
                {
                    'comanda_id': row[0],
                    'mesa_id': row[1],
                    'nome_cliente': row[2],
                    'data_abertura': row[3],
                    'numero_mesa': row[4],
                    'total_itens': row[5],
                    'itens_abertos': row[6],
                    'itens_prontos': row[7],
                }
                for row in rows
            ]
