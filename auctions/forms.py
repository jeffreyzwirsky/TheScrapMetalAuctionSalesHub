# SMASH Marketplace - Forms
# Scrap Metal Auction Sales Hub
# File: auctions/forms.py
# REPLACE your existing forms.py with this complete file

from django import forms
from .models import Product, Bid, Category, Package, Sale


class ProductForm(forms.ModelForm):
    """Form for creating/editing catalytic converters"""
    
    image = forms.FileField(
        widget=forms.ClearableFileInput, 
        required=False,
        help_text="Upload photo of the catalytic converter"
    )
    
    class Meta:
        model = Product
        fields = [
            'unique_unit_id',
            'title', 
            'description', 
            'category',
            'package',
            'fullness',
            'appraisal_category',
            'appraisal_value',
            'starting_price',
            'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the catalytic converter (make, model, year, condition)'
            }),
            'unique_unit_id': forms.TextInput(attrs={
                'placeholder': 'e.g., CAT-2025-001'
            }),
            'starting_price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'appraisal_value': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'unique_unit_id': 'Unit ID',
            'starting_price': 'Starting Price ($)',
            'appraisal_value': 'Appraisal Value ($/lb)',
        }
    
    def clean_image(self):
        """Validate image upload"""
        image = self.cleaned_data.get('image')
        if self.instance.pk and self.instance.additional_images.exists() and image:
            raise forms.ValidationError("Maximum images reached for this product.")
        return image


class BidForm(forms.ModelForm):
    """Form for placing bids on catalytic converters"""
    
    class Meta:
        model = Bid
        fields = [
            'amount',
            'appraisal_category',
            'appraisal_value',
            'fullness_applied'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'bid-amount-input',
                'placeholder': 'Enter bid amount'
            }),
            'appraisal_value': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'amount': 'Bid Amount ($)',
            'appraisal_category': 'Appraisal Category',
            'appraisal_value': 'Base Value ($/lb)',
            'fullness_applied': 'Fullness Level'
        }


class PackageForm(forms.ModelForm):
    """Form for creating/editing packages"""
    
    class Meta:
        model = Package
        fields = [
            'name',
            'status',
            'final_weight',
            'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., November 2025 Batch 1'
            }),
            'final_weight': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Internal notes about this package'
            }),
        }
        labels = {
            'final_weight': 'Total Weight (lbs)',
        }


class SaleForm(forms.ModelForm):
    """Form for creating/editing sales (LOTs)"""
    
    class Meta:
        model = Sale
        fields = [
            'lot_number',
            'title',
            'description',
            'packages',
            'zip_code',
            'unit_count',
            'total_weight',
            'seller_type',
            'bid_due_date',
            'pickup_instructions',
            'status'
        ]
        widgets = {
            'lot_number': forms.TextInput(attrs={
                'placeholder': 'e.g., LOT-2025-001'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Thunder Bay Premium Cats - November 2025'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Detailed description of this sale'
            }),
            'zip_code': forms.TextInput(attrs={
                'placeholder': 'e.g., P7A1A1'
            }),
            'unit_count': forms.NumberInput(attrs={
                'min': '0'
            }),
            'total_weight': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'bid_due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),
            'pickup_instructions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Instructions for buyers on how to arrange pickup'
            }),
            'packages': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'lot_number': 'LOT Number',
            'unit_count': 'Total Number of Converters',
            'total_weight': 'Total Weight (lbs)',
            'bid_due_date': 'Bidding Deadline',
        }


class QuickBidForm(forms.Form):
    """Quick bid form for item-by-item bidding interface"""
    
    bid_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'quick-bid-input',
            'placeholder': '0.00',
            'readonly': True  # Calculated automatically
        }),
        label='Calculated Bid'
    )
