from app import validators
from banking.selector import BANK_CHOICES


class PurchaseValidator(validators.Validator):
    name = validators.CharField(required=True)
    email = validators.EmailField(required=True)
    desired_bank = validators.ChoiceField(choices=BANK_CHOICES, required=False)

    class Meta:
        fields = [
            "name",
            "email",
            "desired_bank",
        ]
