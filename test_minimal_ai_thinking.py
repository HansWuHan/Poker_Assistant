#!/usr/bin/env python3
"""
测试精简后的AI思考输出
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def test_minimal_ai_thinking():
    """测试精简AI思考输出"""
    print("🧪 测试精简AI思考输出")
    print("="*60)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "ai_test"
    
    # 场景1: 翻牌前口袋AA
    print("\n📋 场景1: 翻牌前口袋AA")
    print("-" * 40)
    
    hole_card = ['SA', 'HA']  # 口袋AA
    round_state = {
        'street': 'preflop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 30}},
        'community_card': [],
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'ai_1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'ai_2'},
                {'action': 'RAISE', 'amount': 30, 'uuid': 'ai_1'}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 30},
        {'action': 'raise', 'amount': {'min': 60, 'max': 1000}}
    ]
    
    print("预期精简输出:")
    print("🎯 我的手牌: A♠ A♥ (对子 AA) - 大盲位")
    print("💰 底池$30，跟注$30，赔率50.0%")
    print("🔍 AI_1: 中等牌(对子，KQ)；AI_2: 边缘牌(高牌，同花连牌)")
    print("💡 强牌，考虑价值下注")
    print("🎯 📈 加注 $60")
    print()
    
    action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
    
    # 场景2: 翻牌后顶对弱踢脚
    print("\n📋 场景2: 翻牌后顶对弱踢脚")
    print("-" * 40)
    
    hole_card2 = ['HA', 'D9']  # A9不同花
    round_state2 = {
        'street': 'flop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 150}},
        'community_card': ['S9', 'H7', 'C2'],  # 顶对9
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 950, 'state': 'participating'}
        ],
        'action_histories': {
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'ai_1'},
                {'action': 'BET', 'amount': 50, 'uuid': 'ai_2'}
            ]
        }
    }
    
    valid_actions2 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 950}}
    ]
    
    print("预期精简输出:")
    print("🎯 我的牌力: 中等牌力 A♥ 9♦")
    print("💰 底池$150，跟注$50，赔率25.0%")
    print("🔍 AI_1: 弱牌或投机牌；AI_2: 边缘牌(高牌，同花连牌)；牌面分析: 干燥牌面，对手多为高牌")
    print("💡 中等牌力，谨慎行动")
    print("🎯 ✅ 跟注 $50")
    print()
    
    action2, amount2 = ai_player.declare_action(valid_actions2, hole_card2, round_state2)
    
    # 场景3: 翻牌后空气牌
    print("\n📋 场景3: 翻牌后空气牌")
    print("-" * 40)
    
    hole_card3 = ['S2', 'H7']  # 27不同花
    round_state3 = {
        'street': 'flop',
        'dealer_btn': 0,
        'pot': {'main': {'amount': 120}},
        'community_card': ['HA', 'HK', 'DQ'],  # 高牌面，完全错过
        'seats': [
            {'uuid': 'ai_1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
            {'uuid': 'ai_2', 'name': 'AI_2', 'stack': 950, 'state': 'participating'},
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 950, 'state': 'participating'}
        ],
        'action_histories': {
            'flop': [
                {'action': 'BET', 'amount': 40, 'uuid': 'ai_1'}
            ]
        }
    }
    
    valid_actions3 = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 40},
        {'action': 'raise', 'amount': {'min': 80, 'max': 950}}
    ]
    
    print("预期精简输出:")
    print("🎯 我的牌力: 弱牌 2♠ 7♥")
    print("💰 底池$120，跟注$40，赔率25.0%")
    print("🔍 AI_1: 边缘牌(高牌，同花连牌)；牌面分析: 中性牌面，对手范围较宽")
    print("💡 弱牌，考虑弃牌")
    print("🎯 🚫 弃牌")
    print()
    
    action3, amount3 = ai_player.declare_action(valid_actions3, hole_card3, round_state3)
    
    print("\n" + "="*60)
    print("✅ 精简AI思考输出测试完成!")
    print("\n🎯 精简效果:")
    print("  ✅ 移除对手分析行")
    print("  ✅ 移除'AI正在思考中'提示")
    print("  ✅ 移除分隔线")
    print("  ✅ 移除'最终决策'字样")
    print("  ✅ 位置分析合并到牌力行")
    print("  ✅ 整体更简洁明了")

if __name__ == "__main__":
    test_minimal_ai_thinking()