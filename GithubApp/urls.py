from django.conf.urls import url

from . import views

app_name = 'Github-App'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^index/$', views.index, name='index'),
	url(r'^repository/$', views.repository, name='repository'),
	#url(r'^details/(?P<username>[A-z 0-9&.-_+]+)/(?P<repository>[A-z 0-9&.-_+]+)/(?P<sha>[A-z 0-9&.-_+]+)/$', views.details, name='details'),
	url(r'^details/(?P<username>[A-z 0-9&-_+]+)/(?P<repository>.*)/(?P<sha>[A-z 0-9&.-_+]+)/$', views.details, name='details'),
	url(r'^add/$', views.index, name='add'),
	#url(r'^details/(?P<username>[A-z 0-9&.-_+]+)/(?P<repository>[A-z 0-9&.-_+]+)/(?P<sha>[A-z 0-9&.-_+]+)/$', views.details, name='details')
	#url(r'^download/(?P<owner_name>[A-z 0-9&.-_+]+)/(?P<repo_name>[A-z 0-9&.-_+]+)/(?P<branch_name>[A-z 0-9&.-_+]+)/$', views.download, name='download')
#
]