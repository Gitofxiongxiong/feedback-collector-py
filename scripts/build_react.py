#!/usr/bin/env python3
"""
React 应用构建脚本
自动安装依赖并构建 React 应用
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_node_npm():
    """检查 Node.js 和 npm 是否安装"""
    try:
        # 检查 Node.js
        node_result = subprocess.run(['node', '--version'], 
                                   capture_output=True, text=True, check=True)
        logger.info(f"Node.js 版本: {node_result.stdout.strip()}")
        
        # 检查 npm
        npm_result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, check=True)
        logger.info(f"npm 版本: {npm_result.stdout.strip()}")
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error("Node.js 或 npm 未安装或不在 PATH 中")
        logger.error("请安装 Node.js: https://nodejs.org/")
        return False

def install_dependencies():
    """安装 npm 依赖"""
    logger.info("安装 npm 依赖...")
    try:
        result = subprocess.run(['npm', 'install'], 
                              check=True, capture_output=True, text=True)
        logger.info("依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"依赖安装失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False

def build_react_app():
    """构建 React 应用"""
    logger.info("构建 React 应用...")
    try:
        result = subprocess.run(['npm', 'run', 'build'], 
                              check=True, capture_output=True, text=True)
        logger.info("React 应用构建成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"React 应用构建失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        return False

def check_build_output():
    """检查构建输出"""
    build_dir = Path("build")
    if not build_dir.exists():
        logger.error("构建目录不存在")
        return False
    
    index_file = build_dir / "index.html"
    if not index_file.exists():
        logger.error("index.html 文件不存在")
        return False
    
    static_dir = build_dir / "static"
    if not static_dir.exists():
        logger.warning("static 目录不存在")
    
    logger.info("构建输出检查通过")
    return True

def main():
    """主函数"""
    logger.info("开始构建 React 应用...")

    # 检查当前目录是否有 package.json
    if not Path("package.json").exists():
        logger.error("当前目录没有 package.json 文件")
        logger.error("请确保在 frontend 目录运行此脚本")
        logger.error("或者使用主启动脚本: python start.py build")
        return False
    
    # 检查 Node.js 和 npm
    if not check_node_npm():
        return False
    
    # 安装依赖
    if not install_dependencies():
        return False
    
    # 构建应用
    if not build_react_app():
        return False
    
    # 检查构建输出
    if not check_build_output():
        return False
    
    logger.info("🎉 React 应用构建完成！")
    logger.info("现在可以通过 FastAPI 服务器访问 React 应用:")
    logger.info("  - React 版本: http://localhost:8000/react")
    logger.info("  - HTML 版本: http://localhost:8000/feedback_ui.html")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
