#!/usr/bin/env python3
"""
安装验证脚本
检查所有模块是否正常加载
"""
import sys
import os

print("🔍 验证德州扑克 AI 助手安装...")
print("="*60)

errors = []

# 1. 检查 Python 版本
print("\n1. 检查 Python 版本...")
if sys.version_info < (3, 8):
    errors.append("Python 版本过低，需要 3.8+")
    print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor}")
else:
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# 2. 检查依赖包
print("\n2. 检查依赖包...")
required_packages = [
    'pypokerengine',
    'openai',
    'rich',
    'dotenv',
    'prompt_toolkit'
]

for package in required_packages:
    try:
        if package == 'dotenv':
            __import__('dotenv')
        else:
            __import__(package.replace('-', '_'))
        print(f"✅ {package}")
    except ImportError:
        errors.append(f"缺少依赖包: {package}")
        print(f"❌ {package}")

# 3. 检查环境变量
print("\n3. 检查环境变量...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('DEEPSEEK_API_KEY', '')
if not api_key or api_key == 'your_api_key_here':
    print("⚠️  DEEPSEEK_API_KEY 未配置（AI 功能将不可用）")
else:
    print(f"✅ DEEPSEEK_API_KEY 已配置: {api_key[:10]}...")

# 4. 检查模块导入
print("\n4. 检查项目模块...")
try:
    from poker_assistant.utils.config import config
    print("✅ utils.config")
    
    from poker_assistant.engine.game_controller import GameController
    print("✅ engine.game_controller")
    
    from poker_assistant.cli.game_renderer import GameRenderer
    print("✅ cli.game_renderer")
    
    from poker_assistant.llm_service.deepseek_client import DeepseekClient
    print("✅ llm_service.deepseek_client")
    
    from poker_assistant.ai_analysis.strategy_advisor import StrategyAdvisor
    print("✅ ai_analysis.strategy_advisor")
    
except Exception as e:
    errors.append(f"模块导入失败: {e}")
    print(f"❌ {e}")

# 5. 总结
print("\n" + "="*60)
if errors:
    print("❌ 验证失败，发现以下问题:")
    for error in errors:
        print(f"  - {error}")
    print("\n请解决上述问题后重试。")
    sys.exit(1)
else:
    print("✅ 所有检查通过！")
    print("\n🎉 德州扑克 AI 助手已准备就绪！")
    print("\n运行以下命令开始游戏:")
    print("  python3 main.py")
    sys.exit(0)

