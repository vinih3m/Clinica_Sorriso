from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views

from Clinica_Sorriso.views import (
    CustomLoginView,
    redirect_pos_login,
    alterar_senha,
    Tela_InicialView,
    Criar_UsuarioView,
    Minha_ContaView,
    Editar_Minha_ContaView,
    Dados_Da_ClinicaView,
    Editar_Dados_Da_ClinicaView,
    ProdutoEstoqueListView,
    Adicionar_Estoque,
    Entrada_Produto_Existente,
    Confirmar_Entrada_Estoque,
    ProdutoEstoqueDeleteView,
    Editar_Produto_Estoque,
    Retirar_Produto,
    Historico_De_Retiradas,
    Exportar_Estoque_Excel,
    agenda,
    criar_agendamento,
    alterar_status_agendamento,
    editar_despesa
)


urlpatterns = [
    
    # AUTH
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('pos-login/', redirect_pos_login, name='redirect_pos_login'),

    # TELA INICIAL
    path('Tela_Inicial/', Tela_InicialView.as_view(), name='Tela_Inicial'),

    # USUÁRIO
    path('alterar-senha/', alterar_senha, name='alterar_senha'),
    path('cadastrar_usuario/', Criar_UsuarioView.as_view(), name='cadastrar_usuario'),
    path('Minha_Conta/', Minha_ContaView.as_view(), name='Minha_Conta'),
    path('Editar_Minha_Conta/', Editar_Minha_ContaView.as_view(), name='Editar_Minha_Conta'),

    # CLÍNICA
    path('dados_da_clinica/', Dados_Da_ClinicaView.as_view(), name='dados_clinica'),
    path('Editar_dados-da-clinica/', Editar_Dados_Da_ClinicaView.as_view(), name='Editar_dados_clinica'),

    # ESTOQUE (não mexi em nada da lógica)
    path('Estoque/', ProdutoEstoqueListView.as_view(), name='Estoque'),
    path('Adicionar_Estoque/', Adicionar_Estoque, name='Adicionar_Estoque'),
    path('estoque/entrada/existente/', Entrada_Produto_Existente, name='Entrada_Produto_Existente'),
    path('estoque/entrada/confirmar/', Confirmar_Entrada_Estoque, name='Confirmar_Entrada_Estoque'),
    path('Editar_Estoque/<int:pk>/', Editar_Produto_Estoque, name='Editar_Produto_Estoque'),
    path('Deleta_Produto/<int:pk>/', ProdutoEstoqueDeleteView.as_view(), name='Deleta_Produto'),
    path('Retirar_Produto/<int:pk>/', Retirar_Produto, name='Retirar_Produto'),
    path('Historico_De_Retiradas/', Historico_De_Retiradas, name='Historico_De_Retiradas'),
    path('Exportar_Estoque_Excel/', Exportar_Estoque_Excel, name='Exportar_Estoque_Excel'),

    # AGENDA
    path("agenda/", views.agenda, name="agenda"),
    path("agenda/novo/", views.criar_agendamento, name="criar_agendamento"),
    path("agenda/alterar-status/",views.alterar_status_agendamento,name="alterar_status_agendamento"),
    path("agenda/salvar-retorno/", views.salvar_retorno, name="salvar_retorno"),
    path("agenda/parcial/", views.agenda_parcial, name="agenda_parcial"),
    path("exportar-retornos/", views.exportar_retornos, name="exportar_retornos"),
    path("agenda/detalhes/<int:id>/",views.detalhes_agendamento,name="detalhes_agendamento"),
    path("agenda/buscar-pacientes/",views.buscar_pacientes_agenda,name="buscar_pacientes_agenda"),
    path("pacientes/novo/", views.criar_paciente, name="criar_paciente"),
    path("agenda/horarios-livres/",views.horarios_livres_agenda,name="horarios_livres_agenda"),
    path("agenda/etiquetas/criar/", views.criar_etiqueta_agenda, name="criar_etiqueta_agenda"),

    # Financeiro
    path("financeiro/", views.fluxo_caixa, name="financeiro"),
    path("financeiro/fluxo-caixa/", views.fluxo_caixa, name="fluxo_caixa"),
    path("criar-categoria/", views.criar_categoria, name="criar_categoria"),
    path("financeiro/salvar-despesa/", views.salvar_despesa, name="salvar_despesa"),
    path("financeiro/salvar-receita/", views.salvar_receita, name="salvar_receita"),
    path("financeiro/criar-despesa/", views.criar_despesa, name="criar_despesa"),
    path("criar-plano/", views.criar_plano, name="criar_plano"),
    path("financeiro/exportar/", views.exportar_transacoes_pdf, name="exportar_transacoes_pdf"),
    path("financeiro/comissoes/", views.comissoes, name="comissoes"),
    path("financeiro/comissoes/exportar/", views.exportar_comissoes_pdf, name="exportar_comissoes_pdf"),
    path('financeiro/receber/<int:pk>/', views.receber_transacao, name='receber_transacao'),
    path('financeiro/pagar/<int:transacao_id>/', views.pagar_despesa, name='pagar_despesa'),
    path('financeiro/excluir/<int:transacao_id>/', views.excluir_despesa, name='excluir_despesa'),
    path('financeiro/editar/<int:transacao_id>/',views.editar_despesa, name='editar_despesa'),
    path('financeiro/cancelar-pagamento/<int:transacao_id>/',views.cancelar_pagamento, name='cancelar_pagamento'),
    path('financeiro/cancelar-recebimento/<int:transacao_id>/', views.cancelar_recebimento, name='cancelar_recebimento'),
    path('financeiro/salvar-etiqueta/', views.salvar_etiqueta_ajax, name='salvar_etiqueta_ajax'),
    path("financeiro/editar-receita/<int:receita_id>/", views.editar_receita, name="editar_receita"),


]
