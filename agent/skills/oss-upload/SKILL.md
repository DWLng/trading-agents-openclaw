---
name: oss-upload
description: |
  阿里云OSS文件上传工具，用于将HTML报告、图表等文件上传到OSS并生成分享链接。
  生成的链接可以直接分享给用户访问，无需下载附件。
homepage: https://github.com/openclaw-trading/oss-upload
version: 1.1.0
---

# oss-upload 阿里云OSS上传工具

本skill用于将生成的报告文件上传到阿里云OSS，并生成分享链接。

## 前置条件

1. 已安装Python 3环境
2. 已安装oss2库: `pip install oss2`
3. 已配置阿里云AccessKey

## 配置信息

在 `~/.openclaw/env` 或shell配置文件中设置以下环境变量：

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `OSS_ACCESS_KEY_ID` | 阿里云AccessKey ID | LTAI5txxxxxxxxxx |
| `OSS_ACCESS_KEY_SECRET` | 阿里云AccessKey Secret | xxxxxxxxxx |
| `OSS_ENDPOINT` | OSS节点 (可选) | oss-cn-hangzhou.aliyuncs.com |
| `OSS_DEFAULT_BUCKET` | 默认Bucket (可选) | trading-agent-reports |

## 使用方法

### 基本用法

```bash
source ~/.venv/oss/bin/activate
python3 skills/oss-upload/oss_upload.py <文件路径>
```

### 指定Bucket和保存路径

```bash
python3 skills/oss-upload/oss_upload.py <文件路径> <bucket名称> <保存路径>
```

### 在Agent工作流中调用

```python
import subprocess
import os

result = subprocess.run(
    [
        "python3",
        "/path/to/oss_upload.py",
        "memory/reports/600519_maotai_20260510.html"
    ],
    capture_output=True,
    text=True,
    env={**os.environ, "PATH": "/path/to/venv/bin:" + os.environ.get("PATH", "")}
)

# 解析输出获取URL
url = result.stdout.strip().split("分享链接: ")[-1]
```

## 输出格式

上传成功后返回:
```
上传成功!
分享链接: https://trading-agent-reports.oss-cn-shanghai.aliyuncs.com/600519_maotai_20260510.html
```

## 注意事项

1. Bucket需要设置为公共读权限
2. 文件名中包含中文可能会导致URL编码问题，建议使用英文或拼音
3. 确保OSS Bucket已创建
4. AccessKey建议使用RAM子账号，遵循最小权限原则
