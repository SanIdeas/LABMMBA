from django.shortcuts import render
from intranet.models import Document
from unidecode import unidecode
from django.http import HttpResponseRedirect
from webpage.models import Section
from django.core.urlresolvers import reverse
from intranet.views import get_filters, filters_selected
from collections import Counter

# Create your views here.
def search(request, search=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('intranet'))
    else:
        kwargs = get_filters(request)
        all_docs = Document.objects.filter(is_public=True, **kwargs)
        if search is None: #Si no es una busqueda
            documents = all_docs
        else:
            documents = []
            high_acc_result = []
            low_acc_result = []
            authors = []
            years = []
            owners = []
            categories = []
            for document in all_docs:
                result = document.match(search)
                if result['match']:
                    if result['extract'] != '':
                        setattr(document, 'extract', result['extract'])
                    if result['exact']:
                        high_acc_result.append(document)
                    else:
                        low_acc_result.append(document)
                    authors.append(document.author)
                    years.append(document.date.year)
                    owners.append(document.owner)
                    categories.append(document.category)
            documents = high_acc_result + low_acc_result
            authors = filters_selected(Counter(authors).most_common(), request, 'author')
            years = filters_selected(Counter(years).most_common(), request, 'date')
            owners = filters_selected(Counter(owners).most_common(), request, 'owner')
            categories = filters_selected(Counter(categories).most_common(), request, 'category')

        sections = Section.objects.all()
        section = Section.objects.get(slug='publications')
        parameters = {'current_view': section, 'current_section': section, 'sections': sections.exclude(slug__in=['intranet', 'administrator']), 'documents': documents, 'body': 'eventos'}
        if search is not None:
            parameters['authors'] = authors
            parameters['years'] = years
            parameters['categories'] = categories
            parameters['owners'] = owners
            parameters['search'] = search
        return render(request, 'public_search/search.html', parameters)