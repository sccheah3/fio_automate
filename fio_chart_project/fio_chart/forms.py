from django import forms

class UploadFioLog(forms.Form):
    file = forms.FileField()

class AutomateFio(forms.Form):
    