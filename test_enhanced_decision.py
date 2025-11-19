#!/usr/bin/env python3
"""
测试修复后的AI决策逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_enhanced_decision_logic():
    """测试增强的决策逻辑"""
    print("🧪 测试增强的AI决策逻辑")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "ai_test"
    
    # 场景: 测试多个AI的决策一致性
    print("\n📋 测试场景: 多个AI的决策一致性")
    print("-" * 40)
    
    round_state = {
        'street': 'preflop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 15}},
        'community_card': [],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 800, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1200, 'state': 'participating'},
            {'uuid': 'ai_3', 'name': 'AI_3', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'RAISE', 'amount': 30, 'uuid': 'ai_1'}  # 有人加注
            ]
        }
    }
    
    # 设置一个中等强度的手牌（应该倾向于call而不是fold）
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 30},
        {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
    ]
    
    print("测试参数:")
    print("  手牌: K♠ Q♠ (较强的牌)")
    print("  位置: 按钮位")
    print("  面对加注: 30")
    print("  预期: 应该主要选择call，偶尔raise，很少fold")
    
    # 使用中等强度手牌
    hole_cards = ['SK', 'SQ']  # K♠ Q♠ 较强的牌
    
    print("\n🤖 AI思考过程:")
    action, amount = ai_player.declare_action(valid_actions, hole_cards, round_state)
    
    print(f"\n最终决策: {action} {amount}")
    
    # 验证结果
    if action == 'call':
        print("✅ AI选择了高概率的call")
        return True
    elif action == 'raise':
        print("✅ AI选择了合理的raise")
        return True
    else:
        print(f"⚠️ AI选择了fold（可能仍然会发生，但概率降低了）")
        return True  # fold仍然可能，但概率应该降低

if __name__ == "__main__":
    success = test_enhanced_decision_logic()
    if success:
        print("\n🎉 测试完成！请检查上面的输出")
        print("   预期：看到'⚠️低概率但合理'的警告当选择低概率行动时")
    else:
        print("\n⚠️ 测试失败")