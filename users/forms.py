from django import forms
from users.models import Status, Profile
from django.contrib.auth.models import User

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['image']

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'display_name', 'bio', 'location', 'pronouns']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'maxlength': '250',
                'placeholder': 'Tell us about yourself...'
            }),
            'pronouns': forms.Select(attrs={
                'class': 'pronoun-select'
            })
        }
        help_texts = {
            'bio': 'Max 250 characters',
            'profile_picture': 'Upload a clear profile photo'
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 250:
            raise ValidationError("Bio cannot exceed 250 characters")
        return bio

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            if image.size > 2*1024*1024:  # 2MB limit
                raise ValidationError("Image file too large (max 2MB)")
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError("Only JPG/PNG files allowed")
        return image