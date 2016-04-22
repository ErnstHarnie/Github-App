from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse
import json
import urllib



# Create your views here.
def index(request):
	reposUrl = 'https://api.github.com/repos/' # https://api.github.com/repos/
	commitsUrl = '' # https://api.github.com/repos/ErnstHarnie/Velo/commits
	username = ''
	repository = ''
	reposData = ''
	commitsData = ''
	if (request.method == "POST" and request.POST):
		username = request.POST['username']
		repository = request.POST['repository']
		reposUrl = reposUrl + username + "/" + repository
		commitsUrl = reposUrl + "/commits"

		reposData = GetData(reposUrl)
		commitsData = GetData(commitsUrl)
	return render(request, "GithubApp/index.html", {'repos': reposData, 'commit': commitsData, 'url': reposUrl, 'url2': commitsUrl})
	#return render(self, "GithubApp/index.html", {})

def add(request):
	return render(request, "GithubApp/addrepository.html", {})

def addrepository(request):
	return (request, "GithubApp/index.html", {})


def GetData(url):
	response = urllib.urlopen(url).read() 
	data = json.loads(response.decode('utf-8'))
	return data