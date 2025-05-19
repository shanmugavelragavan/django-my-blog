from sre_parse import CATEGORIES
from typing import Any
from unicodedata import category
from blog.models import Category
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Populate data into the category model'

    def handle(self, *args: Any, **options: Any):
      # Delete existing data
      Category.objects.all().delete()

      CATEGORIES = [
          "Technology",
          "Science",
          "Sports",
          "Music",
          "Art",
      ]

      for category_name in CATEGORIES:
          Category.objects.create(name=category_name)

      self.stdout.write(self.style.SUCCESS("Data populated_category successfully!"))