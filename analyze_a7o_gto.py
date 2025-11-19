#!/usr/bin/env python3
"""
分析翻牌前A7不同花的GTO决策问题
"""

import sys
sys.path.append('/Users/bytedance/hanbro/Poker_Assistant')

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
from poker_assistant.gto_strategy.gto_core import GTOCore
from poker_assistant.gto_strategy.gto_advisor import GTOAdvisor

def analyze_a7o_decision():
    """分析A7不同花的决策问题"""
    print("🔍 分析A7不同花翻牌前GTO决策")
    print("=" * 60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(
        difficulty="medium",
        show_thinking=True,
        gto_enabled=True
    )
    ai_player.uuid = "test_ai"
    
    # 模拟场景：A7不同花，靠前位置
    hole_card = ['HA', 'C7']  # A7不同花
    
    # 测试不同位置的情况
    test_scenarios = [
        {
            'name': 'UTG位置 (最靠前)',
            'round_state': {
                'street': 'preflop',
                'dealer_btn': 5,
                'small_blind_pos': 0,
                'big_blind_pos': 1,
                'pot': {'main': {'amount': 15}},
                'community_card': [],
                'seats': [
                    {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player3', 'name': 'AI_3', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player4', 'name': 'AI_4', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player5', 'name': 'AI_5', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
                ],
                'action_histories': {
                    'preflop': [
                        {'action': 'RAISE', 'amount': 10, 'uuid': 'player1'}
                    ]
                }
            }
        },
        {
            'name': 'MP位置 (中间位置)',
            'round_state': {
                'street': 'preflop',
                'dealer_btn': 5,
                'small_blind_pos': 0,
                'big_blind_pos': 1,
                'pot': {'main': {'amount': 15}},
                'community_card': [],
                'seats': [
                    {'uuid': 'player1', 'name': '你', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player3', 'name': 'AI_3', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'test_ai', 'name': 'AI_Player', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player4', 'name': 'AI_4', 'stack': 1000, 'state': 'participating'},
                    {'uuid': 'player5', 'name': 'AI_5', 'stack': 1000, 'state': 'participating'},
                ],
                'action_histories': {
                    'preflop': [
                        {'action': 'RAISE', 'amount': 10, 'uuid': 'player1'}
                    ]
                }
            }
        }
    ]
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 10},
        {'action': 'raise', 'amount': {'min': 20, 'max': 1000}}
    ]
    
    for scenario in test_scenarios:
        print(f"\n📍 {scenario['name']}")
        print("-" * 40)
        
        # 获取位置信息
        position = ai_player._get_position_name(scenario['round_state'])
        print(f"检测到的位置: {position}")
        
        # 直接测试GTO核心
        gto_core = GTOCore()
        hand_string = gto_core._format_hand(hole_card)
        print(f"手牌格式: {hand_string}")
        
        # 检查是否在范围内
        is_in_open_range = gto_core._is_in_open_range(hand_string, position)
        is_in_defend_range = gto_core._is_in_defend_range(hand_string, position)
        range_strength = gto_core._calculate_range_strength(hand_string, position)
        
        print(f"在开池范围内: {is_in_open_range}")
        print(f"在防守范围内: {is_in_defend_range}")
        print(f"范围强度: {range_strength:.2f}")
        
        # 执行完整决策
        action, amount = ai_player.declare_action(valid_actions, hole_card, scenario['round_state'])
        print(f"\n最终决策: {action} ${amount}")
        
        print()

def analyze_gto_logic():
    """深入分析GTO逻辑"""
    print("\n🔬 深入分析GTO决策逻辑")
    print("=" * 60)
    
    gto_core = GTOCore()
    
    # 测试A7不同花的评估
    hole_card = ['HA', 'C7']
    hand_string = gto_core._format_hand(hole_card)
    print(f"手牌: {hole_card} -> 格式: {hand_string}")
    
    # 测试手牌强度评估
    hand_strength = gto_core._evaluate_hand_strength(hole_card, [])
    print(f"手牌强度: {hand_strength}")
    
    # 测试不同位置的情况
    positions = ['UTG', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB']
    
    print(f"\n位置分析:")
    for pos in positions:
        is_open = gto_core._is_in_open_range(hand_string, pos)
        is_defend = gto_core._is_in_defend_range(hand_string, pos)
        strength = gto_core._calculate_range_strength(hand_string, pos)
        print(f"{pos:4}: 开池{is_open:5} | 防守{is_defend:5} | 强度{strength:.2f}")

if __name__ == "__main__":
    analyze_a7o_decision()
    analyze_gto_logic()