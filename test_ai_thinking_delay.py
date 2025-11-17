#!/usr/bin/env python3
"""
测试AI思考延时效果
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
import time

def test_ai_thinking_delay():
    """测试AI思考延时"""
    print("🧪 测试AI思考延时效果")
    print("=" * 50)
    
    # 创建AI玩家
    ai_player = ImprovedAIOpponentPlayer(difficulty="medium", show_thinking=True)
    ai_player.uuid = "test_ai"
    
    # 模拟测试场景
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
        'community_card': ['S7', 'H2', 'D9'],  # 翻牌：7♠ 2♥ 9♦
        'action_histories': {}
    }
    
    # 模拟有效行动
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 20},
        {'action': 'raise', 'amount': {'min': 40, 'max': 200}}
    ]
    
    print(f"🃏 AI手牌: {hole_card[0]} {hole_card[1]}")
    print(f"🎴 公共牌: {' '.join(round_state['community_card'])}")
    print(f"💰 底池: ${round_state['pot']['main']['amount']}")
    print(f"📍 当前街道: {round_state['street']}")
    print()
    
    print("⏳ 开始计时，观察AI思考过程...")
    start_time = time.time()
    
    # 调用AI决策
    action, amount = ai_player.declare_action(valid_actions, hole_card, round_state)
    
    end_time = time.time()
    thinking_time = end_time - start_time
    
    print()
    print(f"✅ AI决策完成！")
    print(f"🎯 决策: {action}")
    if amount > 0:
        print(f"💰 金额: ${amount}")
    print(f"⏱️  思考时间: {thinking_time:.2f}秒")
    
    # 验证是否有1秒延时
    if thinking_time >= 1.0:
        print("✅ 延时效果正常！")
    else:
        print("⚠️  延时效果可能有问题")
    
    print()
    print("=" * 50)
    print("🎮 测试完成！")

if __name__ == "__main__":
    test_ai_thinking_delay()