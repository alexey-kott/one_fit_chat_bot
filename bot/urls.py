from django.conf.urls import url

from . import views




urlpatterns = [
    url(r'^$', views.auth, name='auth'),
    # url(r'^auth/', views.auth, name='auth'),
    url(r'^deauth/', views.deauth, name='deauth'),
    url(r'^admin/', views.admin, name='admin'),
]