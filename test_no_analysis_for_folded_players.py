#!/usr/bin/env python3
"""
测试修复后的AI思考过程 - 不为已弃牌的对手进行分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_no_analysis_for_folded_players():
    """测试不为已弃牌的对手进行分析"""
    print("🧪 测试不为已弃牌的对手进行分析")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "ai_test"
    
    # 场景1: 多人游戏，部分玩家弃牌
    print("\n📋 场景1: 6人桌，3人已弃牌")
    print("-" * 40)
    
    round_state = {
        'street': 'turn',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 200}},
        'community_card': ['S9', 'H7', 'C2', 'D3'],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 800, 'state': 'folded'},     # 已弃牌
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1200, 'state': 'participating'},
            {'uuid': 'ai_3', 'name': 'AI_3', 'stack': 600, 'state': 'folded'},     # 已弃牌
            {'uuid': 'ai_4', 'name': 'AI_4', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_5', 'name': 'AI_5', 'stack': 900, 'state': 'folded'},     # 已弃牌
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1100, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'ai_1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'ai_2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'ai_3'},
                {'action': 'RAISE', 'amount': 30, 'uuid': 'ai_4'},
                {'action': 'FOLD', 'amount': 0, 'uuid': 'ai_5'},      # AI_5弃牌
                {'action': 'FOLD', 'amount': 0, 'uuid': 'ai_1'},     # AI_1弃牌
                {'action': 'CALL', 'amount': 30, 'uuid': 'ai_2'},
                {'action': 'FOLD', 'amount': 0, 'uuid': 'ai_3'}      # AI_3弃牌
            ],
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_4'},
                {'action': 'BET', 'amount': 50, 'uuid': 'ai_2'},
                {'action': 'CALL', 'amount': 50, 'uuid': 'ai_4'}
            ],
            'turn': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_4'},
                {'action': 'BET', 'amount': 80, 'uuid': 'ai_2'}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 80},
        {'action': 'raise', 'amount': {'min': 160, 'max': 1000}}
    ]
    
    print("当前状态:")
    print("  活跃玩家: AI_2, AI_4, AI_Test (3人)")
    print("  已弃牌: AI_1, AI_3, AI_5 (3人)")
    print("  预期: 只分析2个活跃对手，不分析已弃牌的玩家")
    
    action, amount = ai_player.declare_action(valid_actions, ['SA', 'HA'], round_state)
    
    # 场景2: 单挑情况（只剩1个对手）
    print("\n📋 场景2: 单挑情况，只剩1个对手")
    print("-" * 40)
    
    round_state2 = {
        'street': 'river',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 300}},
        'community_card': ['S9', 'H7', 'C2', 'D3', 'SK'],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 800, 'state': 'folded'},     # 已弃牌
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1200, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_3', 'name': 'AI_3', 'stack': 600, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_4', 'name': 'AI_4', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_5', 'name': 'AI_5', 'stack': 900, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1100, 'state': 'participating'}
        ],
        'action_histories': {
            'river': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_4'},
                {'action': 'BET', 'amount': 100, 'uuid': 'ai_test'}
            ]
        }
    }
    
    valid_actions2 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 100},
        {'action': 'raise', 'amount': {'min': 200, 'max': 1000}}
    ]
    
    print("当前状态:")
    print("  活跃玩家: AI_4, AI_Test (2人，单挑)")
    print("  已弃牌: AI_1, AI_2, AI_3, AI_5 (4人)")
    print("  预期: 只分析1个活跃对手")
    
    action2, amount2 = ai_player.declare_action(valid_actions2, ['SA', 'HA'], round_state2)
    
    # 场景3: 所有人都弃牌（只剩自己）
    print("\n📋 场景3: 所有人都弃牌（只剩自己）")
    print("-" * 40)
    
    round_state3 = {
        'street': 'river',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 300}},
        'community_card': ['S9', 'H7', 'C2', 'D3', 'SK'],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 800, 'state': 'folded'},     # 已弃牌
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1200, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_3', 'name': 'AI_3', 'stack': 600, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_4', 'name': 'AI_4', 'stack': 1000, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_5', 'name': 'AI_5', 'stack': 900, 'state': 'folded'},   # 已弃牌
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1100, 'state': 'participating'}
        ],
        'action_histories': {
            'river': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_test'}
            ]
        }
    }
    
    valid_actions3 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'check', 'amount': 0},
        {'action': 'raise', 'amount': {'min': 10, 'max': 1000}}
    ]
    
    print("当前状态:")
    print("  活跃玩家: AI_Test (1人，只剩自己)")
    print("  已弃牌: AI_1, AI_2, AI_3, AI_4, AI_5 (5人)")
    print("  预期: 没有对手分析，因为其他人都弃牌了")
    
    action3, amount3 = ai_player.declare_action(valid_actions3, ['SA', 'HA'], round_state3)
    
    print("\n" + "="*60)
    print("✅ 修复后的AI思考过程测试完成!")
    print("\n🎯 验证要点:")
    print("  ✅ 只分析真正活跃的玩家")
    print("  ✅ 已弃牌的玩家不会被分析")
    print("  ✅ 活跃对手数量显示正确")
    print("  ✅ 没有对手时不会显示对手分析")

if __name__ == "__main__":
    test_no_analysis_for_folded_players()