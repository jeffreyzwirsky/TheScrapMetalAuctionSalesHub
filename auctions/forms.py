from django import forms
from .models import *


class ProductForm(forms.ModelForm):
    image = forms.FileField(widget=forms.ClearableFileInput, required=False)
    end_time = forms.DateTimeField(
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = ['title', 'description', 'starting_bid', 'end_time', 'category']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if self.instance.pk and self.instance.images.exists() and image:
            raise forms.ValidationError("You can't add images when one already exists.")
        return image


class ArtForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Art
        fields = ProductForm.Meta.fields + ['artist_name', 'art_type', 'dimensions']


class BookForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Book
        fields = ProductForm.Meta.fields + ['author', 'genre', 'isbn', 'condition']


class ComicForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Comic
        fields = ProductForm.Meta.fields + ['issue_number', 'publisher', 'condition']


class JewelleryForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Jewellery
        fields = ProductForm.Meta.fields + ['jewellery_type', 'material', 'size']


class FashionForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Fashion
        fields = ProductForm.Meta.fields + ['fashion_type', 'size', 'condition']


class MusicForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Music
        fields = ProductForm.Meta.fields + ['artist_name', 'format', 'genre']


class MovieForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Movie
        fields = ProductForm.Meta.fields + ['director', 'format', 'genre']


class SportForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Sport
        fields = ProductForm.Meta.fields + ['sport_type', 'sport_name', 'condition']


class ElectronicForm(ProductForm):
    class Meta(ProductForm.Meta):
        model = Electronic
        fields = ProductForm.Meta.fields + ['brand', 'model', 'condition']


form_mapping = {
            'Art': ArtForm,
            'Music': MusicForm,
            'Comic': ComicForm,
            'Book': BookForm,
            'Jewellery': JewelleryForm,
            'Fashion': FashionForm,
            'Movie': MovieForm,
            'Sport': SportForm,
            'Electronic': ElectronicForm}
