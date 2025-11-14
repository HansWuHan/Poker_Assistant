#!/usr/bin/env python3
"""
测试思考过程显示开关功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_thinking_display_toggle():
    """测试思考过程显示开关"""
    print("🧠 测试AI思考过程显示开关")
    print("="*60)
    
    from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer as EnhancedAIOpponentPlayer
    
    # 测试场景
    hole_card = ['HA', 'D9']  # A9不同花
    round_state = {
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
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 950}}
    ]
    
    print("\n📋 测试1: 显示思考过程 (show_thinking=True)")
    print("-" * 50)
    
    ai_with_thinking = EnhancedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_with_thinking.uuid = 'ai_player'
    
    print("AI正在思考...")
    action1, amount1 = ai_with_thinking.declare_action(valid_actions, hole_card, round_state)
    print(f"最终决策: {action1} ${amount1}")
    
    print("\n📋 测试2: 不显示思考过程 (show_thinking=False)")
    print("-" * 50)
    
    ai_without_thinking = EnhancedAIOpponentPlayer(difficulty="medium", show_thinking=False)
    ai_without_thinking.uuid = 'ai_player'
    
    print("AI正在思考... (静默模式)")
    action2, amount2 = ai_without_thinking.declare_action(valid_actions, hole_card, round_state)
    print(f"最终决策: {action2} ${amount2}")
    
    print("\n✅ 测试完成!")
    print("\n🎯 功能说明:")
    print("- show_thinking=True: 显示详细的思考过程")
    print("- show_thinking=False: 只显示最终决策")
    print("- 可以通过配置控制是否显示AI思考")

if __name__ == "__main__":
    test_thinking_display_toggle()