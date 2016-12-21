from django import forms
from intranet.models import Document, Forum, ForumComment
from login.models import SubArea, User


class DocumentForm(forms.ModelForm):
	title = forms.CharField(required=False)
	author = forms.CharField(required=False)
	title_slug = forms.CharField(required=False)
	author_slug = forms.CharField(required=False)
	category = forms.ModelChoiceField(queryset=SubArea.objects.all(), required=False)
	abstract = forms.CharField(required=False)
	content = forms.CharField(required=False)
	drive_id = forms.CharField(required=False)
	date = forms.DateField(required=False, input_formats=['%d-%m-%Y'])
	thumbnail = forms.FileField(required=False)
	words = forms.CharField(required=False)
	issn = forms.CharField(required=False)
	url = forms.CharField(required=False)
	doi = forms.CharField(required=False)
	pages = forms.CharField(required=False)
	is_public = forms.BooleanField(required=False)

	class Meta:
		model = Document
		fields = '__all__'

class ForumForm(forms.ModelForm):
	title = forms.CharField(required=True)
	slug = forms.CharField(required=False)
	author = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
	content = forms.CharField(required=True)
	type = forms.CharField(required=True)

	class Meta:
		model = Forum
		fields = '__all__'