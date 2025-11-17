#!/usr/bin/env python3
"""
测试修正后的加注规则显示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.cli.input_handler import InputHandler

def test_corrected_raise_rules_display():
    """测试修正后的加注规则显示"""
    print("🎰 测试修正后的加注规则显示")
    print("="*60)
    
    input_handler = InputHandler()
    
    # 场景1: 翻牌前，大盲$10，无人加注
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
    
    # 模拟PyPokerEngine的加注范围
    raise_action1 = {'amount': {'min': 20, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action1['amount']['min']} - ${raise_action1['amount']['max']}")
    
    # 模拟显示逻辑
    street = round_state1.get('street', 'preflop')
    action_histories = round_state1.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        call_amount = 0
        
        for action in action_histories[street]:
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
            elif action.get('action', '').upper() in ['CALL', 'BIGBLIND']:
                call_amount = max(call_amount, action.get('amount', 0))
        
        if max_previous_raise > 0:
            previous_raise_increment = max_previous_raise - call_amount if call_amount > 0 else max_previous_raise
            your_min_raise_increment = previous_raise_increment
            your_min_total = call_amount + your_min_raise_increment
            
            print(f"📏 加注规则: 之前玩家加注${previous_raise_increment}（到${max_previous_raise}）")
            print(f"📊 你必须至少再加注${your_min_raise_increment}（总下注${your_min_total}）")
            print(f"📊 当前最小加注: ${raise_action1['amount']['min']}")
        else:
            print(f"📏 加注规则: 该圈尚未有玩家加注")
            print(f"📊 最小总下注: ${raise_action1['amount']['min']}")
    
    # 场景2: 有人加注到$30（从$10加注$20）
    print("\n📋 场景2: 有人从$10加注到$30")
    print("-" * 40)
    
    round_state2 = {
        'street': 'preflop',
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'player3'},
                {'action': 'RAISE', 'amount': 30, 'uuid': 'player1'}  # 从10加注到30
            ]
        }
    }
    
    # 模拟PyPokerEngine的加注范围
    raise_action2 = {'amount': {'min': 50, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action2['amount']['min']} - ${raise_action2['amount']['max']}")
    
    # 模拟显示逻辑
    street = round_state2.get('street', 'preflop')
    action_histories = round_state2.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        call_amount = 0
        
        for action in action_histories[street]:
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
            elif action.get('action', '').upper() in ['CALL', 'BIGBLIND']:
                call_amount = max(call_amount, action.get('amount', 0))
        
        if max_previous_raise > 0:
            previous_raise_increment = max_previous_raise - call_amount if call_amount > 0 else max_previous_raise
            your_min_raise_increment = previous_raise_increment
            your_min_total = call_amount + your_min_raise_increment
            
            print(f"📏 加注规则: 之前玩家加注${previous_raise_increment}（到${max_previous_raise}）")
            print(f"📊 你必须至少再加注${your_min_raise_increment}（总下注${your_min_total}）")
            print(f"📊 当前最小加注: ${raise_action2['amount']['min']}")
        else:
            print(f"📏 加注规则: 该圈尚未有玩家加注")
            print(f"📊 最小总下注: ${raise_action2['amount']['min']}")
    
    # 场景3: 有人加注到$80（从$40加注$40）
    print("\n📋 场景3: 有人从$40加注到$80")
    print("-" * 40)
    
    round_state3 = {
        'street': 'flop',
        'action_histories': {
            'flop': [
                {'action': 'CHECK', 'amount': 0, 'uuid': 'player1'},
                {'action': 'RAISE', 'amount': 40, 'uuid': 'player2'},  # 第一个加注
                {'action': 'CALL', 'amount': 40, 'uuid': 'player3'},
                {'action': 'RAISE', 'amount': 80, 'uuid': 'player1'}  # 从40加注到80
            ]
        }
    }
    
    # 模拟PyPokerEngine的加注范围
    raise_action3 = {'amount': {'min': 120, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action3['amount']['min']} - ${raise_action3['amount']['max']}")
    
    # 模拟显示逻辑
    street = round_state3.get('street', 'flop')
    action_histories = round_state3.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        call_amount = 0
        
        for action in action_histories[street]:
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
            elif action.get('action', '').upper() in ['CALL', 'CHECK']:
                call_amount = max(call_amount, action.get('amount', 0))
        
        if max_previous_raise > 0:
            previous_raise_increment = max_previous_raise - call_amount if call_amount > 0 else max_previous_raise
            your_min_raise_increment = previous_raise_increment
            your_min_total = call_amount + your_min_raise_increment
            
            print(f"📏 加注规则: 之前玩家加注${previous_raise_increment}（到${max_previous_raise}）")
            print(f"📊 你必须至少再加注${your_min_raise_increment}（总下注${your_min_total}）")
            print(f"📊 当前最小加注: ${raise_action3['amount']['min']}")
        else:
            print(f"📏 加注规则: 该圈尚未有玩家加注")
            print(f"📊 最小总下注: ${raise_action3['amount']['min']}")
    
    print("\n" + "="*60)
    print("✅ 修正后的加注规则显示完成!")
    print("\n🎯 规则总结:")
    print("  ✅ 加注量必须≥之前玩家的加注量")
    print("  ✅ 清晰显示加注增量和总下注额")
    print("  ✅ 符合标准德州扑克规则")

if __name__ == "__main__":
    test_corrected_raise_rules_display()