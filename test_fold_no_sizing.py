#!/usr/bin/env python3
"""
测试修复后的AI思考过程 - fold时不显示尺度建议
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_fold_no_sizing():
    """测试fold时不显示尺度建议"""
    print("🧪 测试fold时不显示尺度建议")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "ai_test"
    
    # 场景: AI玩家选择fold
    print("\n📋 测试场景: AI玩家选择fold")
    print("-" * 40)
    
    round_state = {
        'street': 'preflop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 15}},
        'community_card': [],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 800, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1200, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'ai_1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'ai_2'}
            ]
        }
    }
    
    # 设置一个会触发fold的场景（很弱的手牌）
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 10},
        {'action': 'raise', 'amount': {'min': 20, 'max': 1000}}
    ]
    
    print("测试参数:")
    print("  手牌: 7♠ 2♦ (很弱的牌)")
    print("  位置: 按钮位")
    print("  底池: $15")
    print("  需要跟注: $10")
    print("  预期: AI应该fold，且不显示尺度建议")
    
    # 使用弱牌来促使AI选择fold
    hole_cards = ['S7', 'D2']  # 7♠ 2♦ 非常弱的牌
    
    print("\n🤖 AI思考过程:")
    action, amount = ai_player.declare_action(valid_actions, hole_cards, round_state)
    
    print(f"\n最终决策: {action} ${amount}")
    
    # 验证结果
    if action == 'fold':
        print("✅ AI正确选择了fold")
        return True
    else:
        print(f"❌ AI没有选择fold，而是选择了{action}")
        return False

if __name__ == "__main__":
    success = test_fold_no_sizing()
    if success:
        print("\n🎉 测试完成！请检查上面的输出是否包含尺度建议")
    else:
        print("\n⚠️  AI没有选择fold，但思考过程仍然可见")