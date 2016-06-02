from django.conf import settings
from GithubApp import views

def client_id(request):
    return {'client_id': settings.CLIENT_ID}

def access_token(request):
	accessToken = ''
	if 'access_token' in request.session:
		accessToken = request.session['access_token']
	return {'access_token': accessToken}

def user_data(request):
	userData = ''
	if 'access_token' in request.session:
		userData = views.GetData(views.userUrl, request.session['access_token'])
	return {'user_data': userData}