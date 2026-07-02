from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin

class AvisoPermissaoMixin(UserPassesTestMixin):
    mensagem_sem_permissao = '🚫 Acesso Negado! Você não tem permissão para realizar isso.'

    def handle_no_permission(self):
        # usar error para ficar vermelho
        messages.error(self.request, self.mensagem_sem_permissao)
        return redirect('redirect_pos_login')
    
