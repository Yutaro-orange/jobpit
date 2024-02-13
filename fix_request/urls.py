from django.urls import path
from .views import (
    FixAttendanceRequestView
)

urlpatterns = [
    path('request', FixAttendanceRequestView.as_view(), name='fix_request')
]
