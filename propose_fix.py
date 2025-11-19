#!/usr/bin/env python3
"""
修复AI决策逻辑：增加决策一致性检查
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def propose_fix():
    """提出修复方案"""
    print("🔧 提出AI决策逻辑修复方案")
    print("="*60)
    
    print("问题核心:")
    print("  频率分布显示理论概率（如fold 19%）")
    print("  但实际决策可能连续选择低概率事件")
    print("  导致用户困惑：为什么总是选最低概率的？")
    print()
    
    print("修复方案:")
    print("1. 增加决策一致性权重")
    print("2. 避免连续极端低概率选择")
    print("3. 保持GTO策略的真实性")
    print("4. 增加随机种子控制可重复性")
    print()
    
    print("具体实现:")
    print("  - 当某个行动概率<25%时，降低其选择权重")
    print("  - 增加'决策稳定性'参数")
    print("  - 保持长期统计一致性")
    print()
    
    print("代码修改位置:")
    print("  /Users/bytedance/hanbro/Poker_Assistant/poker_assistant/gto_strategy/gto_core.py")
    print("  方法: _calculate_vs_raise_action() 第507-519行")
    print()

if __name__ == "__main__":
    propose_fix()