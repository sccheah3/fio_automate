from django.urls import include, path
from rest_framework import routers
from fio_chart_project.fio_chart import views

app_name = 'drive_benchmark'

urlpatterns = [
	path('drives/', views.view_drives, name="drives"),
	path('drives/<int:drive_id>/', views.drive_detail, name='drive_detail'),
	path('drives/performance_comparison/', views.performance_comparison, name='performance_comparison'),
    path('chart_log/', views.upload_fio_log, name="upload_fio_logs"),
	path('automate_fio_form/', views.automate_fio_test_and_chart, name="automate_fio"),
	path('upload_performance_data/', views.parse_and_save_performance, name="parse_and_save"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
