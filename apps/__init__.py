# # auth app
# from apps.auth_app.models import User, City, Student, Coach
#
# # core app
# from apps.core_app.models import (
#     Photo,
#     Video,
#     ActiveMixin,
#     CreateMixin,
#     UpdateMixin,
#     SoftDeleteMixin,
#     Attachment
# )
#
# # challenge app
# from apps.challenge_app.models import Challenge, ChallengeSubmission, UserChallengeScore, UserChallengeProgress
#
# # course app
# from apps.course_app.models import (
#     Course,
#     LessonCourse,
#     Category,
#     CategoryComment,
#     CommentAttachment,
#     SectionVideo,
#     Section,
#     StudentAccessSection,
#     StudentEnrollment,
#     StudentStatusEnum
# )
#
# # discount app
# from apps.discount_app.models import Coupon
#
# # exam app
# from apps.exam_app.models import SectionExam, ExamGrading, StudentExamAttempt, StudentAnswer, Choice, Question
#
# # gateway app
# from apps.gateway_app.models import Gateway, ResultGateway
#
# # subscription app
# from apps.subscription_app.models import (
#     SubscriptionPlan,
#     UserSubscription,
#     UserInstallment,
#     InstallmentPlan,
#     InstallmentOption
# )
#
#
# __all__ = [
#     # auth app
#     "User",
#     "City",
#     "Student",
#     "Coach",
#     # core app
#     "Photo",
#     "Video",
#     "ActiveMixin",
#     "CreateMixin",
#     "UpdateMixin",
#     "SoftDeleteMixin",
#     # challenge app
#     "Attachment",
#     "Challenge",
#     "ChallengeSubmission",
#     "UserChallengeScore",
#     "UserChallengeProgress",
#     # course app
#     "Course",
#     "LessonCourse",
#     "Category",
#     "CategoryComment",
#     "CommentAttachment",
#     "SectionVideo",
#     "Section",
#     "StudentAccessSection",
#     "StudentEnrollment",
#     "StudentStatusEnum",
#     # discount app
#     "Coupon",
#     # exam app
#     "SectionExam",
#     "ExamGrading",
#     "StudentExamAttempt",
#     "StudentAnswer",
#     "Choice",
#     "Question",
#     # gateway app
#     "Gateway",
#     "ResultGateway",
#     # subscription app
#     "SubscriptionPlan",
#     "UserSubscription",
#     "UserInstallment",
#     "InstallmentPlan",
#     "InstallmentOption",
# ]