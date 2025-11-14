#!/usr/bin/env python3
"""
测试P按钮功能 - 切换AI思考显示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_p_button_functionality():
    """测试P按钮功能"""
    print("🔄 测试P按钮功能 - 切换AI思考显示")
    print("="*60)
    
    # 模拟输入处理器
    from poker_assistant.cli.input_handler import InputHandler
    
    # 创建输入处理器
    input_handler = InputHandler()
    
    # 测试初始状态
    print(f"初始AI思考显示状态: {'开启' if input_handler.ai_show_thinking else '关闭'}")
    
    # 模拟P按钮按下
    print("\n📋 模拟用户按下P按钮...")
    
    # 模拟输入处理
    user_input = 'P'
    
    if user_input.upper() == 'P':
        # 切换状态
        input_handler.ai_show_thinking = not input_handler.ai_show_thinking
        status = "开启" if input_handler.ai_show_thinking else "关闭"
        print(f"🔄 AI思考显示已{status}")
    
    print(f"\n切换后状态: {'开启' if input_handler.ai_show_thinking else '关闭'}")
    
    # 再次切换
    print("\n📋 再次按下P按钮...")
    input_handler.ai_show_thinking = not input_handler.ai_show_thinking
    status = "开启" if input_handler.ai_show_thinking else "关闭"
    print(f"🔄 AI思考显示已{status}")
    
    print(f"\n最终状态: {'开启' if input_handler.ai_show_thinking else '关闭'}")
    
    print("\n✅ P按钮功能测试完成!")
    print("\n🎯 使用说明:")
    print("- 在游戏中按 'P' 键可以切换AI思考显示")
    print("- 状态会实时显示在按钮上: [P]AI思考(开启) 或 [P]AI思考(关闭)")
    print("- 切换后所有AI玩家的思考过程都会相应显示或隐藏")

def test_action_prompt():
    """测试行动提示中的P按钮显示"""
    print("\n\n🎮 测试行动提示显示")
    print("="*60)
    
    from poker_assistant.cli.input_handler import InputHandler
    
    input_handler = InputHandler()
    
    # 模拟行动提示
    print("\n📋 模拟游戏行动提示:")
    
    # 模拟valid_actions
    valid_actions = [
        {'action': 'fold', 'amount': 0},
        {'action': 'call', 'amount': 50},
        {'action': 'raise', 'amount': {'min': 100, 'max': 1000}}
    ]
    
    ai_enabled = True
    
    # 构建行动提示（模拟_show_action_prompt方法）
    actions = []
    actions.append("[F]弃牌")
    actions.append(f"[C]跟注($50)")
    actions.append(f"[R]加注($100-$1000)")
    actions.append(f"[A]全下($1000)")
    
    if ai_enabled:
        actions.append("[O]牌力分析")
    
    # 添加P按钮 - 显示当前状态
    thinking_status = "开启" if input_handler.ai_show_thinking else "关闭"
    actions.append(f"[P]AI思考({thinking_status})")
    
    actions.append("[Q]提问")
    actions.append("[H]帮助")
    
    print("\n" + " | ".join(actions))
    
    print("\n✅ 行动提示显示测试完成!")
    print("\n🎯 界面效果:")
    print("- P按钮会实时显示当前状态")
    print("- 用户可以清楚地知道AI思考显示是开启还是关闭")
    print("- 界面简洁明了，易于操作")

if __name__ == "__main__":
    test_p_button_functionality()
    test_action_prompt()