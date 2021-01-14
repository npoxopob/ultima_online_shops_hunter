from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.StoreFront.as_view(), name='store_front'),
	path('result', views.Result.as_view(), name='result'),
	path('categories', views.Category.as_view(), name='categories'),
	path('item_statistic', views.Itemstatistic.as_view(), name='item_statistic'),
	path('vendors', views.Vendors.as_view(), name='vendors'),
	path('vendor_productes', views.VendorProducts.as_view(), name='vendor_productes'),
	path('login', views.ShopLogin.as_view(), name='login'),
	path('logout', auth_views.LogoutView.as_view(template_name='store/logout.html'), name='logout'),
]