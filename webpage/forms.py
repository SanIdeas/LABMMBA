from django import forms
from django.forms import ModelForm
from webpage.models import News, Image
from login.models import User


class NewsForm(forms.ModelForm):
	title = forms.CharField(required=False)
	title_html = forms.CharField(required=False)
	slug = forms.SlugField(required=False)
	body = forms.CharField(required=False)
	admin_annotation = forms.CharField(required=False)
	date = forms.DateField(required=False)
	author = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
	source_text = forms.CharField(required=False)
	source_url = forms.CharField(required=False)
	description = forms.CharField(required=True)
	mini_description = forms.CharField(required=False)
	thumbnail = forms.FileField(required=True)
	header = forms.FileField(required=False)
	class Meta:
		model = News
		fields = '__all__'

class ImageForm(forms.ModelForm):
	news = forms.ModelChoiceField(queryset=News.objects.all(), required=True)
	class Meta:
		model = Image
		fields = '__all__'