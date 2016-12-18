from django import forms
from login.models import User, SubArea
from django_countries.fields import LazyTypedChoiceField


class UserForm(forms.ModelForm):
	email = forms.EmailField(required=True)
	first_name = forms.CharField(required=False)
	last_name = forms.CharField(required=False)
	institution = forms.CharField(required=False)
	country = LazyTypedChoiceField(choices=countries)
	area = forms.ModelChoiceField(queryset=SubArea.objects.all(), required=False)
	career = forms.CharField(required=False)
	is_active = forms.BooleanField(required=True)
	is_blocked = forms.BooleanField(required=True)
	is_admin = forms.BooleanField(required=True)
	last_activity = forms.DateField(required=True)
	profile_picture = forms.FileField(required=False)
	doc_count = forms.IntegerField(required=False)
	drive_credentials = forms.BinaryField(required=False)
	access_token = forms.CharField(required=False)

	class Meta:
		model = User
		fields = '__all__'