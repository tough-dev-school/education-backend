from django.forms.widgets import NumberInput


class AppNumberInput(NumberInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = dict()

        attrs['autocomplete'] = 'off'
        attrs['step'] = 1

        classes = attrs.get('class', '')
        attrs['class'] = f'{classes} app-number-input'

        super().__init__(attrs)
