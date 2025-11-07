from rest_framework.urls import path
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
from . import views


app_name = "v1_course"
router = SimpleRouter()
router.register("lesson_course", views.ListLessonClassView, basename="lesson_course")

lesson_course_router = NestedSimpleRouter(router, r"lesson_course", lookup="lesson_course")
lesson_course_router.register("sections", views.SectionLessonCourseViewSet, basename="sections")

urlpatterns = [
    path("list_category/", views.ListCategoryView.as_view(), name="list_category"),
] + router.urls + lesson_course_router.urls
