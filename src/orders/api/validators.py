from app import validators


class PurchaseValidator(validators.Validator):
    name = validators.CharField(required=True)
    email = validators.EmailField(required=True)
    price = validators.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        fields = [
            'name',
            'email',
            'price',
        ]
