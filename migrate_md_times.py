import os
import re
import sys
from datetime import datetime

def extract_time(content, field):
    """从内容中提取时间字段(created/updated)"""
    # 匹配格式如：created: 2025-04-11 04:11:14Z 或 updated: 2024-12-19 08:10:06Z
    match = re.search(fr'{field}:\s*([0-9\-]+\s[0-9:]+)Z?', content)
    if not match:
        return None
    
    time_str = match.group(1)
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def update_file_time(file_path, created_dt, updated_dt):
    """修改文件的创建时间和修改时间"""
    if not created_dt and not updated_dt:
        return False
    
    # 设置时间戳 (created_time, updated_time)
    created_ts = created_dt.timestamp() if created_dt else None
    updated_ts = updated_dt.timestamp() if updated_dt else None
    
    # 获取当前文件时间
    stat = os.stat(file_path)
    current_atime = stat.st_atime
    current_mtime = stat.st_mtime
    
    # 设置新时间 (保留未指定的时间为原值)
    new_atime = created_ts if created_ts else current_atime
    new_mtime = updated_ts if updated_ts else (created_ts if created_ts else current_mtime)
    
    os.utime(file_path, (new_atime, new_mtime))
    return True

def process_md_files(root_dir):
    """处理目录下所有.md文件"""
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                created_time = extract_time(content, 'created')
                updated_time = extract_time(content, 'updated')
                
                if created_time or updated_time:
                    if update_file_time(file_path, created_time, updated_time):
                        log_msg = []
                        if created_time:
                            log_msg.append(f"created: {created_time}")
                        if updated_time:
                            log_msg.append(f"updated: {updated_time}")
                        print(f"Updated: {file_path} -> {' | '.join(log_msg)}")
                    else:
                        print(f"Failed to update: {file_path}")
                else:
                    print(f"No time fields found in: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate_md_times.py <obsidian_vault_path>")
        sys.exit(1)
    
    obsidian_path = sys.argv[1]
    if not os.path.isdir(obsidian_path):
        print(f"Error: {obsidian_path} is not a valid directory")
        sys.exit(1)
    
    process_md_files(obsidian_path)

# /Users/keke/Documents/Obsidian/Default
