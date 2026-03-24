from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from common.util import get_multiplier_kg


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_superuser(self, email, password, **extra_fields):
        if password is None:
            raise TypeError("provide password please")
        user = self.model(email=email, password=password)
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()


class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        null=True,
        blank=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    mfa_hash = models.CharField(max_length = 50, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


# Create your models here.


class RawMaterials(models.Model):
    rm_name = models.CharField(max_length=30, unique=True)
    price = models.IntegerField()
    manufacturer = models.CharField(max_length=30)
    supplier = models.CharField(max_length=30)
    compliance = models.CharField(max_length=30)
    notes = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=30, blank=True)

    __original_price = None

    def __init__(self, *args, **kwargs):
        super(RawMaterials, self).__init__(*args, **kwargs)
        self.__original_price = self.price

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.price != self.__original_price:
            rm_price_delta = self.price - self.__original_price
            rm_comp_list = Compositions.objects.filter(rm=self)
            for rm_comp in rm_comp_list:
                try:
                    total_weight = 0
                    fg = FinishedGoods.objects.get(pk=rm_comp.fg_id)
                    fg_comp_list = Compositions.objects.filter(fg=rm_comp.fg_id)

                    for fg_comp in fg_comp_list:
                        multiplier = get_multiplier_kg(fg_comp.unit)
                        total_weight = (fg_comp.quantity * multiplier) + total_weight

                    comp_multiplier = get_multiplier_kg(rm_comp.unit)
                    comp_weight = rm_comp.quantity * comp_multiplier
                    comp_proportion = comp_weight/total_weight
                    fg_price_delta = rm_price_delta * comp_proportion
                    fg.price = fg.price + fg_price_delta
                    fg.save()

                except FinishedGoods.DoesNotExist:
                    pass

        super(RawMaterials, self).save()


class FinishedGoods(models.Model):
    fg_name = models.CharField(max_length=30, unique=True)
    customer = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    price = models.FloatField()
    date = models.DateField()
    notes = models.CharField(max_length=200, blank=True)
    composition_exists = models.BooleanField(default=False)


class Compositions(models.Model):
    class WeightUnit(models.TextChoices):
        KG = 'KG'
        GM = 'GM'
        MG = 'MG'

    fg = models.ForeignKey(FinishedGoods, db_column='fg', on_delete=models.CASCADE)
    rm = models.ForeignKey(RawMaterials, db_column='rm', on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(
        max_length=2,
        choices=WeightUnit.choices,
        default=WeightUnit.KG
    )


class JobCards(models.Model):
    date = models.DateTimeField()
    issued_to = models.CharField(max_length=30)
    machine_no = models.CharField(max_length=10)
    fg = models.ForeignKey(FinishedGoods, db_column='fg', on_delete=models.CASCADE)
    total_weight = models.FloatField()
    no_of_batches = models.IntegerField()

