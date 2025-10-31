from django.forms.widgets import NumberInput, Textarea


class AppNumberInput(NumberInput):
    def __init__(self, attrs: dict | None = None) -> None:
        if attrs is None:
            attrs = dict()

        attrs["autocomplete"] = "off"
        attrs["step"] = 1

        classes = attrs.get("class", "")
        attrs["class"] = f"{classes} app-number-input"

        super().__init__(attrs)


class AppJSONEditor(Textarea):
    class Media:
        js = [
            "admin/json_editor.js",
        ]

        css = {
            "all": ["admin/json_editor.css"],
        }

    def __init__(self, attrs: dict | None = None) -> None:
        super().__init__(attrs={"class": "app-json-editor", "cols": "40"})
