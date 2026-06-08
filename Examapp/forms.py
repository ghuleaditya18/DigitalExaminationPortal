import re

from django import forms
from django.contrib.auth.hashers import make_password

from .models import UserInfo


BLOCKED_WORDS = {
    'admin', 'root', 'system',
    'abuse', 'fuck', 'shit', 'bitch',
}
COMMON_PASSWORDS = {'password123', 'admin123', '12345678'}
USERNAME_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9_.]{4,19}$')
MOBILE_PATTERN = re.compile(r'^[6-9][0-9]{9}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%&*!])\S{8,16}$')


def validate_username(username):
    if not USERNAME_PATTERN.fullmatch(username):
        raise forms.ValidationError(
            'Username must be 5 to 20 characters, start with a letter, and '
            'contain only letters, numbers, underscores, or periods.'
        )
    if re.search(r'[_.]{2}', username):
        raise forms.ValidationError('Consecutive underscores or periods are not allowed.')
    lowered = username.lower()
    if any(word in lowered for word in BLOCKED_WORDS):
        raise forms.ValidationError('Username contains a blocked or reserved word.')
    return username


def validate_password(password, username):
    if not PASSWORD_PATTERN.fullmatch(password):
        raise forms.ValidationError(
            'Password must be 8 to 16 characters and include uppercase, '
            'lowercase, number, and one special character: @ # $ % & * !'
        )
    if password.lower() == (username or '').lower():
        raise forms.ValidationError('Password must not be the same as the username.')
    if password.lower() in COMMON_PASSWORDS:
        raise forms.ValidationError('Choose a stronger password.')
    return password


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text='8-16 characters with uppercase, lowercase, number and special character.',
    )

    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'mobile_no', 'role']
        help_texts = {
            'username': '5-20 characters. Start with a letter; use letters, numbers, underscores or periods.',
            'mobile_no': 'Enter a unique 10-digit Indian mobile number starting with 6, 7, 8 or 9.',
        }

    def clean_username(self):
        return validate_username(self.cleaned_data['username'])

    def clean_mobile_no(self):
        mobile = self.cleaned_data['mobile_no']
        if not MOBILE_PATTERN.fullmatch(mobile):
            raise forms.ValidationError(
                'Mobile number must contain exactly 10 digits and start with 6, 7, 8, or 9.'
            )
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        if password:
            try:
                cleaned_data['password'] = validate_password(
                    password, cleaned_data.get('username')
                )
            except forms.ValidationError as error:
                self.add_error('password', error)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class StudentProfileForm(UserForm):
    class Meta(UserForm.Meta):
        fields = ['username', 'password', 'mobile_no']


class OTPForm(forms.Form):
    otp = forms.CharField(
        label='6-digit OTP',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
    )

    def clean_otp(self):
        otp = self.cleaned_data['otp']
        if not otp.isdigit():
            raise forms.ValidationError('OTP must contain exactly 6 digits.')
        return otp


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=100)
    mobile_no = forms.CharField(max_length=10)


class ResetPasswordForm(forms.Form):
    password = forms.CharField(label='New password', widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, username='', **kwargs):
        self.username = username
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        if password:
            try:
                validate_password(password, self.username)
            except forms.ValidationError as error:
                self.add_error('password', error)
        if password and password != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data
