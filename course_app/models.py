from django.contrib.postgres.fields import ArrayField
from django.db import models
from treebeard.mp_tree import MP_Node
from django.utils.translation import gettext_lazy as _

from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from course_app.validators import max_upload_image_validator


class Category(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    category_name = models.CharField(max_length=100, db_index=True)
    node_order_by = ("category_name",)
    image = models.ImageField(upload_to="category_images/%Y/%m/%d", null=True, blank=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name

    @property
    def sub_category_name(self):
        return self.get_children().values("id", "category_name")

    class Meta:
        managed = False
        db_table = 'category'


class Course(CreateMixin, UpdateMixin, SoftDeleteMixin):
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100, db_index=True)
    course_description = models.TextField()
    description_slug = models.SlugField(blank=True, null=True, allow_unicode=True)
    course_image = models.ImageField(upload_to="course_image/%Y/%m/%d", validators=[max_upload_image_validator],
                                     help_text=_("حداکثر اندازه عکس 1 مگابایت هست"), blank=True)
    is_publish = models.BooleanField(default=True)
    project_counter = models.PositiveSmallIntegerField(null=True)
    # price = models.FloatField(help_text=_("قیمت دوره"), blank=True, null=True)
    is_free = models.BooleanField(default=False)
    facilities = ArrayField(models.CharField(max_length=30), blank=True, null=True)
    course_level = models.CharField(max_length=13, null=True, blank=True)
    time_course = models.CharField(max_length=10, help_text="مدت زمان دوره", blank=True)
    course_age = models.CharField(max_length=30, help_text="بازه سنی دوره", blank=True)
    order_number = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.course_name

    class Meta:
        managed = False
        db_table = 'course'
        ordering = ("-id",)
        constraints = (
            models.UniqueConstraint(fields=("id", "order_number"), name="unique_order_per_course_id"),
        )