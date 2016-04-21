from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse

# Create your views here.
def index(self):
	return render(self, "GithubApp/index.html", {})
	#return HttpResponse('<button type="button" class="btn btn-success">Success</button>');