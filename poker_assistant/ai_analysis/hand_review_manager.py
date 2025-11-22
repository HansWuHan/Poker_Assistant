"""
手牌复盘管理器
负责处理每局结束后的AI复盘分析
"""
import time
import sys
from typing import Dict, List, Any, Optional

from poker_assistant.ai_analysis.review_analyzer import ReviewAnalyzer
from poker_assistant.utils.card_utils import format_cards


class HandReviewManager:
    """手牌复盘管理器 - 独立处理复盘功能"""
    
    def __init__(self, review_analyzer: Optional[ReviewAnalyzer] = None):
        """
        初始化复盘管理器
        
        Args:
            review_analyzer: 复盘分析器实例
        """
        self.review_analyzer = review_analyzer or ReviewAnalyzer()
    
    def perform_review(self, round_state: dict, winners: list, hand_info: list, 
                      final_hole_cards: dict, human_player_uuid: str) -> Optional[str]:
        """
        执行手牌复盘分析
        
        Args:
            round_state: 回合状态
            winners: 赢家信息
            hand_info: 手牌信息
            final_hole_cards: 最终玩家底牌
            human_player_uuid: 人类玩家UUID
            
        Returns:
            复盘分析文本，如果失败返回None
        """
        try:
            # 显示加载动画
            self._show_loading_animation()
            
            # 获取人类玩家的信息
            human_hole_cards = final_hole_cards.get(human_player_uuid, [])
            
            # 获取其他信息
            community_cards = round_state.get('community_card', [])
            action_history = self._extract_action_history(round_state)
            final_pot = round_state.get('pot', {}).get('main', {}).get('amount', 0)
            round_count = round_state.get('round_count', 0)
            
            # 生成复盘分析
            review_text = self.review_analyzer.generate_review(
                round_count=round_count,
                hole_cards=human_hole_cards,
                community_cards=community_cards,
                action_history=action_history,
                winners=winners,
                hand_info=hand_info,
                final_pot=final_pot
            )
            
            # 清除加载提示
            sys.stdout.write("\r" + " "*60 + "\r")
            sys.stdout.flush()
            
            return review_text
            
        except Exception as e:
            # 清除加载提示
            sys.stdout.write("\r" + " "*60 + "\r")
            sys.stdout.flush()
            print(f"复盘分析失败: {e}")
            return None

    def _show_loading_animation(self):
        """显示复盘加载动画"""
        animation_chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        
        for i in range(8):  # 显示8个动画帧
            char = animation_chars[i % len(animation_chars)]
            sys.stdout.write(f"\r{char} AI正在深度分析这手牌...")
            sys.stdout.flush()
            time.sleep(1)  # 每帧150ms
    
    def _extract_action_history(self, round_state: dict) -> list:
        """
        从回合状态中提取行动历史
        
        Args:
            round_state: 回合状态
            
        Returns:
            格式化的行动历史列表
        """
        action_history = []
        
        # 从行动历史中解析
        action_histories = round_state.get('action_histories', {})
        
        for street, actions in action_histories.items():
            if actions:  # 确保有行动
                for action in actions:
                    if isinstance(action, dict):
                        player_name = "未知"
                        # 尝试从座位信息中找到玩家名字
                        for seat in round_state.get('seats', []):
                            if seat.get('uuid') == action.get('uuid'):
                                player_name = seat.get('name', '未知')
                                break
                        
                        action_history.append({
                            'street': street,
                            'player_name': player_name,
                            'action': action.get('action', ''),
                            'amount': action.get('amount', 0)
                        })
        
        return action_history
    
    def format_review_output(self, review_text: str, round_count: int, 
                           hole_cards: list, community_cards: list, winners: list) -> str:
        """
        格式化复盘输出
        
        Args:
            review_text: 复盘分析文本
            round_count: 回合数
            hole_cards: 玩家手牌
            community_cards: 公共牌
            winners: 赢家信息
            
        Returns:
            格式化后的复盘报告
        """
        # 构建牌局信息
        game_info = []
        
        if hole_cards:
            formatted_hole_cards = format_cards(hole_cards)
            game_info.append(f"你的手牌: {formatted_hole_cards}")
        
        if community_cards:
            formatted_community = format_cards(community_cards)
            game_info.append(f"公共牌: {formatted_community}")
        
        if winners:
            winner_names = [w.get('name', '未知') for w in winners]
            game_info.append(f"赢家: {', '.join(winner_names)}")
        
        # 构建完整的复盘报告
        output_lines = []
        output_lines.append("\n" + "="*60)
        output_lines.append(f"🤖 AI 复盘分析 - 第 {round_count} 局")
        output_lines.append("="*60)
        
        if game_info:
            output_lines.extend(game_info)
            output_lines.append("")
        
        output_lines.append(review_text)
        output_lines.append("="*60)
        
        return "\n".join(output_lines)