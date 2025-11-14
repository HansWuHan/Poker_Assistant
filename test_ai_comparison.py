#!/usr/bin/env python3
"""
测试改进的AI策略
对比原版和改进版的AI行为
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.engine.ai_opponent import AIOpponentPlayer
from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_ai_strategy_comparison():
    """测试AI策略对比"""
    print("🎰 AI策略对比测试")
    print("="*60)
    
    # 模拟测试场景
    test_scenarios = [
        {
            "name": "翻牌前 - 中等牌力 (KQo)",
            "hole_card": ['SQ', 'HK'],  # 不同花KQo
            "round_state": {
                'street': 'preflop',
                'dealer_btn': 0,
                'pot': {'main': {'amount': 30}},
                'community_card': [],
                'seats': [
                    {'uuid': 'player1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player3', 'name': 'AI_3', 'stack': 1000, 'state': 'participating'},
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
                'pot': {'main': {'amount': 100}},
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
                'pot': {'main': {'amount': 80}},
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
    
    difficulties = ['easy', 'medium', 'hard']
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}")
        print("-" * 50)
        
        for difficulty in difficulties:
            print(f"\n🎯 {difficulty.upper()} 难度:")
            
            # 测试原版AI
            original_ai = AIOpponentPlayer(difficulty)
            original_ai.uuid = 'ai_player'
            original_action, original_amount = original_ai.declare_action(
                scenario["valid_actions"],
                scenario["hole_card"],
                scenario["round_state"]
            )
            
            # 测试改进版AI
            improved_ai = ImprovedAIOpponentPlayer(difficulty)
            improved_ai.uuid = 'ai_player'
            improved_action, improved_amount = improved_ai.declare_action(
                scenario["valid_actions"],
                scenario["hole_card"],
                scenario["round_state"]
            )
            
            print(f"原版AI: {original_action} ${original_amount}")
            print(f"改进AI: {improved_action} ${improved_amount}")
            
            # 分析差异
            if original_action != improved_action:
                print(f"✅ 行为改变: {original_action} → {improved_action}")
            elif original_amount != improved_amount:
                print(f"✅ 金额改变: ${original_amount} → ${improved_amount}")
            else:
                print("➡️  行为相同")
    
    print(f"\n✅ 测试完成!")
    print("\n📊 改进总结:")
    print("- 更合理的弃牌逻辑")
    print("- 基于真实牌力的决策")
    print("- 考虑位置和对手倾向")
    print("- 更精确的下注尺度控制")

if __name__ == "__main__":
    test_ai_strategy_comparison()