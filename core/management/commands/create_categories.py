from django.core.management.base import BaseCommand
from core.models import Category


class Command(BaseCommand):
    help = "Create default categories for projects"

    def handle(self, *args, **options):
        categories = [
            "Machine Learning",
            "Data Visualization",
            "Deep Learning",
            "Natural Language Processing",
            "Computer Vision",
            "Data Analysis",
            "Big Data",
            "Learning",
            "Research",
        ]

        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(f'Category already exists: {category_name}')

        self.stdout.write(self.style.SUCCESS(f'\nTotal categories: {Category.objects.count()}'))
