from django import forms
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError
from .models import SubscriptionPlan


class SubscriptionPlanAdminForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        has_installment = cleaned_data.get('has_installment')
        min_installment_months = cleaned_data.get('min_installment_months')
        max_installments = cleaned_data.get('max_installments')

        if has_installment is False:
            if max_installments and max_installments > 0:
                self.add_error(
                    'max_installments',
                    _("زمانی میتوانید این فیلد رو مقدار دهی کنید که خرید قسطی فعال باشد یا مقدار رو روی صفر تنظیم کنید")
                )
            if min_installment_months and min_installment_months > 0:
                self.add_error(
                    'min_installment_months',
                    _("زمانی میتوانید این فیلد رو مقدار دهی کنید که خرید قسطی فعال باشد یا مقدار رو روی صفر تنظیم کنید")
                )
        else:
            if min_installment_months > max_installments:
                self.add_error(
                    'max_installments',
                    _("حداکثر اقساط نمی‌تواند کمتر از حداقل مدت باشد")
                )
        return cleaned_data
