from django.urls import include, path
from rest_framework import routers
from fio_chart_project.fio_chart import views


urlpatterns = [
    path('chart_log/', views.upload_fio_log),
	path('automate_fio_form/', views.automate_fio_test_and_chart),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
