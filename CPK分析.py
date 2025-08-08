import tkinter as tk  
from tkinter import ttk, messagebox, filedialog  
import statistics  
import numpy as np  
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import pandas as pd  
import datetime  
import os  

class CPKAnalysisTool:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("CPK分析工具")  
        self.root.geometry("900x700")  
        self.root.resizable(True, True)  
        
        # 创建主框架  
        self.notebook = ttk.Notebook(root)  
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)  
        
        # 创建各选项卡  
        self.info_frame = ttk.Frame(self.notebook)  
        self.data_frame = ttk.Frame(self.notebook)  
        self.result_frame = ttk.Frame(self.notebook)  
        self.plot_frame = ttk.Frame(self.notebook)  
        
        self.notebook.add(self.info_frame, text="基本信息")  
        self.notebook.add(self.data_frame, text="数据输入")  
        self.notebook.add(self.result_frame, text="分析结果")  
        self.notebook.add(self.plot_frame, text="图表显示")  
        
        # 初始化数据  
        self.sample_data = []  
        
        # 设置各选项卡内容  
        self.setup_info_tab()  
        self.setup_data_tab()  
        self.setup_result_tab()  
        self.setup_plot_tab()  
    
    def setup_info_tab(self):  
        # 创建基本信息输入区域  
        info_frame = ttk.LabelFrame(self.info_frame, text="基本信息")  
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)  
        
        # 创建输入字段  
        fields = [  
            ("项目名称:", "project_name"),  
            ("产品名称:", "product_name"),  
            ("制程名称:", "process_name"),  
            ("负责人:", "responsible_person"),  
            ("测试日期:", "test_date"),  
            ("测试地点:", "test_location"),  
            ("测试设备/仪器:", "test_equipment")  
        ]  
        
        # 存储变量  
        self.info_vars = {}  
        
        # 创建输入框  
        for i, (label_text, var_name) in enumerate(fields):  
            ttk.Label(info_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)  
            self.info_vars[var_name] = tk.StringVar()  
            ttk.Entry(info_frame, textvariable=self.info_vars[var_name], width=50).grid(row=i, column=1, sticky="w", padx=10, pady=5)  
        
        # 规格信息  
        spec_frame = ttk.LabelFrame(self.info_frame, text="测量与规格信息")  
        spec_frame.pack(fill="both", expand=True, padx=10, pady=10)  
        
        # 规格信息字段  
        spec_fields = [  
            ("规格下限 (LSL):", "lsl"),  
            ("规格上限 (USL):", "usl"),  
            ("目标值:", "target"),  
            ("单位:", "unit")  
        ]  
        
        # 存储规格变量  
        self.spec_vars = {}  
        
        # 创建规格输入框  
        for i, (label_text, var_name) in enumerate(spec_fields):  
            ttk.Label(spec_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)  
            self.spec_vars[var_name] = tk.StringVar()  
            ttk.Entry(spec_frame, textvariable=self.spec_vars[var_name], width=50).grid(row=i, column=1, sticky="w", padx=10, pady=5)  
        
        # 设置当前日期  
        self.info_vars["test_date"].set(datetime.datetime.now().strftime("%Y-%m-%d"))  
    
    def setup_data_tab(self):  
        # 创建数据输入区域  
        data_input_frame = ttk.Frame(self.data_frame)  
        data_input_frame.pack(fill="both", expand=True, padx=10, pady=10)  
        
        # 创建样本数据输入区域  
        ttk.Label(data_input_frame, text="输入样本数据（每行一个数据）:").pack(anchor="w", padx=10, pady=5)  
        
        # 创建文本框和滚动条  
        self.data_text = tk.Text(data_input_frame, height=15, width=50)  
        scrollbar = ttk.Scrollbar(data_input_frame, command=self.data_text.yview)  
        self.data_text.configure(yscrollcommand=scrollbar.set)  
        
        self.data_text.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=5)  
        scrollbar.pack(side=tk.RIGHT, fill="y", padx=0, pady=5)  
        
        # 按钮区域  
        button_frame = ttk.Frame(self.data_frame)  
        button_frame.pack(fill="x", padx=10, pady=10)  
        
        ttk.Button(button_frame, text="导入CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5)  
        ttk.Button(button_frame, text="清除数据", command=self.clear_data).pack(side=tk.LEFT, padx=5)  
        ttk.Button(button_frame, text="分析数据", command=self.analyze_data).pack(side=tk.LEFT, padx=5)  
    
    def setup_result_tab(self):  
        # 创建结果显示区域  
        result_scroll = ttk.Scrollbar(self.result_frame)  
        result_scroll.pack(side=tk.RIGHT, fill="y")  
        
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, yscrollcommand=result_scroll.set)  
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)  
        result_scroll.config(command=self.result_text.yview)  
        
        # 创建按钮帧  
        button_frame = ttk.Frame(self.result_frame)  
        button_frame.pack(fill="x", padx=10, pady=10)  
        
        ttk.Button(button_frame, text="保存报告", command=self.save_report).pack(side=tk.LEFT, padx=5)  
    
    def setup_plot_tab(self):  
        # 创建图表显示区域  
        self.figure, self.ax = plt.subplots(2, 1, figsize=(8, 8))  
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)  
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)  
    
    def import_csv(self):  
        try:  
            file_path = filedialog.askopenfilename(  
                title="选择CSV文件",  
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]  
            )  
            
            if file_path:  
                df = pd.read_csv(file_path)  
                
                # 假设CSV中第一列是测量值  
                if len(df.columns) > 0:  
                    data = df.iloc[:, 0].dropna().tolist()  
                    self.data_text.delete(1.0, tk.END)  
                    self.data_text.insert(tk.END, "\n".join(map(str, data)))  
                    messagebox.showinfo("成功", f"已导入{len(data)}个样本数据")  
                else:  
                    messagebox.showerror("错误", "CSV文件格式不正确")  
        except Exception as e:  
            messagebox.showerror("错误", f"导入CSV时出错：{str(e)}")  
    
    def clear_data(self):  
        self.data_text.delete(1.0, tk.END)  
        self.sample_data = []  
    
    def analyze_data(self):  
        try:  
            # 获取数据  
            data_text = self.data_text.get(1.0, tk.END).strip()  
            if not data_text:  
                messagebox.showerror("错误", "请输入样本数据")  
                return  
            
            # 转换数据为浮点数列表  
            self.sample_data = []  
            for line in data_text.split("\n"):  
                if line.strip():  
                    try:  
                        value = float(line.strip())  
                        self.sample_data.append(value)  
                    except ValueError:  
                        pass  
            
            if len(self.sample_data) < 2:  
                messagebox.showerror("错误", "至少需要2个有效的样本数据")  
                return  
            
            # 获取规格限  
            try:  
                lsl = float(self.spec_vars["lsl"].get()) if self.spec_vars["lsl"].get() else None  
                usl = float(self.spec_vars["usl"].get()) if self.spec_vars["usl"].get() else None  
                
                if lsl is None or usl is None:  
                    messagebox.showerror("错误", "请输入规格上限和规格下限")  
                    return  
                
                if lsl >= usl:  
                    messagebox.showerror("错误", "规格下限必须小于规格上限")  
                    return  
                
            except ValueError:  
                messagebox.showerror("错误", "规格上下限必须是有效的数字")  
                return  
            
            # 计算统计量  
            mean = statistics.mean(self.sample_data)  
            std_dev = statistics.stdev(self.sample_data)  
            min_val = min(self.sample_data)  
            max_val = max(self.sample_data)  
            data_range = max_val - min_val  
            
            # 计算Cp和Cpk  
            cp = (usl - lsl) / (6 * std_dev) if std_dev > 0 else float('inf')  
            cpu = (usl - mean) / (3 * std_dev) if std_dev > 0 else float('inf')  
            cpl = (mean - lsl) / (3 * std_dev) if std_dev > 0 else float('inf')  
            cpk = min(cpu, cpl)  
            
            # 生成报告  
            self.generate_report(mean, std_dev, min_val, max_val, data_range, cp, cpk, cpu, cpl, lsl, usl)  
            
            # 生成图表  
            self.generate_plots(mean, std_dev, lsl, usl)  
            
            # 切换到结果选项卡  
            self.notebook.select(2)  
            
        except Exception as e:  
            messagebox.showerror("错误", f"分析数据时出错：{str(e)}")  
    
    def generate_report(self, mean, std_dev, min_val, max_val, data_range, cp, cpk, cpu, cpl, lsl, usl):  
        # 清除之前的结果  
        self.result_text.delete(1.0, tk.END)  
        
        # 获取项目信息  
        project_info = {}  
        for key, var in self.info_vars.items():  
            project_info[key] = var.get()  
        
        # 获取规格信息  
        spec_info = {}  
        for key, var in self.spec_vars.items():  
            spec_info[key] = var.get()  
        
        # 生成报告文本  
        report = f"""CPK分析报告  
{'='*50}  

1. 基本信息  
------------  
项目名称: {project_info.get('project_name', '')}  
产品名称: {project_info.get('product_name', '')}  
制程名称: {project_info.get('process_name', '')}  
负责人: {project_info.get('responsible_person', '')}  
测试日期: {project_info.get('test_date', '')}  
测试地点: {project_info.get('test_location', '')}  
测试设备/仪器: {project_info.get('test_equipment', '')}  

2. 测量与规格信息  
----------------  
规格下限 (LSL): {lsl}  
规格上限 (USL): {usl}  
目标值: {spec_info.get('target', '')}  
单位: {spec_info.get('unit', '')}  

3. 数据摘要  
----------  
样本个数 (n): {len(self.sample_data)}  
平均值 (μ): {mean:.4f}  
标准偏差 (σ): {std_dev:.4f}  
最小值 (Min): {min_val:.4f}  
最大值 (Max): {max_val:.4f}  
范围 (R): {data_range:.4f}  

4. 过程能力分析  
--------------  
过程能力指数 (Cp): {cp:.4f}  
CPK上值 (CPU): {cpu:.4f}  
CPK下值 (CPL): {cpl:.4f}  
制程能力指数 (Cpk): {cpk:.4f}  

5. 结果解释与分析  
---------------  
"""  
        # 根据Cpk评估结果  
        if cpk < 1.0:  
            report += "制程能力不足，产品质量不能满足规格要求，需要进行改进。\n"  
        elif 1.0 <= cpk < 1.33:  
            report += "制程能力勉强满足要求，但仍有改进空间，建议进行制程优化。\n"  
        else:  
            report += "制程能力良好，能够满足规格要求，可持续保持当前控制水平。\n"  
        
        # 偏移分析  
        if abs(mean - (usl + lsl) / 2) > 0.1 * (usl - lsl):  
            report += "制程存在明显偏移，平均值与规格中心相差较大，建议调整制程中心。\n"  
        
        # 是否有超出规格的样本  
        out_of_spec = [x for x in self.sample_data if x < lsl or x > usl]  
        if out_of_spec:  
            report += f"有{len(out_of_spec)}个样本超出规格范围，占比{len(out_of_spec)/len(self.sample_data)*100:.2f}%，需检查异常原因。\n"  
        
        report += """  
6. 改进措施与后续计划  
------------------  
[此处填写具体的改进措施和后续计划]  

7. 结论  
------  
[此处填写最终结论]  

"""  
        
        # 填充到结果文本框  
        self.result_text.insert(tk.END, report)  
    
    def generate_plots(self, mean, std_dev, lsl, usl):  
        # 清除之前的图表  
        for ax in self.ax:  
            ax.clear()  
        
        # 创建直方图  
        self.ax[0].hist(self.sample_data, bins=10, alpha=0.7, color='blue', edgecolor='black')  
        self.ax[0].set_title('样本数据分布直方图')  
        self.ax[0].set_xlabel('测量值')  
        self.ax[0].set_ylabel('频数')  
        
        # 添加规格限和平均值线  
        self.ax[0].axvline(lsl, color='red', linestyle='--', label=f'LSL={lsl}')  
        self.ax[0].axvline(usl, color='red', linestyle='--', label=f'USL={usl}')  
        self.ax[0].axvline(mean, color='green', linestyle='-', label=f'平均值={mean:.4f}')  
        self.ax[0].legend()  
        
        # 创建正态分布曲线  
        x = np.linspace(mean - 4*std_dev, mean + 4*std_dev, 1000)  
        y = 1/(std_dev * np.sqrt(2 * np.pi)) * np.exp(-(x - mean)**2 / (2 * std_dev**2))  
        self.ax[1].plot(x, y, 'r-', linewidth=2)  
        self.ax[1].set_title('正态分布曲线')  
        self.ax[1].set_xlabel('测量值')  
        self.ax[1].set_ylabel('概率密度')  
        
        # 添加规格限和平均值线  
        self.ax[1].axvline(lsl, color='red', linestyle='--', label=f'LSL={lsl}')  
        self.ax[1].axvline(usl, color='red', linestyle='--', label=f'USL={usl}')  
        self.ax[1].axvline(mean, color='green', linestyle='-', label=f'平均值={mean:.4f}')  
        self.ax[1].legend()  
        
        # 添加±3σ区域  
        self.ax[1].axvline(mean - 3*std_dev, color='purple', linestyle=':', label='-3σ')  
        self.ax[1].axvline(mean + 3*std_dev, color='purple', linestyle=':', label='+3σ')  
        
        # 更新图表  
        self.figure.tight_layout()  
        self.canvas.draw()  
    
    def save_report(self):  
        try:  
            file_path = filedialog.asksaveasfilename(  
                title="保存CPK分析报告",  
                defaultextension=".txt",  
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]  
            )  
            
            if file_path:  
                with open(file_path, 'w', encoding='utf-8') as f:  
                    f.write(self.result_text.get(1.0, tk.END))  
                messagebox.showinfo("成功", "报告已成功保存")  
                
                # 询问是否保存图表  
                if messagebox.askyesno("保存图表", "是否同时保存分析图表?"):  
                    fig_path = os.path.splitext(file_path)[0] + ".png"  
                    self.figure.savefig(fig_path, dpi=300, bbox_inches='tight')  
                    messagebox.showinfo("成功", f"图表已保存至 {fig_path}")  
                    
        except Exception as e:  
            messagebox.showerror("错误", f"保存报告时出错：{str(e)}")  

# 运行应用程序  
if __name__ == "__main__":  
    root = tk.Tk()  
    app = CPKAnalysisTool(root)  
    root.mainloop()  