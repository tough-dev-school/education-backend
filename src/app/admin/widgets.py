from django.forms.widgets import Select, TextInput


class TextInputWithoutAutocomplete(TextInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = dict()

        attrs['autocomplete'] = 'off'

        super().__init__(attrs)


class Select2Widget(Select):
    """
    Fancy select widget based on Select2 (https://select2.github.io/)
    """
    def __init__(self, attrs=None, **kwargs):
        """
        Adds a special class to the widget
        """
        attrs = attrs or {}
        classes = attrs.get('class', '')

        if 'select2 ' not in classes:
            classes = 'select2 ' + classes
            attrs['class'] = classes

        super().__init__(attrs, **kwargs)
