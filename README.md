# Yoobit Docker Mirror System

一个用于自动拉取、标记和推送 Docker 镜像到私有镜像仓库的 Web 应用。

## 功能特点

- 简洁的 Web 界面
- 实时显示操作日志
- 自动发送邮件通知
- 支持自定义镜像仓库地址
- 支持一键清理本地镜像

## 系统要求

- Python 3.8+
- Docker
- SMTP 服务器（用于发送邮件通知）

## 安装部署

1. 克隆仓库：
```bash
git clone https://github.com/OliverMao/yoobit-docker-mirror.git
cd DockerRegistry
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
   - 复制 `.env.default` 为 `.env`
   - 编辑 `.env` 文件，填入必要的配置信息：
```ini
SMTP_SERVER=your-smtp-server
SMTP_PORT=your-smtp-port
SENDER_EMAIL=your-sender-email
SENDER_PASSWORD=your-email-password
RECEIVER_EMAIL=["email1@example.com", "email2@example.com"]
DOCKER_REGISTRY_URL=your-registry-url
```

4. 启动服务：
```bash
python web.py
```
服务将在 `http://localhost:8001` 启动

## 使用方法

1. 访问 Web 界面：
   - 打开浏览器访问 `http://localhost:8001`

2. 更新镜像：
   - 在输入框中输入要更新的镜像名称和标签（例如：`nginx:latest`）
   - 点击"更新并推送"按钮
   - 在日志窗口实时查看操作进度

3. 查看结果：
   - 操作完成后会收到邮件通知
   - 可以在日志窗口查看详细操作记录
   - 可以使用清除按钮清空日志

## 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| SMTP_SERVER | SMTP服务器地址 | smtp.example.com |
| SMTP_PORT | SMTP服务器端口 | 587 |
| SENDER_EMAIL | 发件人邮箱 | sender@example.com |
| SENDER_PASSWORD | 发件人密码/授权码 | your-password |
| RECEIVER_EMAIL | 收件人邮箱列表（JSON格式） | ["user1@example.com"] |
| DOCKER_REGISTRY_URL | Docker镜像仓库地址 | registry.example.com |

### 邮件通知

系统会在以下情况发送邮件通知：
- 镜像更新成功
- 更新过程中发生错误

## 开发说明

### 项目结构

```
DockerRegistry/
├── web.py              # 主应用程序
├── requirements.txt    # Python依赖
├── .env.default       # 环境变量模板
├── .env              # 实际环境变量配置
├── templates/        # HTML模板
│   └── index.html   # 主页面
└── README.md        # 项目文档
```

### 技术栈

- 后端：Flask
- 前端：Bootstrap 5 + Boxicons
- 实时日志：Server-Sent Events (SSE)
- 容器技术：Docker

## 常见问题

1. 邮件发送失败
   - 检查SMTP服务器配置是否正确
   - 确认密码/授权码是否有效
   - 检查端口是否被防火墙阻止

2. Docker操作失败
   - 确保Docker服务正在运行
   - 检查用户是否有Docker操作权限
   - 验证镜像仓库地址是否可访问

3. 页面无法访问
   - 确认服务是否正在运行
   - 检查端口(8001)是否被占用
   - 验证防火墙设置

## 安全建议

1. 环境变量
   - 不要将 `.env` 文件提交到版本控制系统
   - 定期更换邮箱密码/授权码
   - 使用环境变量管理敏感信息

2. 部署
   - 建议使用反向代理（如Nginx）
   - 启用HTTPS
   - 添加访问控制

## 许可证

[Your License]

## 贡献指南

欢迎提交 Issue 和 Pull Request
