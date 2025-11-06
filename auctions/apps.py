# SMASH Marketplace - Django App Configuration
# Scrap Metal Auction Sales Hub  
# File: auctions/apps.py
# REPLACE your existing apps.py with this complete file

from django.apps import AppConfig


class AuctionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auctions'
    verbose_name = 'SMASH Marketplace - Catalytic Converter Auctions'
