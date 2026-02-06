from django.apps import apps
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user_object(self, mobile_phone, email, password, **extra_fields):
        if not mobile_phone:
            raise ValueError("The given mobile_phone mobile_phone be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        # username = GlobalUserModel.normalize_username(username)
        user = self.model(mobile_phone=mobile_phone, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, mobile_phone, email, password, **extra_fields):
        """
        Create and save a user with the given mobile_phone, email, and password.
        """
        user = self._create_user_object(mobile_phone, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, mobile_phone, email, password, **extra_fields):
        """See _create_user()"""
        user = self._create_user_object(mobile_phone, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, mobile_phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(mobile_phone, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, mobile_phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(mobile_phone, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, mobile_phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(mobile_phone, email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(
        self, mobile_phone, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(mobile_phone, email, password, **extra_fields)

    acreate_superuser.alters_data = True

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
