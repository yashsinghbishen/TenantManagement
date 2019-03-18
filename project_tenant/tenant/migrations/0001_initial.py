# Generated by Django 2.1.5 on 2019-03-18 10:16

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0010_auto_20190202_0531'),
    ]

    operations = [
        migrations.CreateModel(
            name='TblAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('ag_contact', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must\n                              be entered in the format: \n                            '+999999999'. Up to 13 digits\n                             allowed.", regex='^\\+?1?\\d{10,13}$')])),
                ('ag_local_address', models.CharField(max_length=255)),
                ('ag_permanent_address', models.CharField(max_length=255)),
                ('ag_profile_image', models.ImageField(blank=True, upload_to='agents/profiles')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Agent Details',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TblAgentAllocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('al_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Agent Allocation Details',
            },
        ),
        migrations.CreateModel(
            name='TblMasterProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msp_name', models.CharField(default='My Property', max_length=100)),
                ('msp_address', models.CharField(default='My Property', max_length=255)),
                ('msp_description', models.CharField(max_length=255, null=True)),
                ('msp_is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Master Properties',
            },
        ),
        migrations.CreateModel(
            name='TblMasterPropertyClone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cln_alias', models.CharField(max_length=100)),
                ('cln_is_master_clone', models.BooleanField(default=False)),
                ('cln_is_allocated', models.BooleanField(default=False)),
                ('cln_is_active', models.BooleanField(default=True)),
                ('cln_master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblMasterProperty')),
            ],
        ),
        migrations.CreateModel(
            name='TblProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pr_address', models.CharField(max_length=255)),
                ('pr_rent', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pr_deposite', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pr_description', models.CharField(max_length=255, null=True)),
                ('pr_is_allocated', models.BooleanField(default=False)),
                ('pr_is_active', models.BooleanField(default=True)),
                ('pr_master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblMasterPropertyClone')),
            ],
            options={
                'verbose_name_plural': 'All  Properties',
            },
        ),
        migrations.CreateModel(
            name='TblPropertyAllocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pa_agreement_date', models.DateField(null=True)),
                ('pa_agreement_end_date', models.DateField(null=True)),
                ('pa_acceptance_letter', models.ImageField(upload_to='rent/acceptance_latter')),
                ('pa_tenancy_agreement', models.ImageField(upload_to='rent/tenancy/agreement')),
                ('pa_final_rent', models.FloatField(max_length=10, null=True)),
                ('pa_is_allocated', models.BooleanField(default=False)),
                ('pa_property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblProperty')),
            ],
            options={
                'verbose_name_plural': 'Property Allocation Details',
            },
        ),
        migrations.CreateModel(
            name='TblRentCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rc_recipt_no', models.IntegerField()),
                ('rc_month', models.IntegerField(default=1)),
                ('rc_year', models.ImageField(max_length=4, upload_to='')),
                ('rc_pay_off_date', models.DateField()),
                ('rc_allocation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblPropertyAllocation')),
            ],
            options={
                'verbose_name_plural': 'Rent Collection Details',
            },
        ),
        migrations.CreateModel(
            name='TblTenant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tn_name', models.CharField(max_length=25)),
                ('tn_contact', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must\n                              be entered in the format: \n                            '+999999999'. Up to 13 digits\n                             allowed.", regex='^\\+?1?\\d{10,13}$')])),
                ('tn_permanent_address', models.CharField(max_length=255)),
                ('tn_profile', models.ImageField(upload_to='tenant/profiles')),
                ('tn_document_description', models.CharField(max_length=255, null=True)),
                ('tn_document', models.ImageField(upload_to='tenant/documents')),
                ('tn_reference_name', models.CharField(max_length=25)),
                ('tn_reference_address', models.CharField(max_length=255)),
                ('tn_status', models.IntegerField(default=1)),
                ('tn_joining_date', models.DateField()),
                ('tn_is_active', models.BooleanField(default=True)),
                ('tn_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Tenant Datails',
            },
        ),
        migrations.CreateModel(
            name='TblVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vs_date', models.DateField()),
                ('vs_intrest_status', models.IntegerField(default=1)),
                ('vs_property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblProperty')),
                ('vs_tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblTenant')),
            ],
            options={
                'verbose_name_plural': 'Visit Details',
            },
        ),
        migrations.AddField(
            model_name='tblpropertyallocation',
            name='pa_tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblTenant'),
        ),
        migrations.AddField(
            model_name='tblagentallocation',
            name='al_master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenant.TblMasterPropertyClone'),
        ),
    ]
