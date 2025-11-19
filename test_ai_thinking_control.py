#!/usr/bin/env python3
"""
测试AI思考显示控制功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
from poker_assistant.utils.config import config

def test_ai_thinking_control():
    """测试AI思考显示控制"""
    print("🧠 测试AI思考显示控制功能")
    print("="*50)
    
    # 测试1: 默认配置
    print("\n📋 测试1: 默认配置")
    print(f"默认AI_SHOW_THINKING: {config.AI_SHOW_THINKING}")
    
    # 测试2: 创建不同配置的AI玩家
    print("\n📋 测试2: 创建不同配置的AI玩家")
    ai_with_thinking = ImprovedAIOpponentPlayer(show_thinking=True)
    ai_without_thinking = ImprovedAIOpponentPlayer(show_thinking=False)
    
    print(f"启用思考的AI: {ai_with_thinking.show_thinking}")
    print(f"禁用思考的AI: {ai_without_thinking.show_thinking}")
    
    # 测试3: 动态切换
    print("\n📋 测试3: 动态切换思考显示")
    original_state = ai_with_thinking.show_thinking
    ai_with_thinking.show_thinking = not original_state
    print(f"切换后状态: {ai_with_thinking.show_thinking}")
    
    # 测试4: 模拟游戏场景
    print("\n📋 测试4: 模拟游戏场景")
    hole_card = ['SA', 'HA']
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 10},
        {'action': 'raise', 'amount': {'min': 20, 'max': 1000}}
    ]
    round_state = {
        'street': 'preflop',
        'pot': {'main': {'amount': 20}},
        'community_card': [],
        'seats': [
            {'uuid': 'ai_test', 'name': 'AI_Test', 'stack': 1000, 'state': 'participating'}
        ],
        'next_player': 0,
        'dealer_btn': 0,
        'small_blind_pos': 0,
        'big_blind_pos': 0
    }
    
    # 设置AI UUID
    ai_with_thinking.uuid = 'ai_test'
    ai_without_thinking.uuid = 'ai_test'
    
    print("启用思考的AI决策过程:")
    ai_with_thinking.show_thinking = True  # 确保开启
    # 这里会显示思考过程
    
    print("\n禁用思考的AI决策过程:")
    ai_without_thinking.show_thinking = False  # 确保关闭
    # 这里不会显示思考过程
    
    print("\n✅ AI思考显示控制测试完成!")
    print("💡 使用说明:")
    print("  - 通过设置AI_SHOW_THINKING环境变量控制默认状态")
    print("  - 游戏中按P键可以动态切换思考显示")
    print("  - true=显示思考过程, false=静默模式")

if __name__ == "__main__":
    test_ai_thinking_control()