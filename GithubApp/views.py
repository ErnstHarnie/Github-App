from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse
import json
import urllib



# Create your views here.
def index(self):
	return render(self, "GithubApp/index.html", {})

def add(request):
	return render(request, "GithubApp/addrepository.html", {})

def addrepository(request):
	reposUrl = "https://api.github.com/repos/"
	commitsUrl = "https://api.github.com/repos/ErnstHarnie/Velo/commits"
	username = ''
	repository = ''
	data = ''
	if (request.method == "POST" and request.POST):
		username = request.POST['username']
		repository = request.POST['repository']
		reposUrl = reposUrl + username + "/" + repository 

		response = urllib.urlopen(reposUrl).read() 
		data = json.loads(response.decode('utf-8'))		
	return render(request, "GithubApp/index.html", {'data': data, 'url': reposUrl})