from django.apps import AppConfig


class ProductionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'production'
    verbose_name = '生产管理'

    def ready(self):
        import production.signals  # 确保信号被注册
