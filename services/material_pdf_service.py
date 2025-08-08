from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import platform
from django.conf import settings

class MaterialPurchasePDFService:
    def __init__(self):
        # 根据操作系统选择字体
        if platform.system() == 'Windows':
            font_path = "C:\\Windows\\Fonts\\simhei.ttf"  # Windows 系统黑体字体
        else:  # Linux/Mac
            font_path = "/usr/share/fonts/truetype/arphic/uming.ttc"
        
        try:
            # 注册中文字体
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
        except:
            # 如果注册失败，使用内置字体
            print("Warning: Chinese font not found, using default font")
            self.use_default_font = True
        else:
            self.use_default_font = False

    def draw_company_seal(self, canvas, x, y, radius=60):
        """绘制公司印章"""
        # 保存当前图形状态
        canvas.saveState()
        
        # 设置印章颜色（鲜艳的红色）
        canvas.setFillColorRGB(0.95, 0, 0, alpha=0.95)  # 更鲜艳的红色
        canvas.setStrokeColorRGB(0.95, 0, 0, alpha=0.95)
        
        # 设置线条宽度
        canvas.setLineWidth(3)  # 加粗外圈线条
        
        # 绘制外圆和内圆
        canvas.circle(x, y, radius, fill=0)
        canvas.circle(x, y, radius-2, fill=0)  # 双圈效果
        
        # 设置字体
        font_name = 'SimHei' if not self.use_default_font else 'Helvetica'
        canvas.setFont(font_name, 14)  # 调小字体
        
        # 绘制上半部分文字（公司名称）
        canvas.saveState()
        canvas.translate(x, y)  # 移动到圆心
        
        # 计算文字
        text = "东莞市伟呈塑胶制品有限公司"
        text_len = len(text)
        for i in range(text_len):
            angle = (i - text_len/2) * 16  # 调整字间角度
            canvas.rotate(angle)
            canvas.drawString(0, radius-18, text[i])  # 调整文字位置
            canvas.rotate(-angle)
        
        canvas.restoreState()
        
        # 绘制五角星
        canvas.saveState()
        canvas.translate(x, y+8)  # 调整五角星位置
        self.draw_star(canvas, 20)  # 五角星大小
        canvas.restoreState()
        
        # 绘制下半部分文字（改为采购专用章）
        canvas.saveState()
        canvas.translate(x, y-20)  # 调整位置
        canvas.setFont(font_name, 14)  # 字体大小
        canvas.drawCentredString(0, 0, "采购专用章")  # 修改文字
        canvas.restoreState()
        
        # 恢复图形状态
        canvas.restoreState()

    def draw_star(self, canvas, size):
        """绘制五角星（实心）"""
        from math import cos, sin, pi
        
        # 计算五角星的外部顶点
        outer_points = []
        for i in range(5):
            angle = (i * 72 - 90) * pi / 180
            outer_points.append((size * cos(angle), size * sin(angle)))
        
        # 计算五角星的内部顶点（用于填充）
        inner_points = []
        inner_size = size * 0.382  # 黄金分割比例
        for i in range(5):
            angle = (i * 72 - 90 + 36) * pi / 180
            inner_points.append((inner_size * cos(angle), inner_size * sin(angle)))
        
        # 设置颜色
        canvas.setFillColorRGB(0.95, 0, 0, alpha=0.95)
        
        # 创建完整的五角星路径（包括内部）
        path = canvas.beginPath()
        
        # 从第一个外部点开始
        path.moveTo(outer_points[0][0], outer_points[0][1])
        
        # 按照特定顺序连接所有点以形成实心五角星
        for i in range(5):
            path.lineTo(outer_points[i][0], outer_points[i][1])
            path.lineTo(inner_points[i][0], inner_points[i][1])
            next_i = (i + 1) % 5
            path.lineTo(outer_points[next_i][0], outer_points[next_i][1])
        
        # 闭合路径
        path.close()
        
        # 填充五角星（实心）
        canvas.drawPath(path, fill=1, stroke=0)

    def generate_purchase_pdf(self, purchase):
        # 创建PDF文件
        filename = f'purchase_{purchase.purchase_number}.pdf'
        filepath = os.path.join('media', 'pdfs', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 创建PDF画布
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # 设置字体
        font_name = 'SimHei' if not self.use_default_font else 'Helvetica'
        
        # 绘制公司信息
        c.setFont(font_name, 14)
        c.drawString(width/2 - 100, height - 40, "东莞市伟呈塑胶制品有限公司")
        
        c.setFont(font_name, 10)
        c.drawString(width/2 - 120, height - 60, "地址：东莞市大朗镇西牛陂大院地横街8号")
        
        # 绘制联系信息
        c.drawString(50, height - 80, f"电话：0769-81066297")
        c.drawString(width - 200, height - 80, f"传真：0769-83319879")
        
        # 绘制标题
        c.setFont(font_name, 12)
        c.drawString(width/2 - 20, height - 100, "采购单")
        
        # 绘制供应商信息
        info_y = height - 140
        c.setFont(font_name, 10)
        
        # 左侧信息
        c.drawString(50, info_y, f"供应商：{purchase.supplier.name}")
        c.drawString(50, info_y - 20, f"联系人：{purchase.supplier.contact}")
        c.drawString(50, info_y - 40, f"电话：{purchase.supplier.phone}")
        
        # 右侧信息
        c.drawString(width/2, info_y, f"订购日期：{purchase.purchase_date.strftime('%Y年%m月%d日')}")
        c.drawString(width/2, info_y - 20, f"订单交期：{purchase.delivery_date.strftime('%Y年%m月%d日')}")
        c.drawString(width/2, info_y - 40, f"订单编号：{purchase.purchase_number}")
        
        # 绘制表格
        table_top = info_y - 80
        table_width = width - 100  # 表格总宽度
        row_height = 25  # 行高
        
        # 修改列宽，使其均匀分布
        col_widths = [
            table_width / 6,  # 管制单号
            table_width / 6,  # 材质
            table_width / 6,  # 长度*宽度MM
            table_width / 6,  # 数量/KG
            table_width / 6,  # 来料方式
            table_width / 6   # 备注
        ]
        
        # 计算列的x坐标
        col_positions = [50]  # 起始x坐标
        for w in col_widths[:-1]:
            col_positions.append(col_positions[-1] + w)
        
        # 绘制表头
        headers = ["管制单号", "材质", "长度*宽度MM", "数量/KG", "来料方式", "备注"]
        
        # 绘制表格外框
        c.rect(50, table_top - (8 * row_height), table_width, row_height * 8)
        
        # 绘制表头背景色
        c.setFillColorRGB(0.9, 0.9, 0.9)  # 设置浅灰色背景
        c.rect(50, table_top - row_height, table_width, row_height, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)  # 重置回黑色用于文字
        
        # 绘制表头行
        for i, header in enumerate(headers):
            # 绘制垂直线
            x = col_positions[i]
            c.line(x, table_top - (8 * row_height), x, table_top)
            # 写入表头文字（居中显示）
            header_width = col_widths[i]
            text_width = c.stringWidth(header, font_name, 10)
            x_centered = x + (header_width - text_width) / 2
            c.drawString(x_centered, table_top - 15, header)
        
        # 绘制最后一条垂直线
        c.line(50 + table_width, table_top - (8 * row_height), 50 + table_width, table_top)
        
        # 绘制横线
        for i in range(9):  # 8个格子需要9条横线
            y = table_top - (i * row_height)
            c.line(50, y, 50 + table_width, y)
        
        # 填充表格内容
        y = table_top - row_height - 15
        for item in purchase.items.all():
            # 修正数据填充
            texts = [
                item.control_number,
                item.material.name,  # 材质列显示材料名称
                item.specification,  # 规格列显示规格信息
                str(item.quantity),
                item.material_type,
                item.notes or ''
            ]
            
            # 居中显示每个单元格的内容
            for i, text in enumerate(texts):
                text_width = c.stringWidth(text, font_name, 10)
                cell_width = col_widths[i]
                x_centered = col_positions[i] + (cell_width - text_width) / 2
                c.drawString(x_centered, y, text)
            
            y -= row_height
        
        # 绘制备注信息
        y = table_top - (9 * row_height) - 20
        c.drawString(50, y, "备注：以上含税单价")
        y -= 20
        c.drawString(50, y, "1.请收到订单5小时内确认订单交期回签我司")
        y -= 20
        c.drawString(50, y, "2.我司月结周期：本月26至下月25，以后所有订单均按照此规定请款。")
        y -= 20
        c.drawString(50, y, "3.付款方式月结60天")
        y -= 20
        c.drawString(50, y, "4.确保材料内部无断裂，表面无刮伤，无麻点，无分眼，无拉痕。")
        
        # 绘制签字栏
        y -= 40
        c.drawString(50, y, "确认回签：")
        c.drawString(200, y, "审核：卢瑶")
        c.drawString(350, y, "制表人：周赛柳")
        
        # 在签字栏下方添加印章
        seal_x = width - 150  # 印章位置x坐标
        seal_y = y - 30      # 印章位置y坐标
        self.draw_company_seal(c, seal_x, seal_y)
        
        c.save()
        return filepath

    def generate_purchase_pdf_with_reportlab(self, purchase):
        pdf_dir = 'media/pdfs'
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
            
        pdf_path = os.path.join(pdf_dir, f"material_purchase_{purchase.purchase_number}.pdf")
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            topMargin=15*mm,
            leftMargin=20*mm,
            rightMargin=20*mm,
            bottomMargin=15*mm
        )
        
        elements = []
        
        # 添加标题
        elements.append(Paragraph('东莞市伟呈塑胶制品有限公司', self.styles['ChineseTitle']))
        
        # 添加公司信息
        company_info = [
            ['地址：东莞市大朗镇犀牛陂村大院地横街8号'],
            ['电话：0769-81066897', '传真：0769-83319879']
        ]
        company_table = Table(company_info, colWidths=[doc.width/2]*2)
        company_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(company_table)
        
        # 添加采购单标题
        elements.append(Paragraph('采购单', self.styles['ChineseTitle']))
        
        # 添加采购信息
        purchase_info = [
            ['供应商：', purchase.supplier.name, '订购日期：', purchase.order_date.strftime('%Y年%m月%d日')],
            ['联系人：', purchase.supplier.contact_person or '', '交货日期：', purchase.expected_date.strftime('%Y年%m月%d日') if purchase.expected_date else ''],
            ['电话：', purchase.supplier.contact_phone or '', '订单编号：', purchase.purchase_number]
        ]
        info_table = Table(purchase_info, colWidths=[doc.width/4]*4)
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(info_table)
        
        # 添加采购明细表格
        headers = ['管制编号', '材质', '规格尺寸', '数量/KG', '来料方式', '备注']
        data = [headers]
        
        # 添加实际的采购明细数据
        for item in purchase.items.all():
            data.append([
                item.control_number,
                item.material.name,
                item.specification,
                str(item.quantity),
                '平料',  # 这里可以添加来料方式字段
                item.notes or ''
            ])
        
        # 如果明细少于6行，添加空行
        while len(data) < 7:
            data.append([''] * len(headers))
        
        # 设置列宽
        col_widths = [30*mm, 30*mm, 40*mm, 30*mm, 25*mm, 25*mm]
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(table)
        
        # 添加备注信息
        notes = [
            "备注：以上含税单价",
            "1.请收到订单5小时内确认订单交期回签我司",
            "2.我司月结周期：本月26至下月25，以后所有订单均按照此规定请款。",
            "3.付款方式月结60天",
            "4.确保材料内部无断裂，表面无刮伤，无麻点，无沙眼，无拉痕。"
        ]
        for note in notes:
            elements.append(Paragraph(note, self.styles['ChineseText']))
        
        # 添加底部签名栏
        signature_data = [['确认回签:', '', '审核:', '卢瑶', '制表人:', '周赛柳']]
        signature_table = Table(signature_data, colWidths=[25*mm, 45*mm, 25*mm, 45*mm, 25*mm, 45*mm])
        signature_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'SimSun'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        elements.append(signature_table)
        
        # 生成PDF
        doc.build(elements)
        return pdf_path 