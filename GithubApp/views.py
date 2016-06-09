from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from zipfile import ZipFile
from django.template import RequestContext
import os.path, json, urllib, urllib2, requests, re, logging, urlparse

githubRepoUrls = {}
userUrl = 'https://api.github.com/user'

def add(request):
	if (request.method == "POST" and request.POST):
		username = request.POST['username']
		repository = request.POST['repository']
		reposUrl = "https://api.github.com/repos/" + username + "/" + repository
		key = username + '/' + repository
		githubRepoUrls[key] = reposUrl
		print 'added ' + githubRepoUrls[key]
		if request.POST.get('download', False):
			downloadUrl =  "http://github.com/" + username + "/" + repository +  "/archive/master.zip"
			downloadedRepoPath = 'Repositories/' + username + '/' + repository  # users/naam/repo
			DownloadAndExtract(downloadUrl, downloadedRepoPath)
	  	return HttpResponseRedirect('/GithubApp/')
	else:
		return render(request, "GithubApp/addrepository.html", {})

def delete(request):
	k = request.POST.get('repokey', False)
	githubRepoUrls.pop(k, None)
	return HttpResponseRedirect("/GithubApp/")

def repository(request):
	commitsUrl = '' # e.g: https://api.github.com/repos/ErnstHarnie/Velo/commits
	userData = ''
	message = ''
	sessionKey = ''

	jsonReposData = {}
	jsonCommitsData = {}

	if 'access_token' in request.session:
		sessionKey = request.session['access_token']

	if githubRepoUrls:	 # if list is not empty
		for key in githubRepoUrls:
			reposUrl = githubRepoUrls[key]
			commitsUrl = githubRepoUrls[key] + "/commits" 
			downloadedRepoPath = 'Repositories/' + key
			print 'attempting to get ' + key

			jsonReposData[key] = GetData(reposUrl, sessionKey)
			jsonCommitsData[key] = GetData(commitsUrl, sessionKey)

			if 'message' in jsonReposData[key]:
				message = jsonReposData[key]['message']

	return render(request, "GithubApp/index.html", {'repos': jsonReposData, 'commit': jsonCommitsData, 'message': message})

def details(request, username, repository, sha):
	reposUrl = 'https://api.github.com/repos/' + username + "/" + repository
	commitsUrl = reposUrl + "/commits/" + sha
	message = ''
	lines = ''
	sessionKey = ''

	if 'access_token' in request.session:
		sessionKey = request.session.get('access_token')

	commitsData = GetData(commitsUrl, sessionKey)
	reposData = GetData(reposUrl, sessionKey)

	if 'message' in reposData:			# on error
		message = reposData['message']
		commitsData = ''
		reposData = ''

	if commitsData:
		lines = sorted(commitsData['files'], key=lambda c: c.get('changes', 0), reverse=True) # sorts files array from json
		maxElements = 10 
		del lines[:-maxElements] # deletes all elements after maxElements (10)

	return render(request, "GithubApp/details.html", {'commits': commitsData, 'sorted': lines,  'repos': reposData, 'message': message})

def addAllRepositories(request):
	if 'access_token' in request.session:
		repoUrl = userUrl + "/repos" 
		repoData = GetData(repoUrl, request.session['access_token'])

		for repo in repoData:
			reposUrl = "https://api.github.com/repos/" + repo['full_name']
			githubRepoUrls[repo['full_name']] = reposUrl

	return HttpResponseRedirect('/GithubApp/')

def downloadAllRepositories(request):
	message = ''
	if len(githubRepoUrls) > 0:
		repoUrl = userUrl + "/repos"

		for k, v in githubRepoUrls.iteritems():
			downloadUrl = "http://github.com/" + k + "/archive/master.zip"
			downloadedRepoPath = 'Repositories/' + k
			DownloadAndExtract(downloadUrl, downloadedRepoPath)
			message += k + ', '
		message += ' has been downloaded and extracted.'

	else:
		message = 'You need to add at least 1 repository.'

	return render(request, "GithubApp/downloadall.html", {'message': message})

def clearAllRepositories(request):
	githubRepoUrls.clear()
	return HttpResponseRedirect('/GithubApp/')

def authorize(request):
	message = ''
	if 'access_token' in request.session:
		message = 'You are authenticated already.'
	elif request.GET.get('code', ''):
		settings.CLIENT_CODE = request.GET.get('code', '')

		header = {'content-type':'application/json'} # required
		r = requests.post('https://github.com/login/oauth/access_token', data=json.dumps({'client_id':settings.CLIENT_ID, 'client_secret':settings.CLIENT_SECRET,'code':settings.CLIENT_CODE}), headers=header)
		if r.status_code is 200:
			parsed = urlparse.parse_qs(r.content)
			if 'access_token' in parsed:
				access_token = parsed['access_token'] 
				request.session['access_token'] = access_token[0]
				message = 'You have successfully been authenticated!'
			else:
				message = 'You cannot be authenticated. (' + str(parsed['error_description'][0]) + ')'
		else:
			message = 'You cannot be authenticated (' + str(r.status_code) + ').' 
	else:
		message = 'You cannot be authenticated.'
	return render(request, "GithubApp/authorize.html", {'message': message})

def DownloadAndExtract(url, destinationPath):
	#http://stackoverflow.com/questions/16760992/how-to-download-a-zip-file-from-a-site-python
	try:
		response = urllib.urlopen(url)
		zipFile = response.read()

		if not os.path.isdir(destinationPath):
			 os.makedirs(destinationPath)

		with open(destinationPath + "/master.zip", "wb") as f:
			f.write(zipFile)

		zf = ZipFile(destinationPath + "/master.zip")
		zf.extractall(path = destinationPath)
		zf.close()
	except Exception as e:
		print 'Unable to download and unzip: ' + str(e)

def GetData(url, token):
	try:
		response = ''
		data = ''
		logging.info('Attempting to get ' + url + ' with the following token: ' + token)

		if token: # if user is authenticated, add the token to header
			req = urllib2.Request(url)
			req.add_header('Authorization', 'token %s' % token)
			response = urllib2.urlopen(req).read() 
		else:
			response = urllib2.urlopen(url).read()

		data = json.loads(response.decode('utf-8'))
		print 'returned from ' + url

		return data
	except urllib2.HTTPError as h:
		print 'HTTPERROR: ' + str(h)
		if h.code == 403:
			response = '{"message": "You have reached the API limit. You need to authenticate, or wait until the next hour."}'
		elif h.code == 404:
			response = '{"message": "One or more repositories could not be found."}' 
		else:
			response = '{"message": "An error occured."}' 
		data = json.loads(response.decode('utf-8'))
		return data
	except Exception as e: 
		response = '{"message": "' + str(e) + '"}' 
		print 'Error when getting data: ' + str(e)
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