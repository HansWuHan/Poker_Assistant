"""
测试运行器 - 运行所有测试

提供统一的测试运行接口
"""

import sys
import os
import pytest
from pathlib import Path


def run_all_tests():
    """运行所有测试"""
    print("🧪 开始运行所有测试...")
    
    # 获取测试目录
    test_dir = Path(__file__).parent
    
    # 运行测试
    exit_code = pytest.main([
        str(test_dir),
        "-v",  # 详细输出
        "--tb=short",  # 简短的错误回溯
        "--color=yes",  # 彩色输出
        "-m", "not slow"  # 跳过慢速测试
    ])
    
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 测试失败，退出码: {exit_code}")
    
    return exit_code


def run_unit_tests():
    """运行单元测试"""
    print("🧪 开始运行单元测试...")
    
    test_dir = Path(__file__).parent / "unit"
    
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if exit_code == 0:
        print("✅ 单元测试通过！")
    else:
        print(f"❌ 单元测试失败，退出码: {exit_code}")
    
    return exit_code


def run_integration_tests():
    """运行集成测试"""
    print("🔗 开始运行集成测试...")
    
    test_dir = Path(__file__).parent / "integration"
    
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if exit_code == 0:
        print("✅ 集成测试通过！")
    else:
        print(f"❌ 集成测试失败，退出码: {exit_code}")
    
    return exit_code


def run_e2e_tests():
    """运行端到端测试"""
    print("🎮 开始运行端到端测试...")
    
    test_dir = Path(__file__).parent / "e2e"
    
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    if exit_code == 0:
        print("✅ 端到端测试通过！")
    else:
        print(f"❌ 端到端测试失败，退出码: {exit_code}")
    
    return exit_code


def run_gto_tests():
    """运行GTO相关测试"""
    print("🎯 开始运行GTO策略测试...")
    
    test_dir = Path(__file__).parent
    
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes",
        "-m", "gto"
    ])
    
    if exit_code == 0:
        print("✅ GTO策略测试通过！")
    else:
        print(f"❌ GTO策略测试失败，退出码: {exit_code}")
    
    return exit_code


def run_ai_tests():
    """运行AI相关测试"""
    print("🤖 开始运行AI引擎测试...")
    
    test_dir = Path(__file__).parent
    
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes",
        "-m", "ai"
    ])
    
    if exit_code == 0:
        print("✅ AI引擎测试通过！")
    else:
        print(f"❌ AI引擎测试失败，退出码: {exit_code}")
    
    return exit_code


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="运行扑克助手测试")
    parser.add_argument("--type", choices=[
        "all", "unit", "integration", "e2e", "gto", "ai"
    ], default="all", help="测试类型")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 设置Python路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 运行相应的测试
    if args.type == "all":
        exit_code = run_all_tests()
    elif args.type == "unit":
        exit_code = run_unit_tests()
    elif args.type == "integration":
        exit_code = run_integration_tests()
    elif args.type == "e2e":
        exit_code = run_e2e_tests()
    elif args.type == "gto":
        exit_code = run_gto_tests()
    elif args.type == "ai":
        exit_code = run_ai_tests()
    else:
        print(f"❌ 未知的测试类型: {args.type}")
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()