from django.forms import ModelForm
from intranet.models import Document


class DocumentForm(ModelForm):
	class Meta:
		model = Document
		fields = '__all__'
		exclude = ['abstract', 'owner']