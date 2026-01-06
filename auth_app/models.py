from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from auth_app.managers import CustomUserManager
from auth_app.validators import NationCodeRegexValidator
from core_app.models import UpdateMixin, CreateMixin, ActiveMixin


# Create your models here.
class User(AbstractBaseUser, UpdateMixin, CreateMixin, PermissionsMixin, ActiveMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=15, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("email address"), null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    image = models.ForeignKey(
        "core_app.Photo",
        blank=True,
        null=True,
        related_name="user_images",
        on_delete=models.PROTECT,
    )
    state = models.ForeignKey(
        "State",
        on_delete=models.PROTECT,
        related_name='user_state',
        verbose_name=_("استان"),
        blank=True,
        null=True)

    city = models.ForeignKey(
        "City",
        on_delete=models.PROTECT,
        related_name='user_city',
        blank=True,
        null=True
    )
    nation_code = models.CharField(
        _("کد ملی"),
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=(NationCodeRegexValidator(),)
    )
    address = models.TextField(_("ادرس"), blank=True, null=True)
    birth_date = models.DateField(_("تاریخ نولد"), blank=True, null=True)
    bio = models.CharField(max_length=500, blank=True, null=True)
    is_coach = models.BooleanField(default=False)

    class Gender(models.TextChoices):
        MALE = 'male', _("پسر")
        FEMALE = 'Female', _("دختر")

    gender = models.CharField(
        _("gender"),
        max_length=6,
        choices=Gender.choices,
        blank=True,
        null=True
    )
    school = models.CharField(
        _("نام مدرسه"),
        max_length=30,
        blank=True,
        null=True
    )
    groups = None
    user_permissions = None

    objects = CustomUserManager()

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}' if self.first_name and self.last_name else None

    @property
    def is_student(self):
        return not self.is_coach

    def __str__(self):
        return self.mobile_phone

    USERNAME_FIELD = 'mobile_phone'
    REQUIRED_FIELDS = ('first_name', "last_name", "email")

    class Meta:
        ordering = ("id",)
        db_table = "users"


class State(ActiveMixin):
    state_name = models.CharField(_("استان"), max_length=30, unique=True)

    class Meta:
        db_table = "state"


class City(ActiveMixin):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="cities", verbose_name=_("استان"))
    city = models.CharField(_("شهر"), max_length=40, db_index=True)


    class Meta:
        db_table = "city"


class Coach(CreateMixin, UpdateMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='coach_profile',
    )
    coach_number = models.CharField(max_length=15, blank=True)

    @property
    def get_coach_name(self):
        return self.user.get_full_name

    @property
    def get_coach_phone(self):
        return self.user.mobile_phone

    class Meta:
        db_table = 'coach'


class Student(CreateMixin, UpdateMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='student_profile',
        limit_choices_to={"is_coach": False}
    )
    student_number = models.CharField(max_length=11)
    referral_code = models.CharField(max_length=30, blank=True)

    @property
    def student_name(self):
        return self.user.get_full_name

    @property
    def get_student_phone(self):
        return self.user.mobile_phone

    class Meta:
        db_table = 'student'
