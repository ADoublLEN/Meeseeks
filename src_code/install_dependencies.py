#!/usr/bin/env python3
"""
OG_meeseeks 依赖安装脚本
独立运行此脚本来安装所有必要的依赖包
"""

import sys
import subprocess
import os

def install_requirements():
    """安装requirements.txt中的依赖包"""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')

    print("🚀 OG_meeseeks 依赖安装脚本")
    print("=" * 50)

    if not os.path.exists(requirements_file):
        print("❌ 未找到requirements.txt文件")
        return False

    print("🔧 开始安装依赖包...")

    try:
        # 读取requirements.txt
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = f.readlines()

        # 过滤掉注释和空行
        packages = []
        for line in requirements:
            line = line.strip()
            if line and not line.startswith('#'):
                packages.append(line)

        if not packages:
            print("📦 未发现需要安装的依赖包")
            return True

        print(f"📦 发现 {len(packages)} 个依赖包:")
        for i, package in enumerate(packages, 1):
            print(f"   {i}. {package}")

        print("\n🔄 开始安装...")

        # 升级pip
        print("📈 升级pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])

        # 安装依赖
        print("📦 安装依赖包...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])

        print("\n✅ 所有依赖包安装完成!")
        print("🎉 现在可以运行 run.py 了!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 安装依赖包时出错: {e}")
        print("💡 请尝试手动运行:")
        print(f"   pip install -r {requirements_file}")
        return False

    except Exception as e:
        print(f"\n❌ 读取requirements.txt时出错: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ 需要Python 3.6或更高版本")
        return False

    print("✅ Python版本符合要求")
    return True

def main():
    """主函数"""
    print("🎯 OG_meeseeks 环境检查与依赖安装")
    print("=" * 60)

    # 检查Python版本
    if not check_python_version():
        sys.exit(1)

    print()

    # 安装依赖
    if install_requirements():
        print("\n🎊 安装完成! 可以开始使用OG_meeseeks了!")
        print("\n📖 使用方法:")
        print("   python run.py --help")
    else:
        print("\n💔 安装失败，请检查错误信息并手动安装依赖")
        sys.exit(1)

if __name__ == "__main__":
    main()
