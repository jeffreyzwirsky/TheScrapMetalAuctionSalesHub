from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    objects = InheritanceManager()

    def __str__(self):
        return self.title



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')


# Specific Product Types


class Art(Product):
    artist_name = models.CharField(max_length=100)
    art_type = models.CharField(max_length=20, choices=[('Painting', 'Painting'), ('Sculpture', 'Sculpture')])
    dimensions = models.CharField(max_length=50)


class Book(Product):
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=50, choices=[
        ('Fiction', 'Fiction'), ('Non-fiction', 'Non-fiction'),
        ('Mystery', 'Mystery'), ('Fantasy', 'Fantasy'), ('Biography', 'Biography')
    ])
    isbn = models.CharField(max_length=13)
    condition = models.CharField(max_length=10, choices=[('New', 'New'), ('Used', 'Used')])


class Comic(Product):
    issue_number = models.CharField(max_length=20)
    publisher = models.CharField(max_length=100)
    condition = models.CharField(max_length=10, choices=[('Mint', 'Mint'), ('Good', 'Good'), ('Fair', 'Fair')])


class Jewellery(Product):
    jewellery_type = models.CharField(max_length=20, choices=[
        ('Necklace', 'Necklace'), ('Ring', 'Ring'),
        ('Bracelet', 'Bracelet'), ('Earrings', 'Earrings')
    ])
    material = models.CharField(max_length=20, choices=[
        ('Gold', 'Gold'), ('Silver', 'Silver'),
        ('Platinum', 'Platinum'), ('Gemstone', 'Gemstone')
    ])
    size = models.CharField(max_length=20, blank=True, null=True)


class Fashion(Product):
    fashion_type = models.CharField(max_length=20, choices=[
        ('Shirt', 'Shirt'), ('Pants', 'Pants'),
        ('Dress', 'Dress'), ('Jacket', 'Jacket')
    ])
    size = models.CharField(max_length=5, choices=[
        ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')
    ])
    condition = models.CharField(max_length=10, choices=[('New', 'New'), ('Used', 'Used')])


class Music(Product):
    artist_name = models.CharField(max_length=100)
    format = models.CharField(max_length=20, choices=[
        ('Vinyl', 'Vinyl'), ('CD', 'CD'), ('Cassette', 'Cassette')
    ])
    genre = models.CharField(max_length=50)


class Movie(Product):
    director = models.CharField(max_length=100)
    format = models.CharField(max_length=20, choices=[
        ('DVD', 'DVD'), ('Blu-ray', 'Blu-ray'), ('Digital', 'Digital')
    ])
    genre = models.CharField(max_length=50)


class Sport(Product):
    sport_type = models.CharField(max_length=20, choices=[
        ('Equipment', 'Equipment'), ('Memorabilia', 'Memorabilia')
    ])
    sport_name = models.CharField(max_length=50)
    condition = models.CharField(max_length=10, choices=[('New', 'New'), ('Used', 'Used')])


class Electronic(Product):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    condition = models.CharField(max_length=10, choices=[('New', 'New'), ('Used', 'Used')])


# Favorite

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate favorites





# Bids



class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def validate_bid(self):
        if self.product.current_bid is not None:
            if self.amount <= self.product.current_bid:
                raise ValidationError({"amount": "Bid must be higher than current bid."})
            else:
                if self.amount <= self.product.starting_bid:
                    raise ValidationError({"amount": "Bid must be higher than starting bid."})

    def clean(self):
        self.validate_bid()
