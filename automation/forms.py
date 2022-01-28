from django import forms
from django.core.validators import FileExtensionValidator
import json


class ImportActionForm(forms.Form):
    file_json = forms.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['json'])],
        help_text='Загрузите JSON-файл'
    )

    def form_action(self):
        raise NotImplementedError()

    def save(self):
        action = self.form_action()

        return action


class StudentImportForm(ImportActionForm):
    def form_action(self):
        return json.loads(self.cleaned_data['file_json'].read())


class ManagerImportForm(ImportActionForm):
    def form_action(self):
        return json.loads(self.cleaned_data['file_json'].read())
