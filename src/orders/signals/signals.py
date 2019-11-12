from django.dispatch import Signal

order_got_shipped = Signal(providing_args=['order'])
