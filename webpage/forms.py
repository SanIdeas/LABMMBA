from django import forms
from webpage.models import News, Image, Section, SectionImage
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
	thumbnail = forms.FileField(required=True)
	header = forms.FileField(required=False)
	in_header = forms.BooleanField(required=False)
	class Meta:
		model = News
		fields = '__all__'


class ImageForm(forms.ModelForm):
	news = forms.ModelChoiceField(queryset=News.objects.all(), required=True)
	class Meta:
		model = Image
		fields = '__all__'


class SectionImageForm(forms.ModelForm):
	section = forms.ModelChoiceField(queryset=Section.objects.all(), required=True)

	class Meta:
		model = SectionImage
		fields = '__all__'