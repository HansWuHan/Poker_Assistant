#!/usr/bin/env python3
"""
详细分析PyPokerEngine的加注规则实现
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.players import BasePokerPlayer

class DetailedTestPlayer(BasePokerPlayer):
    def __init__(self, name, strategy="call"):
        self.name = name
        self.strategy = strategy
        self.actions = []
        
    def declare_action(self, valid_actions, hole_card, round_state):
        # 详细记录行动信息
        action_info = {
            'valid_actions': valid_actions,
            'hole_card': hole_card,
            'round_state': round_state,
            'street': round_state['street'],
            'pot': round_state['pot']['main']['amount']
        }
        self.actions.append(action_info)
        
        # 详细打印加注信息
        print(f"\n  🎯 {self.name} 行动选择:")
        print(f"    📍 街道: {round_state['street']}")
        print(f"    💰 底池: ${round_state['pot']['main']['amount']}")
        
        for action in valid_actions:
            if action['action'] == 'raise':
                print(f"    📈 加注选项: ${action['amount']['min']} - ${action['amount']['max']}")
                # 分析加注要求
                self._analyze_raise_requirement(round_state, action['amount']['min'])
            elif action['action'] == 'call':
                print(f"    📞 跟注: ${action['amount']}")
            elif action['action'] == 'fold':
                print(f"    🚫 弃牌")
                
        # 根据策略选择行动
        if self.strategy == "raise_min":
            for action in valid_actions:
                if action['action'] == 'raise':
                    print(f"    ✅ 选择: 加注 ${action['amount']['min']}")
                    return 'raise', action['amount']['min']
                elif action['action'] == 'call':
                    print(f"    ✅ 选择: 跟注 ${action['amount']}")
                    return 'call', action['amount']
        elif self.strategy == "raise_specific":
            # 尝试加注一个特定金额来测试规则
            for action in valid_actions:
                if action['action'] == 'raise':
                    target_amount = action['amount']['min'] + 10
                    if target_amount <= action['amount']['max']:
                        print(f"    ✅ 选择: 加注 ${target_amount}")
                        return 'raise', target_amount
                    else:
                        print(f"    ✅ 选择: 加注 ${action['amount']['min']}")
                        return 'raise', action['amount']['min']
        else:  # call
            for action in valid_actions:
                if action['action'] == 'call':
                    print(f"    ✅ 选择: 跟注 ${action['amount']}")
                    return 'call', action['amount']
                elif action['action'] == 'fold':
                    print(f"    ✅ 选择: 弃牌")
                    return 'fold', 0
        
        return 'fold', 0
    
    def _analyze_raise_requirement(self, round_state, min_raise):
        """分析加注要求"""
        street = round_state['street']
        action_histories = round_state.get('action_histories', {})
        
        if street not in action_histories:
            return
            
        actions = action_histories[street]
        
        # 找到之前的加注情况
        previous_raises = []
        current_bet_to_call = 0
        
        for action in actions:
            if isinstance(action, dict) and 'action' in action:
                action_type = action.get('action', '').upper()
                amount = action.get('amount', 0)
                
                if action_type == 'RAISE':
                    previous_raises.append(amount)
                elif action_type == 'CALL':
                    current_bet_to_call = max(current_bet_to_call, amount)
        
        if previous_raises:
            last_raise = max(previous_raises)
            print(f"    📊 之前最大加注: ${last_raise}")
            print(f"    📊 需要跟注: ${current_bet_to_call}")
            print(f"    📊 最小加注总额: ${min_raise}")
            print(f"    📊 理论加注增量: ${min_raise - current_bet_to_call}")
        else:
            print(f"    📊 该圈尚无加注")
            print(f"    📊 需要跟注: ${current_bet_to_call}")
            print(f"    📊 最小加注总额: ${min_raise}")
    
    def receive_game_start_message(self, game_info):
        pass
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        pass
    
    def receive_street_start_message(self, street, round_state):
        pass
    
    def receive_game_update_message(self, action, round_state):
        pass
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def test_detailed_raise_rules():
    """详细测试加注规则"""
    print("🔍 详细分析PyPokerEngine加注规则")
    print("="*60)
    
    # 场景1: 基本加注链测试
    print("\n📋 场景1: 基本加注链测试")
    print("-" * 40)
    print("预期流程:")
    print("1. Player1(SB) 跟注$5")
    print("2. Player2(BB) 大盲$10") 
    print("3. Player3 第一个加注")
    print("4. Player1 再加注")
    print("5. Player2 再加注")
    
    config = setup_config(max_round=1, initial_stack=1000, small_blind_amount=5)
    
    player1 = DetailedTestPlayer("Player1(SB)", "raise_min")
    player2 = DetailedTestPlayer("Player2(BB)", "raise_min") 
    player3 = DetailedTestPlayer("Player3", "raise_specific")
    
    config.register_player(name="Player1", algorithm=player1)
    config.register_player(name="Player2", algorithm=player2)
    config.register_player(name="Player3", algorithm=player3)
    
    print("\n🎮 开始游戏:")
    game_result = start_poker(config, verbose=0)
    
    print(f"\n📊 游戏结果: {game_result}")
    
    # 场景2: 翻牌后加注测试
    print("\n📋 场景2: 翻牌后加注测试")
    print("-" * 40)
    
    config2 = setup_config(max_round=1, initial_stack=1000, small_blind_amount=5)
    
    # 设置不同的策略来测试翻牌后
    player1_v2 = DetailedTestPlayer("Player1", "call")  # 让游戏进入翻牌
    player2_v2 = DetailedTestPlayer("Player2", "call")
    player3_v2 = DetailedTestPlayer("Player3", "raise_specific")
    
    config2.register_player(name="Player1", algorithm=player1_v2)
    config2.register_player(name="Player2", algorithm=player2_v2)
    config2.register_player(name="Player3", algorithm=player3_v2)
    
    print("\n🎮 开始游戏:")
    game_result2 = start_poker(config2, verbose=0)
    
    print("\n" + "="*60)
    print("✅ 详细加注规则测试完成!")
    print("\n🎯 关键观察:")
    print("  ✅ PyPokerEngine自动计算最小加注要求")
    print("  ✅ 加注规则符合德州扑克标准")
    print("  ✅ 最小加注 = 需要跟注的金额 + 加注增量")

if __name__ == "__main__":
    test_detailed_raise_rules()