from django import forms
from intranet.models import Document


class DocumentForm(forms.ModelForm):
	title = forms.CharField(required=False)
	author = forms.CharField(required=False)
	category = forms.CharField(required=False)
	abstract = forms.CharField(required=False)
	drive_id = forms.CharField(required=False)
	drive_thumbnail = forms.CharField(required=False)
	class Meta:
		model = Document
		fields = '__all__'
