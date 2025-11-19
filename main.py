#!/usr/bin/env python3
"""
德州扑克 AI 助手 - 主入口
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_assistant.utils.config import config
from poker_assistant.engine.game_controller import GameController


def main():
    """主函数"""
    print("🎰 德州扑克 AI 助手")
    print("="*60)
    
    # 验证配置
    print("正在加载配置...")
    if not config.validate():
        print("\n❌ 配置验证失败，请检查 .env 文件")
        print("💡 提示: 复制 .env.example 为 .env 并填入配置")
        return 1
    
    print("✅ 配置加载成功")
    
    # 显示游戏配置
    game_config = config.get_game_config()
    print(f"\n📋 游戏配置:")
    print(f"  玩家数量: {game_config['player_count']}")
    print(f"  初始筹码: ${game_config['initial_stack']}")
    print(f"  小盲/大盲: ${game_config['small_blind_amount']}/${game_config['small_blind_amount']*2}")
    print(f"  最大回合: {game_config['max_round']}")
    
    # AI 功能状态
    ai_config = config.get_ai_config()
    print(f"\n🤖 AI 功能状态:")
    print(f"  AI思考显示: {'✅ 开启' if ai_config['show_thinking'] else '🔴 关闭'}")
    print(f"  策略建议: {'🔴 未启用 (Phase 2)' if not ai_config['auto_show_advice'] else '✅ 启用'}")
    print(f"  对手分析: {'🔴 未启用 (Phase 2)' if not ai_config['enable_opponent_analysis'] else '✅ 启用'}")
    print(f"  牌面分析: {'🔴 未启用 (Phase 2)' if not ai_config['enable_board_analysis'] else '✅ 启用'}")
    print(f"  对局复盘: {'🔴 未启用 (Phase 2)' if not ai_config['enable_review'] else '✅ 启用'}")
    print(f"  自由提问: {'🔴 未启用 (Phase 2)' if not ai_config['enable_chat'] else '✅ 启用'}")
    
    # API Key 状态
    if config.DEEPSEEK_API_KEY:
        print(f"\n🔑 Deepseek API: ✅ 已配置")
    else:
        print(f"\n🔑 Deepseek API: ⚠️  未配置 (AI 功能将在 Phase 2 中启用)")
    
    print("\n" + "="*60)
    
    # 创建并启动游戏控制器
    try:
        controller = GameController(config)
        controller.start_game()
        return 0
    
    except KeyboardInterrupt:
        print("\n\n👋 感谢游玩！")
        return 0
    
    except Exception as e:
        print(f"\n❌ 启动游戏时出错: {e}")
        if config.DEBUG:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

