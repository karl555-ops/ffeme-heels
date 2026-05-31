import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_tienda', '0004_perfilusuario'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('mensaje', models.TextField()),
                ('tipo', models.CharField(
                    choices=[('pedido', 'Pedido'), ('info', 'Información'), ('promo', 'Promoción')],
                    default='info',
                    max_length=20,
                )),
                ('leida', models.BooleanField(default=False)),
                ('creada_en', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notificaciones',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-creada_en'],
            },
        ),
    ]
