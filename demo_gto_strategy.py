#!/usr/bin/env python3
"""
GTO策略演示脚本
演示GTO策略在实际扑克情境中的应用
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_assistant.gto_strategy import GTOAdvisor
from poker_assistant.gto_strategy.gto_core import GTOSituation


def demo_gto_strategy():
    """演示GTO策略应用"""
    print("🎯 GTO策略演示")
    print("="*50)
    
    gto_advisor = GTOAdvisor()
    
    # 演示1: 翻牌前不同位置的GTO策略
    print("\n📊 演示1: 翻牌前不同位置的GTO策略")
    print("-"*40)
    
    positions = ['UTG', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB']
    test_hands = [
        ['SA', 'HA'],      # AA
        ['SK', 'SQ'],      # KQs
        ['S7', 'H2'],      # 72o
        ['S5', 'S4'],      # 54s
    ]
    
    for hand in test_hands:
        hand_desc = f"{hand[0][1]}{hand[1][1]} {'s' if hand[0][0] == hand[1][0] else 'o'}"
        print(f"\n🎴 手牌: {hand_desc}")
        
        for pos in positions:
            situation = GTOSituation(
                street='preflop',
                position=pos,
                stack_size=1000,
                pot_size=15,
                community_cards=[],
                hole_cards=hand,
                opponent_actions=[],
                active_opponents=1
            )
            
            advice = gto_advisor.get_gto_advice(
                hole_cards=hand,
                community_cards=[],
                street='preflop',
                position=pos,
                pot_size=15,
                stack_size=1000,
                call_amount=0,
                valid_actions=[
                    {'action': 'fold', 'amount': 0},
                    {'action': 'call', 'amount': 0},
                    {'action': 'raise', 'amount': {'min': 20, 'max': 100}}
                ],
                opponent_actions=[],
                active_opponents=['SB', 'BB']
            )
            
            print(f"  {pos:4}: {advice['action']:6} ${advice['amount']:<3} "
                  f"(置信度: {advice['confidence']*100:.0f}%)")
    
    # 演示2: 翻牌后不同牌面的GTO策略
    print("\n\n📊 演示2: 翻牌后不同牌面的GTO策略")
    print("-"*40)
    
    board_textures = [
        (['SA', 'SK', 'SQ'], "A-K-Q 彩虹面"),
        (['S9', 'H8', 'D7'], "9-8-7 连牌面"),
        (['S2', 'H3', 'D9'], "2-3-9 干燥面"),
        (['SK', 'HK', 'DQ'], "K-K-Q 对子面"),
    ]
    
    hero_hand = ['SA', 'HA']  # AA
    
    for board, description in board_textures:
        print(f"\n🎴 牌面: {description}")
        print(f"  具体牌: {' '.join(board)}")
        
        advice = gto_advisor.get_gto_advice(
            hole_cards=hero_hand,
            community_cards=board,
            street='flop',
            position='BTN',
            pot_size=50,
            stack_size=950,
            call_amount=0,
            valid_actions=[
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 0},
                {'action': 'raise', 'amount': {'min': 25, 'max': 150}}
            ],
            opponent_actions=[{'action': 'check'}],
            active_opponents=['SB', 'BB']
        )
        
        print(f"  GTO建议: {advice['action']} ${advice['amount']}")
        print(f"  理由: {advice['reasoning'][:150]}...")
    
    # 演示3: 面对对手行动时的GTO应对
    print("\n\n📊 演示3: 面对对手行动时的GTO应对")
    print("-"*40)
    
    scenarios = [
        ([], "无人行动"),
        ([{'action': 'raise', 'amount': 30}], "对手加注到$30"),
        ([{'action': 'bet', 'amount': 25}], "对手下注$25"),
        ([{'action': 'check'}], "对手过牌"),
    ]
    
    hero_hand = ['SK', 'SQ']  # KQs
    board = ['S9', 'H8', 'D7']  # 9-8-7连牌面
    
    for opponent_actions, description in scenarios:
        print(f"\n🎯 情境: {description}")
        
        call_amount = 30 if any(a['action'] == 'raise' for a in opponent_actions) else (
            25 if any(a['action'] == 'bet' for a in opponent_actions) else 0
        )
        
        advice = gto_advisor.get_gto_advice(
            hole_cards=hero_hand,
            community_cards=board,
            street='flop',
            position='CO',
            pot_size=50,
            stack_size=950,
            call_amount=call_amount,
            valid_actions=[
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': call_amount},
                {'action': 'raise', 'amount': {'min': 75, 'max': 200}}
            ],
            opponent_actions=opponent_actions,
            active_opponents=['BTN']
        )
        
        print(f"  GTO建议: {advice['action']} ${advice['amount']}")
        if 'frequencies' in advice:
            print(f"  频率分布: {advice['frequencies']}")
        else:
            print(f"  置信度: {advice.get('confidence', 0)*100:.0f}%")


def demo_gto_vs_exploitative():
    """演示GTO与剥削策略的对比"""
    print("\n\n⚖️  GTO vs 剥削策略对比")
    print("="*50)
    
    gto_advisor = GTOAdvisor()
    
    # 创建一个对手很激进的情境
    print("\n🎯 情境: 对手非常激进，频繁加注")
    
    situation = GTOSituation(
        street='flop',
        position='BB',
        stack_size=800,
        pot_size=100,
        community_cards=['S2', 'H3', 'DK'],  # 2-3-K彩虹面
        hole_cards=['S9', 'H9'],  # 99
        opponent_actions=[
            {'action': 'raise', 'amount': 40},
            {'action': 'bet', 'amount': 60}
        ],
        active_opponents=1
    )
    
    comparison = gto_advisor.get_gto_vs_exploitative_comparison(situation)
    
    print(f"\n📊 策略对比:")
    print(f"  GTO策略:      {comparison['gto_action']['action']} "
          f"${comparison['gto_action']['amount']}")
    print(f"  剥削策略:     {comparison['exploitative_action']['action']} "
          f"${comparison['exploitative_action']['amount']}")
    print(f"  平衡性得分:   GTO={comparison['gto_action']['balance_score']:.2f}, "
          f"EXP={comparison['exploitative_action']['balance_score']:.2f}")
    print(f"  可剥削性:     GTO={comparison['gto_action']['exploitability']:.2f}, "
          f"EXP={comparison['exploitative_action']['exploitability']:.2f}")
    print(f"  推荐策略:     {comparison['recommendation']}")


def demo_mixed_strategy():
    """演示混合策略的应用"""
    print("\n\n🎲 混合策略演示")
    print("="*50)
    
    gto_advisor = GTOAdvisor()
    
    # 设置不同的权重
    weights = [
        (1.0, 0.0, "纯GTO策略"),
        (0.7, 0.3, "GTO偏向混合"),
        (0.5, 0.5, "平衡混合"),
        (0.3, 0.7, "剥削偏向混合"),
        (0.0, 1.0, "纯剥削策略"),
    ]
    
    hero_hand = ['SA', 'HK']  # AKo
    board = ['SQ', 'HJ', 'DT']  # Q-J-T彩虹面
    
    print(f"\n🎴 手牌: AKo")
    print(f"  牌面: Q-J-T彩虹面")
    print(f"  位置: BTN")
    print(f"  情境: 对手过牌")
    
    for gto_weight, exp_weight, description in weights:
        gto_advisor.update_weights(gto_weight, exp_weight)
        
        advice = gto_advisor.get_gto_advice(
            hole_cards=hero_hand,
            community_cards=board,
            street='flop',
            position='BTN',
            pot_size=80,
            stack_size=900,
            call_amount=0,
            valid_actions=[
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 0},
                {'action': 'raise', 'amount': {'min': 40, 'max': 200}}
            ],
            opponent_actions=[{'action': 'check'}],
            active_opponents=['SB', 'BB']
        )
        
        print(f"\n{description} (GTO:{gto_weight*100:.0f}%/EXP:{exp_weight*100:.0f}%):")
        print(f"  建议: {advice['action']} ${advice['amount']}")
        print(f"  置信度: {advice['confidence']*100:.0f}%")


def main():
    """主演示函数"""
    print("🚀 GTO策略演示开始")
    print("="*60)
    
    try:
        # 运行演示
        demo_gto_strategy()
        demo_gto_vs_exploitative()
        demo_mixed_strategy()
        
        print("\n\n🎉 GTO策略演示完成！")
        print("\n💡 总结:")
        print("  • GTO策略提供理论最优的决策框架")
        print("  • 可以根据对手特点调整GTO与剥削策略的权重")
        print("  • 混合策略能够平衡理论最优和实际剥削")
        print("  • GTO策略特别适合未知对手或多变环境")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())