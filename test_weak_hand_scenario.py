#!/usr/bin/env python3
"""
检查你观察到的具体场景：弱牌面对加注的情况
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.gto_strategy.gto_core import GTOCore
from poker_assistant.gto_strategy.gto_core import GTOSituation

def test_weak_hand_scenario():
    """测试弱牌面对加注的场景"""
    print("🔍 检查弱牌面对加注的GTO决策")
    print("="*60)
    
    gto_core = GTOCore()
    
    # 模拟你观察到的场景：2♣ K♦ 和 4♠ A♦
    test_hands = [
        (['C2', 'DK'], "2♣ K♦"),  # AI_4的手牌
        (['S4', 'DA'], "4♠ A♦")   # AI_5的手牌
    ]
    
    for hole_cards, hand_desc in test_hands:
        print(f"\n📋 测试手牌: {hand_desc}")
        print("-" * 40)
        
        situation = GTOSituation(
            street='preflop',
            position='BTN',  # 靠后位置
            stack_size=100,
            pot_size=15,  # 小底池
            community_cards=[],
            hole_cards=hole_cards,
            opponent_actions=[
                {'player': 'AI_1', 'action': 'raise', 'amount': 10}  # 加注到10
            ],
            active_opponents=1
        )
        
        # 获取GTO决策
        gto_action = gto_core.calculate_gto_action(situation)
        
        print(f"手牌: {hand_desc}")
        print(f"位置: 按钮位")
        print(f"底池: \)15")
        print(f"需要跟注: \(10")
        print(f"最终决策: {gto_action.action}")
        print(f"决策理由: {gto_action.reasoning}")
        
        # 获取详细频率
        from poker_assistant.gto_strategy.types import GTOContext
        context = GTOContext(
            street='preflop', position='BTN', stack_size=100, pot_size=15,
            community_cards=[], hole_cards=hole_cards,
            opponent_actions=[{'player': 'AI_1', 'action': 'raise', 'amount': 10}],
            active_opponents=1, call_amount=10,
            valid_actions=[
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 10},
                {'action': 'raise', 'amount': {'min': 20, 'max': 1000}}
            ]
        )
        
        freq_result = gto_core._calculate_action_frequencies_new(context)
        frequencies = freq_result.action_frequencies
        
        print(f"\n📊 频率分布:")
        for action, freq in frequencies.items():
            percentage = freq * 100
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {action}: {percentage:.1f}% [{bar}]")
        
        # 检查是否在防守范围内
        position_range = gto_core.preflop_ranges.get('BTN', gto_core.preflop_ranges['BB'])
        defend_range = position_range.get('defend', position_range.get('call_3bet', []))
        
        # 格式化手牌
        hand_string = gto_core._format_hand(hole_cards)
        in_defend_range = hand_string in defend_range
        
        print(f"\n🔍 分析:")
        print(f"  手牌格式: {hand_string}")
        print(f"  在防守范围内: {in_defend_range}")
        print(f"  选择fold的概率: {frequencies.get('fold', 0)*100:.1f}%")
        
        if frequencies.get('fold', 0) > 0.6:  # 如果fold概率>60%
            print(f"  ⚠️  高fold概率合理：手牌较弱且面对加注")
        elif frequencies.get('fold', 0) < 0.3:  # 如果fold概率<30%
            print(f"  ✅ 低fold概率合理：手牌较强或位置有利")
        else:
            print(f"  🤔 中等fold概率：标准GTO混合策略")

def analyze_hand_strength():
    """分析具体手牌强度"""
    print(f"\n🔍 手牌强度分析")
    print("="*60)
    
    gto_core = GTOCore()
    
    # 分析具体手牌
    hands = [
        (['C2', 'DK'], "2♣ K♦"),  # AI_4
        (['S4', 'DA'], "4♠ A♦"),  # AI_5
        (['SK', 'SQ'], "K♠ Q♠"),  # 对比：KQs同花连牌
        (['SA', 'HA'], "A♠ A♥")   # 对比：AA对子
    ]
    
    for hole_cards, hand_desc in hands:
        hand_strength = gto_core._evaluate_hand_strength(hole_cards, [])
        hand_string = gto_core._format_hand(hole_cards)
        
        print(f"\n{hand_desc}:")
        print(f"  格式化: {hand_string}")
        print(f"  强度评估: {hand_strength:.3f}")
        
        # 强度解释
        if hand_strength >= 0.8:
            print(f"  强度等级: 超强牌")
        elif hand_strength >= 0.6:
            print(f"  强度等级: 强牌")
        elif hand_strength >= 0.4:
            print(f"  强度等级: 中等牌")
        elif hand_strength >= 0.25:
            print(f"  强度等级: 边缘牌")
        else:
            print(f"  强度等级: 弱牌")

if __name__ == "__main__":
    test_weak_hand_scenario()
    analyze_hand_strength()