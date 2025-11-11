#!/usr/bin/env python3
"""
测试新的动作log显示功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.cli.game_renderer import GameRenderer
from poker_assistant.engine.game_state import GameState

def test_enhanced_action_log():
    """测试增强的动作log显示"""
    print("🎰 测试增强动作log显示")
    print("="*60)
    
    renderer = GameRenderer()
    
    # 模拟游戏状态
    round_state = {
        'dealer_btn': 0,
        'seats': [
            {'uuid': 'player1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'AI_2', 'stack': 1100, 'state': 'participating'},
            {'uuid': 'player3', 'name': 'AI_3', 'stack': 800, 'state': 'participating'},
            {'uuid': 'player4', 'name': '你', 'stack': 1050, 'state': 'participating'},
        ],
        'pot': {'main': {'amount': 100}}
    }
    
    print("\n📋 测试不同行动类型:")
    print("-" * 40)
    
    # 测试各种行动
    test_cases = [
        ('player1', 'AI_1', 'call', 30, False),      # 跟注
        ('player2', 'AI_2', 'raise', 60, False),     # 加注
        ('player3', 'AI_3', 'fold', 0, False),       # 弃牌
        ('player4', '你', 'call', 60, True),         # 玩家跟注
        ('player1', 'AI_1', 'raise', 120, False),    # 再加注
    ]
    
    for player_uuid, player_name, action, amount, is_human in test_cases:
        print(f"\n行动: {action} ${amount}")
        renderer.render_player_action(
            player_name, action, amount, is_human, 
            round_state, player_uuid
        )
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    test_enhanced_action_log()