from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from adrf.serializers import ModelSerializer as AdrfModelSerializer


from auth_app.models import Student
from course_app.models import Category, LessonCourse, Section, SectionVideo, CategoryComment
from exam_app.models import SectionExam, Question, Choice, StudentExamAttempt, StudentAnswer


class ListCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
        )


class ListClassSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.course_name", read_only=True)
    project_counter = serializers.CharField(source="course.project_counter", read_only=True)
    course_image = serializers.SerializerMethodField()
    course_category = serializers.CharField(source="course.category.course_category", read_only=True)

    class Meta:
        model = LessonCourse
        fields = (
            "id",
            "class_name",
            "course_category",
            "course_name",
            "project_counter",
            "course_image",
            "progress",
        )

    @extend_schema_field(serializers.URLField())
    def get_course_image(self, obj):
        return obj.course.course_image.course_image if obj.course.course_image else None


class SectionExamSerializer(AdrfModelSerializer):
    class Meta:
        model = SectionExam
        fields = (
            "id",
            "title",
            "description",
            "exam_type",
            'total_score',
            "passing_score",
            # "time_limit"
        )


class SectionLessonCourseSerializer(serializers.ModelSerializer):
    has_access = serializers.SerializerMethodField()
    section_image = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "section_image",
            "is_last_section",
            "description",
            "has_access",
        )

    @extend_schema_field(serializers.BooleanField())
    def get_has_access(self, obj):
        return obj.has_access

    @extend_schema_field(serializers.URLField())
    def get_section_image(self, obj):
        return obj.cover_image.course_image if obj.cover_image else None


class SectionVideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = SectionVideo
        fields = ("id", "title", "video_url")

    @extend_schema_field(serializers.URLField())
    def get_video_url(self, obj):
        return obj.video.get_video_file_url if obj.video else None


class DetailSectionLessonCourseSerializer(serializers.ModelSerializer):
    section_videos = SectionVideoSerializer(many=True, read_only=True)
    has_access = serializers.SerializerMethodField()
    cover_image_url = serializers.SerializerMethodField()
    section_exams = SectionExamSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = (
            "id",
            "title",
            "description",
            "cover_image_url",
            "is_last_section",
            "section_videos",
            "section_exams",
            "has_access",
        )

    @extend_schema_field(serializers.BooleanField())
    def get_has_access(self, obj):
        return obj.has_access

    @extend_schema_field(serializers.URLField())
    def get_cover_image_url(self ,obj):
        return obj.cover_image.course_image if obj.cover_image else None


class ChoiceSerializer(AdrfModelSerializer):
    class Meta:
        model = Choice
        fields = (
            "id",
            "choice_text"
        )


class ExamQuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "question_type",
            "score",
            "display_order",
            "choices"
        )


class CreateStudentExamAttemptSerializer(serializers.Serializer):
    exam = serializers.PrimaryKeyRelatedField(
        queryset=SectionExam.objects.filter(is_active=True).only("id"),
    )

    def create(self, validated_data):
        user_id = self.context["request"].user.id
        get_student = Student.objects.filter(is_active=True, user_id=user_id).only("id")
        return StudentExamAttempt.objects.create(
            student_id=get_student.first().id,
            exam_id=validated_data["exam"].id,
        )


class ListDetailStudentExamAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamAttempt
        fields = (
            "id",
            "exam",
            "started_at",
            "submitted_at",
            "total_score",
            "obtained_score",
            "is_passed",
            "status"
        )


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = (
            "id",
            "student",
            "attempt",
            "question",
            "selected_choices",
        )
        extra_kwargs = {
            "question": {"read_only": True},
            "attempt": {'read_only': True},
            "student": {'read_only': True},
        }

    def create(self, validated_data):
        exam_id = self.context['exam_pk']
        question_id = self.context['question_pk']
        user_id = self.context['request'].user.id

        get_student = Student.objects.filter(user_id=user_id, is_active=True).only("id").first()
        get_student_exam_attempt = StudentExamAttempt.objects.filter(
            student_id=get_student.id,
            is_active=True,
            exam_id=exam_id
        ).only("id").last()

        selected_choices = validated_data.pop("selected_choices", [])
        student_answer =  StudentAnswer.objects.create(
            question_id=question_id,
            student_id=get_student.id,
            attempt_id=get_student_exam_attempt.id,
            **validated_data
        )
        student_answer.selected_choices.set(selected_choices)
        return student_answer


class ListDetailCategoryCommentSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = CategoryComment
        exclude = ("is_active", "category")

    @extend_schema_field(serializers.BooleanField())
    def get_is_owner(self, obj):
        user_id = self.context['request'].user.id
        return True if obj.user_id == user_id else False


class CategoryCommentSerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)

    class Meta:
        model = CategoryComment
        fields = (
            "id",
            "comment_body",
            "is_pined",
            "parent"
        )

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        category_id = self.context['category_pk']
        parent = validated_data.pop("parent")

        if parent:
            get_obj = get_object_or_404(CategoryComment, pk=parent)
            comment = CategoryComment.add_child(user_id=user_id, category_id=category_id, pk=parent, **validated_data)
            return  comment
        else:
            comment = CategoryComment.add_child(user_id=user_id, category_id=category_id, **validated_data)
            return comment


class UpdateCategoryCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryComment
        fields = ("comment_body", "is_pined")
