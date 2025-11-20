#!/usr/bin/env python3
"""
验证GTO频率计算和决策逻辑的一致性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.gto_strategy.gto_core import GTOCore
from poker_assistant.gto_strategy.gto_core import GTOSituation

def test_frequency_consistency():
    """测试频率计算和决策的一致性"""
    print("🔍 验证GTO频率计算和决策逻辑一致性")
    print("="*60)
    
    # 创建GTO核心引擎
    gto_core = GTOCore()
    
    # 测试场景：面对加注的情况（类似你观察到的场景）
    print("\n📋 测试场景：面对加注的防守决策")
    print("-" * 40)
    
    # 模拟K♠ Q♠ 在按钮位面对加注
    situation = GTOSituation(
        street='preflop',
        position='BTN',  # 按钮位
        stack_size=100,
        pot_size=45,  # 底池45（加注到30）
        community_cards=[],
        hole_cards=['SK', 'SQ'],  # K♠ Q♠
        opponent_actions=[
            {'player': 'AI_1', 'action': 'raise', 'amount': 30}
        ],
        active_opponents=1
    )
    
    print("输入参数:")
    print(f"  手牌: K♠ Q♠")
    print(f"  位置: 按钮位")
    print(f"  底池: \)45")
    print(f"  需要跟注: \(30")
    print(f"  对手: 1个玩家加注到\)30")
    
    # 获取GTO决策
    gto_action = gto_core.calculate_gto_action(situation)
    
    print(f"\n🎯 GTO决策结果:")
    print(f"  推荐行动: {gto_action.action}")
    print(f"  建议金额: {gto_action.amount}")
    print(f"  执行频率: {gto_action.frequency:.1%}")
    print(f"  决策理由: {gto_action.reasoning}")
    
    # 获取频率分析（用于思考过程显示）
    from poker_assistant.gto_strategy.types import GTOContext
    context = GTOContext(
        street='preflop',
        position='BTN',
        stack_size=100,
        pot_size=45,
        community_cards=[],
        hole_cards=['SK', 'SQ'],
        opponent_actions=[{'player': 'AI_1', 'action': 'raise', 'amount': 30}],
        active_opponents=1,
        call_amount=30,
        valid_actions=[
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
    )
    
    # 获取详细频率分析
    freq_result = gto_core._calculate_action_frequencies_new(context)
    frequencies = freq_result.action_frequencies
    
    print(f"\n📊 频率分析:")
    for action, freq in frequencies.items():
        percentage = freq * 100
        bar_length = int(percentage / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {action}: {percentage:.1f}% [{bar}]")
    
    # 验证决策是否与频率一致
    print(f"\n🔍 一致性验证:")
    actual_action = gto_action.action
    actual_freq = frequencies.get(actual_action, 0)
    
    if actual_freq < 0.2:
        print(f"  ⚠️  警告：选择了低概率行动 {actual_action} ({actual_freq:.1%})")
        print(f"  📈 建议检查频率计算逻辑")
    else:
        print(f"  ✅ 决策合理：选择了{actual_action} ({actual_freq:.1%})")
    
    return actual_freq

def test_multiple_simulations():
    """进行多次模拟测试统计"""
    print(f"\n📈 多次模拟测试（100次）")
    print("-" * 40)
    
    gto_core = GTOCore()
    situation = GTOSituation(
        street='preflop',
        position='BTN',
        stack_size=100,
        pot_size=45,
        community_cards=[],
        hole_cards=['SK', 'SQ'],  # K♠ Q♠
        opponent_actions=[
            {'player': 'AI_1', 'action': 'raise', 'amount': 30}
        ],
        active_opponents=1
    )
    
    # 统计100次决策
    action_counts = {'fold': 0, 'call': 0, 'raise': 0}
    
    for i in range(100):
        gto_action = gto_core.calculate_gto_action(situation)
        action_counts[gto_action.action] += 1
    
    print("100次模拟结果:")
    for action, count in action_counts.items():
        percentage = count / 100
        print(f"  {action}: {count}次 ({percentage:.1%})")
    
    # 获取理论频率对比
    from poker_assistant.gto_strategy.types import GTOContext
    context = GTOContext(
        street='preflop', position='BTN', stack_size=100, pot_size=45,
        community_cards=[], hole_cards=['SK', 'SQ'],
        opponent_actions=[{'player': 'AI_1', 'action': 'raise', 'amount': 30}],
        active_opponents=1, call_amount=30,
        valid_actions=[
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 30},
            {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
        ]
    )
    
    freq_result = gto_core._calculate_action_frequencies_new(context)
    theoretical_freq = freq_result.action_frequencies
    
    print(f"\n理论vs实际对比:")
    for action in ['fold', 'call', 'raise']:
        actual = action_counts[action] / 100
        theoretical = theoretical_freq.get(action, 0)
        diff = abs(actual - theoretical)
        print(f"  {action}: 实际{actual:.1%} vs 理论{theoretical:.1%} (差异{diff:.1%})")

if __name__ == "__main__":
    test_frequency_consistency()
    test_multiple_simulations()