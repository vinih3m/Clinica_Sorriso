from django.apps import AppConfig

class ClinicaSorrisoConfig(AppConfig):
    name = 'Clinica_Sorriso'
    
    def ready(self):
        import Clinica_Sorriso.signals