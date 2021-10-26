from django.forms.widgets import TextInput


class TextInputWithoutAutocomplete(TextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = dict()

        attrs['autocomplete'] = 'off'

        super().__init__(attrs)
