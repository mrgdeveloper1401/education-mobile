from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from django.db.models import JSONField
from .models import SectionExam, Question, StudentExamAttempt, StudentAnswer, ExamGrading, Choice


@admin.register(SectionExam)
class SectionExamAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    raw_id_fields = ('section',)
    search_help_text = _("برای جست و جو میتوانید از نام ازمون استفاده کنید")
    list_editable = ("is_active", "passing_score", "time_limit")
    list_display = (
        "title",
        'id',
        "section_id",
        "exam_type",
        "total_score",
        "passing_score",
        "time_limit",
        "created_at",
        "is_active",
    )
    list_filter = ("is_active", "created_at")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
    list_display = (
        "get_exam_title",
        "exam_id",
        "get_exam_section_id",
        "id",
        "question_type",
        "score",
        "display_order",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at", "question_type")
    search_fields = ("exam__title",)
    search_help_text = _("برای جست و جو میتوانید از عنوان ازمون استفاده کیند")
    raw_id_fields = ("exam",)
    readonly_fields = ("display_order", "created_at")

    def get_exam_title(self, obj):
        return obj.exam.title

    def get_exam_section_id(self, obj):
        return obj.exam.section_id

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("exam").only(
            "exam__title",
            "exam__section_id",
            "question_type",
            "score",
            "display_order",
            "is_active",
            "created_at",
            "explanation",
            "question_text"
        )


@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    search_fields = ("student__user__mobile_phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید")
    list_display = (
        "exam_id",
        "id",
        "student_id",
        "get_student_phone",
        "is_active",
        "started_at",
        "submitted_at",
        "obtained_score",
        "is_passed",
        "status"
    )
    list_editable = ("is_active",)
    raw_id_fields = ("exam", "student")
    list_display_links = ("id", "student_id", "exam_id", "get_student_phone")
    def get_student_phone(self, obj):
        return obj.student.get_student_phone

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("student__user").only(
            "student__user__mobile_phone",
            "is_active",
            "started_at",
            "submitted_at",
            "obtained_score",
            "is_passed",
            "status",
            "created_at",
            "exam_id",
            "total_score"
        )


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "question_id", 'get_question_title', 'is_correct', "choice_text", "created_at")
    list_filter = ('is_active', 'is_correct', "created_at")
    raw_id_fields = ("question",)
    ordering = ('-id',)
    list_display_links = ("id", "question_id", "get_question_title")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("question").only(
            "question__question_text",
            "is_correct",
            "choice_text",
            "created_at",
            "is_active",
        )

    def get_question_title(self, obj):
        return obj.question.question_text


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", 'attempt_id', 'question_id', "student_id", 'score', 'is_correct', 'graded_at')
    list_filter = ('is_correct', "is_active")
    ordering = ("-id",)
    raw_id_fields = ("attempt", "question", "student")
    filter_horizontal = ("selected_choices",)
    list_display_links = ("id", "attempt_id", "question_id", "score")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "attempt_id",
            "question_id",
            "score",
            "is_correct",
            "graded_at",
            "is_active",
            "created_at",
            "updated_at",
            "teacher_feedback",
            "student_id"
        )


@admin.register(ExamGrading)
class ExamGradingAdmin(admin.ModelAdmin):
    list_display = ('exam_id', 'student_id', "id", 'total_score', 'obtained_score', 'grade')
    list_filter = ("is_active",)
    ordering = ("-id",)
    raw_id_fields = ("exam", "student")
    list_display_links = ("exam_id", "student_id", "id", "total_score")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "exam_id",
            "student_id",
            "is_active",
            "created_at",
            "updated_at",
            "total_score",
            "obtained_score",
            "grade",
            "feedback"
        )
