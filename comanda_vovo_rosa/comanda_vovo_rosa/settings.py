"""
====================================================
SETTINGS.PY - Configurações Centrais do Projeto
====================================================

Este arquivo contém TODAS as configurações do sistema Django.

O QUE ESTÁ CONFIGURADO AQUI:
- Banco de dados (SQLite)
- Apps instalados (pedidos, admin, auth, etc.)
- Middleware (segurança, sessões, autenticação)
- Templates (HTML)
- Arquivos estáticos (CSS, JavaScript, imagens)
- Configurações de login/logout
- Segurança (SECRET_KEY, DEBUG, etc.)

IMPORTANTE:
- SECRET_KEY: Usado para criptografia (NUNCA compartilhe em produção!)
- DEBUG = True: Mostra erros detalhados (apenas em desenvolvimento!)
- INSTALLED_APPS: Lista de apps que o Django carrega
- MIDDLEWARE: Camada de segurança e processamento de requisições

Documentação oficial:
https://docs.djangoproject.com/en/5.2/topics/settings/
"""

from pathlib import Path

# ============================================
# CONFIGURAÇÃO DE DIRETÓRIOS
# ============================================
# BASE_DIR é o caminho raiz do projeto
# Usado para construir outros caminhos (ex: banco de dados, templates)
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================================

# SECRET_KEY: Chave secreta usada para:
# - Criptografar senhas
# - Assinar cookies de sessão
# - Gerar tokens CSRF (proteção contra ataques)
# ⚠️ ATENÇÃO: Em produção, esta chave deve ser mantida em segredo!
SECRET_KEY = 'django-insecure-$1d%13-ad#h5mhavpl9n7at^+@26u#pjy2%rnar&t^2=n&eeus'

# DEBUG: Define se o sistema mostra erros detalhados
# True = Mostra mensagens de erro completas (útil durante desenvolvimento)
# False = Mostra apenas página genérica de erro (obrigatório em produção)
DEBUG = True

# ALLOWED_HOSTS: Lista de domínios permitidos para acessar o sistema
# [] = Apenas localhost/127.0.0.1 (desenvolvimento)
# Em produção, adicionar: ['meusite.com', 'www.meusite.com']
ALLOWED_HOSTS = []


# ============================================
# APLICAÇÕES INSTALADAS
# ============================================
# Lista de todos os apps que o Django carrega
# Apps do Django (admin, auth) + Nosso app (pedidos)

INSTALLED_APPS = [
    'django.contrib.admin',        # Painel administrativo (/admin/)
    'django.contrib.auth',         # Sistema de autenticação (login, usuários)
    'django.contrib.contenttypes', # Sistema de tipos de conteúdo
    'django.contrib.sessions',     # Gerenciamento de sessões (quem está logado)
    'django.contrib.messages',     # Sistema de mensagens (alertas de sucesso/erro)
    'django.contrib.staticfiles',  # Gerenciamento de arquivos CSS/JS/imagens
    'pedidos',                     # NOSSO APP - Sistema de comandas
]

# ============================================
# MIDDLEWARE - Camadas de Processamento
# ============================================
# Middleware processa TODAS as requisições antes de chegar nas views
# Ordem IMPORTA! Cada middleware é executado na ordem definida

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Configurações de segurança (HTTPS, etc.)
    'django.contrib.sessions.middleware.SessionMiddleware',    # Gerencia sessões (cookies)
    'django.middleware.common.CommonMiddleware',               # Funcionalidades comuns (URLs, etc.)
    'django.middleware.csrf.CsrfViewMiddleware',               # Proteção contra ataques CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Adiciona request.user (usuário logado)
    'django.contrib.messages.middleware.MessageMiddleware',    # Habilita sistema de mensagens
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Proteção contra clickjacking
]

ROOT_URLCONF = 'comanda_vovo_rosa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'comanda_vovo_rosa.wsgi.application'


# ============================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================
# SQLite: Banco de dados em arquivo único (db.sqlite3)
# Vantagens: Leve, não precisa instalação, perfeito para pequenos projetos
# Alternativas: PostgreSQL, MySQL, MariaDB (para projetos maiores)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Motor do banco (SQLite)
        'NAME': BASE_DIR / 'db.sqlite3',         # Arquivo do banco (db.sqlite3 na raiz)
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CONFIGURAÇÕES DE LOGIN E AUTENTICAÇÃO
# ============================================
# Define o comportamento do sistema de login

# LOGIN_URL: Para onde redireciona se tentar acessar página protegida sem login
LOGIN_URL = 'login'

# LOGIN_REDIRECT_URL: Para onde vai após login bem-sucedido
LOGIN_REDIRECT_URL = 'index'

# LOGOUT_REDIRECT_URL: Para onde vai após fazer logout
LOGOUT_REDIRECT_URL = 'login'
