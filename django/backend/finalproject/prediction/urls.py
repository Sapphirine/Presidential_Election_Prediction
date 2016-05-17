from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^showstats$', views.showstats, name='showstats'),
    url(r'^final$', views.final, name='final'),
    url(r'^(?P<name>[a-zA-Z0-9]+)/byname$', views.byname, name='byname'),
    url(r'^stats$', views.stats, name='stats'),
]