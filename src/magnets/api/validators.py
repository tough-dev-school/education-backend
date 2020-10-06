from app import validators


class LeadValidator(validators.Validator):
    name = validators.CharField(required=False)
    email = validators.EmailField(required=True)

    class Meta:
        fields = [
            'name',
            'email',
        ]
