#!/usr/bin/env python3
"""
微信附件提取脚本（配合原版 WechatExporter 使用）

使用方法：
1. 先用原版 WechatExporter 导出聊天记录
2. 运行此脚本提取附件并生成链接
"""

import os
import sqlite3
import shutil
from pathlib import Path

# 配置
BACKUP_PATH = os.path.expanduser("~/Library/Application Support/MobileSync/Backup/00008140-000139E62247001C")
WECHAT_EXPORT_PATH = os.path.expanduser("~/Documents/WechatExport_Output")
MANIFEST_DB = os.path.join(BACKUP_PATH, "Manifest.db")

def extract_attachments():
    """提取所有文档附件"""

    print("🔍 正在扫描附件...")

    # 连接 Manifest.db
    conn = sqlite3.connect(MANIFEST_DB)
    cursor = conn.cursor()

    # 查询所有文档附件
    query = """
    SELECT fileID, relativePath
    FROM Files
    WHERE relativePath LIKE '%OpenData%'
      AND (relativePath LIKE '%.pdf'
        OR relativePath LIKE '%.doc'
        OR relativePath LIKE '%.docx'
        OR relativePath LIKE '%.xls'
        OR relativePath LIKE '%.xlsx'
        OR relativePath LIKE '%.ppt'
        OR relativePath LIKE '%.pptx'
        OR relativePath LIKE '%.zip'
        OR relativePath LIKE '%.rar'
        OR relativePath LIKE '%.7z')
    """

    cursor.execute(query)
    files = cursor.fetchall()

    print(f"✅ 找到 {len(files)} 个文档附件")

    # 创建 attachments 目录
    attachments_dir = os.path.join(WECHAT_EXPORT_PATH, "attachments")
    os.makedirs(attachments_dir, exist_ok=True)

    # 提取文件
    extracted = 0
    for file_id, relative_path in files:
        # 构建源文件路径
        src_path = os.path.join(BACKUP_PATH, file_id[:2], file_id)

        if not os.path.exists(src_path):
            continue

        # 提取会话 hash
        parts = relative_path.split('/')
        if len(parts) >= 4:
            session_hash = parts[3]
        else:
            session_hash = "unknown"

        # 创建会话目录
        session_dir = os.path.join(attachments_dir, session_hash)
        os.makedirs(session_dir, exist_ok=True)

        # 提取文件名
        filename = os.path.basename(relative_path)

        # 复制文件
        dest_path = os.path.join(session_dir, filename)
        try:
            shutil.copy2(src_path, dest_path)
            extracted += 1
            if extracted % 100 == 0:
                print(f"   已提取 {extracted}/{len(files)} 个文件...")
        except Exception as e:
            print(f"❌ 复制失败: {filename} - {e}")

    conn.close()

    print(f"\n✅ 完成！共提取 {extracted} 个文档附件")
    print(f"📁 输出目录: {attachments_dir}")

    return extracted

def add_html_links():
    """在 HTML 中添加附件链接（简化版）"""

    print("\n🔗 正在添加 HTML 链接...")

    # 这个功能需要解析 HTML 并插入链接
    # 由于原版 WechatExporter 已经生成了 HTML，修改会比较复杂
    # 建议：手动在浏览器中打开 attachments 目录查看

    print("⚠️  HTML 链接功能需要修改 WechatExporter 源码")
    print("💡 您可以手动打开 attachments 目录查看附件")

if __name__ == "__main__":
    print("=== 微信附件提取工具 ===\n")

    # 检查路径
    if not os.path.exists(BACKUP_PATH):
        print(f"❌ iTunes 备份不存在: {BACKUP_PATH}")
        exit(1)

    if not os.path.exists(WECHAT_EXPORT_PATH):
        print(f"❌ WechatExporter 导出目录不存在: {WECHAT_EXPORT_PATH}")
        print("💡 请先使用 WechatExporter 导出聊天记录")
        exit(1)

    # 提取附件
    extracted = extract_attachments()

    if extracted > 0:
        print("\n📊 统计信息:")
        attachments_dir = os.path.join(WECHAT_EXPORT_PATH, "attachments")

        # 按类型统计
        extensions = {}
        for root, dirs, files in os.walk(attachments_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1

        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count} 个")

        print(f"\n✅ 附件已提取到: {attachments_dir}")
        print("💡 您可以在 Finder 中打开此目录查看附件")
