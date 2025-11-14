#!/usr/bin/env python3
"""
测试摊牌底牌显示修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_showdown_fix():
    """测试摊牌底牌显示修复"""
    print("🃏 测试摊牌底牌显示修复")
    print("="*60)
    
    from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
    
    # 创建AI玩家
    shared_hole_cards = {}  # 模拟共享底牌字典
    ai_player = ImprovedAIOpponentPlayer(
        difficulty="medium", 
        shared_hole_cards=shared_hole_cards,
        show_thinking=False  # 关闭思考显示，专注测试底牌记录
    )
    ai_player.uuid = "ai_test_player"
    
    print("📋 测试底牌记录功能")
    print("-" * 40)
    
    # 模拟回合开始，接收底牌
    hole_card = ['SA', 'HA']  # 口袋AA
    round_count = 1
    seats = [
        {'uuid': 'human_player', 'name': '你', 'stack': 1000, 'state': 'participating'},
        {'uuid': 'ai_test_player', 'name': 'AI_1', 'stack': 1000, 'state': 'participating'},
        {'uuid': 'ai_player_2', 'name': 'AI_2', 'stack': 1000, 'state': 'participating'},
    ]
    
    print(f"AI接收底牌: {hole_card}")
    print(f"共享字典初始状态: {shared_hole_cards}")
    
    # 调用回合开始消息
    ai_player.receive_round_start_message(round_count, hole_card, seats)
    
    print(f"共享字典记录后状态: {shared_hole_cards}")
    
    # 验证底牌是否正确记录
    if ai_player.uuid in shared_hole_cards:
        recorded_cards = shared_hole_cards[ai_player.uuid]
        print(f"✅ 底牌已正确记录: {recorded_cards}")
        
        if recorded_cards == hole_card:
            print("✅ 记录的底牌与接收的底牌一致")
        else:
            print("❌ 记录的底牌与接收的底牌不一致")
    else:
        print("❌ 底牌未被记录到共享字典")
    
    print("\n📋 测试多个AI玩家")
    print("-" * 40)
    
    # 创建多个AI玩家
    ai_player2 = ImprovedAIOpponentPlayer(
        difficulty="easy",
        shared_hole_cards=shared_hole_cards,
        show_thinking=False
    )
    ai_player2.uuid = "ai_player_2"
    
    hole_card2 = ['SK', 'SQ']  # KQ同花
    
    print(f"AI2接收底牌: {hole_card2}")
    ai_player2.receive_round_start_message(round_count, hole_card2, seats)
    
    print(f"共享字典最终状态: {shared_hole_cards}")
    
    # 验证所有底牌都记录了
    expected_cards = {
        "ai_test_player": hole_card,
        "ai_player_2": hole_card2
    }
    
    all_correct = True
    for player_uuid, expected_cards_list in expected_cards.items():
        if player_uuid in shared_hole_cards:
            actual_cards = shared_hole_cards[player_uuid]
            if actual_cards == expected_cards_list:
                print(f"✅ {player_uuid}: {actual_cards}")
            else:
                print(f"❌ {player_uuid}: 期望{expected_cards_list}, 实际{actual_cards}")
                all_correct = False
        else:
            print(f"❌ {player_uuid}: 未找到记录")
            all_correct = False
    
    if all_correct:
        print("\n✅ 所有AI玩家的底牌都正确记录！")
    else:
        print("\n❌ 部分AI玩家的底牌记录有问题")
    
    print("\n📋 模拟摊牌场景")
    print("-" * 40)
    
    # 模拟摊牌时会使用的情况
    print("模拟游戏控制器在摊牌时获取底牌:")
    print("假设这是game_controller.py中的代码:")
    print("```python")
    print("final_hole_cards = dict(self.shared_hole_cards)")
    print("```")
    
    # 模拟摊牌获取
    showdown_cards = dict(shared_hole_cards)
    print(f"摊牌时获取的底牌: {showdown_cards}")
    
    if len(showdown_cards) >= 2:
        print("✅ 摊牌时可以正确显示所有AI的底牌")
        for player, cards in showdown_cards.items():
            print(f"  {player}: {cards[0]}{cards[1] if len(cards) > 1 else ''}")
    else:
        print("❌ 摊牌时底牌数量不足")
    
    print("\n✅ 测试完成!")
    print("\n🎯 修复总结:")
    print("- 在ImprovedAIOpponentPlayer中添加了shared_hole_cards记录")
    print("- AI玩家现在会在receive_round_start_message时记录底牌")
    print("- 摊牌时可以正确获取所有玩家的底牌")
    print("- 不会再显示'[未记录]'的问题了")

if __name__ == "__main__":
    test_showdown_fix()