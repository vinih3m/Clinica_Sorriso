from django import forms
from django.forms import BaseModelFormSet
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, DentistaProfile, UFChoices, DadosDaClinica, ProdutoEstoque
from .models import Agendamento

# Cadastro de Usuário
class CriarUsuarioForm(forms.ModelForm):
    grupo = forms.ChoiceField(
        choices=[
            ('', 'Selecione'),
            ('Administrador', 'Administrador'),
            ('Dentista', 'Dentista'),
            ('Recepcionista', 'Recepcionista'),
        ],
        label='Tipo de usuário',
        widget=forms.Select()
    )

    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput()
    )

    password2 = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',  
            'last_name',   
            'email'
        ]
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email'
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'As senhas não conferem')
        return cleaned_data

# Foto
class FotoProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['foto']

class UsuarioContaForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.HiddenInput(),
        }
        labels = {
            'username': 'Usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    estado = forms.ChoiceField(
        choices=UFChoices.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False, 
    )

    class Meta:
        model = Profile
        exclude = ['user']
        widgets = {
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_pais_telefone': forms.Select(attrs={'class': 'form-select'}),
            'codigo_pais_whatsapp': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            self.fields['sexo'].widget.attrs.update({'class': 'form-select'})
            self.fields['estado'].widget.attrs.update({'class': 'form-select'})

class DentistaProfileForm(forms.ModelForm):
    class Meta:
        model = DentistaProfile
        exclude = ['profile'] 
        widgets = {
            'conselho_tipo': forms.Select(attrs={'class': 'form-select'}),
            'numero_conselho': forms.TextInput(attrs={'class': 'form-control'}),
            'uf_conselho': forms.Select(attrs={'class': 'form-select'}),
        }

class DadosDaClinicaForm(forms.ModelForm):
    class Meta:
        model = DadosDaClinica
        fields = '__all__'
        widgets = {
            'nome_clinica': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control','accept': 'image/*'}),

            'nome_comunicacoes': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_clinica': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'horario_fim': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'fuso_horario': forms.Select(attrs={'class': 'form-select'}),
            'emitir_recibo_em_nome_de': forms.Select(attrs={'class': 'form-select'}),
            'email_clinica': forms.EmailInput(attrs={'class': 'form-control'}),
            'codigo_pais_telefone_clinica': forms.Select(attrs={'class': 'form-select'}),
            'codigo_pais_celular_clinica': forms.Select(attrs={'class': 'form-select'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            self.fields['fuso_horario'].widget.attrs.update({'class': 'form-select'})
            self.fields['estado'].widget.attrs.update({'class': 'form-select'})
            self.fields['emitir_recibo_em_nome_de'].widget.attrs.update({'class': 'form-select'})


class BaseProdutoEstoqueFormSet(BaseModelFormSet):

    def validate_unique(self):
        pass

    def clean(self):
        super().clean()

        nomes = set()

        for form in self.forms:
            if not form.cleaned_data:
                continue

            nome = form.cleaned_data.get('nome')
            if not nome:
                continue

            nome_normalizado = nome.strip().lower()

            if nome_normalizado in nomes:
                raise ValidationError(
                    "Há produtos repetidos no formulário. Verifique os nomes."
                )

            nomes.add(nome_normalizado)

class ProdutoEstoqueForm(forms.ModelForm):
    class Meta:
        model = ProdutoEstoque
        fields = ['nome', 'quantidade_atual', 'quantidade_ideal']
        validate_unique = False 
        error_messages = {
            'nome': {'unique': ''},
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'quantidade_atual': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'quantidade_ideal': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()

        exists = ProdutoEstoque.objects.filter(nome__iexact=nome)
        if self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise ValidationError(
                f"O produto '{nome}' já está cadastrado no sistema."
            )

        return nome
    

# ============================
# FORMULÁRIO DE AGENDAMENTO
# ============================
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Agendamento


class AgendamentoForm(forms.ModelForm):

    paciente_nome = forms.CharField(
        label="Paciente",
        max_length=100,
        widget=forms.TextInput(attrs={
            "placeholder": "Digite o nome do paciente"
        })
    )

    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "style": "resize:none;",
                "maxlength": "500",
                "placeholder": "Observação"
            }
        )
    )

    class Meta:
        model = Agendamento
        fields = [
            "paciente_nome",
            "profissional",
            "data",
            "hora_inicio",
            "hora_fim",
            "observacoes",
        ]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        profissionais = (
            User.objects
            .filter(is_active=True)
            .filter(
                Q(groups__name__iexact="Medico") |
                Q(groups__name__iexact="Médico") |
                Q(groups__name__iexact="Administrador") |
                Q(is_superuser=True)
            )
            .order_by("first_name", "username")
            .distinct()
        )

        self.fields["profissional"].queryset = profissionais
        self.fields["profissional"].empty_label = "---------"

        self.fields["profissional"].widget.attrs.update({
            "class": "select-profissional-agendamento"
        })