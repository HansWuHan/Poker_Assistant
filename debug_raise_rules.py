#!/usr/bin/env python3
"""
重现并修复加注规则显示的bug
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.cli.input_handler import InputHandler

def debug_raise_rules_bug():
    """重现加注规则显示的bug"""
    print("🐛 重现加注规则显示的bug")
    print("="*60)
    
    input_handler = InputHandler()
    
    # 重现用户报告的场景
    print("\n📋 Bug场景: 加注范围$24-$1000，但显示之前玩家加注$0到$17")
    print("-" * 40)
    
    # 模拟导致bug的游戏状态
    round_state = {
        'street': 'preflop',
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'player3'},
                {'action': 'RAISE', 'amount': 17, 'uuid': 'player1'}  # 这可能是导致bug的情况
            ]
        }
    }
    
    # 模拟PyPokerEngine的加注范围
    raise_action = {'amount': {'min': 24, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action['amount']['min']} - ${raise_action['amount']['max']}")
    print(f"📋 行动历史: {round_state['action_histories']['preflop']}")
    
    # 分析当前逻辑的问题
    print("\n🔍 分析当前逻辑的问题:")
    
    street = round_state.get('street', 'preflop')
    action_histories = round_state.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        call_amount = 0
        
        for action in action_histories[street]:
            print(f"  📄 处理行动: {action}")
            if action.get('action', '').upper() == 'RAISE':
                amount = action.get('amount', 0)
                max_previous_raise = max(max_previous_raise, amount)
                print(f"    🎯 找到加注: ${amount}")
            elif action.get('action', '').upper() in ['CALL', 'CHECK']:
                call_amount = max(call_amount, action.get('amount', 0))
                print(f"    📞 找到跟注/check: ${action.get('amount', 0)}")
        
        print(f"\n  📊 结果统计:")
        print(f"    最大之前加注: ${max_previous_raise}")
        print(f"    最大跟注金额: ${call_amount}")
        
        if max_previous_raise > 0:
            previous_raise_increment = max_previous_raise - call_amount if call_amount > 0 else max_previous_raise
            print(f"    之前加注增量: ${previous_raise_increment}")
            
            your_min_raise_increment = previous_raise_increment
            your_min_total = call_amount + your_min_raise_increment
            print(f"    你的最小加注增量: ${your_min_raise_increment}")
            print(f"    你的最小总下注: ${your_min_total}")
            print(f"    PyPokerEngine最小加注: ${raise_action['amount']['min']}")
            
            print(f"\n❌ 问题分析:")
            if previous_raise_increment == 0:
                print(f"    🔴 错误: 之前加注增量计算为0！")
                print(f"    🔍 原因: max_previous_raise(${max_previous_raise}) - call_amount(${call_amount}) = 0")
            if your_min_total != raise_action['amount']['min']:
                print(f"    🔴 错误: 我们的计算与PyPokerEngine不符！")
                print(f"    🔍 我们的计算: ${your_min_total}, PyPokerEngine: ${raise_action['amount']['min']}")
    
    print("\n" + "="*60)
    print("🎯 问题根源:")
    print("  1. call_amount计算错误 - 没有正确处理BIGBLIND")
    print("  2. 加注增量计算逻辑有误")
    print("  3. 没有考虑当前需要跟注的金额")

def test_corrected_logic():
    """测试修正后的逻辑"""
    print("\n✅ 测试修正后的逻辑")
    print("="*60)
    
    # 同样的场景，用修正后的逻辑
    round_state = {
        'street': 'preflop',
        'action_histories': {
            'preflop': [
                {'action': 'SMALLBLIND', 'amount': 5, 'uuid': 'player1'},
                {'action': 'BIGBLIND', 'amount': 10, 'uuid': 'player2'},
                {'action': 'CALL', 'amount': 10, 'uuid': 'player3'},
                {'action': 'RAISE', 'amount': 17, 'uuid': 'player1'}
            ]
        }
    }
    
    raise_action = {'amount': {'min': 24, 'max': 1000}}
    
    print(f"💰 加注范围: ${raise_action['amount']['min']} - ${raise_action['amount']['max']}")
    print(f"📋 行动历史: {round_state['action_histories']['preflop']}")
    
    print("\n🔧 修正后的逻辑:")
    
    street = round_state.get('street', 'preflop')
    action_histories = round_state.get('action_histories', {})
    
    if street in action_histories:
        max_previous_raise = 0
        current_bet_level = 0  # 当前需要跟注的金额
        
        for action in action_histories[street]:
            print(f"  📄 处理行动: {action}")
            action_type = action.get('action', '').upper()
            amount = action.get('amount', 0)
            
            if action_type == 'BIGBLIND':
                current_bet_level = max(current_bet_level, amount)
                print(f"    🎯 大盲设置当前下注级别: ${current_bet_level}")
            elif action_type == 'RAISE':
                max_previous_raise = max(max_previous_raise, amount)
                current_bet_level = max(current_bet_level, amount)  # 加注后更新下注级别
                print(f"    🎯 加注到: ${amount}, 当前下注级别: ${current_bet_level}")
            elif action_type == 'CALL':
                current_bet_level = max(current_bet_level, amount)
                print(f"    📞 跟注: ${amount}, 当前下注级别: ${current_bet_level}")
        
        print(f"\n  📊 修正后结果:")
        print(f"    最大之前加注: ${max_previous_raise}")
        print(f"    当前下注级别: ${current_bet_level}")
        
        if max_previous_raise > 0:
            # 正确的加注增量计算
            previous_raise_increment = max_previous_raise - current_bet_level if current_bet_level < max_previous_raise else max_previous_raise
            print(f"    之前加注增量: ${previous_raise_increment}")
            
            # 你的最小加注 = 当前下注级别 + 之前加注增量
            your_min_total = current_bet_level + previous_raise_increment
            print(f"    你的最小总下注: ${your_min_total}")
            print(f"    PyPokerEngine最小加注: ${raise_action['amount']['min']}")
            
            if your_min_total == raise_action['amount']['min']:
                print(f"    ✅ 计算正确！与PyPokerEngine一致")
            else:
                print(f"    ⚠️  仍有差异，需要进一步分析")
                
                # 可能还有其他因素，让我们直接显示正确的信息
                print(f"\n  📋 正确的加注规则显示:")
                print(f"    📏 加注规则: 之前玩家加注${previous_raise_increment}（到${max_previous_raise}）")
                print(f"    📊 你必须至少再加注${previous_raise_increment}（总下注${your_min_total}）")
                print(f"    📊 当前最小加注: ${raise_action['amount']['min']}")

if __name__ == "__main__":
    debug_raise_rules_bug()
    test_corrected_logic()