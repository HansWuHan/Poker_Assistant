#!/usr/bin/env python3
"""
测试增强AI的思考过程显示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_ai_thinking():
    """测试增强AI的思考过程"""
    print("🧠 测试增强AI思考过程显示")
    print("="*60)
    
    # 导入增强AI
    from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer as EnhancedAIOpponentPlayer
    
    # 创建测试场景
    test_scenarios = [
        {
            "name": "翻牌前 - 口袋对子AA",
            "hole_card": ['SA', 'HA'],  # 不同花AA
            "round_state": {
                'street': 'preflop',
                'dealer_btn': 0,
                'pot': {'main': {'amount': 30}},
                'community_card': [],
                'seats': [
                    {'uuid': 'player1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'ai_player', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
                ],
                'action_histories': {
                    'preflop': [
                        {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}
                    ]
                }
            },
            "valid_actions": [
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 30},
                {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
            ]
        },
        {
            "name": "翻牌后 - 顶对弱踢脚",
            "hole_card": ['HA', 'D9'],  # 不同花A9
            "round_state": {
                'street': 'flop',
                'dealer_btn': 0,
                'pot': {'main': {'amount': 150}},
                'community_card': ['S9', 'H7', 'C2'],  # 顶对9
                'seats': [
                    {'uuid': 'player1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
                    {'uuid': 'ai_player', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
                ],
                'action_histories': {
                    'flop': [
                        {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                        {'action': 'BET', 'amount': 50, 'uuid': 'player2'}
                    ]
                }
            },
            "valid_actions": [
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 50},
                {'action': 'raise', 'amount': {'min': 100, 'max': 950}}
            ]
        },
        {
            "name": "翻牌后 - 空气牌",
            "hole_card": ['S2', 'H7'],  # 不同花27
            "round_state": {
                'street': 'flop',
                'dealer_btn': 0,
                'pot': {'main': {'amount': 120}},
                'community_card': ['HA', 'HK', 'DQ'],  # 高牌面，无连接
                'seats': [
                    {'uuid': 'player1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
                    {'uuid': 'ai_player', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
                ],
                'action_histories': {
                    'flop': [
                        {'action': 'BET', 'amount': 40, 'uuid': 'player1'}
                    ]
                }
            },
            "valid_actions": [
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 40},
                {'action': 'raise', 'amount': {'min': 80, 'max': 950}}
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}")
        print("-" * 60)
        
        # 创建增强AI
        ai_player = EnhancedAIOpponentPlayer(difficulty="medium", show_thinking=True)
        ai_player.uuid = 'ai_player'
        
        print(f"手牌: {scenario['hole_card']}")
        if scenario['round_state']['community_card']:
            print(f"公共牌: {scenario['round_state']['community_card']}")
        print(f"底池: ${scenario['round_state']['pot']['main']['amount']}")
        print(f"需要跟注: ${scenario['valid_actions'][1]['amount']}")
        print()
        
        # 执行决策
        action, amount = ai_player.declare_action(
            scenario["valid_actions"],
            scenario["hole_card"],
            scenario["round_state"]
        )
        
        print(f"\n最终行动: {action} ${amount}")
        print("=" * 60)
        print()
    
    print("✅ 测试完成!")
    print("\n🎯 新功能:")
    print("- 详细的AI思考过程显示")
    print("- 手牌强度分析")
    print("- 牌面结构评估")
    print("- 位置因素考虑")
    print("- 对手行为分析")
    print("- 底池赔率计算")
    print("- 对手范围估算")

if __name__ == "__main__":
    test_enhanced_ai_thinking()