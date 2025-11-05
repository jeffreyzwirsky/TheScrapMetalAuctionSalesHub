from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from auctions.models import *
import random
from datetime import timedelta, datetime, date
import json
from django.core.serializers.json import DjangoJSONEncoder


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.pk
        elif isinstance(obj, models.Model):
            return obj.pk
        return super().default(obj)


class Command(BaseCommand):
    help = 'Creates test data for the auction platform and stores it in a JSON file'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create categories
        categories = ['Art', 'Book', 'Comic', 'Jewellery', 'Fashion', 'Music', 'Movie', 'Sport', 'Electronic']
        for cat in categories:
            Category.objects.get_or_create(name=cat)

        # Create users
        user_objects = []
        for i in range(5):
            user, created = User.objects.get_or_create(username=f'user{i}', email=f'user{i}@example.com')
            user.set_password('password')  # Set a default password
            user.save()
            user_objects.append(user)


        # List to store all created objects
        all_objects = []

        # Create Art items
        art_category = Category.objects.get(name='Art')
        for _ in range(15):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            art = Art.objects.create(
                title=f'Test Art Item',
                description=f'This is a test Art item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=art_category,
                artist_name=f'Artist {random.randint(1, 100)}',
                art_type=random.choice(['Painting', 'Sculpture']),
                dimensions=f'{random.randint(10, 100)}x{random.randint(10, 100)} cm'
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=art,
                user = random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(art)

        # Create Book items
        book_category = Category.objects.get(name='Book')
        for _ in range(15):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            book = Book.objects.create(
                title=f'Test Book Item',
                description=f'This is a test Book item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=book_category,
                author=f'Author {random.randint(1, 100)}',
                genre=random.choice(['Fiction', 'Non-fiction', 'Mystery', 'Fantasy', 'Biography']),
                isbn=f'{random.randint(1000000000000, 9999999999999)}',
                condition=random.choice(['New', 'Used'])
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=book,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(book)

        # Create Comic items
        comic_category = Category.objects.get(name='Comic')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            comic = Comic.objects.create(
                title=f'Test Comic Item',
                description=f'This is a test Comic item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=comic_category,
                issue_number=f'#{random.randint(1, 1000)}',
                publisher=f'Publisher {random.randint(1, 10)}',
                condition=random.choice(['Mint', 'Good', 'Fair'])

            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=comic,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(comic)

        # Create Jewellery items
        jewellery_category = Category.objects.get(name='Jewellery')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            jewellery = Jewellery.objects.create(
                title=f'Test Jewellery Item',
                description=f'This is a test Jewellery item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=jewellery_category,
                jewellery_type=random.choice(['Necklace', 'Ring', 'Bracelet', 'Earrings']),
                material=random.choice(['Gold', 'Silver', 'Platinum', 'Gemstone']),
                size=f'{random.randint(5, 20)} cm'
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=jewellery,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(jewellery)

        # Create Fashion items
        fashion_category = Category.objects.get(name='Fashion')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            fashion = Fashion.objects.create(
                title=f'Test Fashion Item',
                description=f'This is a test Fashion item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=fashion_category,
                fashion_type=random.choice(['Shirt', 'Pants', 'Dress', 'Jacket']),
                size=random.choice(['S', 'M', 'L', 'XL', 'XXL']),
                condition=random.choice(['New', 'Used'])
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=fashion,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(fashion)

        # Create Music items
        music_category = Category.objects.get(name='Music')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            music = Music.objects.create(
                title=f'Test Music Item',
                description=f'This is a test Music item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=music_category,
                artist_name=f'Artist {random.randint(1, 100)}',
                format=random.choice(['Vinyl', 'CD', 'Cassette']),
                genre=f'Genre {random.randint(1, 20)}'
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=music,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(music)

        # Create Movie items
        movie_category = Category.objects.get(name='Movie')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            movie = Movie.objects.create(
                title=f'Test Movie Item',
                description=f'This is a test Movie item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=movie_category,
                director=f'Director {random.randint(1, 50)}',
                format=random.choice(['DVD', 'Blu-ray', 'Digital']),
                genre=f'Genre {random.randint(1, 20)}'
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=movie,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(movie)

        # Create Sport items
        sport_category = Category.objects.get(name='Sport')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            sport = Sport.objects.create(
                title=f'Test Sport Item',
                description=f'This is a test Sport item',
                starting_bid=starting_bid,
                current_bid=current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=sport_category,
                sport_type=random.choice(['Equipment', 'Memorabilia']),
                sport_name=f'Sport {random.randint(1, 30)}',
                condition=random.choice(['New', 'Used'])
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=sport,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(sport)

        # Create Electronic items
        electronic_category = Category.objects.get(name='Electronic')
        for _ in range(10):
            starting_bid = round(random.uniform(10.0, 1000.0), 2)
            current_bid = round(random.uniform(starting_bid, 1000.0), 2)
            seller = random.choice(user_objects)
            electronic = Electronic.objects.create(
                title=f'Test Electronic Item',
                description=f'This is a test Electronic item',
                starting_bid=starting_bid,
                current_bid= current_bid,
                end_time=timezone.now() + timedelta(days=random.randint(1, 30)),
                seller=seller,
                category=electronic_category,
                brand=f'Brand {random.randint(1, 20)}',
                model=f'Model {random.randint(100, 999)}',
                condition=random.choice(['New', 'Used'])
            )
            available_users = [user for user in user_objects if user != seller]
            bid = Bid.objects.create(
                product=electronic,
                user=random.choice(available_users),
                amount=current_bid
            )
            all_objects.append(electronic)

        # Serialize the data
        serialized_data = []
        for obj in all_objects:
            if isinstance(obj, User):
                data = {
                    'model': f'{obj._meta.app_label}.{obj._meta.model_name}',
                    'pk': obj.pk,
                    'fields': {
                        'username': obj.username,
                        'email': obj.email,
                    }
                }
            else:
                data = {
                    'model': f'{obj._meta.app_label}.{obj._meta.model_name}',
                    'pk': obj.pk,
                    'fields': {}
                }
                for field in obj._meta.fields:
                    if field.name != 'id':
                        value = getattr(obj, field.name)
                        if isinstance(value, User):
                            data['fields'][field.name] = value.pk  # Use User's primary key instead of the object
                        elif isinstance(value, (datetime, date )):
                            data['fields'][field.name] = value.isoformat()
                        elif isinstance(value, models.Model):
                            data['fields'][field.name] = value.pk  # Use primary key for other model instances
                        else:
                            data['fields'][field.name] = value
            serialized_data.append(data)

        # Write to JSON file
        with open('test_data.json', 'w') as f:
            json.dump(serialized_data, f, cls=DjangoJSONEncoder, indent=4)

        self.stdout.write(self.style.SUCCESS('Successfully created test data and stored in test_data.json'))