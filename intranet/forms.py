from django import forms
from intranet.models import Document
from login.models import Area


class DocumentForm(forms.ModelForm):
	title = forms.CharField(required=False)
	author = forms.CharField(required=False)
	category = forms.ModelChoiceField(queryset=Area.objects.all(), required=False)
	abstract = forms.CharField(required=False)
	content = forms.CharField(required=False)
	drive_id = forms.CharField(required=False)
	date = forms.DateField(required=False)
	thumbnail = forms.FileField(required=False)
	words = forms.CharField(required=False)
	issn = forms.CharField(required=False)
	url = forms.CharField(required=False)
	doi = forms.CharField(required=False)
	pages = forms.CharField(required=False)
	class Meta:
		model = Document
		fields = '__all__'
