# PDF 批量文字替换工具

一个基于 Tauri 和 Rust 开发的桌面应用程序，用于批量替换 PDF 文件中的指定文字。

## 功能特性

- 支持 PDF 文件的批量文字替换
- 支持中文字符替换
- 保持原 PDF 格式（布局、图片、字体等）
- 极简设计的用户界面
- 显示替换进度和结果统计

## 技术栈

- **前端框架**：Svelte 5
- **后端语言**：Rust
- **框架**：Tauri
- **PDF 处理库**：lopdf

## 系统要求

- Windows 10 或更高版本
- Rust 1.92.0 或更高版本
- Node.js 18 或更高版本

## 安装与构建

### 1. 安装依赖

```bash
# 安装 Node.js 依赖
npm install
```

### 2. 开发模式运行

```bash
# 启动开发服务器
npm run tauri dev
```

### 3. 构建生产版本

```bash
# 构建应用程序
npm run tauri build
```

构建完成后，可执行文件将位于 `src-tauri/target/release/` 目录下。

## 使用说明

1. **选择 PDF 文件**：点击"选择文件"按钮或拖拽 PDF 文件到选择区
2. **选择输出目录**：选择替换后文件的保存位置
3. **设置替换内容**：在"查找内容"输入框中输入要替换的文字，在"替换为"输入框中输入替换后的文字
4. **开始替换**：点击"开始替换"按钮，等待替换完成
5. **查看结果**：替换完成后，将显示成功替换的次数

## 代码结构

```
pdf-replace/
├── src/                      # 前端代码目录
│   ├── lib/                  # Svelte 组件库
│   └── routes/               # 路由页面
│       └── +page.svelte      # 主页面组件
├── src-tauri/                # Tauri 后端代码目录
│   ├── src/                  # Rust 源代码
│   │   └── lib.rs            # 主 Rust 库文件
│   ├── Cargo.toml            # Rust 依赖配置
│   └── tauri.conf.json       # Tauri 配置文件
├── package.json              # Node.js 依赖配置
└── vite.config.js            # Vite 配置文件
```

## 核心功能实现

### 前端实现

- 使用 Svelte 5 构建用户界面
- 调用 Tauri API 实现文件选择和目录选择
- 通过 Tauri 命令与 Rust 后端通信

### 后端实现

- 使用 lopdf 库处理 PDF 文件
- 实现 PDF 文字替换算法
- 提供 Tauri 命令供前端调用

## 许可证

MIT License
