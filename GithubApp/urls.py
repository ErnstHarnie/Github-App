from django.conf.urls import url

from . import views

app_name = 'Github-App'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^index/$', views.index, name='index'),
	url(r'^repository/$', views.repository, name='repository'),
	#url(r'^$repository/(?P<owner_name>[A-z 0-9&.-_+]+)/(?P<repo_name>[A-z 0-9&.-_+]+)/$', views.repository, name='repository'),
	url(r'^add/$', views.index, name='add'),
	url(r'^download/(?P<owner_name>[A-z 0-9&.-_+]+)/(?P<repo_name>[A-z 0-9&.-_+]+)/(?P<branch_name>[A-z 0-9&.-_+]+)/$', views.download, name='download')
#
]