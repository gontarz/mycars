from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from cars.views import CarViewSet, RateViewSet, PopularViewSet

router = routers.DefaultRouter()
router.register(r'cars', CarViewSet, basename='cars')
router.register(r'rate', RateViewSet)
router.register(r'popular', PopularViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls))
]
