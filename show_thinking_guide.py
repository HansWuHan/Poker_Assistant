#!/usr/bin/env python3
"""
show_thinking 参数使用指南
"""

print("🧠 show_thinking 参数使用指南")
print("="*60)

print("""
📋 什么是 show_thinking 参数？

show_thinking 是一个布尔参数，用于控制AI是否显示详细的思考过程。

🔧 参数说明：
- show_thinking=True  (默认): 显示AI的完整思考过程
- show_thinking=False (静默模式): 只显示AI的最终决策

""")

print("💡 使用场景：")
print("-" * 30)
print("""
1. 学习和分析时：设置为True，观察AI如何思考
2. 正常游戏时：设置为False，保持界面简洁
3. 调试AI时：设置为True，了解决策逻辑
4. 比赛模式：设置为False，避免信息干扰
""")

print("⚙️  如何设置 show_thinking 参数？")
print("-" * 40)

print("""
方法1：在创建AI玩家时设置

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

# 显示思考过程
ai_player = ImprovedAIOpponentPlayer(
    difficulty="medium", 
    shared_hole_cards=shared_dict,
    show_thinking=True  # 显示详细思考
)

# 静默模式
ai_player = ImprovedAIOpponentPlayer(
    difficulty="medium", 
    shared_hole_cards=shared_dict,
    show_thinking=False  # 只显示结果
)
""")

print("\n方法2：通过游戏配置设置")
print("""
# 在配置文件中添加
AI_SHOW_THINKING=true  # 显示思考
AI_SHOW_THINKING=false # 静默模式
""")

print("\n方法3：运行时动态切换")
print("""
# 创建后可以动态修改
ai_player.show_thinking = True   # 开启显示
ai_player.show_thinking = False  # 关闭显示
""")

print("\n🎯 实际效果对比：")
print("-" * 30)

# 演示代码
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer

def demo_show_thinking():
    print("\n📊 演示：show_thinking=True vs show_thinking=False")
    print("="*50)
    
    # 测试场景
    test_scenario = {
        "hole_card": ['HA', 'D9'],
        "round_state": {
            'street': 'flop',
            'dealer_btn': 0,
            'pot': {'main': {'amount': 150}},
            'community_card': ['S9', 'H7', 'C2'],
            'seats': [
                {'uuid': 'player1', 'name': 'AI_1', 'stack': 950, 'state': 'participating'},
                {'uuid': 'ai_player', 'name': 'AI_Player', 'stack': 950, 'state': 'participating'},
            ],
            'action_histories': {
                'flop': [
                    {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                    {'action': 'BET', 'amount': 50, 'uuid': 'player2'}
                ]
            }
        },
        "valid_actions": [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 50},
            {'action': 'raise', 'amount': {'min': 100, 'max': 950}}
        ]
    }
    
    print("\n🧠 show_thinking=True (显示思考过程):")
    print("-" * 40)
    ai_with_thinking = ImprovedAIOpponentPlayer(
        difficulty="medium", 
        shared_hole_cards={},
        show_thinking=True
    )
    ai_with_thinking.uuid = 'ai_player'
    
    # 这会显示详细的思考过程
    action1, amount1 = ai_with_thinking.declare_action(
        test_scenario["valid_actions"],
        test_scenario["hole_card"],
        test_scenario["round_state"]
    )
    
    print(f"\n最终决策: {action1} ${amount1}")
    
    print("\n🤫 show_thinking=False (静默模式):")
    print("-" * 40)
    ai_without_thinking = ImprovedAIOpponentPlayer(
        difficulty="medium", 
        shared_hole_cards={},
        show_thinking=False
    )
    ai_without_thinking.uuid = 'ai_player'
    
    # 这只会显示最终决策
    action2, amount2 = ai_without_thinking.declare_action(
        test_scenario["valid_actions"],
        test_scenario["hole_card"],
        test_scenario["round_state"]
    )
    
    print(f"最终决策: {action2} ${amount2}")
    
    print("\n✅ 总结:")
    print("- show_thinking=True: 适合学习分析，信息丰富")
    print("- show_thinking=False: 适合正常游戏，界面简洁")
    print("- 可以根据需要随时切换")

if __name__ == "__main__":
    demo_show_thinking()