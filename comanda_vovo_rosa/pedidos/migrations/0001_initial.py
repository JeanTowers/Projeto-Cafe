from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(db_column='Id_Categoria', primary_key=True, serialize=False)),
                ('descricao', models.CharField(db_column='Descricao', max_length=50)),
            ],
            options={
                'db_table': 'Categoria',
                'ordering': ['descricao'],
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Mesa',
            fields=[
                ('id', models.AutoField(db_column='ID_Mesa', primary_key=True, serialize=False)),
                ('numero', models.IntegerField(db_column='Numero', unique=True)),
                ('status', models.CharField(choices=[('L', 'Livre'), ('O', 'Ocupada'), ('I', 'Inativa')], db_column='Status', default='L', max_length=1)),
            ],
            options={
                'db_table': 'Mesa',
                'ordering': ['numero'],
                'verbose_name': 'Mesa',
                'verbose_name_plural': 'Mesas',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('password', models.CharField(db_column='Senha', max_length=128, verbose_name='senha')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(db_column='Login', max_length=150, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, db_column='Nome', max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, db_column='Email', max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(db_column='Ativo', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('tipo', models.CharField(choices=[('GARCOM', 'Garçom/Atendente'), ('COZINHA', 'Cozinha'), ('ADMIN', 'Administrador')], default='GARCOM', max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='usuario_set', related_query_name='usuario', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='usuario_set', related_query_name='usuario', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'Usuario',
                'verbose_name': 'Usuário',
                'verbose_name_plural': 'Usuários',
            },
        ),
        migrations.CreateModel(
            name='ItemCardapio',
            fields=[
                ('id', models.AutoField(db_column='ID_Produto', primary_key=True, serialize=False)),
                ('nome', models.CharField(db_column='Nome', max_length=100)),
                ('descricao', models.TextField(blank=True, db_column='Descricao', default='')),
                ('preco', models.DecimalField(db_column='Vlr_Produto', decimal_places=2, max_digits=10)),
                ('disponivel', models.CharField(choices=[('S', 'Sim'), ('N', 'Não')], db_column='Disponivel', default='S', max_length=1)),
                ('quantidade_estoque', models.IntegerField(db_column='Qtde_Estoque', default=0)),
                ('categoria', models.ForeignKey(blank=True, db_column='Id_Categoria', null=True, on_delete=django.db.models.deletion.SET_NULL, to='pedidos.categoria')),
            ],
            options={
                'db_table': 'Produto',
                'ordering': ['nome'],
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
            },
        ),
        migrations.CreateModel(
            name='Comanda',
            fields=[
                ('id', models.AutoField(db_column='ID_Pedido', primary_key=True, serialize=False)),
                ('nome_cliente', models.CharField(db_column='Cliente', max_length=100)),
                ('data_abertura', models.DateTimeField(db_column='DT_Pedido', default=django.utils.timezone.now)),
                ('qtde_pessoas', models.IntegerField(db_column='Qtde_Pessoas', default=1)),
                ('status', models.CharField(choices=[('A', 'Aberto'), ('F', 'Fechado')], db_column='Status', default='A', max_length=1)),
                ('mesa', models.ForeignKey(db_column='ID_Mesa', on_delete=django.db.models.deletion.PROTECT, to='pedidos.mesa')),
                ('usuario', models.ForeignKey(db_column='ID_Usuario', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Pedido',
                'ordering': ['-data_abertura', '-id'],
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
            },
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantidade', models.IntegerField(db_column='Qtde_Pedido')),
                ('vlr_total_pedido_produto', models.DecimalField(db_column='Vlr_Total_Pedido_Produto', decimal_places=2, default=0, max_digits=7)),
                ('observacao', models.CharField(blank=True, db_column='Observacao', default='', max_length=100)),
                ('status', models.CharField(choices=[('A', 'Aberto'), ('P', 'Pronto'), ('E', 'Entregue')], db_column='Status', default='A', max_length=1)),
                ('comanda', models.ForeignKey(db_column='ID_Pedido', on_delete=django.db.models.deletion.CASCADE, to='pedidos.comanda')),
                ('item', models.ForeignKey(db_column='ID_Produto', on_delete=django.db.models.deletion.PROTECT, to='pedidos.itemcardapio')),
            ],
            options={
                'db_table': 'Pedido_Produto',
                'ordering': ['id'],
                'verbose_name': 'Item do Pedido',
                'verbose_name_plural': 'Itens do Pedido',
            },
        ),
        migrations.AddConstraint(
            model_name='itempedido',
            constraint=models.UniqueConstraint(fields=('comanda', 'item'), name='pedido_produto_unico_por_pedido_e_item'),
        ),
    ]
