from django import forms

class UploadFioLogForm(forms.Form):
    file = forms.FileField()

class AutomateFioForm(forms.Form):
	bmc_ip = forms.CharField()
	lan_mac = forms.CharField()
	cburn_img = forms.CharField()
	burnin_dir = forms.CharField()
