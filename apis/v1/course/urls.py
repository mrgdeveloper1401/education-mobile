from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
from rest_framework.urls import path
from . import views


app_name = "v1_course"

router = SimpleRouter()

router.register("lesson_course", views.ListLessonClassView, basename="lesson_course")
router.register("student_exam_attempts", views.StudentExamAttemptView, basename='student_exam_attempts')
router.register("category", views.ListDetailCategoryView, basename="category")
router.register("upload_attachment", views.UploadAttachmentView, basename="upload_attachment")

lesson_course_router = NestedSimpleRouter(router, r"lesson_course", lookup="lesson_course")
lesson_course_router.register("sections", views.SectionLessonCourseViewSet, basename="sections")

category_router = NestedSimpleRouter(router, r"category", lookup="category")
category_router.register("category_comment", views.CategoryCommentViewSet, basename="category_comment")

urlpatterns = [
    path('exam/<int:exam_pk>/questions/', views.QuestionView.as_view(), name='exam_question'),
    path(
        'exam/<int:exam_pk>/questions/<int:pk>/student_answer/',
        views.StudentAnswerViewSet.as_view(
            {"get": "list", 'post': "create"}
        ),
        name='student-answer-list'
    ),
    path("exam_done/<int:exam_pk>/", views.ExamDoneView.as_view(), name="exam_done"),
] + router.urls + lesson_course_router.urls + category_router.urls
