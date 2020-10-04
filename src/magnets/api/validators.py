from app import validators


class LeadValidator(validators.Validator):
    name = validators.CharField(required=True)
    email = validators.EmailField(required=True)

    class Meta:
        fields = [
            'name',
            'email',
        ]
