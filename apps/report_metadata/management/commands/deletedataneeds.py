from django.core.management.base import BaseCommand
from ...models import AnonyomizedDataNeed


def delete_needs():
    adns = AnonyomizedDataNeed.objects.all()
    r =adns.delete()
    return r
            



class Command(BaseCommand):
    help = "Delet data needs"

    def handle(self, *args, **options):
        r = delete_needs()
        print(r)