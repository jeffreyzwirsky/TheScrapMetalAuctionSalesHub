# SMASH Marketplace - URL Configuration
# Scrap Metal Auction Sales Hub
# File: auctions/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    # Product (Catalytic Converter) URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', CategorySelectView.as_view(), name='product_create'),
    path('products/create/<str:category>/', ProductCreateView.as_view(), name='product_create_with_category'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    
    # Bidding URLs
    path('products/<int:pk>/bid/', place_bid, name='place_bid'),
    
    # Sale (LOT) URLs
    path('sales/', SaleListView.as_view(), name='sale_list'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale_detail'),
    path('sales/<int:pk>/watch/', toggle_favorite, name='toggle_favorite'),
    
    # Dashboard URLs
    # path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
]
