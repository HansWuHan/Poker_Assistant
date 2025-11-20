#!/usr/bin/env python3
"""
检查实际的牌格式和修复格式化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.gto_strategy.gto_core import GTOCore

def debug_card_format():
    """调试牌的格式"""
    print("🔍 调试牌的格式和格式化逻辑")
    print("="*60)
    
    gto_core = GTOCore()
    
    # 模拟你观察到的实际牌
    test_cases = [
        # 你观察到的格式
        ['10D', '8S'],   # 10♦ 8♠
        ['2C', 'KD'],    # 2♣ K♦
        ['4S', 'AD'],    # 4♠ A♦
        
        # 系统内部可能使用的格式
        ['TD', '8S'],    # T♦ 8♠
        ['C2', 'DK'],    # ♣2 ♦K
        ['S4', 'DA'],    # ♠4 ♦A
    ]
    
    for hole_cards in test_cases:
        print(f"\n输入: {hole_cards}")
        
        # 手动解析看看
        card1, card2 = hole_cards[0], hole_cards[1]
        print(f"  card1: '{card1}' (长度{len(card1)})")
        print(f"  card2: '{card2}' (长度{len(card2)})")
        
        # 检查格式
        if len(card1) == 2 and len(card2) == 2:
            # 标准格式：rank + suit
            rank1, suit1 = card1[0], card1[1]
            rank2, suit2 = card2[0], card2[1]
            print(f"  解析1: rank1='{rank1}' suit1='{suit1}'")
            print(f"  解析1: rank2='{rank2}' suit2='{suit2}'")
        elif len(card1) == 3 or len(card2) == 3:
            # 可能有10
            if len(card1) == 3:
                if card1.startswith('10'):
                    rank1, suit1 = 'T', card1[2]
                else:
                    rank1, suit1 = card1[1], card1[0]  # 假设是suit+rank
            else:
                rank1, suit1 = card1[0], card1[1]
                
            if len(card2) == 3:
                if card2.startswith('10'):
                    rank2, suit2 = 'T', card2[2]
                else:
                    rank2, suit2 = card2[1], card2[0]
            else:
                rank2, suit2 = card2[0], card2[1]
            
            print(f"  解析2: rank1='{rank1}' suit1='{suit1}'")
            print(f"  解析2: rank2='{rank2}' suit2='{suit2}'")
        
        # 测试格式化
        try:
            formatted = gto_core._format_hand(hole_cards)
            print(f"  格式化结果: '{formatted}'")
            
            # 检查是否在范围内
            position_range = gto_core.preflop_ranges.get('BTN', {})
            defend_range = position_range.get('defend', [])
            in_range = formatted in defend_range
            print(f"  在防守范围内: {in_range}")
            
        except Exception as e:
            print(f"  格式化错误: {e}")

def check_actual_ranges():
    """检查实际的防守范围"""
    print(f"\n🔍 检查BTN位置的防守范围")
    print("-" * 40)
    
    gto_core = GTOCore()
    position_range = gto_core.preflop_ranges.get('BTN', {})
    defend_range = position_range.get('defend', position_range.get('call_3bet', []))
    
    print(f"防守范围 ({len(defend_range)} 个手牌):")
    
    # 显示部分范围
    for i, hand in enumerate(defend_range[:20]):
        print(f"  {hand}")
    
    if len(defend_range) > 20:
        print(f"  ... 还有 {len(defend_range) - 20} 个")
    
    # 检查关键手牌
    test_hands = ['K2o', 'A4o', 'T8o', '98s', 'AA', 'KK']
    for hand in test_hands:
        in_range = hand in defend_range
        print(f"  {hand}: {'✅ 在范围内' if in_range else '❌ 不在范围内'}")

if __name__ == "__main__":
    debug_card_format()
    check_actual_ranges()