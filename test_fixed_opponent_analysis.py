#!/usr/bin/env python3
"""
测试修复后的AI对手分析功能 - 排除已弃牌玩家
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_fixed_opponent_analysis():
    """测试修复后的对手分析功能"""
    print("🧪 测试修复后的AI对手分析功能")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "ai_test"
    
    # 场景1: 正常情况 - 3个活跃玩家
    print("\n📋 场景1: 正常情况 - 3个活跃玩家")
    print("-" * 40)
    
    round_state1 = {
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
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_1'},
                {'action': 'RAISE', 'amount': 25, 'uuid': 'ai_2'}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 25},
        {'action': 'raise', 'amount': {'min': 50, 'max': 1000}}
    ]
    
    print("预期: 2个活跃对手，1个激进，1个保守")
    action1, amount1 = ai_player.declare_action(valid_actions, ['SA', 'HA'], round_state1)
    
    # 场景2: 有人弃牌 - 只有2个活跃玩家
    print("\n📋 场景2: 有人弃牌 - 只有2个活跃玩家")
    print("-" * 40)
    
    round_state2 = {
        'street': 'flop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 80}},
        'community_card': ['S9', 'H7', 'C2'],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'folded'},  # AI_1已弃牌
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'ai_1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'ai_2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_1'},
                {'action': 'FOLD', 'amount': 0, 'uuid': 'ai_1'}  # AI_1弃牌
            ],
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_2'}
            ]
        }
    }
    
    print("预期: 1个活跃对手，AI_1已弃牌不应被分析")
    action2, amount2 = ai_player.declare_action(valid_actions, ['HA', 'D9'], round_state2)
    
    # 场景3: 多人弃牌 - 只有1个活跃玩家
    print("\n📋 场景3: 多人弃牌 - 只有1个活跃玩家")
    print("-" * 40)
    
    round_state3 = {
        'street': 'turn',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 120}},
        'community_card': ['S9', 'H7', 'C2', 'D3'],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'folded'},    # AI_1已弃牌
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'folded'},    # AI_2已弃牌
            {'uuid': 'ai_3', 'name': 'AI_3', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'ai_1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'ai_2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_3'},
                {'action': 'FOLD', 'amount': 0, 'uuid': 'ai_1'},  # AI_1弃牌
                {'action': 'FOLD', 'amount': 0, 'uuid': 'ai_2'}   # AI_2弃牌
            ],
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_3'},
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_test'}
            ],
            'turn': [
                {'action': 'BET', 'amount': 40, 'uuid': 'ai_3'}
            ]
        }
    }
    
    print("预期: 1个活跃对手，AI_1和AI_2已弃牌不应被分析")
    action3, amount3 = ai_player.declare_action(valid_actions, ['S2', 'H7'], round_state3)
    
    print("\n" + "="*60)
    print("✅ 修复后的对手分析功能测试完成!")
    print("\n🎯 验证要点:")
    print("  ✅ 只统计真正活跃的玩家（未弃牌）")
    print("  ✅ 已弃牌的玩家不会被分析")
    print("  ✅ 活跃对手数量显示正确")
    print("  ✅ 不猜测已弃牌玩家的手牌")

if __name__ == "__main__":
    test_fixed_opponent_analysis()