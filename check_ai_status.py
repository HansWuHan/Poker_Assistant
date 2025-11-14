#!/usr/bin/env python3
"""
简单验证 - 检查AI替换是否成功
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_ai_replacement():
    """检查AI替换状态"""
    print("🔍 检查AI替换状态")
    print("="*50)
    
    # 检查game_controller.py文件
    controller_file = "/Users/bytedance/hanbro/Poker_Assistant/poker_assistant/engine/game_controller.py"
    
    try:
        with open(controller_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入语句
        if "from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer" in content:
            print("✅ 导入语句已更新为改进AI")
        else:
            print("❌ 导入语句未更新")
        
        # 检查实例化语句
        if "ImprovedAIOpponentPlayer(difficulty=diff, shared_hole_cards=self.shared_hole_cards)" in content:
            print("✅ AI实例化已使用改进AI")
        else:
            print("❌ AI实例化未更新")
        
        # 检查是否还有旧引用
        if "AIOpponentPlayer(" in content and "ImprovedAIOpponentPlayer" not in content:
            print("❌ 仍然使用旧AI类")
        elif "ImprovedAIOpponentPlayer(" in content:
            print("✅ 成功替换为改进AI")
        
        print("\n📋 文件状态:")
        print(f"文件大小: {len(content)} 字符")
        
        # 显示相关行
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'improved_ai_opponent' in line or 'AIOpponentPlayer' in line:
                print(f"第{i}行: {line.strip()}")
        
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
    
    # 检查改进AI文件是否存在
    improved_ai_file = "/Users/bytedance/hanbro/Poker_Assistant/poker_assistant/engine/improved_ai_opponent.py"
    if os.path.exists(improved_ai_file):
        print(f"\n✅ 改进AI文件存在: {improved_ai_file}")
        
        # 检查文件内容
        try:
            with open(improved_ai_file, 'r', encoding='utf-8') as f:
                improved_content = f.read()
            
            if "class ImprovedAIOpponentPlayer" in improved_content:
                print("✅ 改进AI类定义存在")
            
            # 统计方法数量
            method_count = improved_content.count("def ")
            print(f"✅ 包含 {method_count} 个方法")
            
        except Exception as e:
            print(f"❌ 读取改进AI文件失败: {e}")
    else:
        print(f"\n❌ 改进AI文件不存在")
    
    print("\n✅ 检查完成!")
    print("\n🎯 下一步:")
    print("1. 运行游戏测试新的AI行为")
    print("2. 观察AI是否更理性地弃牌")
    print("3. 检查下注尺度是否更合理")

if __name__ == "__main__":
    check_ai_replacement()