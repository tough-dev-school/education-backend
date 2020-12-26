from app import validators


class PurchaseValidator(validators.Validator):
    name = validators.CharField(required=True)
    email = validators.EmailField(required=True)

    class Meta:
        fields = [
            'name',
            'email',
        ]


class GiftValidator(validators.Validator):
    receiver_name = validators.CharField(required=True)
    receiver_email = validators.EmailField(required=True)
    giver_name = validators.CharField(required=True)
    giver_email = validators.EmailField(required=True)
    desired_shipment_date = validators.DateTimeField(required=True)

    class Meta:
        fields = [
            'receiver_name',
            'receiver_email',
            'giver_name',
            'giver_email',
            'desired_shipment_date',
        ]
