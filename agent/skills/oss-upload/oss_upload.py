#!/usr/bin/env python3
"""
阿里云OSS上传脚本
用法: python3 oss_upload.py <本地文件路径> [OSS Bucket名称] [保存路径]

⚠️ 免责声明：本文件包含占位符配置。请在运行前设置以下环境变量：
  OSS_ACCESS_KEY_ID
  OSS_ACCESS_KEY_SECRET
  OSS_ENDPOINT (可选，默认 oss-cn-hangzhou.aliyuncs.com)
  OSS_DEFAULT_BUCKET (可选，默认 trading-agent-reports)
"""

import sys
import os
import oss2

# 从环境变量读取配置
ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "YOUR_OSS_ACCESS_KEY_ID")
ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "YOUR_OSS_ACCESS_KEY_SECRET")
DEFAULT_BUCKET = os.environ.get("OSS_DEFAULT_BUCKET", "trading-agent-reports")
OSS_ENDPOINT = os.environ.get("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")


def upload_file(file_path, bucket_name=None, save_path=None):
    """上传文件到OSS并返回分享链接"""
    if bucket_name is None:
        bucket_name = DEFAULT_BUCKET

    # 如果没有指定保存路径，使用文件名
    if save_path is None:
        save_path = os.path.basename(file_path)

    # 确保bucket存在（如果不存在会抛出异常）
    bucket = oss2.Bucket(oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET), OSS_ENDPOINT, bucket_name)

    # 上传文件（设置Content-Type和Content-Disposition，浏览器直接显示HTML）
    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Disposition': 'inline'
    }
    with open(file_path, 'rb') as f:
        bucket.put_object(save_path, f, headers)

    # 生成分享链接（公共读）
    # 链接格式: https://bucket.endpoint/保存路径
    url = f"https://{bucket_name}.{OSS_ENDPOINT}/{save_path}"

    return url


def main():
    if len(sys.argv) < 2:
        print("用法: python3 oss_upload.py <本地文件路径> [OSS Bucket名称] [保存路径]")
        print("")
        print("环境变量:")
        print("  OSS_ACCESS_KEY_ID     - 阿里云AccessKey ID")
        print("  OSS_ACCESS_KEY_SECRET - 阿里云AccessKey Secret")
        print("  OSS_ENDPOINT          - OSS节点 (默认: oss-cn-hangzhou.aliyuncs.com)")
        print("  OSS_DEFAULT_BUCKET    - 默认Bucket名称 (默认: trading-agent-reports)")
        sys.exit(1)

    # 检查环境变量
    if ACCESS_KEY_ID == "YOUR_OSS_ACCESS_KEY_ID" or ACCESS_KEY_SECRET == "YOUR_OSS_ACCESS_KEY_SECRET":
        print("错误: 请设置环境变量 OSS_ACCESS_KEY_ID 和 OSS_ACCESS_KEY_SECRET")
        print("或创建 ~/.openclaw/env 文件添加以下配置:")
        print("  export OSS_ACCESS_KEY_ID=your_access_key_id")
        print("  export OSS_ACCESS_KEY_SECRET=your_access_key_secret")
        sys.exit(1)

    file_path = sys.argv[1]
    bucket_name = sys.argv[2] if len(sys.argv) > 2 else None
    save_path = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)

    try:
        url = upload_file(file_path, bucket_name, save_path)
        print(f"上传成功!")
        print(f"分享链接: {url}")
    except oss2.exceptions.NoSuchBucket:
        print(f"错误: Bucket '{bucket_name}' 不存在，请先在阿里云OSS控制台创建")
        sys.exit(1)
    except Exception as e:
        print(f"上传失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
