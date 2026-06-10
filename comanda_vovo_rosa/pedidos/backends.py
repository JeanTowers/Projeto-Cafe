from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from .db import Database

UserModel = get_user_model()


class SQLAuthBackend:
    """Autenticação via SQL bruto usando Database.get_usuario_por_login.

    Retorna uma instância do modelo de usuário caso as credenciais estejam corretas.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        db = Database()
        row = db.get_usuario_por_login(username)
        if not row:
            return None

        hashed = row.get('password')
        if not hashed:
            return None

        if check_password(password, hashed):
            try:
                # Retorna instância persistida se existir
                return UserModel.objects.get(pk=row['id'])
            except UserModel.DoesNotExist:
                # Cria instância não salva compatível com Django (não persiste)
                user = UserModel(pk=row['id'])
                user.username = row.get('username')
                user.email = row.get('email')
                user.first_name = row.get('first_name')
                user.is_active = row.get('is_active', True)
                return user

        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
