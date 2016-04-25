from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse
import os.path
import json
import urllib



# Create your views here.
def index(request):
	return render(request, "GithubApp/addrepository.html", {})

def add(request):
	return render(request, "GithubApp/addrepository.html", {})

def repository(request):
	reposUrl = 'https://api.github.com/repos/' # https://api.github.com/repos/
	commitsUrl = '' # https://api.github.com/repos/ErnstHarnie/Velo/commits
	username = ''
	repository = ''
	reposData = ''
	commitsData = ''
	message = ''


	if (request.method == "POST" and request.POST):
		username = request.POST['username']
		repository = request.POST['repository']
		reposUrl = reposUrl + username + "/" + repository
		commitsUrl = reposUrl + "/commits"

		repoPath = 'Users/' + username + '/' + repository + '/repository.txt'
		commitPath = 'Users/' + username + '/' + repository + '/commits.txt'

		reposData = GetData(reposUrl)
		commitsData = GetData(commitsUrl)
		if 'message' in reposData:				
				message = reposData['message']
				if DoesFileExist(repoPath):
					file = open(repoPath, 'r')
					reposData = json.loads(file.read().decode('utf-8'))
					if DoesFileExist(commitPath):
						file = open(commitPath, 'r')
						commitsData = json.loads(file.read().decode('utf-8'))
		else:
			SaveJsonToFile(reposData, commitsData, username, repository)

	return render(request, "GithubApp/index.html", {'repos': reposData, 'commit': commitsData, 'message': message})

def download(request, owner_name, repo_name, branch_name):
	message = 'Download started.'
	return HttpResponse("Download started")
	#return render(request, "GithubApp/index.html", {'message': message})


def GetData(url):
	try:
		response = urllib.urlopen(url).read() 
		data = json.loads(response.decode('utf-8'))
		return data
	except:
		response = '{"message": "Unable to get online data."}'
		data = json.loads(response.decode('utf-8'))
		return data

def DoesKeyExist(json, key):
	for result in json:
	    if key in result:
	        return True
	    else:
	    	return False

def DoesFileExist(path):
	if os.path.isfile(path):
		return True
	else:
		return False

def SaveJsonToFile(repoJson, commitJson, username, repository):
	start_path = 'Users/'
	final_path = os.path.join(start_path, username, repository)
	#if not os.path.exists(username):
		#start_path.join(username)
	#if not os.path.exists(repository):
		#start_path.join(repository)
	if not os.path.isdir(final_path):
		os.makedirs(final_path)
	with open('Users/' + username + '/' + repository + '/repository.txt', 'w+') as outfile:
		json.dump(repoJson, outfile)
	with open('Users/' + username +  '/' + repository + '/commits.txt', 'w+') as outfile:
		json.dump(commitJson, outfile)