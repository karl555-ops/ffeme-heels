from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


class LoginForm(forms.Form):
    identificador = forms.CharField(
        label="Usuario o correo",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "usuario o correo@gmail.com"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Tu contraseña"}),
    )


class RegistroForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nombre de usuario"}),
    )
    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={"placeholder": "correo@gmail.com"}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Crea una contraseña"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "Repite la contraseña"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        if password1:
            try:
                validate_password(password1)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        return cleaned_data
