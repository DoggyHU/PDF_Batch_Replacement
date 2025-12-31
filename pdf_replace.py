#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文本替换工具

功能：批量替换PDF文件中的指定文本

用法：
1. 直接运行脚本启动GUI界面
2. 拖拽PDF文件到界面或点击按钮选择文件
3. 输入要查找和替换的文本
4. 选择保存位置（可选）
5. 点击确定开始替换
"""

import argparse
import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

def get_next_output_path(output_path):
    """
    如果输出文件已存在，自动生成带序号的文件名
    例如：output.pdf -> output(2).pdf -> output(3).pdf
    """
    if not os.path.exists(output_path):
        return output_path
    
    # 分离文件名和扩展名
    base_name, ext = os.path.splitext(output_path)
    
    # 查找最后一个括号中的数字
    i = 2
    while True:
        new_path = f"{base_name}({i}){ext}"
        if not os.path.exists(new_path):
            return new_path
        i += 1

def replace_text_in_pdf(input_path, output_path, find_text, replace_text):
    """
    替换PDF文件中的文本
    
    参数：
    input_path: 输入PDF文件路径
    output_path: 输出PDF文件路径
    find_text: 要查找的文本
    replace_text: 要替换的文本
    
    返回：
    tuple: (成功标志, 消息, 输出文件路径)
    """
    try:
        # 检查输出文件是否存在，如果存在则自动重命名
        output_path = get_next_output_path(output_path)
        
        # 打开PDF文档
        doc = fitz.open(input_path)
        replacements_count = 0
        
        # 遍历每一页
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 使用search_for方法查找文本
            text_instances = page.search_for(find_text)
            
            if text_instances:
                # 遍历每个匹配的文本实例
                for inst in text_instances:
                    rect = fitz.Rect(inst)
                    
                    # 获取页面的文本信息，包括字体和大小
                    page_text = page.get_text("dict")
                    font_size = 11.0  # 默认字体大小
                    font_name = ""     # 默认字体名称
                    
                    # 遍历文本块、行和跨度，获取字体信息
                    for block in page_text["blocks"]:
                        if block["type"] == 0:  # 文本块
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    span_rect = fitz.Rect(span["bbox"])
                                    if rect.intersects(span_rect):
                                        font_size = span["size"]
                                        font_name = span["font"]
                                        break
                                if font_name:
                                    break
                            if font_name:
                                break
                    
                    # 尝试获取整个文本块，而不仅仅是匹配的文本片段
                    # 这样可以确保替换后整个文本块重新排版，不会重叠
                    text_block = None
                    
                    # 遍历文本块、行和跨度，找到包含匹配文本的整个行
                    for block in page_text["blocks"]:
                        if block["type"] == 0:  # 文本块
                            for line in block["lines"]:
                                line_rect = fitz.Rect(line["bbox"])
                                if rect.intersects(line_rect):
                                    # 找到包含匹配文本的行
                                    # 构建整个行的文本
                                    line_text = "".join([span["text"] for span in line["spans"]])
                                    
                                    # 替换行中的文本
                                    new_line_text = line_text.replace(find_text, replace_text)
                                    
                                    if new_line_text != line_text:
                                        # 绘制白色背景覆盖整个行
                                        page.draw_rect(line_rect, color=(1, 1, 1), fill=(1, 1, 1))
                                        
                                        # 重新添加替换后的整个行文本
                                        # 创建TextWriter对象
                                        tw = fitz.TextWriter(page.rect)
                                        # 设置文本颜色为黑色
                                        tw.fill_color = (0, 0, 0)
                                        # 计算基线位置
                                        baseline_y = line_rect.y1 - font_size * 0.2
                                        insert_point = (line_rect.x0, baseline_y)
                                        
                                        # 使用TextWriter添加新文本
                                        tw.append(
                                            insert_point,  # 行的起始位置
                                            new_line_text,  # 替换后的整行文本
                                            fontsize=font_size  # 使用原文本的字体大小
                                        )
                                        
                                        # 将TextWriter的内容写入页面
                                        tw.write_text(page)
                                        replacements_count += 1
                                        text_block = block
                                        break
                            if text_block:
                                break
        
        # 保存修改后的PDF
        doc.save(output_path)
        doc.close()
        
        return True, f"替换完成，共替换 {replacements_count} 处", output_path
    except Exception as e:
        return False, f"替换失败：{str(e)}", ""

class PDFReplaceGUI:
    """PDF文本替换工具GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF文本替换工具")
        self.root.geometry("600x600")  # 进一步增加高度，确保按钮能显示
        self.root.resizable(True, True)
        
        # 变量初始化
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. PDF文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="PDF文件", padding="10")
        file_frame.pack(fill=tk.X, pady=10, anchor=tk.N)
        
        # 文件拖拽区域
        self.drag_label = ttk.Label(
            file_frame, 
            text="拖拽PDF文件到此处或点击按钮选择", 
            relief=tk.SUNKEN, 
            padding="20", 
            background="#f0f0f0"
        )
        self.drag_label.pack(fill=tk.X, pady=5)
        
        # 注册拖拽事件
        self.drag_label.drop_target_register(DND_FILES)
        self.drag_label.dnd_bind("<<Drop>>", self.on_drop)
        
        # 文件选择按钮
        file_button_frame = ttk.Frame(file_frame)
        file_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(file_button_frame, textvariable=self.input_file, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_button_frame, text="选择文件", command=self.select_file).pack(side=tk.RIGHT, padx=5)
        
        # 2. 保存位置选择区域
        save_frame = ttk.LabelFrame(main_frame, text="保存位置", padding="10")
        save_frame.pack(fill=tk.X, pady=10, anchor=tk.N)
        
        save_button_frame = ttk.Frame(save_frame)
        save_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(save_button_frame, textvariable=self.output_dir, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(save_button_frame, text="选择目录", command=self.select_output_dir).pack(side=tk.RIGHT, padx=5)
        
        # 3. 文本替换区域
        replace_frame = ttk.LabelFrame(main_frame, text="文本替换", padding="10")
        replace_frame.pack(fill=tk.X, pady=10, anchor=tk.N)  # 不允许垂直扩展，避免占用过多空间
        
        # 查找文本
        find_label = ttk.Label(replace_frame, text="查找文本:")
        find_label.pack(anchor=tk.W, pady=(5, 0))
        find_entry = ttk.Entry(replace_frame, textvariable=self.find_text)
        find_entry.pack(fill=tk.X, pady=(0, 10), padx=0)
        find_entry.focus()  # 设置焦点到查找文本框
        
        # 替换文本
        replace_label = ttk.Label(replace_frame, text="替换文本:")
        replace_label.pack(anchor=tk.W, pady=(5, 0))
        replace_entry = ttk.Entry(replace_frame, textvariable=self.replace_text)
        replace_entry.pack(fill=tk.X, pady=(0, 10), padx=0)
        
        # 4. 操作按钮区域 - 确保能显示
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=30, anchor=tk.CENTER)  # 居中显示，增加pady
        
        # 确保按钮能显示
        ok_button = ttk.Button(button_frame, text="确定", command=self.on_ok, width=15)
        ok_button.pack(side=tk.LEFT, padx=20)
        cancel_button = ttk.Button(button_frame, text="取消", command=self.on_cancel, width=15)
        cancel_button.pack(side=tk.RIGHT, padx=20)
    
    def on_drop(self, event):
        """处理文件拖拽事件"""
        # 获取拖拽的文件路径
        file_path = event.data
        # 处理Windows路径格式（去除花括号）
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        # 检查是否是PDF文件
        if file_path.lower().endswith('.pdf'):
            self.input_file.set(file_path)
            # 设置默认输出目录为源文件所在目录
            self.output_dir.set(os.path.dirname(file_path))
        else:
            messagebox.showwarning("警告", "请选择PDF文件")
    
    def select_file(self):
        """选择PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_file.set(file_path)
            # 设置默认输出目录为源文件所在目录
            self.output_dir.set(os.path.dirname(file_path))
    
    def select_output_dir(self):
        """选择保存位置"""
        dir_path = filedialog.askdirectory(title="选择保存位置")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def on_ok(self):
        """确定按钮事件"""
        # 验证输入
        if not self.input_file.get():
            messagebox.showwarning("警告", "请选择PDF文件")
            return
        
        if not os.path.exists(self.input_file.get()):
            messagebox.showwarning("警告", "PDF文件不存在")
            return
        
        if not self.find_text.get():
            messagebox.showwarning("警告", "请输入要查找的文本")
            return
        
        if not self.output_dir.get():
            messagebox.showwarning("警告", "请选择保存位置")
            return
        
        # 获取输入参数
        input_path = self.input_file.get()
        find_text = self.find_text.get()
        replace_text = self.replace_text.get()
        
        # 生成输出文件名
        input_filename = os.path.basename(input_path)
        output_filename = os.path.splitext(input_filename)[0] + "_完成替换.pdf"
        output_path = os.path.join(self.output_dir.get(), output_filename)
        
        # 执行替换
        self.root.config(cursor="wait")
        self.root.update()
        
        success, message, output_file = replace_text_in_pdf(input_path, output_path, find_text, replace_text)
        
        self.root.config(cursor="")
        self.root.update()
        
        if success:
            messagebox.showinfo("成功", f"{message}\n输出文件: {output_file}")
        else:
            messagebox.showerror("错误", message)
    
    def on_cancel(self):
        """取消按钮事件"""
        self.root.quit()

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='PDF文本替换工具')
    parser.add_argument('-i', '--input', help='输入PDF文件路径')
    parser.add_argument('-o', '--output', help='输出PDF文件路径')
    parser.add_argument('-f', '--find', help='要查找的文本')
    parser.add_argument('-r', '--replace', help='要替换的文本')
    
    args = parser.parse_args()
    
    # 如果提供了命令行参数，则直接执行替换
    if args.input and args.output and args.find:
        try:
            replace_text_in_pdf(args.input, args.output, args.find, args.replace)
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        # 否则启动GUI界面
        root = TkinterDnD.Tk()
        app = PDFReplaceGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
