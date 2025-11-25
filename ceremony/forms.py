from django import forms
from .models import Graduate


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Scan or type Student ID, Name, Email or Unique ID',
            'list': 'search-options',
            'autofocus': 'autofocus',
        })
    )


class CheckInForm(forms.ModelForm):
    staff_initials = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Optional – your initials for audit'
    )

    class Meta:
        model = Graduate
        fields = [
            'attended',
            'seat_row',
            'seat_number',
            'presentation_order',
            'photo',
        ]
        widgets = {
            'attended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seat_row': forms.TextInput(attrs={'class': 'form-control'}),
            'seat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'presentation_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GownForm(forms.ModelForm):
    class Meta:
        model = Graduate
        fields = [
            'gown_size',
            'gown_collected',
            'gown_returned',
            'gown_notes',
        ]
        widgets = {
            'gown_size': forms.TextInput(attrs={'class': 'form-control'}),
            'gown_collected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gown_returned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gown_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StudentDetailForm(forms.ModelForm):
    """Combined view/edit form for admin student detail page."""

    class Meta:
        model = Graduate
        fields = [
            'attended',
            'seat_row',
            'seat_number',
            'presentation_order',
            'gown_size',
            'gown_collected',
            'gown_returned',
            'gown_notes',
            'photo',
        ]
        widgets = {
            'attended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seat_row': forms.TextInput(attrs={'class': 'form-control'}),
            'seat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'presentation_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'gown_size': forms.TextInput(attrs={'class': 'form-control'}),
            'gown_collected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gown_returned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gown_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
