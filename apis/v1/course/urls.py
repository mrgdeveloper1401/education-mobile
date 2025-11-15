from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
from rest_framework.urls import path
from . import views


app_name = "v1_course"
router = SimpleRouter()
router.register("lesson_course", views.ListLessonClassView, basename="lesson_course")
router.register("student_exam_attempts", views.StudentExamAttemptView, basename='student_exam_attempts')

lesson_course_router = NestedSimpleRouter(router, r"lesson_course", lookup="lesson_course")
lesson_course_router.register("sections", views.SectionLessonCourseViewSet, basename="sections")

urlpatterns = [
    # path("list_category/", views.ListCategoryView.as_view(), name="list_category"),
    path('exam/<int:exam_pk>/questions/', views.QuestionView.as_view(), name='exam_question'),
    path(
        'exam/<int:exam_pk>/questions/<int:pk>/student_answer/',
        views.StudentAnswerViewSet.as_view(
            {"get": "list", 'post': "create"}
        ),
        name='student-answer-list'
    ),
] + router.urls + lesson_course_router.urls
