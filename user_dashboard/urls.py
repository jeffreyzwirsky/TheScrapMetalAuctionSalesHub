from django.urls import path
from .views import *

urlpatterns = [

    path('user_dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('favorites/', FavoritesView.as_view(), name='favorites'),
    path('products_on_sale/', ProductsOnSaleView.as_view(), name='products_on_sale'),
    path('submitted_bids/', SubmittedBidsView.as_view(), name='submitted_bids'),

]

