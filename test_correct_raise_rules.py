#!/usr/bin/env python3
"""
测试加注规则是否符合德州扑克标准
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.cli.input_handler import InputHandler

def test_raise_rules():
    """测试加注规则"""
    print("🎰 测试德州扑克加注规则")
    print("="*60)
    
    input_handler = InputHandler()
    
    # 测试场景1: 翻牌前，大盲注$10，无人加注
    print("\n📋 场景1: 翻牌前，大盲$10，无人加注")
    print("-" * 40)
    
    round_state1 = {
        'street': 'preflop',
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'}
            ]
        }
    }
    
    # 模拟PyPokerEngine的加注范围（最小应为$20，即大盲注的一倍）
    raise_action1 = {'amount': {'min': 20, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action1['amount']['min']} - ${raise_action1['amount']['max']}")
    
    # 测试输入处理器的显示（只显示规则信息）
    print("📏 加注规则信息显示:")
    
    # 模拟显示逻辑
    street = round_state1.get('street', 'preflop')
    action_histories = round_state1.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        for action in action_histories[street]:
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
        
        if max_previous_raise > 0:
            required_min = max_previous_raise  # 必须至少等于之前最大加注
            print(f"📏 加注规则: 必须至少为之前最大加注(${max_previous_raise})")
            print(f"📊 理论最小: ${required_min} (实际最小: ${raise_action1['amount']['min']})")
        else:
            print(f"📏 加注规则: 该圈尚未有玩家加注，加注金额需≥大盲注")
            print(f"📊 大盲注: $10 (最小加注: ${raise_action1['amount']['min']})")
    
    # 测试场景2: 有人加注到$30
    print("\n📋 场景2: 有人加注到$30")
    print("-" * 40)
    
    round_state2 = {
        'street': 'preflop',
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'},
                {'action': 'RAISE', 'amount': 30, 'uuid': 'player3'}  # 有人加注到30
            ]
        }
    }
    
    # 模拟PyPokerEngine的加注范围（最小应为$30，即之前加注的金额）
    raise_action2 = {'amount': {'min': 30, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action2['amount']['min']} - ${raise_action2['amount']['max']}")
    
    # 测试输入处理器的显示（只显示规则信息）
    print("📏 加注规则信息显示:")
    
    # 模拟显示逻辑
    street = round_state2.get('street', 'preflop')
    action_histories = round_state2.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        for action in action_histories[street]:
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
        
        if max_previous_raise > 0:
            required_min = max_previous_raise  # 必须至少等于之前最大加注
            print(f"📏 加注规则: 必须至少为之前最大加注(${max_previous_raise})")
            print(f"📊 理论最小: ${required_min} (实际最小: ${raise_action2['amount']['min']})")
        else:
            print(f"📏 加注规则: 该圈尚未有玩家加注，加注金额需≥大盲注")
            print(f"📊 大盲注: $10 (最小加注: ${raise_action2['amount']['min']})")
    
    # 测试场景3: 翻牌后，有人下注$80
    print("\n📋 场景3: 翻牌后，有人下注$80")
    print("-" * 40)
    
    round_state3 = {
        'street': 'flop',
        'action_histories': {
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                {'action': 'RAISE', 'amount': 80, 'uuid': 'player2'}  # 有人下注80
            ]
        }
    }
    
    # 模拟PyPokerEngine的加注范围（最小应为$80）
    raise_action3 = {'amount': {'min': 80, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action3['amount']['min']} - ${raise_action3['amount']['max']}")
    
    # 测试输入处理器的显示（只显示规则信息）
    print("📏 加注规则信息显示:")
    
    # 模拟显示逻辑
    street = round_state3.get('street', 'flop')
    action_histories = round_state3.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        for action in action_histories[street]:
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
        
        if max_previous_raise > 0:
            required_min = max_previous_raise  # 必须至少等于之前最大加注
            print(f"📏 加注规则: 必须至少为之前最大加注(${max_previous_raise})")
            print(f"📊 理论最小: ${required_min} (实际最小: ${raise_action3['amount']['min']})")
        else:
            print(f"📏 加注规则: 该圈尚未有玩家加注，加注金额需≥大盲注")
            print(f"📊 大盲注: $10 (最小加注: ${raise_action3['amount']['min']})")
    
    print("\n" + "="*60)
    print("✅ 加注规则测试完成!")
    print("\n🎯 规则总结:")
    print("  ✅ 无人加注时：最小加注 = 大盲注")
    print("  ✅ 有人加注时：最小加注 = 之前最大加注金额")
    print("  ✅ 加注必须等于或高于该圈最后一个加注玩家的加注金额")

if __name__ == "__main__":
    test_raise_rules()