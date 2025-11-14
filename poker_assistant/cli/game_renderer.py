"""
游戏渲染器模块
使用 Rich 库渲染游戏界面
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.box import ROUNDED, HEAVY, DOUBLE
from typing import List, Dict, Any, Optional
import os

from poker_assistant.utils.card_utils import (
    format_card, format_cards, get_card_color,
    format_action, format_chips, get_street_name
)


class GameRenderer:
    """游戏渲染器 - 使用 Rich 美化输出"""
    
    def __init__(self):
        self.console = Console()
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def render_welcome(self):
        """渲染欢迎界面"""
        self.clear_screen()
        
        welcome_text = """
    ♠ ♥ ♦ ♣  德州扑克 AI 助手  ♠ ♥ ♦ ♣
        
    欢迎来到 AI 驱动的德州扑克练习平台
    
    在这里你将：
    • 与 5 个 AI 对手进行 6 人桌对局
    • 获得实时的 AI 策略建议
    • 随时向 AI 提问学习扑克知识
    
    祝你好运！🎰
        """
        
        panel = Panel(
            welcome_text,
            title="🎮 Poker AI Assistant",
            border_style="green",
            box=DOUBLE
        )
        self.console.print(panel)
        self.console.print()
    
    def render_game_start(self, game_info: Dict[str, Any]):
        """渲染游戏开始信息"""
        self.console.print("\n" + "="*60)
        self.console.print("🎮 游戏开始！", style="bold green")
        self.console.print(f"玩家数量: {game_info['player_num']}")
        self.console.print(f"初始筹码: ${game_info['rule']['initial_stack']}")
        self.console.print(f"小盲/大盲: ${game_info['rule']['small_blind_amount']}/${game_info['rule']['small_blind_amount']*2}")
        self.console.print("="*60 + "\n")
    
    def render_round_start(self, round_count: int, hole_card: List[str], 
                          seats: List[Dict], dealer_btn: int):
        """渲染回合开始"""
        self.clear_screen()
        
        # 标题
        title = f"🎰 第 {round_count} 局 - 翻牌前"
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print(title.center(60), style="bold cyan")
        self.console.print("="*60, style="cyan")
        
        # 手牌
        self._render_hole_cards(hole_card)
        
        # 玩家信息
        self._render_players_info(seats, dealer_btn)
        
        self.console.print()
    
    def render_street_start(self, street: str, community_cards: List[str], 
                           pot_size: int):
        """渲染街道开始"""
        self.console.print("\n" + "-"*60, style="yellow")
        self.console.print(f"🎴 {get_street_name(street)}", style="bold yellow")
        
        # 公共牌
        if community_cards:
            self._render_community_cards(community_cards)
        
        # 底池
        self.console.print(f"💰 底池: {format_chips(pot_size)}", style="green")
        self.console.print("-"*60, style="yellow")
    
    def render_player_action(self, player_name: str, action: str, 
                            amount: int, is_human: bool = False, 
                            round_state: Dict = None, player_uuid: str = None):
        """渲染玩家行动"""
        action_text = format_action(action, amount)
        
        if is_human:
            style = "bold green"
            icon = "👤"
        else:
            style = "white"
            icon = "🤖"
        
        # 获取额外信息
        extra_info = []
        
        if round_state and player_uuid:
            # 获取位置信息
            position = self._get_player_position_display(player_uuid, round_state)
            if position:
                extra_info.append(f"[{position}]")
            
            # 获取剩余筹码
            stack = self._get_player_stack(player_uuid, round_state)
            if stack is not None:
                extra_info.append(f"剩余:${stack}")
            
            # 加注时计算与底池的比例
            if action.lower() == 'raise' and amount > 0:
                pot_size = round_state.get('pot', {}).get('main', {}).get('amount', 0)
                if pot_size > 0:
                    ratio = int((amount / pot_size) * 100)
                    extra_info.append(f"底池:{ratio}%")
        
        # 构建完整信息
        if extra_info:
            info_text = " ".join(extra_info)
            self.console.print(f"{icon} {player_name}: {action_text} {info_text}", style=style)
        else:
            self.console.print(f"{icon} {player_name}: {action_text}", style=style)
    
    def _get_player_position_display(self, player_uuid: str, round_state: Dict) -> str:
        """获取玩家位置显示"""
        seats = round_state.get('seats', [])
        dealer_btn = round_state.get('dealer_btn', 0)
        
        for idx, seat in enumerate(seats):
            if seat.get('uuid') == player_uuid:
                if seat.get('stack', 0) <= 0:
                    return ""
                
                # 计算位置
                if idx == dealer_btn:
                    return "BTN"
                else:
                    # 计算相对位置
                    active_seats = [i for i, s in enumerate(seats) if s.get('stack', 0) > 0]
                    if len(active_seats) >= 2:
                        try:
                            dealer_idx = active_seats.index(dealer_btn)
                            current_idx = active_seats.index(idx)
                            relative_pos = (current_idx - dealer_idx) % len(active_seats)
                            if relative_pos == 1:
                                return "SB"
                            elif relative_pos == 2:
                                return "BB"
                        except ValueError:
                            pass
                break
        
        return ""
    
    def _get_player_stack(self, player_uuid: str, round_state: Dict) -> int:
        """获取玩家剩余筹码"""
        seats = round_state.get('seats', [])
        for seat in seats:
            if seat.get('uuid') == player_uuid:
                return seat.get('stack', 0)
        return 0
    
    def render_round_result(self, winners: List[Dict], hand_info: List[Dict], 
                           round_state: Dict, initial_stacks: Dict[str, int] = None,
                           player_hole_cards: Dict[str, List[str]] = None):
        """
        渲染回合结果
        
        Args:
            winners: 赢家列表
            hand_info: 手牌信息
            round_state: 回合状态
            initial_stacks: 本局开始时的筹码（用于计算赢得金额）
            player_hole_cards: 玩家底牌映射 {uuid: [card1, card2]}
        """
        self.console.print("\n" + "="*60, style="magenta")
        self.console.print("🏆 本局结果", style="bold magenta")
        self.console.print("="*60, style="magenta")
        
        # 显示底池
        pot_amount = round_state.get('pot', {}).get('main', {}).get('amount', 0)
        self.console.print(f"\n💰 底池: {format_chips(pot_amount)}", style="bold yellow")
        
        # 显示公共牌
        community_cards = round_state.get('community_card', [])
        if community_cards and len(community_cards) > 0:
            self.console.print("\n🎴 公共牌:")
            self._render_community_cards(community_cards)
        
        # 创建获胜者UUID集合（用于标注）
        winner_uuids = {w['uuid'] for w in winners}
        
        # 显示所有玩家的手牌（如果到了摊牌）
        if hand_info and len(hand_info) > 0:
            self.console.print("\n🃏 摊牌阶段 - 玩家手牌:", style="bold cyan")
            
            for info in hand_info:
                uuid = info['uuid']
                
                # 找到玩家名字
                player_name = "未知"
                for seat in round_state['seats']:
                    if seat['uuid'] == uuid:
                        player_name = seat['name']
                        break
                
                # 检查是否是获胜者
                is_winner = uuid in winner_uuids
                
                # 获取玩家底牌
                hole_cards = player_hole_cards.get(uuid, []) if player_hole_cards else []
                
                # 显示手牌
                self._render_showdown_hand(player_name, info, hole_cards, is_winner)
        
        # 显示赢家和赢得金额
        self.console.print("\n🎉 赢家:", style="bold yellow")
        for winner in winners:
            uuid = winner['uuid']
            current_stack = winner['stack']
            
            # 找到玩家名字
            player_name = "未知"
            for seat in round_state['seats']:
                if seat['uuid'] == uuid:
                    player_name = seat['name']
                    break
            
            # 计算本局赢得的金额
            if initial_stacks and uuid in initial_stacks:
                prize = current_stack - initial_stacks[uuid]
            else:
                # 如果没有初始筹码数据，就显示总筹码
                prize = current_stack
            
            # 显示信息
            if player_name == "你":
                style = "bold green"
                icon = "👤"
            else:
                style = "bold yellow"
                icon = "🤖"
            
            self.console.print(
                f"  {icon} {player_name} 赢得 {format_chips(prize)} (总筹码: {format_chips(current_stack)})", 
                style=style
            )
        
        # 显示当前所有玩家筹码
        self.console.print("\n💵 筹码状态:", style="bold")
        for seat in round_state['seats']:
            name = seat['name']
            stack = seat['stack']
            
            # 计算变化
            change_str = ""
            if initial_stacks and seat['uuid'] in initial_stacks:
                initial = initial_stacks[seat['uuid']]
                change = stack - initial
                if change > 0:
                    change_str = f" [green](+{change})[/green]"
                elif change < 0:
                    change_str = f" [red]({change})[/red]"
            
            # 为人类玩家添加高亮
            if name == "你":
                self.console.print(f"  👤 {name}: {format_chips(stack)}{change_str}", 
                                 style="bold green")
            else:
                self.console.print(f"  🤖 {name}: {format_chips(stack)}{change_str}")
        
        self.console.print("="*60, style="magenta")
    
    def _render_showdown_hand(self, player_name: str, hand_info: Dict, 
                              hole_cards: List[str] = None, is_winner: bool = False):
        """渲染摊牌时的手牌"""
        if player_name == "你":
            icon = "👤"
            name_style = "bold green"
        else:
            icon = "🤖"
            name_style = "bold white"
        
        # 添加获胜者标记
        winner_mark = " 🏆 [bold yellow]胜者[/bold yellow]" if is_winner else ""
        self.console.print(f"\n  {icon} {player_name}{winner_mark}:", style=name_style)
        
        # 显示底牌（真实的牌面，带颜色）
        if hole_cards and len(hole_cards) > 0:
            hole_text = Text("    底牌: ")
            for card in hole_cards:
                formatted_card = format_card(card)
                color = get_card_color(card)
                # 使用浅色背景让牌面更清晰，花色颜色更鲜明
                hole_text.append(f" {formatted_card} ", style=f"bold {color} on grey93")
                hole_text.append("  ")
            
            self.console.print(hole_text)
        else:
            # 如果没有底牌数据（不应该发生），显示提示而不是"高牌低牌"
            self.console.print(f"    底牌: [未记录]", style="dim yellow")
        
        # 显示牌型
        hand_strength = hand_info.get('hand', {}).get('hand', {}).get('strength', 'UNKNOWN')
        hand_strength_cn = self._translate_hand_strength(hand_strength)
        self.console.print(f"    牌型: {hand_strength_cn}", style="bold cyan")
    
    def _translate_hand_strength(self, strength: str) -> str:
        """将牌型英文翻译为中文"""
        strength_map = {
            'HIGHCARD': '高牌',
            'ONEPAIR': '一对',
            'TWOPAIR': '两对',
            'THREECARD': '三条',
            'STRAIGHT': '顺子',
            'FLUSH': '同花',
            'FULLHOUSE': '葫芦',
            'FOURCARD': '四条',
            'STRAIGHTFLUSH': '同花顺',
            'ROYALFLUSH': '皇家同花顺'
        }
        return strength_map.get(strength, strength)
    
    def _card_num_to_rank(self, num: int) -> str:
        """将牌点数转换为牌面"""
        if num == 14:
            return 'A'
        elif num == 13:
            return 'K'
        elif num == 12:
            return 'Q'
        elif num == 11:
            return 'J'
        elif 2 <= num <= 10:
            return str(num)
        else:
            return '?'
    
    def render_ai_advice(self, advice: Dict[str, Any]):
        """渲染 AI 建议"""
        if not advice or "error" in advice:
            return
        
        # 提取建议内容
        reasoning = advice.get("reasoning", "暂无建议")
        recommended_action = advice.get("recommended_action", "")
        
        # 行动中文化
        action_cn = {
            "fold": "🚫 弃牌",
            "call": "✅ 跟注",
            "raise": "📈 加注"
        }.get(recommended_action, recommended_action)
        
        # 构建显示内容
        content_lines = []
        
        if recommended_action:
            content_lines.append(f"💡 推荐行动: [bold]{action_cn}[/bold]")
        
        # 加注金额
        if "raise_amount" in advice and recommended_action == "raise":
            amount = advice["raise_amount"]
            content_lines.append(f"💰 建议金额: ${amount}")
        
        # 理由（完整显示，不截断）
        if reasoning:
            # 移除长度限制，显示完整的AI建议
            content_lines.append(f"\n📝 {reasoning}")
        
        # 胜率
        if "win_probability" in advice:
            win_prob = advice["win_probability"]
            if isinstance(win_prob, (int, float)):
                content_lines.append(f"\n📊 胜率估算: {win_prob*100:.0f}%")
        
        content = "\n".join(content_lines)
        
        panel = Panel(
            content,
            title="🤖 AI 策略建议",
            border_style="cyan",
            box=ROUNDED
        )
        self.console.print(panel)
    
    def render_error(self, message: str):
        """渲染错误信息"""
        self.console.print(f"❌ 错误: {message}", style="bold red")
    
    def render_info(self, message: str):
        """渲染提示信息"""
        self.console.print(f"ℹ️  {message}", style="cyan")
    
    def _render_hole_cards(self, hole_card: List[str]):
        """渲染手牌"""
        if not hole_card or len(hole_card) < 2:
            return
        
        card1 = format_card(hole_card[0])
        card2 = format_card(hole_card[1])
        
        color1 = get_card_color(hole_card[0])
        color2 = get_card_color(hole_card[1])
        
        self.console.print("\n🃏 你的手牌:", style="bold")
        
        # 创建卡片样式（带颜色）
        cards_text = Text()
        cards_text.append("  ")
        # 使用浅色背景让牌面更清晰，花色颜色更鲜明
        cards_text.append(f" {card1} ", style=f"bold {color1} on grey93")
        cards_text.append("  ")
        cards_text.append(f" {card2} ", style=f"bold {color2} on grey93")
        
        self.console.print(cards_text)
    
    def _render_community_cards(self, community_cards: List[str]):
        """渲染公共牌"""
        if not community_cards:
            return
        
        self.console.print("\n🎴 公共牌:", end=" ")
        
        cards_text = Text()
        for card in community_cards:
            formatted_card = format_card(card)
            color = get_card_color(card)
            # 使用浅色背景让牌面更清晰，花色颜色更鲜明
            cards_text.append(f" {formatted_card} ", style=f"bold {color} on grey93")
            cards_text.append("  ")
        
        self.console.print(cards_text)
    
    def _render_players_info(self, seats: List[Dict], dealer_btn: int):
        """渲染玩家信息"""
        self.console.print("\n👥 玩家状态:", style="bold")
        
        table = Table(show_header=True, header_style="bold cyan", box=ROUNDED)
        table.add_column("玩家", style="white", width=15)
        table.add_column("筹码", justify="right", style="green", width=12)
        table.add_column("状态", justify="center", width=12)
        table.add_column("位置", justify="center", width=8)
        
        # 找出所有还有筹码的玩家（用于计算位置）
        active_seats = [idx for idx, s in enumerate(seats) if s['stack'] > 0]
        active_count = len(active_seats)
        
        for idx, seat in enumerate(seats):
            name = seat['name']
            stack = format_chips(seat['stack'])
            state = self._get_state_display(seat['state'])
            
            # 位置标记（只为有筹码的玩家显示位置）
            position = ""
            if seat['stack'] > 0:  # 只有还有筹码的玩家才显示位置
                if active_count == 2:
                    # 两人对决：Button 同时是 SB
                    if idx == dealer_btn:
                        position = "🔘 BTN/SB"
                    else:
                        position = "BB"
                else:
                    # 多人游戏：正常的 BTN, SB, BB
                    if idx == dealer_btn:
                        position = "🔘 BTN"
                    else:
                        # 在有筹码的玩家中找位置
                        try:
                            dealer_idx_in_active = active_seats.index(dealer_btn)
                            current_idx_in_active = active_seats.index(idx)
                            
                            # 计算相对位置（顺时针）
                            relative_pos = (current_idx_in_active - dealer_idx_in_active) % active_count
                            
                            if relative_pos == 1:
                                position = "SB"
                            elif relative_pos == 2:
                                position = "BB"
                            # 其他位置暂不标记（可以扩展为 UTG, CO 等）
                        except ValueError:
                            pass  # 如果找不到索引，不显示位置
            
            table.add_row(name, stack, state, position)
        
        self.console.print(table)
    
    def _get_state_display(self, state: str) -> str:
        """获取状态显示"""
        state_map = {
            'participating': '✅ 游戏中',
            'folded': '❌ 已弃牌',
            'allin': '💰 全下',
        }
        return state_map.get(state, state)
    
    def render_table_state(self, round_state: Dict, hole_card: List[str]):
        """渲染完整牌桌状态"""
        self.console.print("\n" + "┏" + "━"*58 + "┓")
        
        # 回合信息
        street = get_street_name(round_state['street'])
        pot = format_chips(round_state['pot']['main']['amount'])
        self.console.print(f"┃  {street.center(20)} | 底池: {pot.center(20)}  ┃")
        
        # 公共牌（带颜色）
        community_cards = round_state.get('community_card', [])
        if community_cards:
            line = Text("┃  公共牌: ")
            for card in community_cards:
                formatted_card = format_card(card)
                color = get_card_color(card)
                line.append(f" {formatted_card} ", style=f"bold {color} on grey93")
                line.append(" ")
            # 填充空白到对齐
            line.append(" " * (45 - len(line.plain)), style="")
            line.append(" ┃")
            self.console.print(line)
        
        # 手牌（带颜色）
        if hole_card:
            line = Text("┃  你的手牌: ")
            for card in hole_card:
                formatted_card = format_card(card)
                color = get_card_color(card)
                line.append(f" {formatted_card} ", style=f"bold {color} on grey93")
                line.append(" ")
            # 填充空白到对齐
            line.append(" " * (43 - len(line.plain)), style="")
            line.append(" ┃")
            self.console.print(line)
        
        self.console.print("┗" + "━"*58 + "┛")
    
    def wait_for_continue(self):
        """等待用户按键继续"""
        try:
            input("\n按 Enter 继续...")
        except KeyboardInterrupt:
            pass
    
    def render_game_over(self, final_state: Dict):
        """渲染游戏结束"""
        self.console.print("\n" + "="*60, style="bold magenta")
        self.console.print("🎮 游戏结束", style="bold magenta")
        self.console.print("="*60, style="bold magenta")
        
        self.console.print("\n💰 最终筹码:")
        
        players = final_state.get('players', [])
        # 按筹码排序
        sorted_players = sorted(players, key=lambda p: p['stack'], reverse=True)
        
        for idx, player in enumerate(sorted_players):
            rank_icon = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "  "
            self.console.print(
                f"  {rank_icon} {player['name']}: {format_chips(player['stack'])}",
                style="bold yellow" if idx == 0 else "white"
            )
        
        self.console.print("\n感谢游玩！🎰", style="bold green")
        self.console.print("="*60, style="bold magenta")

