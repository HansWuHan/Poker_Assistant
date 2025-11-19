#!/usr/bin/env python3
"""
分析AI决策逻辑问题：为什么连续选择最低概率的fold
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_decision_logic():
    """分析决策逻辑问题"""
    print("🔍 分析AI决策逻辑问题")
    print("="*60)
    
    print("问题现象:")
    print("  AI_4: fold概率19%，但选择了fold")
    print("  AI_5: fold概率17%，但选择了fold")
    print("  连续两个AI都选择了最低概率的行动")
    print()
    
    print("可能的原因:")
    print("1. 频率分布显示的是理论GTO频率")
    print("2. 实际决策使用随机数生成器")
    print("3. 随机选择可能导致连续选中低概率事件")
    print("4. 缺乏决策一致性检查")
    print()
    
    print("代码逻辑分析:")
    print("  - _calculate_vs_raise_action() 使用随机数选择")
    print("  - rand = random.random()")
    print("  - cumulative += frequency")
    print("  - if rand <= cumulative: 选择该行动")
    print()
    
    print("统计概率:")
    print("  假设fold概率19%，选择fold的概率确实是19%")
    print("  两个独立事件都选择fold的概率: 19% × 17% ≈ 3.2%")
    print("  虽然概率不高，但在统计学上是正常的")
    print()
    
    print("是否需要修复？")
    print("  ✅ 建议修复：增加决策一致性")
    print("  ✅ 避免连续低概率选择")
    print("  ✅ 保持GTO策略的真实性")

if __name__ == "__main__":
    analyze_decision_logic()