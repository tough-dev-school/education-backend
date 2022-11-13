from django.db import models


class BankChoice(models.TextChoices):
    TINKOFF_BANK = ('tinkoff_bank', 'Tinkoff Bank')
    TINKOFF_CREDIT = ('tinkoff_credit', 'Tinkoff Credit')
    STRIPE = ('stripe', 'Stripe')
    DOLYAME = ('dolyame', 'Dolyame')
    ZERO_PRICE = ('zero_price', 'Zero Price Bank')
