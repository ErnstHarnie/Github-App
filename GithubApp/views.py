from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
import urlparse
import logging
import re
import requests
from zipfile import ZipFile
import urllib2
import os.path, json, urllib

githubRepoUrls = {}
logger = logging.getLogger(__name__)
header = {'Authorization': 'token %s' % settings.CLIENT_CODE}
isAuthorized = False

def login(request):
	if (request.method == "POST" and request.POST and not isAuthorized):
		username = request.POST["username"]
		password = request.POST["password"]

		return render(request, "GithubApp/addrepository.html", {isAuthorized})
	else:
		return render(request, "GithubApp/login.html", {})


def add(request):
	if (request.method == "POST" and request.POST):
		username = request.POST['username']
		repository = request.POST['repository']
		reposUrl = "https://api.github.com/repos/" + username + "/" + repository
		githubRepoUrls[repository] = reposUrl
		if request.POST.get('download', False):
			downloadUrl =  "http://github.com/" + username + "/" + repository +  "/archive/master.zip"
			downloadedRepoPath = 'Repositories/' + repository  # users/naam/repo
			DownloadAndExtract(downloadUrl, downloadedRepoPath)
	  	return render(request, "GithubApp/index.html", {})
	else:
		return render(request, "GithubApp/addrepository.html", {'CLIENT_ID': settings.CLIENT_ID})

def repository(request):

	reposUrl = 'https://api.github.com/repos/'
	commitsUrl = '' # e.g: https://api.github.com/repos/ErnstHarnie/Velo/commits
	reposData = ''
	commitsData = ''
	message = ''

	if githubRepoUrls:	 # if list is not empty
		for key in githubRepoUrls:
			reposUrl = githubRepoUrls[key]
			commitsUrl = githubRepoUrls[key] + "/commits"

			#repoPath = 'Users/' + username + '/' + repository + '/repository.json'
			#downloadedRepoPath = 'Users/' + username + '/' + repository  # users/naam/repo
			downloadedRepoPath = 'Repositories/' + key
			#commitPath = 'Users/' + username + '/' + repository + '/commits.json'

			reposData = GetData(reposUrl, request.session['access_token'])
			commitsData = GetData(commitsUrl, request.session['access_token'])
			if 'message' in reposData:							# on error
					message = reposData['message']

	return render(request, "GithubApp/index.html", {'repos': reposData, 'commit': commitsData, 'message': message, 'access_token': request.session['access_token'], 'authorized': isAuthorized})

def details(request, username, repository, sha):
	reposUrl = 'https://api.github.com/repos/' + username + "/" + repository
	commitsUrl = reposUrl + "/commits/" + sha
	message = ''
	lines = ''

	commitsData = GetData(commitsUrl, request.session['access_token'])
	reposData = GetData(reposUrl, request.session['access_token'])

	if 'message' in reposData:			# on error
		message = reposData['message']
		commitsData = ''
		reposData = ''

	if commitsData:
		lines = sorted(commitsData['files'], key=lambda c: c.get('changes', 0), reverse=True) # sorts files array from json
		maxElements = 10 
		del lines[:-maxElements] # deletes all elements after maxElements (10)

	return render(request, "GithubApp/details.html", {'commits': commitsData, 'sorted': lines,  'repos': reposData, 'message': message})

def authorize(request):
	if request.GET.get('code', ''):
		settings.CLIENT_CODE = request.GET.get('code', '')

		header = {'content-type':'application/json'}
		r = requests.post('https://github.com/login/oauth/access_token', data=json.dumps({'client_id':settings.CLIENT_ID, 'client_secret':settings.CLIENT_SECRET,'code':settings.CLIENT_CODE}), headers=header)
		if r.status_code is 200:
			parsed = urlparse.parse_qs(r.content)
			access_token = parsed['access_token']
			request.session['access_token'] = access_token[0]
			isAuthorized = True
			message = 'You have successfully been authorized!'

		else:
			message = 'You cannot be authorized (' + str(r.status_code) + ').' 

		isAuthorized = True
	return render(request, "GithubApp/index.html", {'message': message})


def DownloadAndExtract(url, destinationPath):
	#http://stackoverflow.com/questions/16760992/how-to-download-a-zip-file-from-a-site-python

		response = urllib.urlopen(url)
		zipFile = response.read()

		if not os.path.isdir(destinationPath):
			 os.makedirs(destinationPath)

		with open(destinationPath + "/master.zip", "wb") as f:
			f.write(zipFile)

		zf = ZipFile(destinationPath + "/master.zip")
		zf.extractall(path = destinationPath)
		zf.close()

def GetData(url, token):
	try:
		response = ''
		logging.info('Attempting to get ' + url + ' with the following token: ' + token)
		#req = urllib2.Request(url)
		#req.add_header("Authorization", "Bearer %s" % self.access_token['access_token'])
		if settings.CLIENT_CODE: # if user is authorized
			req = urllib2.Request(url)
			req.add_header('Authorization', 'token %s' % token)
			#req.add_header('Accept', 'application/json')
			#req.add_header('token', token)
			response = urllib2.urlopen(req).read() 
		else:
			response = urllib2.urlopen(url).read()
		data = json.loads(response.decode('utf-8'))
		return data
	except Exception as e: 
		response = '{"message": "' + str(e) + '"}' 
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