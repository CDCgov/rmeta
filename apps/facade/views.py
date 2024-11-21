from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import SubmissionForm


def home(request):
    return render(request, 'facade/home.html')

def submit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubmissionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    return render(request, 'facade/submit.html')