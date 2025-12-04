#!/usr/bin/env python3
"""
ComfyUI-Login 自动设置脚本
自动将用户名和密码注入到ComfyUI-Login系统中，无需首次登录设置

用法:
    python setup_login.py <username> <password>
    或
    python setup_login.py --username <username> --password <password>

示例:
    python setup_login.py admin mypassword123
    python setup_login.py --username admin --password mypassword123
"""

import os
import sys
import argparse
import bcrypt

def get_comfy_dir():
    """获取ComfyUI根目录"""
    # 尝试从当前脚本位置推断ComfyUI根目录
    # 脚本在 custom_nodes/ComfyUI-Login/ 目录下
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上两级到达ComfyUI根目录
    comfy_dir = os.path.dirname(os.path.dirname(script_dir))
    
    # 验证是否是ComfyUI目录（检查是否有folder_paths.py）
    folder_paths_file = os.path.join(comfy_dir, "folder_paths.py")
    if os.path.exists(folder_paths_file):
        return comfy_dir
    
    # 如果推断失败，尝试使用环境变量或当前工作目录
    # 检查当前目录是否是ComfyUI根目录
    if os.path.exists(os.path.join(os.getcwd(), "folder_paths.py")):
        return os.getcwd()
    
    # 如果都失败，返回推断的目录（让用户知道可能需要调整）
    return comfy_dir

def setup_login(username, password, comfy_dir=None, force=False):
    """设置登录凭据"""
    if comfy_dir is None:
        comfy_dir = get_comfy_dir()
    
    login_dir = os.path.join(comfy_dir, "login")
    password_path = os.path.join(login_dir, "PASSWORD")
    
    # 创建login目录（如果不存在）
    if not os.path.exists(login_dir):
        os.makedirs(login_dir)
        print(f"已创建目录: {login_dir}")
    
    # 检查是否已存在密码文件
    if os.path.exists(password_path):
        if not force:
            print(f"密码文件已存在 ({password_path})，跳过设置。")
            return True
        else:
            print(f"覆盖已存在的密码文件: {password_path}")
    
    # 使用bcrypt对密码进行哈希
    print("正在加密密码...")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # 写入密码文件
    # 格式：第一行是哈希密码，第二行是用户名
    with open(password_path, "wb") as file:
        file.write(hashed_password + b'\n' + username.encode('utf-8'))
    
    print(f"✓ 登录凭据已成功设置！")
    print(f"  用户名: {username}")
    print(f"  密码文件: {password_path}")
    print(f"\n提示: 重启ComfyUI后，可以使用这些凭据登录。")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='自动设置ComfyUI-Login的用户名和密码',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s admin mypassword123
  %(prog)s --username admin --password mypassword123
  %(prog)s admin mypassword123 --force
  %(prog)s admin mypassword123 --comfy-dir /path/to/ComfyUI
        """
    )
    
    # 支持两种参数格式
    parser.add_argument('username', nargs='?', help='用户名')
    parser.add_argument('password', nargs='?', help='密码')
    parser.add_argument('--username', '--user', '-u', dest='username_arg', help='用户名（可选参数格式）')
    parser.add_argument('--password', '--pass', '-p', dest='password_arg', help='密码（可选参数格式）')
    parser.add_argument('--comfy-dir', '--dir', '-d', dest='comfy_dir', help='ComfyUI根目录路径（可选，默认自动检测）')
    parser.add_argument('--force', '-f', action='store_true', help='强制覆盖已存在的密码文件（非交互模式）')
    
    args = parser.parse_args()
    
    # 确定用户名和密码
    username = args.username_arg if args.username_arg else args.username
    password = args.password_arg if args.password_arg else args.password
    
    # 验证参数
    if not username:
        parser.error("请提供用户名。使用 --help 查看帮助信息。")
    
    if not password:
        parser.error("请提供密码。使用 --help 查看帮助信息。")
    
    # 执行设置
    try:
        success = setup_login(username, password, comfy_dir=args.comfy_dir, force=args.force)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

