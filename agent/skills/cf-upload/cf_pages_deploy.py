#!/usr/bin/env python3
"""
Cloudflare Pages 部署脚本
将 HTML 报告部署到 Cloudflare Pages，生成永久有效的在线链接

用法:
    python3 cf_pages_deploy.py <html文件路径> [project名称]

示例:
    python3 cf_pages_deploy.py memory/reports/报告.html
    python3 cf_pages_deploy.py memory/reports/报告.html my-reports
"""

import os
import sys
import subprocess
import re


def deploy_to_cloudflare(html_file_path, project_name="trading-reports"):
    """
    将本地 HTML 报告部署到 Cloudflare Pages

    Args:
        html_file_path: 本地 HTML 文件路径
        project_name: Cloudflare Pages 项目名称

    Returns:
        部署成功返回在线链接，失败返回 None
    """
    if not os.path.exists(html_file_path):
        print(f"错误: 找不到文件 {html_file_path}")
        return None

    # 获取文件所在的目录（Wrangler 按目录部署）
    target_dir = os.path.dirname(html_file_path)
    file_name = os.path.basename(html_file_path)

    print(f"开始部署 {file_name} 到 Cloudflare Pages [{project_name}]...")

    # 构建 Wrangler 部署命令
    cmd = [
        "npx", "wrangler", "pages", "deploy", target_dir,
        "--project-name", project_name
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        # 提取部署后的预览链接
        # Wrangler 输出格式: https://xxxx.project-name.pages.dev
        # 或: https://trading-reports-eov.pages.dev (带hash的项目子domain)
        # 使用通用模式匹配任何 .pages.dev URL
        # 注意: 模式中[.]表示匹配字面量.
        pattern = r"https://[a-zA-Z0-9.-]+[.]pages[.]dev"
        match = re.search(pattern, output)

        if match:
            base_url = match.group(0)
            final_url = f"{base_url}/{file_name}"
            print(f"部署成功!")
            print(f"链接: {final_url}")
            return final_url
        else:
            # 备用：尝试匹配 production URL
            prod_pattern = r"https://" + re.escape(project_name) + r"\.pages\.dev"
            match_prod = re.search(prod_pattern, output)
            if match_prod:
                final_url = f"{match_prod.group(0)}/{file_name}"
                print(f"部署成功 (Production)!")
                print(f"链接: {final_url}")
                return final_url

            print("部署似乎成功，但未找到链接")
            print("Wrangler 输出:", output)
            return None

    except subprocess.CalledProcessError as e:
        print(f"部署失败!")
        print(f"错误信息: {e.stderr}")
        return None


def main():
    if len(sys.argv) < 2:
        print("用法: python3 cf_pages_deploy.py <html文件路径> [project名称]")
        print("示例: python3 cf_pages_deploy.py memory/reports/报告.html")
        sys.exit(1)

    html_path = sys.argv[1]
    project = sys.argv[2] if len(sys.argv) > 2 else "trading-reports"

    url = deploy_to_cloudflare(html_path, project)
    if url:
        print(f"\n最终链接: {url}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
