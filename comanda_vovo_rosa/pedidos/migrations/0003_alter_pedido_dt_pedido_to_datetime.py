from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_alter_usuario_managers_alter_usuario_email_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "Pedido" '
                'ALTER COLUMN "DT_Pedido" TYPE timestamp with time zone '
                'USING "DT_Pedido"::timestamp with time zone; '
                'ALTER TABLE "Pedido" '
                'ALTER COLUMN "DT_Pedido" SET DEFAULT now();'
            ),
            reverse_sql=(
                'ALTER TABLE "Pedido" '
                'ALTER COLUMN "DT_Pedido" TYPE date '
                'USING "DT_Pedido"::date; '
                'ALTER TABLE "Pedido" '
                'ALTER COLUMN "DT_Pedido" SET DEFAULT CURRENT_DATE;'
            ),
        ),
    ]
