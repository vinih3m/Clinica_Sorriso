from django.views.generic import View ,TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect,  render, get_object_or_404
from django.urls import reverse
from openpyxl.styles import Font, Alignment, PatternFill
from django.contrib import messages
from django.http import JsonResponse , HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
import json, openpyxl
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.forms import modelformset_factory
from .mixins import AvisoPermissaoMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from .forms import CriarUsuarioForm, UsuarioContaForm, ProfileForm, FotoProfileForm , DentistaProfileForm, DadosDaClinicaForm, ProdutoEstoqueForm, BaseProdutoEstoqueFormSet
from .models import Profile, DentistaProfile, DadosDaClinica, ProdutoEstoque, RetiradaEstoque
from .forms import AgendamentoForm
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Agendamento
from django.shortcuts import render
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import AgendamentoForm
from django.views.decorators.http import require_POST
from .models import Paciente, Agendamento



# =========================
# LOGIN
# =========================
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('redirect_pos_login')


# =========================
# REDIRECIONAMENTO PÓS LOGIN
# =========================
@login_required(login_url='/login/')
def redirect_pos_login(request):
    return redirect('Tela_Inicial')


# =========================
# ALTERAR SENHA
# =========================
@login_required(login_url='/login/')
def alterar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso!')
        else:
            messages.error(request, 'Não foi possível alterar a senha. Verifique os dados.')

    return redirect('Minha_Conta')

class Dados_Da_ClinicaView(LoginRequiredMixin, UserPassesTestMixin, View):
    pass



# =========================
# TELA INICIAL
# =========================
@method_decorator(never_cache, name='dispatch')
class Tela_InicialView(LoginRequiredMixin, TemplateView):
    template_name = 'Clinica_Sorriso/Tela_Inicial/Tela_Inicial.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['is_admin'] = user.groups.filter(name='Administrador').exists()
        context['is_dentista'] = user.groups.filter(name='Dentista').exists()
        context['is_recepcionista'] = user.groups.filter(name='Recepcionista').exists()

        return context


# CADASTRAR USUÁRIO
@method_decorator([login_required, never_cache], name='dispatch')
class Criar_UsuarioView(LoginRequiredMixin, AvisoPermissaoMixin, CreateView):
    model = User
    form_class = CriarUsuarioForm
    template_name = 'Clinica_Sorriso/Administrador/Usuario/Cadastrar_Usuario.html'
    success_url = reverse_lazy('Tela_Inicial_Administrador')

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()

        grupo_nome = form.cleaned_data['grupo']
        grupo = Group.objects.get(name=grupo_nome)
        user.groups.add(grupo)

        return super().form_valid(form)

# Administrador
@method_decorator(never_cache, name='dispatch')
class Minha_ContaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Clinica_Sorriso/Minha_Conta/Minha_Conta.html'

    def test_func(self):
        return self.request.user.groups.filter( name__in=['Administrador', 'Dentista' , 'Recepcionista']).exists()

    def handle_no_permission(self):
        return redirect('redirect_pos_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        dentista, _ = DentistaProfile.objects.get_or_create(profile=profile)

        context['profile'] = profile
        context['dentista'] = dentista
        context['form'] = PasswordChangeForm(user=self.request.user)

        return context

@method_decorator(never_cache, name='dispatch')
class Editar_Minha_ContaView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'Clinica_Sorriso/Minha_Conta/Editar_Minha_Conta.html'

    def test_func(self): 
        return self.request.user.groups.filter( name__in=['Administrador', 'Dentista', 'Recepcionista']).exists()

    def handle_no_permission(self):
        return redirect('redirect_pos_login')

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)

        user_form = UsuarioContaForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
        foto_form = FotoProfileForm(instance=profile)

        dentista_form = DentistaProfileForm(
            instance=getattr(profile, 'dentistaprofile', None)
        )

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'foto_form': foto_form,
            'dentista_form': dentista_form
        })

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)

        user_form = UsuarioContaForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        foto_form = FotoProfileForm(request.POST, request.FILES, instance=profile)

        dentista_form = DentistaProfileForm(
            request.POST,
            instance=getattr(profile, 'dentistaprofile', None)
        )

        if (
            user_form.is_valid() and
            profile_form.is_valid() and
            foto_form.is_valid() and
            dentista_form.is_valid()
        ):
            user_form.save()
            profile_form.save()
            foto_form.save()

            dentista = dentista_form.save(commit=False)
            dentista.profile = profile
            dentista.save()

            return redirect('Minha_Conta')

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'foto_form': foto_form,
            'dentista_form': dentista_form
        })

class Dados_Da_ClinicaView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'Clinica_Sorriso/Minha_Conta/Dados_Clinica.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    def get(self, request):
        clinica, created = DadosDaClinica.objects.get_or_create(id=1)
        return render(request, self.template_name, {
            'clinica': clinica
        })

    
class Editar_Dados_Da_ClinicaView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'Clinica_Sorriso/Minha_Conta/Editar_Dados_Clinica.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()

    def get(self, request):
        clinica, created = DadosDaClinica.objects.get_or_create(id=1)
        clinica_form = DadosDaClinicaForm(instance=clinica)
        return render(request, self.template_name, {
            'clinica_form': clinica_form
        })

    def post(self, request):
        clinica, created = DadosDaClinica.objects.get_or_create(id=1)
        clinica_form = DadosDaClinicaForm(
            request.POST,
            request.FILES,
            instance=clinica
        )

        if clinica_form.is_valid():
            clinica_form.save()
            return redirect('dados_clinica')

        return render(request, self.template_name, {
            'clinica_form': clinica_form
        })

# Estoque

# Lista todos os produtos do estoque
class ProdutoEstoqueListView(LoginRequiredMixin, ListView):
    model = ProdutoEstoque
    template_name = 'Clinica_Sorriso/Estoque/Estoque.html'
    context_object_name = 'produtos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtra os produtos onde a quantidade atual é menor que a ideal
        produtos_baixos = [
            p for p in self.get_queryset() 
            if p.quantidade_atual < p.quantidade_ideal
        ]
        
        # Adiciona a lista e a contagem ao contexto do HTML
        context['produtos_baixos'] = produtos_baixos
        context['total_criticos'] = len(produtos_baixos)
        return context


def Adicionar_Estoque(request):
    ProdutoFormSet = modelformset_factory(
        ProdutoEstoque,
        form=ProdutoEstoqueForm,
        formset=BaseProdutoEstoqueFormSet,
        extra=0  # 🔥 IMPORTANTE
    )

    if request.method == 'POST':
        data = request.POST.copy()

        total_forms = int(data.get('form-TOTAL_FORMS', 0))
        forms_validos = []

        # 🔥 REMOVE FORMULÁRIOS SEM NOME
        for i in range(total_forms):
            nome = data.get(f'form-{i}-nome', '').strip()
            if nome:
                forms_validos.append(i)

        # ❌ Nenhum produto preenchido
        if not forms_validos:
            messages.error(request, "Adicione pelo menos um produto.")
            return redirect('Estoque')

        # 🔁 REINDEXA
        data['form-TOTAL_FORMS'] = len(forms_validos)
        data['form-INITIAL_FORMS'] = 0

        for novo_i, velho_i in enumerate(forms_validos):
            for campo in ['nome', 'quantidade_atual', 'quantidade_ideal']:
                data[f'form-{novo_i}-{campo}'] = data.get(f'form-{velho_i}-{campo}')

        formset = ProdutoFormSet(data, queryset=ProdutoEstoque.objects.none())

        if formset.is_valid():
            try:
                with transaction.atomic():
                    formset.save()
                messages.success(request, "Produtos adicionados com sucesso!")
                return redirect('Estoque')
            except Exception:
                messages.error(request, "Erro ao salvar no banco de dados.")
        else:
            erros_ja_enviados = set()

            # 🔥 ERROS DO FORMSET (duplicados na lista)
            for error in formset.non_form_errors():
                if error not in erros_ja_enviados:
                    messages.error(request, error)
                    erros_ja_enviados.add(error)

            # 🔥 ERROS DOS FORMS
            for form in formset:
                for error in form.non_field_errors():
                    if error not in erros_ja_enviados:
                        messages.error(request, error)
                        erros_ja_enviados.add(error)

                for field in form:
                    for error in field.errors:
                        if error not in erros_ja_enviados:
                            messages.error(request, error)
                            erros_ja_enviados.add(error)

    else:
        formset = ProdutoFormSet(queryset=ProdutoEstoque.objects.none())

    produtos = ProdutoEstoque.objects.all()
    return render(request, 'Clinica_Sorriso/Estoque/Estoque.html', {
        'formset': formset,
        'produtos': produtos
    })

def Entrada_Produto_Existente(request):
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade'))

        produto = get_object_or_404(ProdutoEstoque, id=produto_id)
        produto.quantidade_atual += quantidade
        produto.save()

        messages.success(
            request,
            f'Entrada realizada: +{quantidade} no produto "{produto.nome}".'
        )

    return redirect('Estoque')

def Confirmar_Entrada_Estoque(request):
    if request.method == 'POST':
        dados_json = request.POST.get('json_dados')
        if not dados_json:
            messages.error(request, "Nenhum dado recebido.")
            return redirect('Estoque')

        try:
            produtos_alterados = json.loads(dados_json)
            with transaction.atomic():
                for item in produtos_alterados:
                    produto = get_object_or_404(ProdutoEstoque, id=item['id'])
                    produto.quantidade_atual += int(item['qtd'])
                    produto.save()
            messages.success(request, "Estoque atualizado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar: {e}")

    return redirect('Estoque')


# Edita produto existente
@login_required
def Editar_Produto_Estoque(request, pk):
    if not request.user.groups.filter(name='Administrador').exists():
        messages.error(request, "Você não tem permissão para editar produtos.")
        return redirect('Estoque')

    produto = get_object_or_404(ProdutoEstoque, pk=pk)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        quantidade_ideal = request.POST.get('quantidade_ideal')

        # evita nome duplicado
        if ProdutoEstoque.objects.exclude(pk=pk).filter(nome__iexact=nome).exists():
            messages.error(request, "Já existe um produto com esse nome.")
            return redirect('Estoque')

        produto.nome = nome
        produto.quantidade_ideal = quantidade_ideal
        produto.save()

        messages.success(request, "Produto atualizado com sucesso.")
        return redirect('Estoque')

class ProdutoEstoqueDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = ProdutoEstoque
    success_url = reverse_lazy('Estoque')
    success_message = "Produto excluído com sucesso!" # O MIXIN USA ISSO

    def delete(self, request, *args, **kwargs):
        # Esta é a forma correta de garantir a mensagem em uma DeleteView
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.groups.filter(name='Administrador').exists()


@login_required
def Retirar_Produto(request, pk):
    produto = get_object_or_404(ProdutoEstoque, pk=pk)

    if request.method == 'POST':
        qtd = int(request.POST.get('quantidade_retirada'))

        if qtd > produto.quantidade_atual:
            messages.error(
                request,
                "Estoque insuficiente para a quantidade solicitada.",
                extra_tags='retirada'
            )
            return redirect(f"{reverse('Estoque')}?produto={produto.id}&nome={produto.nome}&quantidade={produto.quantidade_atual}")


        # ✅ SÓ CHEGA AQUI SE FOR VÁLIDO
        RetiradaEstoque.objects.create(
            produto=produto,
            quantidade_retirada=qtd,
            retirado_por=request.user,
            autorizado_por=request.user
        )

        messages.success(
            request,
            "Retirada realizada com sucesso.",
            extra_tags='retirada'
        )
        return redirect('Estoque')

@login_required
def Historico_De_Retiradas(request):
    # .select_related evita várias consultas ao banco de dados
    retiradas = RetiradaEstoque.objects.select_related('produto', 'retirado_por', 'autorizado_por').all().order_by('-data_retirada')
    
    dados = []
    for r in retiradas:
        dados.append({
            'produto': r.produto.nome,
            'quantidade': r.quantidade_retirada,
            # Pegamos o nome completo. Se não tiver, pegamos o username.
            'retirado_nome': r.retirado_por.get_full_name() or r.retirado_por.username if r.retirado_por else "N/A",
            'autorizado_nome': r.autorizado_por.get_full_name() or r.autorizado_por.username if r.autorizado_por else "Admin",
            'data': r.data_retirada.strftime('%d/%m/%Y')
        })
    
    return JsonResponse({'historico': dados})

@login_required
def Exportar_Estoque_Excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatório de Estoque"

    # 1. Cabeçalho
    cabecalho = ['PRODUTO', 'QUANTIDADE', 'QTD IDEAL', 'NÍVEL CRÍTICO']
    ws.append(cabecalho)

    # Estilos para o Cabeçalho (Fundo azul, letra branca e negrito)
    estilo_cabecalho = Font(bold=True, color="FFFFFF")
    preenchimento_cabecalho = PatternFill(start_color="2196F3", end_color="2196F3", fill_type="solid")
    alinhamento_central = Alignment(horizontal="center", vertical="center")

    for cell in ws[1]: # Aplica na primeira linha
        cell.font = estilo_cabecalho
        cell.fill = preenchimento_cabecalho
        cell.alignment = alinhamento_central

    # 2. Definição das fontes para os dados
    fonte_vermelha = Font(color="FF0000", bold=True)
    fonte_verde = Font(color="00B050", bold=True)

    # 3. Inserção dos Dados
    for produto in ProdutoEstoque.objects.all().order_by('nome'):
        if produto.quantidade_atual < produto.quantidade_ideal:
            nivel_critico = "Sim"
            cor_status = fonte_vermelha
        else:
            nivel_critico = "Não"
            cor_status = fonte_verde
        
        ws.append([
            produto.nome.upper(), # Nome em maiúsculo para padronizar
            produto.quantidade_atual, 
            produto.quantidade_ideal, 
            nivel_critico
        ])

        # Aplica a cor na última célula inserida (Coluna 4) e centraliza
        ws.cell(row=ws.max_row, column=4).font = cor_status
        ws.cell(row=ws.max_row, column=2).alignment = alinhamento_central
        ws.cell(row=ws.max_row, column=3).alignment = alinhamento_central
        ws.cell(row=ws.max_row, column=4).alignment = alinhamento_central

    # 4. FORMATAÇÃO: Ajuste automático da largura das colunas
    # Isso evita que o texto fique cortado
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter # Pega a letra da coluna (A, B, C...)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 5)
        ws.column_dimensions[column].width = adjusted_width

    # 5. Configuração do Download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Estoque Clínica Sorriso & Cia.xlsx"'
    wb.save(response)
    
    return response


from datetime import date, timedelta, datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Agendamento


@login_required
def agenda(request):
    semana = int(request.GET.get("semana", 0))
    data_str = request.GET.get("data")

    if data_str:
        data_base = datetime.strptime(data_str, "%Y-%m-%d").date()
    else:
        data_base = date.today() + timedelta(weeks=semana)

    inicio_semana = data_base - timedelta(days=data_base.weekday())
    fim_semana = inicio_semana + timedelta(days=6)

    # ================= HORÁRIOS =================
    horas = []

    inicio_expediente = "08:00"
    fim_expediente = "18:00"

    for h in range(8, 19):

        # Hora cheia
        hora = f"{h:02}:00"

        horas.append({
            "valor": hora,
            "cheia": True,
            "fechado": hora < inicio_expediente or hora >= fim_expediente
        })

        # Intervalos de 15 minutos
        if h < 18:
            for minuto in ("15", "30", "45"):

                hora = f"{h:02}:{minuto}"

                horas.append({
                    "valor": hora,
                    "cheia": False,
                    "fechado": hora < inicio_expediente or hora >= fim_expediente
                })

    # ================= DIAS =================

    nomes_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    dias = []

    for i in range(7):
        dia = inicio_semana + timedelta(days=i)

        dias.append({
            "data": dia,
            "nome": nomes_dias[dia.weekday()],
            "num": dia.day,
        })

    # ================= AGENDAMENTOS =================

    agendamentos = (
        Agendamento.objects
        .select_related("paciente", "profissional")
        .filter(data__range=[inicio_semana, fim_semana])
    )

    return render(
        request,
        "Clinica_Sorriso/agenda/agenda.html",
        {
            "horas": horas,
            "dias": dias,
            "today": date.today(),
            "agendamentos": agendamentos,
            "semana": semana,
            "data_base": data_base,
        }
    )


@login_required
def criar_agendamento(request):
    if request.method == "POST":
        form = AgendamentoForm(request.POST)

        if form.is_valid():
            nome_paciente = form.cleaned_data["paciente_nome"].strip()

            # 🔹 Busca paciente ignorando maiúsculas/minúsculas
            paciente = Paciente.objects.filter(
                nome__iexact=nome_paciente
            ).first()

            if not paciente:
                paciente = Paciente.objects.create(
                    nome=nome_paciente
                )

            agendamento = form.save(commit=False)
            agendamento.paciente = paciente
            agendamento.save()

            return redirect("agenda")

        else:
            print("FORM INVALIDO:", form.errors)  # ajuda a debuggar

    else:
        form = AgendamentoForm(
            initial={
                "data": request.GET.get("dia"),
                "hora_inicio": request.GET.get("hora"),
            }
        )

    return render(
        request,
        "Clinica_Sorriso/agenda/criar_agendamento.html",
        {"form": form}
    )




from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def alterar_status_agendamento(request):
    id = request.POST.get("id")
    status = request.POST.get("status")

    try:
        ag = Agendamento.objects.get(id=id)
        ag.status = status
        ag.save()

        return JsonResponse({
            "success": True,
            "novo_status": ag.get_status_display()
        })

    except Agendamento.DoesNotExist:
        return JsonResponse({"success": False})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .models import Agendamento, Paciente, Profissional


@login_required
@require_POST
def salvar_retorno(request):
    paciente_nome = request.POST.get("paciente")
    profissional_nome = request.POST.get("profissional")
    dia = request.POST.get("dia")
    hora = request.POST.get("hora")
    motivo = request.POST.get("motivo")

    if not all([paciente_nome, profissional_nome, dia, hora, motivo]):
        return JsonResponse({
            "ok": False,
            "erro": "Dados incompletos."
        }, status=400)

    paciente, _ = Paciente.objects.get_or_create(
        nome__iexact=paciente_nome.strip(),
        defaults={"nome": paciente_nome.strip()}
    )

    try:
        profissional = Profissional.objects.get(
            nome__iexact=profissional_nome.strip()
        )
    except Profissional.DoesNotExist:
        return JsonResponse({
            "ok": False,
            "erro": "Profissional não encontrado."
        }, status=400)

    hora_inicio = datetime.strptime(hora, "%H:%M").time()
    hora_fim = (
        datetime.combine(date.today(), hora_inicio)
        + timedelta(hours=1)
    ).time()

    try:
        Agendamento.objects.create(
            paciente=paciente,
            profissional=profissional,
            data=dia,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            tipo="retorno",      # 👈 Aqui diferencia
            status="pendente",   # 👈 Mantém padrão
            observacoes=motivo
        )
    except ValidationError as e:
        return JsonResponse({
            "ok": False,
            "erro": e.messages[0]
        }, status=400)

    return JsonResponse({"ok": True})


@login_required
def agenda_parcial(request):
    semana = int(request.GET.get("semana", 0))
    data_str = request.GET.get("data")

    if data_str:
        data_base = datetime.strptime(data_str, "%Y-%m-%d").date()
    else:
        data_base = date.today() + timedelta(weeks=semana)

    inicio_semana = data_base - timedelta(days=data_base.weekday())
    fim_semana = inicio_semana + timedelta(days=6)

    horas = []

    for h in range(8, 19):
        horas.append(f"{h:02}:00")
        
        if h < 18:
            horas.append(f"{h:02}:15")
            horas.append(f"{h:02}:30")
            horas.append(f"{h:02}:45")

    nomes_dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    dias = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        dias.append({
            "data": dia,
            "nome": nomes_dias[dia.weekday()],
            "num": dia.day,
        })

    agendamentos = (
        Agendamento.objects
        .select_related("paciente", "profissional")
        .filter(data__range=[inicio_semana, fim_semana])
    )

    return render(
        request,
        "Clinica_Sorriso/agenda/agenda_parcial.html",
        {
            "horas": horas,
            "dias": dias,
            "today": date.today(),
            "agendamentos": agendamentos,
            "semana": semana,
            "data_base": data_base,  # 👈 ADICIONE ISSO
            "inicio_expediente": "08:00",
            "fim_expediente": "18:00",
        }
    )

from django.http import HttpResponse
def exportar_retornos(request):
    return HttpResponse("Exportação ainda não implementada")


from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Q
from datetime import date, timedelta
from .models import Transacao, CategoriaDespesa, Plano
from django.contrib.auth.models import User


def fluxo_caixa(request):
    hoje = date.today()

    # ==========================
    # PEGANDO FILTROS
    # ==========================
    periodo = request.GET.get("periodo")
    busca = request.GET.get("busca")

    tipo = request.GET.getlist("tipo")
    pago = request.GET.get("pago")
    categoria = request.GET.getlist("categoria")
    meio = request.GET.getlist("meio")
    caixa = request.GET.getlist("caixa")
    recibo = request.GET.get("recibo")
    em_atraso = request.GET.get("atraso")

    # Remove valores vazios
    tipo = [t for t in tipo if t]
    categoria = [c for c in categoria if c and c != "todos"]
    meio = [m for m in meio if m and m != "todos"]
    caixa = [c for c in caixa if c and c != "todos"]

    transacoes = Transacao.objects.select_related("categoria", "plano", "profissional").all()

    # ==========================
    # FILTRO DE PERÍODO
    # ==========================
    if periodo == "hoje":
        transacoes = transacoes.filter(data=hoje)

    elif periodo == "30":
        data_inicio = hoje - timedelta(days=30)
        transacoes = transacoes.filter(data__gte=data_inicio)

    elif periodo == "mes":
        transacoes = transacoes.filter(
            data__year=hoje.year,
            data__month=hoje.month
        )

    # ==========================
    # FILTRO BUSCA
    # ==========================
    if busca:
        transacoes = transacoes.filter(
            Q(descricao__icontains=busca) |
            Q(tipo__icontains=busca) |
            Q(valor__icontains=busca)
        )

    # ==========================
    # FILTRO TIPO
    # ==========================
    if tipo:
        transacoes = transacoes.filter(tipo__in=tipo)

    # ==========================
    # FILTRO PAGO
    # ==========================
    if pago in ["0", "1"]:
        transacoes = transacoes.filter(pago=bool(int(pago)))

    # ==========================
    # FILTRO CATEGORIA
    # ==========================
    if categoria:
        transacoes = transacoes.filter(categoria__id__in=categoria)

    # ==========================
    # FILTRO MEIO PAGAMENTO
    # ==========================
    if meio:
        transacoes = transacoes.filter(meio_pagamento__in=meio)

    # ==========================
    # FILTRO CAIXA
    # ==========================
    if caixa:
        transacoes = transacoes.filter(caixa__in=caixa)

    # ==========================
    # FILTRO COM RECIBO
    # ==========================
    if recibo == "1":
        transacoes = transacoes.filter(com_recibo=True)

    # ==========================
    # FILTRO EM ATRASO
    # ==========================
    if em_atraso == "1":
        transacoes = transacoes.filter(
            pago=False,
            data_vencimento__lt=hoje
        )

    # ==========================
    # ORDENAÇÃO
    # ==========================
    transacoes = transacoes.order_by("-data", "-criado_em")

    # ==========================
    # RESUMO
    # ==========================
    
    # RECEITAS
    receitas_recebidas = (
        transacoes.filter(tipo="receita", pago=True)
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )

    receitas_pendentes = (
        transacoes.filter(tipo="receita", pago=False)
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )

    total_receitas_previsto = receitas_recebidas + receitas_pendentes


    # DESPESAS
    despesas_pagas = (
        transacoes.filter(tipo="despesa", pago=True)
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )

    despesas_pendentes = (
        transacoes.filter(tipo="despesa", pago=False)
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )

    total_despesas_previsto = despesas_pagas + despesas_pendentes


    # SALDOS
    saldo = receitas_recebidas - despesas_pagas

    saldo_previsto = (
        total_receitas_previsto -
        total_despesas_previsto
    )


    # CONTADORES
    qtd_receitas = transacoes.filter(tipo="receita").count()

    qtd_despesas = transacoes.filter(tipo="despesa").count()

    qtd_total = transacoes.count()

    categorias = CategoriaDespesa.objects.all().order_by("nome")
    planos = Plano.objects.all().order_by("nome")

    # ✅ lista de profissionais (User) pra usar no select do modal receita
    users = User.objects.all().order_by("username")

    context = {
        "transacoes": transacoes,

        "receitas_recebidas": receitas_recebidas,
        "receitas_pendentes": receitas_pendentes,
        "total_receitas_previsto": total_receitas_previsto,

        "despesas_pagas": despesas_pagas,
        "despesas_pendentes": despesas_pendentes,
        "total_despesas_previsto": total_despesas_previsto,

        "saldo": saldo,
        "saldo_previsto": saldo_previsto,

        "qtd_receitas": qtd_receitas,
        "qtd_despesas": qtd_despesas,
        "qtd_total": qtd_total,

        "categorias": categorias,
        "planos": planos,
        "status_pagamento": Transacao.STATUS_PAGAMENTO,
        "users": users,
    }

    for t in transacoes:
        print(
        "ID:",
        t.id,
        "TIPO:",
        t.tipo,
        "PAGO:",
        t.pago
        )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        lista_html = render_to_string(
            "Clinica_Sorriso/financeiro/partials/_lista_transacoes.html",
            context,
            request=request
        )
        resumo_html = render_to_string(
            "Clinica_Sorriso/financeiro/partials/_resumo.html",
            context,
            request=request
        )
        return JsonResponse({
            "lista": lista_html,
            "resumo": resumo_html
        })

    return render(request, "Clinica_Sorriso/financeiro/fluxo_caixa.html", context)


from django.http import JsonResponse
from django.utils.text import slugify
from .models import CategoriaDespesa

def criar_categoria(request):
    if request.method == "POST":
        nome = request.POST.get("nome")

        if not nome:
            return JsonResponse({"erro": "Nome inválido"}, status=400)

        slug = slugify(nome)

        categoria, created = CategoriaDespesa.objects.get_or_create(
            slug=slug,
            defaults={"nome": nome}
        )

        return JsonResponse({
            "id": categoria.id,
            "nome": categoria.nome,
            "slug": categoria.slug
        })

from django.shortcuts import redirect
from decimal import Decimal

def salvar_despesa(request):
    if request.method == "POST":

        descricao = request.POST.get("descricao")
        valor = request.POST.get("valor")
        data_vencimento = request.POST.get("data_vencimento")
        categoria_id = request.POST.get("categoria")
        caixa = request.POST.get("caixa")
        meio_pagamento = request.POST.get("meio_pagamento")
        observacao = request.POST.get("observacao")
        pago = True if request.POST.get("pago") == "on" else False

        Transacao.objects.create(
            descricao=descricao,
            tipo="despesa",
            valor=Decimal(valor),
            data_vencimento=data_vencimento,
            categoria_id=categoria_id if categoria_id else None,
            caixa=caixa.lower(),  # importante
            meio_pagamento=meio_pagamento,
            observacao=observacao,
            pago=pago
        )

        return redirect("fluxo_caixa")

    return redirect("fluxo_caixa")

from decimal import Decimal
from django.shortcuts import redirect
from .models import Transacao

def salvar_receita(request):

    if request.method == "POST":

        paciente = request.POST.get("paciente")
        data_vencimento = request.POST.get("data_vencimento")
        observacao = request.POST.get("observacao")
        plano_id = request.POST.get("plano")
        profissional_id = request.POST.get("profissional")

        tratamentos = request.POST.getlist("tratamento[]")
        valores = request.POST.getlist("valor[]")

        for tratamento, valor in zip(tratamentos, valores):

            # ignora linhas vazias
            if not tratamento or not valor:
                continue

            Transacao.objects.create(

                paciente_nome=paciente,

                descricao=tratamento,

                tipo="receita",

                valor=Decimal(valor),

                data=data_vencimento,

                data_vencimento=data_vencimento,

                observacao=observacao,

                pago=False,

                plano_id=plano_id if plano_id else None,

                profissional_id=profissional_id if profissional_id else None,

            )

    return redirect("fluxo_caixa")

from django.shortcuts import redirect
from django.utils import timezone
from decimal import Decimal
from .models import Transacao, CategoriaDespesa


def criar_despesa(request):
    if request.method == "POST":

        descricao = request.POST.get("descricao")
        valor = request.POST.get("valor")
        data_vencimento = request.POST.get("data_vencimento")
        categoria_id = request.POST.get("categoria")
        caixa = request.POST.get("caixa")
        meio_pagamento = request.POST.get("meio_pagamento")
        observacao = request.POST.get("observacao")
        pago = True if request.POST.get("pago") else False

        categoria = None
        if categoria_id:
            categoria = CategoriaDespesa.objects.get(id=categoria_id)

        Transacao.objects.create(
            descricao=descricao,
            tipo="despesa",
            valor=Decimal(valor),
            data=data_vencimento,  # 👈 mesma data
            data_vencimento=data_vencimento,
            categoria=categoria,
            caixa=caixa,
            meio_pagamento=meio_pagamento,
            observacao=observacao,
            pago=pago,
        )

        return redirect("fluxo_caixa")

    return redirect("fluxo_caixa")

    
import json

def criar_plano(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nome = data.get("nome")

        plano, created = Plano.objects.get_or_create(nome=nome)

        return JsonResponse({
            "id": plano.id,
            "nome": plano.nome
        })
    

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils.timezone import localdate
from .models import Transacao  # ajuste para seu model real

def exportar_transacoes_pdf(request):

    qs = Transacao.objects.all()

    # ===== mesmos filtros que você já tinha =====

    busca = request.GET.get("busca", "").strip()
    if busca:
        qs = qs.filter(descricao__icontains=busca)

    periodo = request.GET.get("periodo", "")
    hoje = localdate()

    if periodo == "hoje":
        qs = qs.filter(data_vencimento=hoje)
    elif periodo == "mes":
        qs = qs.filter(
            data_vencimento__year=hoje.year,
            data_vencimento__month=hoje.month
        )

    tipos = request.GET.getlist("tipo")
    if tipos:
        qs = qs.filter(tipo__in=tipos)

    pago = request.GET.get("pago")
    if pago in ("0", "1"):
        qs = qs.filter(pago=(pago == "1"))

    # ============================================

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="financeiro.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Relatório Financeiro")
    y -= 25

    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Data")
    p.drawString(100, y, "Descrição")
    p.drawString(350, y, "Tipo")
    p.drawString(420, y, "Valor")
    y -= 15

    p.setFont("Helvetica", 9)

    for t in qs.order_by("-data_vencimento"):

        if y < 50:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica", 9)

        data_str = t.data_vencimento.strftime("%d/%m/%Y") if t.data_vencimento else ""

        p.drawString(40, y, data_str)
        p.drawString(100, y, (t.descricao or "")[:35])
        p.drawString(350, y, str(t.tipo))
        p.drawRightString(520, y, f"R$ {float(t.valor):.2f}".replace(".", ","))

        y -= 14

    p.save()

    return response

# views.py
# views.py
from datetime import timedelta
from django.shortcuts import render
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import localdate
from django.contrib.auth.models import User

from .models import Transacao, PagamentoComissao


def comissoes(request):
    ver = request.GET.get("ver", "aberto")  # aberto | historico
    periodo = request.GET.get("periodo", "mes")  # hoje|semana|mes|mes_passado|30|todos|custom
    profissional = request.GET.get("profissional", "")  # id do User (string)
    de = request.GET.get("de", "")  # YYYY-MM-DD
    ate = request.GET.get("ate", "")  # YYYY-MM-DD

    hoje = localdate()

    # =========================
    # HELPER: aplica período em um queryset
    # =========================
    def aplicar_periodo(qs, campo_data: str):
        """
        campo_data: "data" (Transacao) ou "data_pagamento" (PagamentoComissao)
        """
        if periodo == "hoje":
            return qs.filter(**{campo_data: hoje})

        if periodo == "semana":
            inicio = hoje - timedelta(days=hoje.weekday())  # seg
            fim = inicio + timedelta(days=6)                # dom
            return qs.filter(**{f"{campo_data}__range": [inicio, fim]})

        if periodo == "mes":
            return qs.filter(**{f"{campo_data}__year": hoje.year, f"{campo_data}__month": hoje.month})

        if periodo == "mes_passado":
            primeiro_mes_atual = hoje.replace(day=1)
            ultimo_mes_passado = primeiro_mes_atual - timedelta(days=1)
            return qs.filter(**{
                f"{campo_data}__year": ultimo_mes_passado.year,
                f"{campo_data}__month": ultimo_mes_passado.month
            })

        if periodo == "30":
            inicio = hoje - timedelta(days=30)
            return qs.filter(**{f"{campo_data}__gte": inicio, f"{campo_data}__lte": hoje})

        if periodo == "custom":
            if de:
                qs = qs.filter(**{f"{campo_data}__gte": de})
            if ate:
                qs = qs.filter(**{f"{campo_data}__lte": ate})
            return qs

        # "todos" não filtra
        return qs

    # =========================
    # 1) EM ABERTO (igual ao seu, só organizado)
    # =========================
    if ver == "aberto":
        qs = Transacao.objects.filter(tipo="receita", pago=False)

        if profissional:
            qs = qs.filter(profissional_id=profissional)

        qs = aplicar_periodo(qs, "data")

        linhas = (
            qs.values("profissional_id", "profissional__first_name", "profissional__last_name", "profissional__username")
              .annotate(
                  total=Coalesce(
                      Sum("valor"),
                      0,
                      output_field=DecimalField(max_digits=10, decimal_places=2)
                  )
              )
              .order_by("profissional__first_name", "profissional__username")
        )

    # =========================
    # 2) HISTÓRICO (UMA LINHA POR PAGAMENTO)
    # =========================
    else:
        qs = PagamentoComissao.objects.select_related("profissional")

        if profissional:
            qs = qs.filter(profissional_id=profissional)

        qs = aplicar_periodo(qs, "data_pagamento")

        # ✅ aqui NÃO agrupa: uma linha por pagamento
        linhas = qs.order_by("-data_pagamento", "-id")

    # =========================
    # Select de profissionais
    # (inclui quem tem receita OU quem já tem pagamento no histórico)
    # =========================
    ids_receitas = (
        Transacao.objects.filter(tipo="receita")
        .exclude(profissional__isnull=True)
        .values_list("profissional_id", flat=True)
        .distinct()
    )

    ids_pagamentos = (
        PagamentoComissao.objects
        .values_list("profissional_id", flat=True)
        .distinct()
    )

    profissionais = User.objects.filter(id__in=set(ids_receitas) | set(ids_pagamentos)).order_by("first_name", "username")

    context = {
        "ver": ver,
        "periodo": periodo,
        "profissional": profissional,
        "de": de,
        "ate": ate,
        "profissionais": profissionais,
        "linhas": linhas,
    }
    return render(request, "Clinica_Sorriso/financeiro/comissoes.html", context)

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, Value
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils.timezone import localdate
from datetime import timedelta
from .models import Transacao

def exportar_comissoes_pdf(request):
    ver = request.GET.get("ver", "aberto")             # aberto | historico
    periodo = request.GET.get("periodo", "mes")        # hoje | semana | mes | mes_passado | 30 | todos | custom
    profissional = request.GET.get("profissional", "") # id do User
    de = request.GET.get("de", "")
    ate = request.GET.get("ate", "")

    qs = Transacao.objects.filter(tipo="receita")

    # filtra por profissional (FK)
    if profissional:
        qs = qs.filter(profissional_id=profissional)

    hoje = localdate()

    # período
    if periodo == "hoje":
        qs = qs.filter(data_vencimento=hoje)
    elif periodo == "semana":
        ini = hoje - timedelta(days=hoje.weekday())
        fim = ini + timedelta(days=6)
        qs = qs.filter(data_vencimento__range=[ini, fim])
    elif periodo == "mes":
        qs = qs.filter(data_vencimento__year=hoje.year, data_vencimento__month=hoje.month)
    elif periodo == "mes_passado":
        ano = hoje.year
        mes = hoje.month - 1
        if mes == 0:
            mes = 12
            ano -= 1
        qs = qs.filter(data_vencimento__year=ano, data_vencimento__month=mes)
    elif periodo == "30":
        qs = qs.filter(data_vencimento__gte=hoje - timedelta(days=30))
    elif periodo == "custom":
        if de and ate:
            qs = qs.filter(data_vencimento__range=[de, ate])
        elif de:
            qs = qs.filter(data_vencimento__gte=de)
        elif ate:
            qs = qs.filter(data_vencimento__lte=ate)

    # status (em aberto vs histórico)
    if ver == "aberto":
        qs = qs.filter(pago=False)
    else:
        qs = qs.filter(pago=True)

    # agrupa por profissional
    linhas = (
        qs.values("profissional_id", "profissional__first_name", "profissional__last_name", "profissional__username")
          .annotate(
              total=Coalesce(
                  Sum("valor"),
                  Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
              )
          )
          .order_by("profissional__first_name", "profissional__username")
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="comissoes.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Relatório de Comissões")
    y -= 18

    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Ver: {ver} | Período: {periodo}")
    y -= 22

    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Profissional")
    p.drawRightString(520, y, "Total")
    y -= 14

    p.setFont("Helvetica", 10)

    for row in linhas:
        if y < 60:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica", 10)

        nome = (row["profissional__first_name"] or "").strip()
        sobrenome = (row["profissional__last_name"] or "").strip()
        usern = row["profissional__username"] or "—"
        display = (f"{nome} {sobrenome}".strip()) or usern

        total = row["total"] or 0
        p.drawString(40, y, display[:45])
        p.drawRightString(520, y, f"R$ {float(total):.2f}".replace(".", ","))
        y -= 16

    p.save()
    return response

from django.shortcuts import get_object_or_404, redirect

def receber_transacao(request, pk):

    print("================================")
    print("ENTROU NA VIEW RECEBER")
    print("METHOD =", request.method)
    print("POST =", request.POST)
    print("PK =", pk)
    print("================================")

    if request.method == "POST":

        transacao = get_object_or_404(Transacao, pk=pk)

        print("ANTES:", transacao.pago)

        valor = request.POST.get("valor_pago")

        if valor:
            transacao.valor = valor.replace(",", ".")

        transacao.meio_pagamento = request.POST.get("meio")
        transacao.data = request.POST.get("data_pagamento")
        transacao.observacao = request.POST.get("observacao")
        transacao.pago = True

        transacao.save()

        print("DEPOIS:", transacao.pago)

    return redirect("fluxo_caixa")


from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal
from .models import Transacao

def pagar_despesa(request, transacao_id):

    print("================================")
    print("ENTROU NA VIEW PAGAR")
    print("METHOD =", request.method)
    print("POST =", request.POST)
    print("================================")

    if request.method == "POST":

        transacao = get_object_or_404(
            Transacao,
            id=transacao_id
        )

        # Marca como paga
        transacao.pago = True

        # Atualiza os dados vindos do modal
        valor_pago = request.POST.get("valor_pago")

        if valor_pago:
            valor_pago = valor_pago.replace(",", ".")
            transacao.valor = Decimal(valor_pago)

        transacao.meio_pagamento = request.POST.get(
            "meio_pagamento",
            transacao.meio_pagamento
        )

        transacao.observacao = request.POST.get(
            "observacao",
            transacao.observacao
        )

        data_pagamento = request.POST.get("data_pagamento")
        if data_pagamento:
            transacao.data = data_pagamento

        transacao.save()

        print("SALVOU COM SUCESSO")

    return redirect("fluxo_caixa")

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Transacao

def excluir_despesa(request, transacao_id):
    # Busca a transação ou retorna erro 404 se não existir
    transacao = get_object_or_404(Transacao, id=transacao_id)
    
    # Executa a exclusão no banco de dados
    transacao.delete()
    
    # Opcional: Adiciona uma mensagem de sucesso que você pode exibir na tela
    messages.success(request, "Despesa excluída com sucesso!")
    
    return redirect("fluxo_caixa")

def editar_despesa(request, transacao_id):

    print("POST =", request.POST)

    if request.method == "POST":

        transacao = get_object_or_404(
            Transacao,
            id=transacao_id
        )

        transacao.descricao = request.POST.get("descricao")

        valor = request.POST.get("valor")
        if valor:
            transacao.valor = valor.replace(",", ".")

        transacao.meio_pagamento = request.POST.get("meio_pagamento")

        transacao.observacao = request.POST.get("observacao")

        transacao.save()

        print("SALVOU")

    return redirect("fluxo_caixa")

def cancelar_pagamento(request, transacao_id):

    transacao = get_object_or_404(
        Transacao,
        id=transacao_id
    )

    transacao.pago = False

    transacao.save()

    return redirect("fluxo_caixa")

from django.shortcuts import get_object_or_404, redirect
from .models import Transacao

def cancelar_recebimento(request, transacao_id):

    transacao = get_object_or_404(
        Transacao,
        id=transacao_id
    )

    transacao.pago = False

    transacao.meio_pagamento = None

    transacao.save()

    return redirect("fluxo_caixa")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Etiqueta # Substitua pelo caminho real do seu model de Etiqueta

def salvar_etiqueta_ajax(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        cor = request.POST.get("cor", "#28a745").strip()

        if not nome:
            return JsonResponse({"success": False, "error": "O nome da etiqueta é obrigatório."}, status=400)

        # Cria a etiqueta no banco de dados
        etiqueta = Etiqueta.objects.create(nome=nome, cor=cor)

        return JsonResponse({
            "success": True,
            "id": etiqueta.id,
            "nome": etiqueta.nome,
            "cor": etiqueta.cor
        })
    
    return JsonResponse({"success": False, "error": "Método não permitido."}, status=405)

# =========================================================================
# NOVA VIEW: RESPONSÁVEL POR CRIAR A ETIQUETA VIA REQUISIÇÃO AJAX (JAVASCRIPT)
# =========================================================================
def salvar_etiqueta_ajax(request):
    if request.method == "POST":
        # Converte o nome para minúsculo ou limpa os espaços para evitar duplicados bobos
        nome = request.POST.get("nome", "").strip()
        cor = request.POST.get("cor", "#28a745").strip()

        if not nome:
            return JsonResponse({"success": False, "error": "O nome da etiqueta é obrigatório."}, status=400)

        # get_or_create tenta buscar; se não achar pelo nome, ele cria uma nova!
        etiqueta, criado = Etiqueta.objects.get_or_create(
            nome__iexact=nome, # Busca ignorando maiúsculas/minúsculas
            defaults={'nome': nome, 'cor': cor}
        )

        return JsonResponse({
            "success": True,
            "id": etiqueta.id,
            "nome": etiqueta.nome,
            "cor": etiqueta.cor,
            "criado_agora": criado # Informação extra caso precise
        })
    
    return JsonResponse({"success": False, "error": "Método não permitido."}, status=405)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.apps import apps

@csrf_protect
def pagar_despesas_em_lote(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            data_pagamento = data.get('data_pagamento')
            meio_pagamento = data.get('meio_pagamento')
            observacao = data.get('observacao', '')

            # Carrega o modelo financeiro dinamicamente para evitar ImportError
            # Se a classe se chamar 'Despesas' ou 'FluxoCaixa', mude apenas o nome abaixo
            ModelFinanceiro = apps.get_model('Clinica_Sorriso', 'Despesa')

            for despesa_id in ids:
                despesa = ModelFinanceiro.objects.get(id=despesa_id)
                
                # ATENÇÃO: Copie exatamente os mesmos campos que sua segunda tela altera!
                # Exemplos comuns de campos:
                despesa.status = 'pago'  # ou despesa.pago = True
                despesa.data_pagamento = data_pagamento
                despesa.meio_pagamento = meio_pagamento
                
                if observacao:
                    despesa.observacao = f"{getattr(despesa, 'observacao', '')}\n{observacao}".strip()
                
                despesa.save() # Dispara a atualização de saldos

            return JsonResponse({'sucesso': True})
            
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)})

    return JsonResponse({'sucesso': False, 'erro': 'Método inválido'})

from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from .models import Transacao

@csrf_protect
def editar_receita(request, receita_id):
    if request.method == 'POST':
        try:
            # 1. Busca a receita exata no banco de dados pelo ID
            receita = get_object_or_404(Transacao, id=receita_id)
            
            # 2. Captura os valores enviados pelo JavaScript
            descricao = request.POST.get('descricao')
            valor_texto = request.POST.get('valor', '0')
            data_vencimento = request.POST.get('data_vencimento')
            observacao = request.POST.get('observacao', '')
            paciente_nome = request.POST.get('paciente_nome')
            plano_id = request.POST.get('plano')
            profissional_id = request.POST.get('dentista')

            # 3. CONVERSÃO DIRETA E LIMPA (O JavaScript já mandou o número com ponto exato)
            # Removemos os replaces antigos que multiplicavam o número por 100
            valor_decimal = Decimal(valor_texto) if valor_texto else Decimal('0.00')

            # 4. Injeta as alterações diretamente nas colunas da tabela Transacao
            receita.paciente_nome = paciente_nome
            receita.descricao = descricao
            receita.valor = valor_decimal
            
            # Força a gravação direta da data para atualizar os filtros
            receita.data = data_vencimento
            receita.data_vencimento = data_vencimento
                
            receita.observacao = observacao
            
            # Vincula as chaves estrangeiras tratando de forma segura
            receita.plano_id = int(plano_id) if plano_id and plano_id.isdigit() else None
            receita.profissional_id = int(profissional_id) if profissional_id and profissional_id.isdigit() else None

            # 5. Salva permanentemente no banco de dados
            receita.save()

            print("========== RECEITA ==========")
            print(receita.id)
            print(descricao)
            print(valor_decimal)
            print(data_vencimento)
            print(observacao)
            print("=============================")

            # Retorna o sinalizador de sucesso para o JavaScript recarregar a página
            return JsonResponse({'sucesso': True})
            
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)})

    return JsonResponse({'sucesso': False, 'erro': 'Método inválido'})
