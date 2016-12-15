from django import forms
from webpage.models import News, Image, Section, SectionImage, GalleryPhoto, Member, News_comment, Event, EventDay
from login.models import User


class NewsForm(forms.ModelForm):
	title = forms.CharField(required=False)
	title_html = forms.CharField(required=False)
	slug = forms.SlugField(required=False)
	body = forms.CharField(required=False)
	description = forms.CharField(required=False)
	admin_annotation = forms.CharField(required=False)
	date = forms.DateField(required=False, input_formats=['%d-%m-%Y'])
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

class GalleryPhotoForm(forms.ModelForm):

	class Meta:
		model = GalleryPhoto
		fields = '__all__'

class NewsCommentForm(forms.ModelForm):
	news = forms.ModelChoiceField(queryset=News.objects.all(), required=True)
	author = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
	content = forms.CharField(required=True)
	class Meta:
		model = News_comment
		fields = '__all__'

class ImageMemberForm(forms.ModelForm):
	member = forms.ModelChoiceField(queryset=News.objects.all(), required=True)
	class Meta:
		model = Image
		fields = '__all__'

class EventForm(forms.ModelForm):
	title = forms.CharField(required=True)
	slug = forms.SlugField(required=False)
	description = forms.CharField(required=True)
	image = forms.FileField(required=False)
	program = forms.FileField(required=False)
	class Meta:
		model = Event
		fields = '__all__'

class EventDayForm(forms.ModelForm):
	day = forms.DateField(required=True, input_formats=['%d-%m-%Y'])
	begin_hour = forms.TimeField(required=True)
	end_hour = forms.TimeField(required=True)
	location = forms.CharField(required=True)
	event = forms.ModelChoiceField(queryset=Event.objects.all(), required=True)
	class Meta:
		model = EventDay
		fields = '__all__'