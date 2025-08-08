from django.db import migrations

def init_process_steps(apps, schema_editor):
    ProcessStep = apps.get_model('production', 'ProcessStep')
    ProcessSchedule = apps.get_model('production', 'ProcessSchedule')
    
    # 先删除所有工序排程记录
    ProcessSchedule.objects.all().delete()
    # 再删除所有工序步骤
    ProcessStep.objects.all().delete()
    
    # 根据实际工艺流程创建工序步骤
    steps = [
        {
            'name': '激光下料',
            'code': 'LASER',
            'daily_capacity': 4000,  # 基础产能2000片/台/天 × 2台
            'sequence': 1,
            'is_bottleneck': False,
            'notes': '基础产能：2000片/台/天，设备：2台固定'
        },
        {
            'name': '热处理',
            'code': 'HEAT',
            'daily_capacity': 8000,
            'sequence': 2,
            'is_bottleneck': False,
            'notes': '夜班生产'
        },
        {
            'name': '粗磨',
            'code': 'ROUGH',
            'daily_capacity': 6000,
            'sequence': 3,
            'is_bottleneck': False,
            'notes': '粗磨工序'
        },
        {
            'name': '校平',
            'code': 'LEVEL',
            'daily_capacity': 6000,
            'sequence': 4,
            'is_bottleneck': False,
            'notes': '校平工序'
        },
        {
            'name': '数控打磨刃面',
            'code': 'CNC',
            'daily_capacity': 6000,
            'sequence': 5,
            'is_bottleneck': False,
            'notes': '数控打磨刃面工序'
        },
        {
            'name': '开刃',
            'code': 'EDGE',
            'daily_capacity': 2400,
            'sequence': 6,
            'is_bottleneck': True,
            'notes': '瓶颈工序，3台×800片'
        },
        {
            'name': '精磨',
            'code': 'FINE',
            'daily_capacity': 5000,
            'sequence': 7,
            'is_bottleneck': False,
            'notes': '精磨工序'
        },
        {
            'name': '包装',
            'code': 'PACK',
            'daily_capacity': 3600,
            'sequence': 8,
            'is_bottleneck': False,
            'notes': '包装工序'
        }
    ]
    
    for step in steps:
        ProcessStep.objects.create(**step)

def reverse_init_process_steps(apps, schema_editor):
    ProcessStep = apps.get_model('production', 'ProcessStep')
    ProcessStep.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('production', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_process_steps, reverse_init_process_steps),
    ] 