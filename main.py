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
    
    # 询问用户是否开启三体人模式
    print(f"\n🛸 三体人模式设置:")
    while True:
        choice = input("是否开启三体人模式(AI明牌)? [y/n]: ").strip().lower()
        if choice in ['y', 'yes', '是']:
            config.set_show_thinking(True)
            print("✅ 三体人模式已开启 - AI将显示其思考过程和手牌")
            break
        elif choice in ['n', 'no', '否', '']:
            config.set_show_thinking(False)
            print("🔴 三体人模式已关闭 - AI思考过程将保持神秘")
            break
        else:
            print("请输入 y/yes/是 或 n/no/否，或直接按回车选择否")
    
    print(f"  三体人模式(AI明牌): {'✅ 开启' if config.get_ai_config()['show_thinking'] else '🔴 关闭'}")
    
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

