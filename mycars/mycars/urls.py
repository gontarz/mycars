from django.contrib import admin
from django.urls import include, path
from django.utils.safestring import mark_safe
from rest_framework import routers

from cars.views import CarViewSet, PopularViewSet, RateViewSet


class MyCarsRootView(routers.APIRootView):
    """
    Controls appearance of the API root view
    """

    def get_view_name(self) -> str:
        return "MyCars"

    def get_view_description(self, html=False) -> str:
        text = "Main View"
        if html:
            return mark_safe(f"<p>{text}</p>")
        else:
            return text


class MyCarsRouter(routers.DefaultRouter):
    APIRootView = MyCarsRootView


router = MyCarsRouter()

router.register(r'cars', CarViewSet, basename='cars')
router.register(r'rate', RateViewSet)
router.register(r'popular', PopularViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls))
]
