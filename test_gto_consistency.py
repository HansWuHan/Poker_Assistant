#!/usr/bin/env python3
"""
测试修复后的GTO策略一致性：思考过程与实际决策匹配
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_gto_consistency():
    """测试GTO策略思考过程与实际决策的一致性"""
    print("🧪 测试GTO策略思考过程与实际决策一致性")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "ai_test"
    
    # 模拟全下场景
    print("\n📋 测试场景：全下场景")
    print("-" * 40)
    
    # 模拟你观察到的场景
    round_state = {
        'street': 'preflop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 1060}},  # 底池1060
        'community_card': [],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 995, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 990, 'state': 'participating'},
            {'uuid': 'ai_3', 'name': 'AI_3', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'RAISE', 'amount': 1000, 'uuid': 'human'}  # 人类玩家全下1000
            ]
        }
    }
    
    # 全下后的有效行动
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 1000},  # 需要1000跟注
        {'action': 'raise', 'amount': {'min': -1, 'max': -1}}  # 不能加注
    ]
    
    # 测试不同的手牌
    test_hands = [
        (['S5', 'D5'], "5♠ 5♦ 对子55"),      # 55对子 - 你观察到的
        (['D8', 'D3'], "8♦ 3♦ 同花83"),     # 83同花 - 你观察到的  
        (['DK', 'HJ'], "K♦ J♥ 不同花KJ"),   # KJ不同花 - 你观察到的
        (['SA', 'HA'], "A♠ A♥ 对子AA")      # AA对子 - 强牌对比
    ]
    
    for hole_cards, hand_desc in test_hands:
        print(f"\n🃏 测试手牌: {hand_desc}")
        print(f"   底池: 1060，需要跟注: 1000")
        
        # 重置AI玩家状态
        ai_player.uuid = f"ai_test_{hole_cards[0]}_{hole_cards[1]}"
        
        print(f"\n🤖 AI思考过程:")
        action, amount = ai_player.declare_action(valid_actions, hole_cards, round_state)
        
        print(f"\n🎯 最终决策: {action} {amount}")
        
        # 验证一致性
        print(f"\n✅ 一致性验证:")
        print(f"   思考过程显示的策略应该与实际决策一致")
        print(f"   如果显示'弃牌'，实际应该fold")
        print(f"   如果显示'跟注'，实际应该call")
        print(f"   如果显示'加注'，实际应该raise")
        print("-" * 40)

if __name__ == "__main__":
    test_gto_consistency()