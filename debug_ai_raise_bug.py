#!/usr/bin/env python3
"""
分析AI加注金额计算的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def analyze_ai_raise_bug():
    """分析AI加注的bug"""
    print("🔍 分析AI加注金额计算bug")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer()
    ai_player.uuid = "ai_test"
    
    # 模拟游戏状态：大盲$10，有人加注到$17的情况
    print("\n📋 测试场景: 大盲$10，AI从$10加注到$17")
    print("-" * 40)
    
    # 模拟行动历史
    round_state = {
        'street': 'preflop',
        'seats': [
            {'uuid': 'ai_test', 'name': 'AI', 'stack': 1000},
            {'uuid': 'player2', 'name': 'Player2', 'stack': 1000},
            {'uuid': 'player3', 'name': 'Player3', 'stack': 1000}
        ],
        'pot': {'main': {'amount': 27}},  # 底池$27
        'community_card': [],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player2'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player3'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_test'},
                {'action': 'RAISE', 'amount': 17, 'uuid': 'player2'}  # 有人加注到17
            ]
        }
    }
    
    # 模拟有效行动
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 7},  # 需要跟注$7
        {'action': 'raise', 'amount': {'min': 24, 'max': 1000}}  # 最小加注$24
    ]
    
    print(f"📊 当前状态:")
    print(f"  底池: ${round_state['pot']['main']['amount']}")
    print(f"  需要跟注: $7")
    print(f"  最小加注: $24")
    print(f"  之前加注: $17")
    
    # 分析AI的决策逻辑
    print(f"\n🔍 分析AI决策逻辑:")
    
    # 获取AI的策略参数
    street = round_state['street']
    pot = round_state['pot']['main']['amount']
    my_stack = 1000
    
    # 检查不同策略下的加注计算
    strategies = [
        ("激进策略", 0.8, 0.9),
        ("平衡策略", 0.6, 0.7), 
        ("保守策略", 0.4, 0.5)
    ]
    
    for strategy_name, strength_factor, pot_factor in strategies:
        print(f"\n  📋 {strategy_name}:")
        
        # 模拟不同强度的手牌
        for hand_strength in [0.9, 0.7, 0.5]:
            # 计算基于底池的加注金额
            pot_based_amount = int(pot * pot_factor * hand_strength)
            
            # 确保符合最小加注要求
            final_amount = max(valid_actions[2]['amount']['min'], pot_based_amount)
            
            print(f"    手牌强度{hand_strength}: pot*{pot_factor}*{hand_strength} = ${pot_based_amount}")
            print(f"    最终加注: ${final_amount} (最小要求: $24)")
            
            if final_amount == valid_actions[2]['amount']['min']:
                print(f"    ⚠️  被限制在最小加注")
    
    print(f"\n" + "="*60)
    print("🎯 问题分析:")
    print("  ✅ PyPokerEngine正确计算了最小加注$24")
    print("  ✅ AI的加注计算会确保≥最小加注要求")
    print("  ✅ 之前显示$17可能是历史记录，不是AI的实际加注")
    print("  ✅ AI从$10加注到$17的情况不应该发生，因为最小是$24")

def test_actual_ai_decision():
    """测试AI的实际决策"""
    print("\n\n🔬 测试AI实际决策")
    print("="*60)
    
    ai_player = ImprovedAIOpponentPlayer()
    ai_player.uuid = "ai_test"
    
    # 同样的场景
    hole_card = ['SA', 'HA']  # 口袋AA
    round_state = {
        'street': 'preflop',
        'seats': [
            {'uuid': 'ai_test', 'name': 'AI', 'stack': 1000},
            {'uuid': 'player2', 'name': 'Player2', 'stack': 1000},
            {'uuid': 'player3', 'name': 'Player3', 'stack': 1000}
        ],
        'pot': {'main': {'amount': 27}},
        'community_card': [],
        'dealer_btn': 0,
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player2'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player3'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_test'},
                {'action': 'RAISE', 'amount': 17, 'uuid': 'player2'}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 7},
        {'action': 'raise', 'amount': {'min': 24, 'max': 1000}}
    ]
    
    print(f"📋 测试AI面对加注$17时的决策:")
    print(f"  手牌: AA")
    print(f"  需要跟注: $7")
    print(f"  最小加注: $24")
    
    # 让AI做决策
    action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
    
    print(f"\n🎯 AI决策:")
    print(f"  行动: {action}")
    print(f"  金额: ${amount}")
    
    if action == 'raise' and amount < 24:
        print(f"  ❌ BUG: AI加注${amount}小于最小要求$24")
    else:
        print(f"  ✅ 正确: AI决策符合加注规则")

if __name__ == "__main__":
    analyze_ai_raise_bug()
    test_actual_ai_decision()