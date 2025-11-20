#!/usr/bin/env python3
"""
检查手牌格式化问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.gto_strategy.gto_core import GTOCore

def test_hand_formatting():
    """测试手牌格式化"""
    print("🔍 检查手牌格式化问题")
    print("="*60)
    
    gto_core = GTOCore()
    
    # 测试各种手牌格式
    test_hands = [
        ['10D', '8S'],    # 10♦ 8♠ (你观察到的)
        ['TD', '8S'],     # 正确的T♦ 8♠ 格式
        ['2C', 'KD'],     # 2♣ K♦ (你观察到的)
        ['C2', 'DK'],     # 系统内部的格式
        ['4S', 'AD'],     # 4♠ A♦ (你观察到的)
        ['S4', 'DA']      # 系统内部的格式
    ]
    
    for hole_cards in test_hands:
        print(f"\n手牌输入: {hole_cards}")
        
        try:
            # 测试格式化
            hand_string = gto_core._format_hand(hole_cards)
            print(f"格式化结果: {hand_string}")
            
            # 测试强度评估
            strength = gto_core._evaluate_preflop_hand_strength(hole_cards)
            print(f"强度评估: {strength:.3f}")
            
            # 创建情境测试完整逻辑
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
            
            print(f"频率分布:")
            for action, freq in frequencies.items():
                print(f"  {action}: {freq*100:.1f}%")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def check_format_hand_method():
    """检查_format_hand方法"""
    print(f"\n🔍 检查_format_hand方法实现")
    print("-" * 40)
    
    gto_core = GTOCore()
    
    # 查找_format_hand方法
    try:
        import inspect
        source = inspect.getsource(gto_core._format_hand)
        print("_format_hand方法源码:")
        print(source)
    except Exception as e:
        print(f"无法获取源码: {e}")
        
    # 测试不同的牌面格式
    test_cases = [
        ['TD', '8S'],   # 标准格式
        ['10D', '8S'],  # 10的完整写法
        ['T', '8'],     # 只有rank
        ['D', 'S']      # 只有suit
    ]
    
    print(f"\n边界测试:")
    for case in test_cases:
        try:
            result = gto_core._format_hand(case)
            print(f"  {case} -> {result}")
        except Exception as e:
            print(f"  {case} -> 错误: {e}")

if __name__ == "__main__":
    test_hand_formatting()
    check_format_hand_method()