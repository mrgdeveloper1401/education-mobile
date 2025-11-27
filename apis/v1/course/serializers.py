from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from adrf.serializers import ModelSerializer as AdrfModelSerializer

from auth_app.models import Student
from core_app.models import Attachment
from course_app.models import Category, LessonCourse, Section, SectionVideo, CategoryComment, CommentAttachment
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
            "explanation",
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
    passing_score = serializers.IntegerField(source="exam.passing_score", read_only=True)

    class Meta:
        model = StudentExamAttempt
        fields = (
            "id",
            "exam",
            "started_at",
            "submitted_at",
            "total_score",
            "obtained_score",
            "passing_score",
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
            "status"
        )
        extra_kwargs = {
            "question": {"read_only": True},
            "attempt": {'read_only': True},
            "student": {'read_only': True},
        }

    def validate(self, attrs):
        question_id = self.context['question_pk']
        exam_id = self.context['exam_pk']
        user_id = self.context['request'].user.id
        selected_choices = attrs.get('selected_choices', None)
        status = attrs.get("status", None)

        # check question is code or multiple_choice
        check_question = Question.objects.filter(id=question_id, is_active=True, exam_id=exam_id).only("id", "question_type")
        get_question_obj = check_question.first()
        if get_question_obj.question_type == "multiple_choice" and not selected_choices:
            raise PermissionDenied("فقط امکان ارسال سوال چهارگزینه ای رو دارید")
        if get_question_obj.question_type == "code" and not status:
            raise PermissionDenied("فقط امکان ارسال سوال کد رو دارید")

        # check duplicate student answer
        get_attempts = StudentExamAttempt.objects.filter(student__user_id=user_id, exam_id=exam_id).only("id").last()
        if not get_attempts:
            raise NotFound("ازمون پیدا نشد")
        student_answer = StudentAnswer.objects.filter(
            student__user_id=user_id,
            question_id=question_id,
            attempt_id=get_attempts.id
        ).only("id")
        if student_answer:
            raise PermissionDenied("شما قبلا جواب رو ارسال کردید نمیتوانید جواب جدیدی رو ایجاد کنید میتوانید ان را ویرایش کنید")

        attrs["question"] = get_question_obj
        return attrs

    def create(self, validated_data):
        exam_id = self.context['exam_pk']
        # question_id = self.context['question_pk']
        user_id = self.context['request'].user.id
        question = validated_data.pop("question")

        get_student = Student.objects.filter(user_id=user_id, is_active=True).only("id").first()
        get_student_exam_attempt = StudentExamAttempt.objects.filter(
            student_id=get_student.id,
            is_active=True,
            exam_id=exam_id
        ).only("id").last()

        selected_choices = validated_data.pop("selected_choices", [])
        student_answer =  StudentAnswer.objects.create(
            question_id=question.id,
            student_id=get_student.id,
            attempt_id=get_student_exam_attempt.id,
            **validated_data
        )
        student_answer.selected_choices.set(selected_choices)
        return student_answer


class CommentAttachmentSerializer(serializers.ModelSerializer):
    file_link = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()

    class Meta:
        model = CommentAttachment
        fields = (
            "id",
            "file_link",
            "file_type"
        )

    @extend_schema_field(serializers.URLField())
    def get_file_link(self, obj):
        return obj.file.attachment_url if obj.file else None

    @extend_schema_field(serializers.CharField())
    def get_file_type(self, obj):
        return obj.file.file_type


class ListDetailCategoryCommentSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    attachments = CommentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryComment
        exclude = ("is_active", "category")

    @extend_schema_field(serializers.CharField())
    def get_user_name(self, obj):
        return obj.user.get_full_name

    @extend_schema_field(serializers.BooleanField())
    def get_is_owner(self, obj):
        user_id = self.context['request'].user.id
        return True if obj.user_id == user_id else False


class UploadAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("id", "file")

    def create(self, validated_data):
        user_id = self.context["request"].user.id
        return Attachment.objects.create(upload_by_id=user_id, **validated_data)


class CategoryCommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=CategoryComment.objects.only("id"),
        required=False,
        allow_null=True
    )
    attachment = serializers.ListSerializer(
        required=False,
        child=serializers.IntegerField(),
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = CategoryComment
        fields = (
            "id",
            "comment_body",
            "is_pined",
            "parent",
            "attachment"
        )

    def check_category_id(self, category_id):
        check_obj = Category.objects.filter(id=category_id, is_active=True).only("id")
        if not check_obj.exists():
            raise NotFound(f"Category with id {category_id} not found")

    def validate_attachment(self, value):
        if value:
            user_id = self.context['request'].user.id
            existing_attachments = Attachment.objects.filter(
                id__in=value,
                is_active=True,
                upload_by_id=user_id
            ).only("id")

            missing_attachments = len(value) != existing_attachments.count()
            if missing_attachments:
                raise serializers.ValidationError(
                    f"some Attachment(s) not found."
                )

        return value

    def create_bulk_comment_attachment(self, attachment, comment_id):
        comment_attachment = [
            CommentAttachment(
                comment_id=comment_id,
                file_id=i
            )
            for i in attachment
        ]
        if comment_attachment:
            CommentAttachment.objects.bulk_create(comment_attachment)

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        category_id = int(self.context['category_pk'])
        parent = validated_data.pop("parent", None)
        attachment = validated_data.pop("attachment", [])

        self.check_category_id(category_id=category_id)

        try:
            comment = CategoryComment.objects.create(
                user_id=user_id,
                category_id=category_id,
                parent=parent,
                **validated_data
            )

            if attachment:
                self.create_bulk_comment_attachment(attachment, comment.id)

            return comment

        except Exception as e:
            raise serializers.ValidationError({"error": f"Failed to create comment: {str(e)}"})


class UpdateCategoryCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryComment
        fields = ("comment_body", "is_pined")
