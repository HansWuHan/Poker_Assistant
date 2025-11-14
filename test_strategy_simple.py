#!/usr/bin/env python3
"""
简化测试 - 对比AI策略逻辑
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def evaluate_hand_simple(hole_card, community_card):
    """原版简单牌力评估"""
    if not hole_card or len(hole_card) < 2:
        return 0.0
    
    ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
            '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    card1_rank = ranks.get(hole_card[0][1], 0)
    card2_rank = ranks.get(hole_card[1][1], 0)
    
    is_pair = (card1_rank == card2_rank)
    is_suited = (hole_card[0][0] == hole_card[1][0])
    
    high_card = max(card1_rank, card2_rank)
    low_card = min(card1_rank, card2_rank)
    
    score = 0.0
    
    if is_pair:
        score = 0.5 + (card1_rank / 28.0)
    else:
        score = (high_card + low_card) / 28.0
        
        if is_suited:
            score += 0.1
        
        if abs(card1_rank - card2_rank) <= 3:
            score += 0.05
        
        if high_card >= 12:
            score += 0.1
    
    return min(1.0, score)

def original_easy_strategy(hole_card, community_card, call_amount, pot, raise_min, raise_max):
    """原版简单策略"""
    if not community_card:
        street = 'preflop'
    else:
        street = 'flop' if len(community_card) == 3 else ('turn' if len(community_card) == 4 else 'river')
    
    hand_strength = evaluate_hand_simple(hole_card, community_card)
    
    import random
    
    if street == 'preflop':
        if hand_strength >= 0.7:
            if random.random() < 0.7 and raise_min != -1:
                return 'RAISE', raise_min
            else:
                return 'CALL', call_amount
        elif hand_strength >= 0.4:
            return 'CALL', call_amount
        else:
            if random.random() < 0.8:
                return 'FOLD', 0
            else:
                return 'CALL', call_amount
    else:
        if hand_strength >= 0.6:
            if random.random() < 0.5 and raise_min != -1:
                return 'RAISE', raise_min
            else:
                return 'CALL', call_amount
        elif hand_strength >= 0.3:
            return 'CALL', call_amount
        else:
            if call_amount == 0:
                return 'CALL', 0
            else:
                return 'FOLD', 0

def improved_easy_strategy(hole_card, community_card, call_amount, pot, raise_min, raise_max):
    """改进版简单策略"""
    import random
    
    if not community_card:
        street = 'preflop'
    else:
        street = 'flop' if len(community_card) == 3 else ('turn' if len(community_card) == 4 else 'river')
    
    hand_strength = evaluate_hand_simple(hole_card, community_card)
    
    # 位置因子（简化版）
    position_factor = 1.0
    adjusted_strength = hand_strength * position_factor
    
    if street == 'preflop':
        if adjusted_strength >= 0.8:
            if random.random() < 0.8 and raise_min != -1:
                amount = max(raise_min, int(pot * 0.7))
                return 'RAISE', amount
            return 'CALL', call_amount
        elif adjusted_strength >= 0.6:
            if call_amount <= pot * 0.1:
                return 'CALL', call_amount
            else:
                return 'FOLD', 0
        else:
            if call_amount == 0:
                return 'CALL', 0
            return 'FOLD', 0
    else:
        if adjusted_strength >= 0.7:
            if random.random() < 0.7 and raise_min != -1:
                bet_size = int(pot * random.uniform(0.5, 0.8))
                amount = max(raise_min, bet_size)
                return 'RAISE', amount
            return 'CALL', call_amount
        elif adjusted_strength >= 0.4:
            pot_odds = call_amount / (pot + call_amount) if (pot + call_amount) > 0 else 0
            if pot_odds <= 0.25 and adjusted_strength >= 0.3:
                return 'CALL', call_amount
            else:
                return 'FOLD', 0
        else:
            if call_amount == 0:
                return 'CALL', 0
            if random.random() < 0.05 and raise_min != -1:
                amount = min(raise_max, int(pot * 0.5))
                return 'RAISE', amount
            return 'FOLD', 0

def test_strategy_comparison():
    """测试策略对比"""
    print("🎰 AI策略对比测试")
    print("="*60)
    
    # 测试场景
    test_cases = [
        {
            "name": "翻牌前 - 中等牌力 (KQo)",
            "hole_card": ['SQ', 'HK'],
            "community_card": [],
            "call_amount": 30,
            "pot": 60,
            "raise_min": 60,
            "raise_max": 1000
        },
        {
            "name": "翻牌后 - 顶对弱踢脚",
            "hole_card": ['HA', 'D9'],
            "community_card": ['S9', 'H7', 'C2'],
            "call_amount": 50,
            "pot": 150,
            "raise_min": 100,
            "raise_max": 950
        },
        {
            "name": "翻牌后 - 空气牌",
            "hole_card": ['S2', 'H7'],
            "community_card": ['HA', 'HK', 'DQ'],
            "call_amount": 40,
            "pot": 120,
            "raise_min": 80,
            "raise_max": 950
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 {case['name']}")
        print("-" * 50)
        
        # 测试原版策略
        original_action, original_amount = original_easy_strategy(
            case['hole_card'], case['community_card'],
            case['call_amount'], case['pot'],
            case['raise_min'], case['raise_max']
        )
        
        # 测试改进版策略
        improved_action, improved_amount = improved_easy_strategy(
            case['hole_card'], case['community_card'],
            case['call_amount'], case['pot'],
            case['raise_min'], case['raise_max']
        )
        
        print(f"手牌: {case['hole_card']}")
        if case['community_card']:
            print(f"公共牌: {case['community_card']}")
        print(f"底池: ${case['pot']}, 需要跟注: ${case['call_amount']}")
        print(f"加注范围: ${case['raise_min']} - ${case['raise_max']}")
        print()
        print(f"原版AI: {original_action} ${original_amount}")
        print(f"改进AI: {improved_action} ${improved_amount}")
        
        if original_action != improved_action:
            print(f"✅ 行为改变: {original_action} → {improved_action}")
        elif original_amount != improved_amount:
            print(f"✅ 金额改变: ${original_amount} → ${improved_amount}")
        else:
            print("➡️  行为相同")
        print()
    
    print("✅ 测试完成!")
    print("\n📊 改进总结:")
    print("- 更严格的起手牌要求")
    print("- 考虑代价和赔率")
    print("- 更合理的弃牌逻辑")
    print("- 更低的诈唬频率")

if __name__ == "__main__":
    test_strategy_comparison()