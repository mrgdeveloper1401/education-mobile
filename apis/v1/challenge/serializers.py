from django.db.models import  F
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from apis.utils.custom_exceptions import ChallengeBlockedException, ChallengeBlockTwoException, \
    PreventSendSubmitChallengeException
from challenge_app.models import Challenge, ChallengeSubmission, UserChallengeScore


class ListChallengeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_accepted = serializers.SerializerMethodField()

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
            "is_accepted"
        )

    @extend_schema_field(serializers.URLField())
    def get_image_url(self, obj):
        return obj.image.course_image if obj.image else None

    @extend_schema_field(serializers.BooleanField())
    def get_is_accepted(self, obj):
        return obj.is_accepted


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
            "answer",
            # "time_limit",
            # "memory_limit",
            # "total_submissions",
            # "successful_submissions",
            # "avg_completion_time",
            # 'test_cases'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        is_accepted = instance.is_accepted
        if is_accepted is False:
            data['answer'] = None
        return data


class SubmitChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeSubmission
        fields = (
            "id",
            'status'
        )

    def validate(self, attrs):
        check_submit_challenge = ChallengeSubmission.objects.filter(
            is_active=True,
            user_id=self.context["request"].user.id,
            challenge_id=self.context["challenge_id"],
            status__in=['accepted', 'solved']
        ).only("id")
        if check_submit_challenge.exists():
            raise PreventSendSubmitChallengeException()
        return attrs

    def _create_user_submit(self, user_id, challenge_id):
        ChallengeSubmission.objects.create(
            challenge_id=challenge_id,
            is_active=True,
            user_id=user_id
        )

    def create(self, validated_data):
        user_id = self.context["request"].user.id
        challenge_id = self.context["challenge_id"]
        status = validated_data.get("status")

        # check challenge
        challenge = Challenge.objects.filter(id=challenge_id, is_active=True).only("id", "points")
        if not challenge.exists():
            raise NotFound("چالش مورد نظر پیدا نشد")

        # get challenge
        get_challenge = challenge.last()

        # check user score
        user_score = UserChallengeScore.objects.filter(user_id=user_id).only("id", "total_score")

        # check user_submit and create
        user_submit = ChallengeSubmission.objects.filter(
            challenge_id=challenge_id,
            is_active=True,
            user_id=user_id,
        ).only("status")
        self._create_user_submit(user_id, challenge_id)

        if status == "solved":
            # update total_submissions challenge
            challenge.update(total_submissions=F("total_submissions") + 1)

            # get user submit and save status
            get_user_submit = user_submit.last()
            get_user_submit.status = "solved"
            get_user_submit.save()

            if user_score.first().total_score <= 0:
                raise ChallengeBlockedException()
            elif user_score.first().total_score < get_challenge.points:
                raise ChallengeBlockTwoException()
            else:
                user_score.update(total_score=F("total_score") - get_challenge.points)
                return user_submit

        elif status == "accepted":
            get_points = challenge.first().points
            user_score.update(total_score=F("total_score") + get_challenge.points)

            # get user submit and save status
            get_user_submit = user_submit.last()
            get_user_submit.status = "accepted"
            get_user_submit.score = get_points
            get_user_submit.save()

            # update successful_submissions and total_submissions challenge
            challenge.update(successful_submissions=F("successful_submissions") + 1, total_submissions=F("total_submissions") + 1)
            return user_submit

        else:
            # get user submit and save status
            get_user_submit = user_submit.last()
            get_user_submit.status = status
            get_user_submit.save()

            # update total_submissions challenge
            challenge.update(total_submissions=F("total_submissions") + 1)
            return user_submit

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status'] = instance.values("status")[0]['status']
        if data['status'] == "solved":
            data['answer'] = instance.last().challenge.answer
        return data
