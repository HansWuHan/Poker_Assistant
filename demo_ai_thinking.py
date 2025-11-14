#!/usr/bin/env python3
"""
完整演示增强AI的思考过程
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_enhanced_ai_thinking():
    """完整演示增强AI的思考过程"""
    print("🧠 增强AI思考过程完整演示")
    print("="*60)
    
    # 导入增强AI
    from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer as EnhancedAIOpponentPlayer
    
    # 详细测试场景 - 翻牌前口袋AA
    print("\n📋 场景1: 翻牌前口袋AA")
    print("-" * 60)
    
    ai_player = EnhancedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = 'ai_player'
    
    # 模拟翻牌前场景
    hole_card = ['SA', 'HA']  # 口袋AA
    round_state = {
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
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'},
                {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}  # 有人加注到30
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 30},
        {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
    ]
    
    print(f"AI手牌: {hole_card}")
    print(f"底池: ${round_state['pot']['main']['amount']}")
    print(f"需要跟注: ${valid_actions[1]['amount']}")
    print(f"加注范围: ${valid_actions[2]['amount']['min']} - ${valid_actions[2]['amount']['max']}")
    print()
    
    # 执行决策
    action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
    
    print(f"\n🎯 最终决策: {action} ${amount}")
    print("=" * 60)
    
    # 场景2: 翻牌后顶对弱踢脚
    print("\n📋 场景2: 翻牌后顶对弱踢脚")
    print("-" * 60)
    
    ai_player2 = EnhancedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player2.uuid = 'ai_player'
    
    hole_card2 = ['HA', 'D9']  # A9不同花
    round_state2 = {
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
                {'action': 'BET', 'amount': 50, 'uuid': 'player2'}  # 有人下注50
            ]
        }
    }
    
    valid_actions2 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 950}}
    ]
    
    print(f"AI手牌: {hole_card2}")
    print(f"公共牌: {round_state2['community_card']}")
    print(f"底池: ${round_state2['pot']['main']['amount']}")
    print(f"对手下注: $50")
    print(f"需要跟注: ${valid_actions2[1]['amount']}")
    print()
    
    # 执行决策
    action2, amount2 = ai_player2.declare_action(valid_actions2, hole_card2, round_state2)
    
    print(f"\n🎯 最终决策: {action2} ${amount2}")
    print("=" * 60)
    
    # 场景3: 翻牌后空气牌
    print("\n📋 场景3: 翻牌后空气牌")
    print("-" * 60)
    
    ai_player3 = EnhancedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player3.uuid = 'ai_player'
    
    hole_card3 = ['S2', 'H7']  # 27不同花 - 最差的起手牌之一
    round_state3 = {
        'street': 'flop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 120}},
        'community_card': ['HA', 'HK', 'DQ'],  # 高牌面，完全错过
        'seats': [
            {'uuid': 'player1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
            {'uuid': 'ai_player', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
        ],
        'action_histories': {
            'flop': [
                {'action': 'BET', 'amount': 40, 'uuid': 'player1'}  # 有人下注40
            ]
        }
    }
    
    valid_actions3 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 40},
        {'action': 'raise', 'amount': {'min': 80, 'max': 950}}
    ]
    
    print(f"AI手牌: {hole_card3}")
    print(f"公共牌: {round_state3['community_card']}")
    print(f"底池: ${round_state3['pot']['main']['amount']}")
    print(f"对手下注: $40")
    print(f"需要跟注: ${valid_actions3[1]['amount']}")
    print()
    
    # 执行决策
    action3, amount3 = ai_player3.declare_action(valid_actions3, hole_card3, round_state3)
    
    print(f"\n🎯 最终决策: {action3} ${amount3}")
    print("=" * 60)
    
    print("\n✅ 演示完成!")
    print("\n🎯 增强AI新功能:")
    print("✨ 详细的思考过程分析")
    print("✨ 手牌强度精确评估")
    print("✨ 牌面结构深度分析")
    print("✨ 位置因素智能考虑")
    print("✨ 对手行为全面分析")
    print("✨ 底池赔率精确计算")
    print("✨ 对手范围科学估算")
    print("✨ 决策理由清晰展示")

if __name__ == "__main__":
    demo_enhanced_ai_thinking()