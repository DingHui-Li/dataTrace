import os
import subprocess
import sys

def run_command(command, cwd=None):
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"执行命令失败: {command}")
        print(f"错误信息: {str(e)}")
        return False

def build_frontend(install_deps=True):
    print("正在构建前端项目...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    # 安装前端依赖
    if install_deps:
        print("安装前端依赖...")
        if not run_command('npm install', cwd=frontend_dir):
            return False
    
    # 构建前端项目
    if not run_command('npm run build', cwd=frontend_dir):
        return False
    
    return True

def install_backend_dependencies():
    print("正在安装后端依赖...")
    # 安装Python依赖
    if not run_command(f'{sys.executable} -m pip install -r requirements.txt'):
        return False
    
    return True

def create_executable():
    print("正在创建可执行文件...")
    # 使用PyInstaller打包
    spec_content = '''\
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),
        ('frontend/dist/assets', 'frontend/dist/assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dataTrace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # 创建spec文件
    with open('dataTrace.spec', 'w') as f:
        f.write(spec_content)
    
    # 运行PyInstaller
    if not run_command('pyinstaller dataTrace.spec'):
        return False
    
    return True

def main():
    # 交互式菜单
    print("\nDataTrace打包工具 - 请选择是否安装依赖：")
    print("1. 安装依赖并构建项目")
    print("2. 跳过依赖安装直接构建")
    print("0. 退出")
    
    choice = input("\n请输入选项编号：")
    
    if choice == '0':
        return
    elif choice == '1':
        # 安装依赖并构建
        if not build_frontend(install_deps=True):
            print("前端构建失败")
            return
        
        if not install_backend_dependencies():
            print("后端依赖安装失败")
            return
    elif choice == '2':
        # 跳过依赖安装直接构建
        if not build_frontend(install_deps=False):
            print("前端构建失败")
            return
    else:
        print("无效的选项")
        return
    
    # 创建可执行文件
    if not create_executable():
        print("可执行文件创建失败")
        return
    
    print("\n构建完成！")
    print("可执行文件位于: dist/dataTrace.exe")

if __name__ == '__main__':
    main()