from django.conf.urls import url

from . import views

app_name = 'Github-App'

urlpatterns = [
	url(r'^$', views.repository, name='repository'),
	url(r'^index/$', views.repository, name='repository'),
	url(r'^repository/$', views.repository, name='repository'),
	url(r'^details/(?P<username>[A-z 0-9&-_+]+)/(?P<repository>.*)/(?P<sha>[A-z 0-9&.-_+]+)/', views.details, name='details'),
	url(r'^add/$', views.add, name='add'),
	url(r'^authorize/$', views.authorize, name='authorize'),
]