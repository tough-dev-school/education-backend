from app import validators
from banking.selector import BANK_CHOICES


class PurchaseValidator(validators.Validator):
    name = validators.CharField(required=True)
    email = validators.EmailField(required=True)
    desired_bank = validators.ChoiceField(choices=BANK_CHOICES, required=False)

    class Meta:
        fields = [
            'name',
            'email',
            'desired_bank',
        ]


class GiftValidator(validators.Validator):
    receiver_name = validators.CharField(required=True)
    receiver_email = validators.EmailField(required=True)
    giver_name = validators.CharField(required=True)
    giver_email = validators.EmailField(required=True)
    desired_shipment_date = validators.DateTimeField(required=True)
    desired_bank = validators.ChoiceField(choices=BANK_CHOICES, required=False)

    class Meta:
        fields = [
            'receiver_name',
            'receiver_email',
            'giver_name',
            'giver_email',
            'desired_shipment_date',
            'desired_bank',
        ]
