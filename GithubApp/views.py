from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from zipfile import ZipFile
import urllib2
import os.path, json, urllib


def index(request):
	return render(request, "GithubApp/addrepository.html", {})

def add(request):
	return render(request, "GithubApp/addrepository.html", {})

def repository(request):
	reposUrl = 'https://api.github.com/repos/'
	commitsUrl = '' # e.g: https://api.github.com/repos/ErnstHarnie/Velo/commits
	reposData = ''
	commitsData = ''
	message = ''

	if (request.method == "POST" and request.POST):
		username = request.POST['username']
		repository = request.POST['repository']
		reposUrl = reposUrl + username + "/" + repository
		commitsUrl = reposUrl + "/commits"


		repoPath = 'Users/' + username + '/' + repository + '/repository.json'
		downloadedRepoPath = 'Users/' + username + '/' + repository  # users/naam/repo
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
		else: # If there are no errors
			SaveJsonToFile(reposData, repoPath, username, repository) 
			SaveJsonToFile(commitsData, commitPath, username, repository)
			if request.POST.get('download', False):
				downloadUrl = "http://github.com/" + username + "/" + repository + "/archive/master.zip"
				download(downloadUrl, downloadedRepoPath)


	return render(request, "GithubApp/index.html", {'repos': reposData, 'commit': commitsData, 'message': message})

def details(request, username, repository, sha):
	reposUrl = 'https://api.github.com/repos/' + username + "/" + repository
	commitsUrl = reposUrl + "/commits/" + sha
	message = ''
	lines = ''

	detailedPath = 'Users/' + username + '/' + repository + '/' + sha + '.json'
	repoPath = 'Users/' + username + '/' + repository + '/repository.json'

	commitsData = GetData(commitsUrl)
	reposData = GetData(reposUrl)

	if 'message' in reposData:			# on error
		message = reposData['message']
		if DoesFileExist(detailedPath):	# load locally stored file
			commitsData = GetData(detailedPath)
			reposData = GetData(repoPath)
		else:
			commitsData = ''
			reposData = ''
	else:  # save only when there are no errors
			SaveJsonToFile(commitsData, detailedPath, username, repository)
			SaveJsonToFile(reposData, repoPath, username, repository)

	if commitsData:
		lines = sorted(commitsData['files'], key=lambda c: c.get('changes', 0), reverse=True) # sorts files array from json
		maxElements = 10 
		del lines[:-maxElements] # deletes all elements after maxElements (10)

	return render(request, "GithubApp/details.html", {'commits': commitsData, 'lines': lines, 'sorted': lines,  'repos': reposData, 'message': message})


def download(url, destinationPath):
	#http://stackoverflow.com/questions/16760992/how-to-download-a-zip-file-from-a-site-python
	response = urllib.urlopen(url)
	zipFile = response.read()

	with open(destinationPath + "/master.zip", "wb") as f:
		f.write(zipFile)

	zf = ZipFile(destinationPath + "/master.zip")
	zf.extractall(path = destinationPath)
	zf.close()


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