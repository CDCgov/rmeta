from django import forms
from .models import RequestAccess

class RequestAccessForm(forms.ModelForm):
    math_quiz = forms.IntegerField(label='What is 2 + 3?')
    class Meta:
        model = RequestAccess
        fields = ['first_name', 'last_name', 'email', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }
    
    def clean_math_quiz(self):
        data = self.cleaned_data['math_quiz']
        if data != 5:
            raise forms.ValidationError("Math quiz answer is incorrect.")
        return data


