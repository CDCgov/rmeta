from django import forms
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['tcn', 'tcr', 'cri_1', 'cri_2', 'cri_3', 'cri_4', 'cri_5', 
                  'dai', 'multiple_entries', 'payload_type', 'payload_file']