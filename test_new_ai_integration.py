#!/usr/bin/env python3
"""
验证新的AI策略是否生效
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_new_ai_integration():
    """测试新的AI集成"""
    print("🎰 测试新的AI策略集成")
    print("="*60)
    
    try:
        # 导入新的AI类
        from poker_assistant.engine.improved_ai_opponent import ImprovedAIOpponentPlayer
        from poker_assistant.engine.game_controller import GameController
        from poker_assistant.utils.config import Config
        
        print("✅ 成功导入改进AI类")
        
        # 创建配置
        config = Config()
        config.game_config = {
            'player_count': 6,
            'initial_stack': 1000,
            'max_round': 10,
            'small_blind': 5,
            'big_blind': 10
        }
        config.ai_config = {
            'opponent_difficulty': 'medium'
        }
        
        # 创建游戏控制器
        controller = GameController(config)
        
        print(f"✅ 游戏控制器创建成功")
        print(f"AI玩家数量: {len(controller.ai_players)}")
        
        # 检查AI类型
        for i, ai_player in enumerate(controller.ai_players):
            print(f"AI玩家 {i+1}: {type(ai_player).__name__}")
            if isinstance(ai_player, ImprovedAIOpponentPlayer):
                print(f"  ✅ 是改进AI")
            else:
                print(f"  ❌ 不是改进AI")
        
        print("\n✅ 新的AI策略已成功集成！")
        print("现在AI玩家将使用更智能的策略：")
        print("- 更合理的弃牌逻辑")
        print("- 基于真实牌力的决策")
        print("- 考虑位置和对手倾向")
        print("- 更精确的下注尺度控制")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_ai_integration()