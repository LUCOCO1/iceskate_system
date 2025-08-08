from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = '库存管理'
    
    def ready(self):
        """导入信号处理模块"""
        import inventory.signals