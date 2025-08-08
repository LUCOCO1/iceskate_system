from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

class OrderPDFService:
    def __init__(self):
        # 注册中文字体（请确保字体文件存在）
        pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
        
        # 创建自定义样式
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName='SimSun',
            fontSize=16,
            alignment=1,  # 居中
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='ChineseText',
            fontName='SimSun',
            fontSize=10
        ))
    
    def generate_order_pdf(self, order):
        """生成订单PDF文件"""
        pdf_dir = 'media/pdfs'
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
            
        pdf_path = os.path.join(pdf_dir, f"order_{order.order_number}.pdf")
        
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(A4),
            topMargin=15*mm,
            leftMargin=15*mm,
            rightMargin=15*mm,
            bottomMargin=15*mm
        )
        
        elements = []
        
        # 添加标题
        elements.append(Paragraph("东莞市伟呈塑胶制品有限公司", self.styles['ChineseTitle']))
        elements.append(Paragraph("生产单", self.styles['ChineseTitle']))
        
        # 创建表头
        headers = ['订单单号', '采购单号', '品名规格', '颜色', '材料', '单位', '数量', '下单日期', '备注']
        
        # 创建数据行
        data = [headers]
        data.append([
            order.order_number,
            order.customer_order_number,
            order.items.first().product.name if order.items.exists() else '',
            '木色',  # 这里可能需要从产品属性中获取
            '3CR13',  # 这里可能需要从产品属性中获取
            '双',
            str(order.items.first().quantity if order.items.exists() else ''),
            order.order_date.strftime('%m月%d日'),
            order.notes or ''
        ])
        
        # 添加空行
        for _ in range(10):
            data.append([''] * len(headers))
        
        # 调整列宽
        col_widths = [
            30*mm,  # 订单单号
            30*mm,  # 采购单号
            40*mm,  # 品名规格
            20*mm,  # 颜色
            20*mm,  # 材料
            15*mm,  # 单位
            20*mm,  # 数量
            25*mm,  # 下单日期
            40*mm,  # 备注
        ]
        
        # 创建表格并设置样式
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        
        elements.append(table)
        
        # 添加底部签名栏
        signature_data = [['主管:', '', '审核:', '', '制表人:', '周赛柳']]
        signature_table = Table(signature_data, colWidths=[50*mm]*6)
        signature_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        elements.append(signature_table)
        
        # 生成PDF
        doc.build(elements)
        return pdf_path 