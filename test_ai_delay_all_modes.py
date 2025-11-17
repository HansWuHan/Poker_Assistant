#!/usr/bin/env python3
"""
测试AI在所有模式下的延时效果
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
import time

def test_ai_delay_modes():
    """测试AI在不同模式下的延时效果"""
    print("🧪 测试AI在不同模式下的延时效果")
    print("=" * 60)
    
    # 测试场景
    hole_card = ['SA', 'HA']  # 黑桃A，红心A
    round_state = {
        'street': 'flop',
        'dealer_btn': 0,
        'seats': [
            {'uuid': 'test_ai', 'name': 'AI玩家', 'stack': 1000},
            {'uuid': 'p2', 'name': '玩家2', 'stack': 1000},
            {'uuid': 'p3', 'name': '玩家3', 'stack': 1000}
        ],
        'pot': {'main': {'amount': 100}},
        'community_card': ['S7', 'H2', 'D9'],
        'action_histories': {
            'preflop': [
                {'uuid': 'p2', 'action': 'call', 'amount': 10},
                {'uuid': 'p3', 'action': 'raise', 'amount': 30}
            ],
            'flop': [
                {'uuid': 'p2', 'action': 'check', 'amount': 0},
                {'uuid': 'p3', 'action': 'raise', 'amount': 50}
            ]
        }
    }
    
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 300}}
    ]
    
    # 测试1: 开启思考显示
    print("📊 测试1: 开启思考显示模式")
    print("-" * 40)
    ai_with_thinking = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_with_thinking.uuid = "test_ai"
    
    start_time = time.time()
    action1, amount1 = ai_with_thinking.declare_action(valid_actions, hole_card, round_state)
    end_time = time.time()
    thinking_time1 = end_time - start_time
    
    print(f"✅ 决策: {action1} ${amount1}")
    print(f"⏱️  总用时: {thinking_time1:.2f}秒")
    print()
    
    # 测试2: 关闭思考显示
    print("📊 测试2: 关闭思考显示模式")
    print("-" * 40)
    ai_without_thinking = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=False)
    ai_without_thinking.uuid = "test_ai"
    
    start_time = time.time()
    action2, amount2 = ai_without_thinking.declare_action(valid_actions, hole_card, round_state)
    end_time = time.time()
    thinking_time2 = end_time - start_time
    
    print(f"✅ 决策: {action2} ${amount2}")
    print(f"⏱️  总用时: {thinking_time2:.2f}秒")
    print()
    
    # 测试结果分析
    print("📈 测试结果分析")
    print("=" * 60)
    
    if thinking_time1 >= 1.0:
        print("✅ 开启思考显示模式: 延时正常 (≥1秒)")
    else:
        print("⚠️  开启思考显示模式: 延时不足 (<1秒)")
    
    if thinking_time2 >= 1.0:
        print("✅ 关闭思考显示模式: 延时正常 (≥1秒)")
    else:
        print("⚠️  关闭思考显示模式: 延时不足 (<1秒)")
    
    print()
    print("🎯 测试目标:")
    print("  ✅ 两种模式都应该有1秒延时")
    print("  ✅ 让AI决策看起来更自然")
    print("  ✅ 避免AI决策过于机械化")
    print()
    print("🎮 测试完成！")

if __name__ == "__main__":
    test_ai_delay_modes()