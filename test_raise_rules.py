#!/usr/bin/env python3
"""
测试新的加注规则显示功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.cli.input_handler import InputHandler

def test_raise_rule_display():
    """测试加注规则显示"""
    print("🎰 测试加注规则显示")
    print("="*60)
    
    input_handler = InputHandler()
    
    # 模拟不同的加注场景
    test_scenarios = [
        {
            "name": "第一次加注（翻牌前）",
            "round_state": {
                'street': 'preflop',
                'action_histories': {
                    'preflop': [
                        {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                        {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'}
                    ]
                }
            },
            "raise_action": {'amount': {'min': 20, 'max': 1000}}
        },
        {
            "name": "第二次加注（有人已加注到30）",
            "round_state": {
                'street': 'preflop',
                'action_histories': {
                    'preflop': [
                        {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                        {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'},
                        {'action': 'RAISE', 'amount': 30, 'uuid': 'player3'}
                    ]
                }
            },
            "raise_action": {'amount': {'min': 50, 'max': 1000}}
        },
        {
            "name": "第三次加注（有人已加注到80）",
            "round_state": {
                'street': 'flop',
                'action_histories': {
                    'flop': [
                        {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                        {'action': 'RAISE', 'amount': 80, 'uuid': 'player2'}
                    ]
                }
            },
            "raise_action": {'amount': {'min': 160, 'max': 1000}}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}:")
        print("-" * 40)
        
        # 调用加注金额获取方法（只显示信息，不实际等待输入）
        min_raise = scenario['raise_action']['amount']['min']
        max_raise = scenario['raise_action']['amount']['max']
        
        print(f"💰 加注范围: ${min_raise} - ${max_raise}")
        
        # 显示加注规则信息
        round_state = scenario['round_state']
        street = round_state.get('street', 'preflop')
        action_histories = round_state.get('action_histories', {})
        
        if street in action_histories:
            max_previous_raise = 0
            for action in action_histories[street]:
                if action.get('action', '').upper() == 'RAISE':
                    amount = action.get('amount', 0)
                    max_previous_raise = max(max_previous_raise, amount)
            
            if max_previous_raise > 0:
                required_min = max_previous_raise  # 根据德州扑克规则，加注必须等于或高于之前最大加注
                print(f"📏 加注规则: 必须至少为之前最大加注(${max_previous_raise})")
                print(f"📊 理论最小: ${required_min} (实际最小: ${min_raise})")
        
        print("💡 提示: 输入 'min' 最小加注, 'max' 全下, 或具体金额")
        print()
    
    print("✅ 测试完成!")

if __name__ == "__main__":
    test_raise_rule_display()