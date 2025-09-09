from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Quote
from django.core.validators import RegexValidator


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
                message='Пароль должен содержать минимум 8 символов, включая буквы и цифры.',
                code='password_too_short'
            )
        ]
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = "Подтвердите пароль"
        self.fields['password2'].widget.attrs.update(
            {'placeholder': 'Подтвердите пароль'})


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите имя пользователя'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = User.objects.filter(username=username).first()
            if not self.user or not self.user.check_password(password):
                raise forms.ValidationError("Неверный логин или пароль.")
        return cleaned_data


class AddQuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['source', 'text', 'weight']
        labels = {
            'source': 'Источник',
            'text': 'Цитата',
            'weight': 'Вес (по умолчанию 1)',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weight'].required = False
