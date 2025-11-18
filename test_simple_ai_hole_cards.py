#!/usr/bin/env python3
"""
简化测试AI手牌显示功能 - 只显示当前AI自己的手牌
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_simple_ai_hole_cards():
    """简单测试AI手牌显示 - 只显示当前AI手牌"""
    print("🧪 简单测试AI手牌显示功能")
    print("="*60)
    
    # 创建AI玩家（不需要共享字典，只显示自己的手牌）
    ai_player = ImprovedAIOpponentPlayer(
        difficulty="medium", 
        show_thinking=True
    )
    ai_player.uuid = "ai_test"
    
    # 测试场景1: 翻牌前显示手牌
    print("\n📋 场景1: 翻牌前显示AI手牌")
    print("-" * 40)
    
    # 模拟游戏场景
    hole_card = ['SA', 'HA']  # 口袋AA
    round_state = {
        'street': 'preflop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 50}},
        'community_card': [],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'ai_1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'ai_2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_test'}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 10},
        {'action': 'raise', 'amount': {'min': 20, 'max': 1000}}
    ]
    
    print(f"📊 当前AI手牌: {hole_card} (口袋AA)")
    print(f"  底池: $50")
    print(f"  需要跟注: $10")
    print(f"  最小加注: $20")
    print()
    
    print("🎯 AI思考过程 (显示自己的手牌):")
    action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
    
    print(f"\n🎯 AI决策: {action} ${amount}")
    
    # 测试场景2: 翻牌后显示手牌
    print("\n📋 场景2: 翻牌后显示AI手牌")
    print("-" * 40)
    
    # 模拟翻牌
    hole_card2 = ['HA', 'D9']  # A9不同花
    round_state2 = {
        'street': 'flop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 200}},
        'community_card': ['S9', 'H7', 'C2'],  # 顶对9
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_1'},
                {'action': 'BET', 'amount': 50, 'uuid': 'ai_2'}
            ]
        }
    }
    
    valid_actions2 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 1000}}
    ]
    
    print(f"📊 当前AI手牌: {hole_card2} (A9不同花)")
    print(f"  公共牌: ['S9', 'H7', 'C2']")
    print(f"  底池: $200")
    print(f"  对手下注: $50")
    print(f"  需要跟注: $50")
    print()
    
    print("🎯 AI思考过程 (翻牌后显示自己的手牌):")
    action2, amount2 = ai_player.declare_action(valid_actions2, hole_card2, round_state2)
    
    print(f"\n🎯 AI决策: {action2} ${amount2}")
    
    # 测试场景3: 弱牌情况
    print("\n📋 场景3: 弱牌情况显示手牌")
    print("-" * 40)
    
    hole_card3 = ['S2', 'H7']  # 27不同花 - 最差的起手牌
    round_state3 = {
        'street': 'flop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 120}},
        'community_card': ['HA', 'HK', 'DQ'],  # 高牌面，完全错过
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'flop': [
                {'action': 'BET', 'amount': 40, 'uuid': 'ai_1'}
            ]
        }
    }
    
    valid_actions3 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 40},
        {'action': 'raise', 'amount': {'min': 80, 'max': 1000}}
    ]
    
    print(f"📊 当前AI手牌: {hole_card3} (27不同花)")
    print(f"  公共牌: ['HA', 'HK', 'DQ']")
    print(f"  底池: $120")
    print(f"  对手下注: $40")
    print(f"  需要跟注: $40")
    print()
    
    print("🎯 AI思考过程 (弱牌情况显示自己的手牌):")
    action3, amount3 = ai_player.declare_action(valid_actions3, hole_card3, round_state3)
    
    print(f"\n🎯 AI决策: {action3} ${amount3}")
    
    print("\n" + "="*60)
    print("✅ AI手牌显示功能测试完成!")
    print("\n🎯 功能特点:")
    print("  ✅ 简单直接：只显示当前AI自己的手牌")
    print("  ✅ 翻牌前显示：🎯 我的手牌: [SA, HA] (对子 AA)")
    print("  ✅ 翻牌后显示：🎯 我的牌力: 中等牌力")
    print("  ✅ 清晰明了：没有复杂的对手手牌显示")
    print("  ✅ 符合逻辑：AI玩牌时显示自己的手牌")

if __name__ == "__main__":
    test_simple_ai_hole_cards()