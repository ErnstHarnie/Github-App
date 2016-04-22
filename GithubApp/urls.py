from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^index$', views.index, name='index'),
	url(r'^add$', views.add, name='add'),
	url(r'^addrepository$', views.addrepository, name='addrepository')
]