# 基于minimax-m2.5 & openclaw 生成的个人图床程序

## 1. 项目概述

- **项目名称**: PicHome 图床系统
- **项目类型**: Web 应用（Flask + SQLite）
- **核心功能**: 带用户系统的轻量级图床，支持图片上传、分享和广场浏览
- **目标用户**: 个人用户、小型团队

## 2. 技术栈

- **后端**: Flask (Python)
- **数据库**: SQLite（轻量，无需配置）
- **前端**: HTML5 + CSS3 + JavaScript（现代简约设计）
- **存储**: 本地文件系统

## 3. 功能列表

### 3.1 用户系统
- 用户注册（用户名、邮箱、密码）
- 用户登录/登出
- Session 会话管理
- 用户头像（可选）

### 3.2 图片管理
- 图片上传（支持拖拽）
- 图片预览（缩略图 + 原图）
- 图片删除（仅本人图片）
- 复制图片链接（Markdown/URL）
- 图片 tagging（标签）

### 3.3 图片广场
- 最新上传图片展示
- 分页浏览
- 图片点击放大
- 上传者信息展示

### 3.4 个人中心
- 我的图片列表
- 上传统计
- 账户设置

## 4. 数据库设计

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| username | TEXT | 唯一用户名 |
| email | TEXT | 邮箱 |
| password_hash | TEXT | 密码哈希 |
| avatar | TEXT | 头像路径 |
| created_at | DATETIME | 注册时间 |

### images 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| user_id | INTEGER | 上传者ID |
| filename | TEXT | 存储文件名 |
| original_name | TEXT | 原始文件名 |
| file_path | TEXT | 文件路径 |
| file_size | INTEGER | 文件大小 |
| width | INTEGER | 宽度 |
| height | INTEGER | 高度 |
| tags | TEXT | 标签（逗号分隔） |
| views | INTEGER | 查看次数 |
| created_at | DATETIME | 上传时间 |

## 5. 页面设计

### 5.1 登录/注册页
- 现代化卡片设计
- 输入验证
- 错误提示

### 5.2 首页（广场）
- 瀑布流/网格布局
- 顶部导航栏
- 登录/未登录状态切换

### 5.3 上传页
- 拖拽上传区域
- 进度条
- 标签输入

### 5.4 个人中心
- 图片网格
- 统计卡片
- 操作按钮

## 6. 存储结构

```
/home/ubuntu/.openclaw/workspace/pichome/
├── app.py              # 主应用
├── database.py         # 数据库初始化
├── static/
│   ├── uploads/        # 图片存储目录
│   │   └── {year}/{month}/  # 按年月分类
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── upload.html
    ├── profile.html
    └── image.html
```

## 7. 验收标准

- [ ] 用户可以注册和登录
- [ ] 上传图片成功并显示
- [ ] 广场展示所有用户图片
- [ ] 可以删除自己的图片
- [ ] 页面美观，响应式设计
- [ ] 无需额外数据库配置
