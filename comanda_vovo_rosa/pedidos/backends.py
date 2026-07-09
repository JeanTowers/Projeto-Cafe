from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from .db import Database

UserModel = get_user_model()


def _montar_usuario(row):
    # Monta o objeto de usuário na mão a partir da linha que veio do SQL.
    # O hash da senha precisa ir junto porque o Django usa ele na sessão.
    user = UserModel(
        id=row['id'],
        username=row['username'],
        email=row['email'] or '',
        first_name=row['first_name'] or '',
        is_active=row['is_active'],
        tipo=row['tipo'],
    )
    user.password = row['password']
    return user


class SQLAuthBackend:
    """Autenticação via SQL bruto usando Database.get_usuario_por_login.

    Retorna uma instância do modelo de usuário caso as credenciais estejam corretas.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        row = Database.get_usuario_por_login(username)
        if not row:
            return None

        hashed = row.get('password')
        if not hashed:
            return None

        if check_password(password, hashed) and row.get('is_active', True):
            return _montar_usuario(row)

        return None

    def get_user(self, user_id):
        row = Database.get_usuario_por_id(user_id)
        if not row:
            return None
        return _montar_usuario(row)
