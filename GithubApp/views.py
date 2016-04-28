from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse
import os.path, json, urllib


# Create your views here.
def index(request):
	return render(request, "GithubApp/addrepository.html", {})

def add(request):
	return render(request, "GithubApp/addrepository.html", {})

def repository(request):
	reposUrl = 'https://api.github.com/repos/' # https://api.github.com/repos/
	commitsUrl = '' # e.g: https://api.github.com/repos/ErnstHarnie/Velo/commits
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
		repoPath = 'Users/' + username + '/' + repository + '/repository.json'
		commitPath = 'Users/' + username + '/' + repository + '/commits.json'

		reposData = GetData(reposUrl)
		commitsData = GetData(commitsUrl)
		if 'message' in reposData:							# on error
				message = reposData['message']
				if DoesFileExist(repoPath) and DoesFileExist(commitPath):	# load locally stored file
					reposData = GetData(repoPath)
					commitsData = GetData(commitPath)
				else:
					reposData = ''
					commitsData = ''
		else:
			SaveJsonToFile(reposData, repoPath, username, repository) # save only when there are no errors
			SaveJsonToFile(commitsData, commitPath, username, repository) # save only when there are no errors

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
	except Exception as e:
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

def SaveJsonToFile(jsonFile, path, username, repository):
	# Path: Users/Username/Repository/File.json
	start_path = 'Users/'
	final_path = os.path.join(start_path, username, repository)
	if not os.path.isdir(final_path):
		os.makedirs(final_path)
	with open(path, 'w+') as outfile:
		json.dump(jsonFile, outfile)