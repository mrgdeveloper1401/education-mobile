from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound, NotAcceptable

from challenge_app.models import Challenge, ChallengeSubmission


class ListChallengeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = (
            "id",
            "name",
            "language",
            "level",
            "success_percent",
            "successful_submissions",
            "points",
            "coins",
            "image_url",
        )

    @extend_schema_field(serializers.URLField())
    def get_image_url(self, obj):
        return obj.image.course_image if obj.image else None


# class TestCateChallengeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TestCase
#         fields = (
#             "id",
#             "input_data",
#             "expected_output",
#             "order"
#         )


class DetailChallengeSerializer(ListChallengeSerializer):
    # test_cases = TestCateChallengeSerializer(many=True, read_only=True)

    class Meta(ListChallengeSerializer.Meta):
        fields = ListChallengeSerializer.Meta.fields + (
            "description",
            # "time_limit",
            # "memory_limit",
            # "total_submissions",
            # "successful_submissions",
            # "avg_completion_time",
            # 'test_cases'
        )


class SubmitChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeSubmission
        fields = (
            "id",
            'status'
        )

    def create(self, validated_data):
        user_id = self.context["request"].user.id
        challenge_id = self.context["challenge_id"]

        check_obj = Challenge.objects.filter(id=challenge_id, is_active=True).only("id")
        if not check_obj.exists():
            raise NotFound("چالش مورد نظر پیدا نشد")

        status_req_data = validated_data.get("status")

        match status_req_data:
            case "pending":
                status_choice = "pending"
            case "accepted":
                status_choice = "accepted"
            case "running":
                status_choice = "running"
            case "wrong_answer":
                status_choice = "wrong_answer"
            case "time_limit_exceeded":
                status_choice = "time_limit_exceeded"
            case "memory_limit_exceeded":
                status_choice = "memory_limit_exceeded"
            case "runtime_error":
                status_choice = "runtime_error"
            case "compilation_error":
                status_choice = "compilation_error"
            case _:
                raise NotAcceptable()

        return ChallengeSubmission.objects.create(
            user_id=user_id,
            challenge_id=challenge_id,
            status=status_choice
        )
