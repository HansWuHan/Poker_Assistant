#!/usr/bin/env python3
"""
测试盲注排除功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
import time

def test_blind_exclusion():
    """测试盲注排除功能"""
    print("🧪 测试盲注排除功能")
    print("=" * 60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "test_ai"
    
    # 测试场景1: 翻牌前有小盲注行为
    print("📋 测试场景1: 翻牌前（排除小盲注）")
    print("-" * 40)
    
    hole_card = ['SA', 'HA']  # 口袋AA
    round_state1 = {
        'street': 'preflop',
        'dealer_btn': 0,
        'seats': [
            {'uuid': 'test_ai', 'name': 'AI玩家', 'stack': 1000},
            {'uuid': 'p2', 'name': '玩家2', 'stack': 1000},  # 小盲
            {'uuid': 'p3', 'name': '玩家3', 'stack': 1000}   # 大盲
        ],
        'pot': {'main': {'amount': 30}},  # 小盲5 + 大盲10 + 加注15
        'community_card': [],
        'action_histories': {
            'preflop': [
                {'uuid': 'p2', 'action': 'call', 'amount': 5},   # 小盲注 - 应该被排除
                {'uuid': 'p3', 'action': 'raise', 'amount': 10},  # 大盲注 - 应该被排除  
                {'uuid': 'p2', 'action': 'call', 'amount': 5},   # 补盲注 - 应该被排除
                {'uuid': 'p3', 'action': 'raise', 'amount': 25}, # 真实加注 - 不应该被排除
                {'uuid': 'test_ai', 'action': 'call', 'amount': 25}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 25},
        {'action': 'raise', 'amount': {'min': 50, 'max': 200}}
    ]
    
    print("翻牌前行动历史:")
    for action in round_state1['action_histories']['preflop']:
        print(f"  {action['name'] if 'name' in action else action['uuid']}: {action['action']} ${action['amount']}")
    print()
    
    # 调用AI决策
    action1, amount1 = ai_player.declare_action(valid_actions, hole_card, round_state1)
    
    print(f"✅ AI决策: {action1} ${amount1}")
    print()
    
    # 测试场景2: 翻牌后有真实下注
    print("📋 测试场景2: 翻牌后（真实下注）")
    print("-" * 40)
    
    round_state2 = {
        'street': 'flop',
        'dealer_btn': 0,
        'seats': [
            {'uuid': 'test_ai', 'name': 'AI玩家', 'stack': 1000},
            {'uuid': 'p2', 'name': '玩家2', 'stack': 1000},
            {'uuid': 'p3', 'name': '玩家3', 'stack': 1000}
        ],
        'pot': {'main': {'amount': 100}},
        'community_card': ['S7', 'H2', 'D9'],
        'action_histories': {
            'preflop': [
                {'uuid': 'p2', 'action': 'call', 'amount': 5},   # 小盲注
                {'uuid': 'p3', 'action': 'raise', 'amount': 10}, # 大盲注
                {'uuid': 'p2', 'action': 'call', 'amount': 5},   # 补盲注
                {'uuid': 'test_ai', 'action': 'call', 'amount': 10}
            ],
            'flop': [
                {'uuid': 'p2', 'action': 'check', 'amount': 0},
                {'uuid': 'p3', 'action': 'raise', 'amount': 50},  # 真实下注
                {'uuid': 'test_ai', 'action': 'call', 'amount': 50}
            ]
        }
    }
    
    valid_actions2 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 300}}
    ]
    
    print("翻牌后行动历史:")
    for action in round_state2['action_histories']['flop']:
        print(f"  {action['name'] if 'name' in action else action['uuid']}: {action['action']} ${action['amount']}")
    print()
    
    # 调用AI决策
    action2, amount2 = ai_player.declare_action(valid_actions2, hole_card, round_state2)
    
    print(f"✅ AI决策: {action2} ${amount2}")
    print()
    
    print("=" * 60)
    print("🎯 测试重点:")
    print("  ✅ 翻牌前的小盲注(≤20)应该被排除在分析之外")
    print("  ✅ 翻牌后的真实下注应该被正常分析")
    print("  ✅ AI应该能正确区分盲注和真实下注")
    print("  ✅ 对手分析应该基于有意义的下注行为")
    print()
    print("🎮 测试完成！")

if __name__ == "__main__":
    test_blind_exclusion()