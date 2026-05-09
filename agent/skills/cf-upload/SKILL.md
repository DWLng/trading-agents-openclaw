---
name: cf-upload
description: |
  Cloudflare Pages 部署工具。
  将生成的 HTML 报告部署到 Cloudflare Pages，生成永久有效的在线链接。
  支持：免备案、全球CDN加速、永久链接不覆盖、相对路径资源自动打包。
homepage: https://github.com/openclaw-trading/cf-upload
version: 1.0.0
---

# cf-upload Cloudflare Pages 部署工具

## 核心优势

| 特性 | 说明 |
|------|------|
| 免备案 | 无需 ICP 备案 |
| 全球加速 | Cloudflare CDN 全球分发 |
| 永久链接 | 每次部署生成独立版本，链接永久有效 |
| 相对路径 | HTML 中的图片/CSS 自动生效 |

## 工作流程

```
Agent 生成 HTML 报告
        ↓
cf_pages_deploy.py 部署到 Cloudflare Pages
        ↓
返回永久在线链接
        ↓
发送给用户
```

## 使用方法

### 命令行

```bash
python3 skills/cf-upload/cf_pages_deploy.py <html文件路径> [project名称]

# 示例
python3 skills/cf-upload/cf_pages_deploy.py memory/reports/报告.html
python3 skills/cf-upload/cf_pages_deploy.py memory/reports/报告.html my-reports
```

### 在 Agent 中调用

```python
import subprocess

result = subprocess.run(
    ["python3", "/Users/mac/.openclaw/agents/trading/skills/cf-upload/cf_pages_deploy.py",
     "/path/to/report.html"],
    capture_output=True,
    text=True
)

url = result.stdout.strip()
# 返回格式: "最终链接: https://xxx.pages.dev/file.html"
```

## 前置条件

1. 安装 Wrangler CLI：`npm install -g wrangler`
2. 登录 Cloudflare：`npx wrangler login`
3. 创建 Pages 项目（在 Cloudflare Dashboard 或首次部署时自动创建）

## 项目名称

默认项目名：`trading-reports`

你可以在 Cloudflare Dashboard 中修改项目设置。
