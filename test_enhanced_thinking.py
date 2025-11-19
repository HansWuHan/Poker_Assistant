#!/usr/bin/env python3
"""
测试优化后的AI思考输出格式
"""

import sys
sys.path.append('/Users/bytedance/hanbro/Poker_Assistant')

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_enhanced_thinking_output():
    """测试增强的AI思考输出格式"""
    print("🧪 测试优化后的AI思考输出格式")
    print("=" * 60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(
        difficulty="medium",
        show_thinking=True,
        gto_enabled=True
    )
    ai_player.uuid = "test_ai"
    
    # 测试场景1: 翻牌前优质手牌
    print("\n📋 场景1: 翻牌前AA")
    print("-" * 40)
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 30},
        {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
    ]
    
    hole_card = ['SA', 'HA']  # AA
    round_state = {
        'street': 'preflop',
        'dealer_btn': 0,
        'small_blind_pos': 1,
        'big_blind_pos': 2,
        'pot': {'main': {'amount': 30}},
        'community_card': [],
        'seats': [
            {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
        ],
        'action_histories': {
            'preflop': [
                {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
            ]
        }
    }
    
    action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
    print(f"\n最终决策: {action} ${amount}")
    
    # 测试场景2: 翻牌后中等牌力
    print("\n📋 场景2: 翻牌后顶对")
    print("-" * 40)
    
    valid_actions2 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 1000}}
    ]
    
    hole_card2 = ['HA', 'D9']  # A9
    round_state2 = {
        'street': 'flop',
        'dealer_btn': 0,
        'small_blind_pos': 1,
        'big_blind_pos': 2,
        'pot': {'main': {'amount': 150}},
        'community_card': ['S9', 'H7', 'C2'],  # 顶对9
        'seats': [
            {'uuid': 'player1', 'name': '你', 'stack': 950, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
            {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
        ],
        'action_histories': {
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                {'action': 'BET', 'amount': 50, 'uuid': 'player2'}
            ]
        }
    }
    
    action2, amount2 = ai_player.declare_action(valid_actions2, hole_card2, round_state2)
    print(f"\n最终决策: {action2} ${amount2}")
    
    # 测试场景3: 弱牌诈唬
    print("\n📋 场景3: 弱牌诈唬")
    print("-" * 40)
    
    hole_card3 = ['S2', 'H7']  # 27不同花
    round_state3 = {
        'street': 'flop',
        'dealer_btn': 0,
        'small_blind_pos': 1,
        'big_blind_pos': 2,
        'pot': {'main': {'amount': 120}},
        'community_card': ['HA', 'HK', 'DQ'],  # 高牌面
        'seats': [
            {'uuid': 'player1', 'name': '你', 'stack': 950, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
            {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
        ],
        'action_histories': {
            'flop': [
                {'action': 'BET', 'amount': 40, 'uuid': 'player1'}
            ]
        }
    }
    
    action3, amount3 = ai_player.declare_action(valid_actions2, hole_card3, round_state3)
    print(f"\n最终决策: {action3} ${amount3}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")

if __name__ == "__main__":
    test_enhanced_thinking_output()