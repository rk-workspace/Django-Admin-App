from django.urls import include, path
from rest_framework import routers
from divine import views
from django.contrib import admin

router = routers.DefaultRouter()
router.register(r'raw_materials', views.RawMaterialsViewSet)
router.register(r'finished_goods', views.FinishedGoodsViewSet)
router.register(r'compositions', views.CompositionsView, basename="compositions")
router.register(r'job_cards', views.JobCardsViewSet)
router.register(r'composition_search', views.CompositionSearchViewSet, basename="composition_search")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('divineapp/api/', include(router.urls)),
    path('divineapp/auth/login', views.Login.as_view(), name="login"),
    path('divineapp/auth/register', views.Register.as_view(), name="register"), 
    path('divineapp/auth/check-auth', views.CheckSession.as_view(), name="check-session"),
    path('divineapp/auth/logout', views.Logout.as_view(), name="logout"),
    path('divineapp/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('divineapp/admin/', admin.site.urls)
]


# urlpatterns = [
#     path('materials', RawMaterialsListView.as_view(), name = 'raw_materials_list'),
#     path('materials/add/', RawMaterialsCreateView.as_view(), name = 'raw_materials_add'),
#     path('materials/<int:pk>/edit/',RawMaterialsUpdateView.as_view(), name = 'raw_materials_edit'),
#     path('goods/add/', FinishedGoodsCreateView.as_view(), name = 'finished_goods_add'),
#     path('goods', FinishedGoodsListView.as_view(), name = 'finished_goods_list'),
#     path('goods/<int:pk>/edit/', FinishedGoodsUpdateView.as_view(), name = 'finished_goods_edit'),
# ]
