from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import MDN
from django.template.loader import render_to_string
import os

def create_readme(directory_name):
    mdns = MDN.objects.all().order_by('common_name')
    # open the README.md file and read its contents
    readme_path = os.path.join(settings.BASE_DIR, "apps", 
                               "sophv", "templates", 
                               "sophv", "README.md")
    notfound_path = os.path.join(settings.BASE_DIR, "apps", 
                               "sophv", "templates", 
                               "sophv", "non-found.json")
    
    with open(readme_path, 'r') as readme_file:
        my_markdown = readme_file.read()

    context = {'mdns': mdns, 'direcorty_name': directory_name,
               "my_markdown": my_markdown}
    rendered_template = render_to_string('sophv/README.html', context)
    with open(f"{directory_name}/README.html", 'w') as index_file:
        index_file.write(rendered_template)
    rendered_template = render_to_string('sophv/notfound.json', {})
    with open(f"{directory_name}/notfound.json", 'w') as notfound_file:
        notfound_file.write(rendered_template)

   
class Command(BaseCommand):
    help = "Export README.html"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('directory_name')

    def handle(self, *args, **options):
        create_readme(options['directory_name'])
         # Create the directory if it doesn't exist
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created README.html.'))

