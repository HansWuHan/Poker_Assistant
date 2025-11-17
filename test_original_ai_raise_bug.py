#!/usr/bin/env python3
"""
重现AI从$10加注到$17的bug
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.ai_opponent import AIOpponentPlayer

def test_original_ai_raise_bug():
    """测试原始AI的加注bug"""
    print("🔍 测试原始AI加注bug")
    print("="*60)
    
    # 创建原始AI玩家
    ai_player = AIOpponentPlayer(difficulty="medium")
    ai_player.uuid = "ai_test"
    
    # 模拟导致bug的场景
    print("\n📋 测试场景: 大盲$10，AI从$10加注到$17")
    print("-" * 40)
    
    # 模拟游戏状态
    hole_card = ['SA', 'HK']  # 不错的手牌
    
    round_state = {
        'street': 'preflop',
        'seats': [
            {'uuid': 'ai_test', 'name': 'AI', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'player2', 'name': 'Player2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'player3', 'name': 'Player3', 'stack': 1000, 'state': 'participating'}
        ],
        'pot': {'main': {'amount': 15}},  # 小底池
        'community_card': [],
        'dealer_btn': 0,
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player2'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player3'}
            ]
        }
    }
    
    # 模拟有效行动 - 这里最小加注应该是$20（大盲的一倍）
    # 但AI可能计算出$17
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 10},  # 需要跟注$10
        {'action': 'raise', 'amount': {'min': 20, 'max': 1000}}  # 最小加注$20
    ]
    
    print(f"📊 游戏状态:")
    print(f"  底池: ${round_state['pot']['main']['amount']}")
    print(f"  需要跟注: $10")
    print(f"  最小加注: $20")
    print(f"  手牌: {hole_card}")
    
    # 测试不同难度
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n🎯 测试{difficulty}难度:")
        ai_player.difficulty = difficulty
        
        # 多次测试看是否有$17的情况
        for i in range(5):
            action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
            
            if action == 'raise':
                print(f"  尝试{i+1}: 加注${amount}")
                if amount < 20:  # 如果小于最小加注，就是bug
                    print(f"    ❌ BUG: 加注${amount}小于最小要求$20")
                elif amount == 17:  # 特别检查$17
                    print(f"    🔍 发现$17加注，分析原因...")
                    
                    # 分析可能的原因
                    pot = round_state['pot']['main']['amount']
                    print(f"    📊 底池: ${pot}")
                    print(f"    📊 pot * 0.85 = ${int(pot * 0.85)}")  # 可能的计算
                    print(f"    📊 pot * 0.9 = ${int(pot * 0.9)}")   # 可能的计算
                    
            else:
                print(f"  尝试{i+1}: {action} ${amount}")
    
    # 特别检查加注计算逻辑
    print(f"\n🔬 详细分析加注计算:")
    pot = round_state['pot']['main']['amount']
    
    # 检查原始AI的加注逻辑
    print(f"  原始AI加注逻辑分析:")
    print(f"  - pot * 0.5 = ${int(pot * 0.5)}")
    print(f"  - pot * 0.6 = ${int(pot * 0.6)}")
    print(f"  - pot * 0.75 = ${int(pot * 0.75)}")
    print(f"  - pot * 0.9 = ${int(pot * 0.9)}")
    
    # 检查是否可能得到17
    if int(pot * 0.85) == 17:
        print(f"  ⚠️  pot * 0.85 = 17，这可能是bug来源")
    if int(pot * 0.9) == 17:
        print(f"  ⚠️  pot * 0.9 = 17，这可能是bug来源")
    
    print(f"\n" + "="*60)
    print("✅ 原始AI加注测试完成!")
    print("\n🎯 发现:")
    print("  ✅ 需要检查原始AI是否可能计算出$17")
    print("  ✅ 所有加注都应该≥$20（最小加注要求）")
    print("  ✅ 如果发现有<$20的加注，说明有bug")

if __name__ == "__main__":
    test_original_ai_raise_bug()