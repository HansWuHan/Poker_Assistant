"""
游戏控制器模块
控制整个游戏流程
"""
from typing import Optional, Callable, Dict, Any, List
from pypokerengine.api.game import setup_config, start_poker

from poker_assistant.engine.human_player import HumanPlayer
from poker_assistant.engine.ai_opponent import AIOpponentPlayer
from poker_assistant.engine.game_state import GameState
from poker_assistant.cli.game_renderer import GameRenderer
from poker_assistant.cli.input_handler import InputHandler
from poker_assistant.utils.config import Config

# AI 分析模块
from poker_assistant.ai_analysis.strategy_advisor import StrategyAdvisor
from poker_assistant.ai_analysis.opponent_analyzer import OpponentAnalyzer
from poker_assistant.ai_analysis.board_analyzer import BoardAnalyzer
from poker_assistant.ai_analysis.review_analyzer import ReviewAnalyzer
from poker_assistant.ai_analysis.chat_agent import ChatAgent
from poker_assistant.ai_analysis.opponent_modeler import OpponentModeler


class GameController:
    """游戏控制器 - 管理整个游戏流程"""
    
    def __init__(self, config: Config):
        """
        Args:
            config: 游戏配置对象
        """
        self.config = config
        self.game_config = config.get_game_config()
        self.ai_config = config.get_ai_config()
        self.renderer = GameRenderer()
        self.input_handler = InputHandler(chat_callback=self._handle_chat, renderer=self.renderer)
        self.game_state = None
        self.human_player = None
        self.ai_players = []
        
        # 初始化对手建模器（无论是否启用 AI 都可以记录对手行为）
        self.opponent_modeler = OpponentModeler()
        self.current_round_id = 0
        
        # 记录每局开始时的筹码（用于计算赢得金额）
        self.initial_stacks = {}
        
        # Button 位置管理（PyPokerEngine 不会自动轮转，我们手动管理）
        self.current_dealer_btn = 0
        self.player_count_for_dealer = self.game_config['player_count']
        
        # 记录每局的玩家底牌（用于摊牌展示）
        self.player_hole_cards = {}  # {uuid: [card1, card2]}
        
        # 共享字典，供AI玩家记录底牌
        self.shared_hole_cards = {}  # {uuid: [card1, card2]}
        
        # 初始化 AI 分析引擎（如果 API Key 已配置）
        self.ai_enabled = bool(config.DEEPSEEK_API_KEY and config.DEEPSEEK_API_KEY != "your_api_key_here")
        if self.ai_enabled:
            try:
                self.strategy_advisor = StrategyAdvisor()
                self.opponent_analyzer = OpponentAnalyzer()
                self.board_analyzer = BoardAnalyzer()
                self.review_analyzer = ReviewAnalyzer()
                self.chat_agent = ChatAgent()
                
                # 设置对手建模器
                self.strategy_advisor.set_opponent_modeler(self.opponent_modeler)
                self.opponent_analyzer.set_opponent_modeler(self.opponent_modeler)
                
                self.renderer.render_info("✅ AI 分析功能已启用（含对手建模）")
            except Exception as e:
                self.ai_enabled = False
                self.renderer.render_info(f"⚠️  AI 功能初始化失败: {e}")
        else:
            self.renderer.render_info("ℹ️  AI 分析功能未启用（未配置 API Key）")
    
    def start_game(self):
        """开始游戏"""
        # 显示欢迎界面
        self.renderer.render_welcome()
        self.renderer.wait_for_continue()
        
        # 初始化游戏
        self._setup_game()
        
        # 配置 PyPokerEngine
        poker_config = self._create_poker_config()
        
        # 开始游戏
        try:
            self.renderer.render_info("游戏即将开始...")
            game_result = start_poker(poker_config, verbose=0)
            
            # 显示游戏结果
            self.renderer.render_game_over(game_result)
        
        except KeyboardInterrupt:
            self.renderer.render_info("\n游戏被中断")
        
        except Exception as e:
            self.renderer.render_error(f"游戏出错: {e}")
            if self.config.DEBUG:
                import traceback
                traceback.print_exc()
    
    def _setup_game(self):
        """设置游戏"""
        player_count = self.game_config['player_count']
        initial_stack = self.game_config['initial_stack']
        
        # 创建游戏状态
        self.game_state = GameState(player_count, initial_stack)
        
        # 创建人类玩家
        self.human_player = HumanPlayer(
            input_callback=self._get_human_action,
            display_callback=self._handle_game_event
        )
        
        # 创建 AI 对手
        ai_difficulties = self._get_ai_difficulties(player_count - 1)
        self.ai_players = [
            AIOpponentPlayer(difficulty=diff, shared_hole_cards=self.shared_hole_cards) 
            for diff in ai_difficulties
        ]
    
    def _create_poker_config(self):
        """创建 PyPokerEngine 配置"""
        config = setup_config(
            max_round=self.game_config['max_round'],
            initial_stack=self.game_config['initial_stack'],
            small_blind_amount=self.game_config['small_blind_amount']
        )
        
        # 注册人类玩家
        config.register_player(name="你", algorithm=self.human_player)
        
        # 注册 AI 玩家
        for idx, ai_player in enumerate(self.ai_players):
            config.register_player(name=f"AI_{idx+1}", algorithm=ai_player)
        
        return config
    
    def _get_ai_difficulties(self, count: int) -> list:
        """
        获取 AI 难度列表
        
        Args:
            count: AI 数量
        
        Returns:
            难度列表
        """
        difficulty_setting = self.ai_config.get('opponent_difficulty', 'mixed')
        
        # 如果设置为单一难度，所有 AI 使用相同难度
        if difficulty_setting in ['easy', 'medium', 'hard']:
            return [difficulty_setting] * count
        
        # 混合难度：根据数量分配不同难度
        if count >= 5:
            return ['easy', 'easy', 'medium', 'medium', 'hard']
        elif count == 4:
            return ['easy', 'medium', 'medium', 'hard']
        elif count == 3:
            return ['easy', 'medium', 'hard']
        elif count == 2:
            return ['medium', 'hard']
        else:
            return ['medium']
    
    def _get_human_action(self, valid_actions: list, hole_card: list, 
                         round_state: dict) -> tuple:
        """
        获取人类玩家行动
        
        Args:
            valid_actions: 可选行动
            hole_card: 手牌
            round_state: 回合状态
        
        Returns:
            (action, amount) 元组
        """
        # 渲染当前状态
        self.renderer.render_table_state(round_state, hole_card)
        
        # 定义AI建议回调函数 - 用户按'O'时才会调用
        def get_ai_advice():
            if self.ai_enabled:
                try:
                    return self._get_ai_advice(valid_actions, hole_card, round_state)
                except Exception as e:
                    if self.config.DEBUG:
                        self.renderer.render_error(f"获取 AI 建议失败: {e}")
                    return None
            return None
        
        # 获取用户输入（现在包含O选项）
        action, amount = self.input_handler.get_action(
            valid_actions, hole_card, round_state, 
            ai_advice_callback=get_ai_advice if self.ai_enabled else None
        )
        
        return action, amount
    
    def _handle_game_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        处理游戏事件
        
        Args:
            event_type: 事件类型
            event_data: 事件数据
        """
        try:
            if event_type == "game_start":
                self.renderer.render_game_start(event_data)
            
            elif event_type == "round_start":
                round_count = event_data['round_count']
                hole_card = event_data['hole_card']
                seats = event_data['seats']
                
                # 记录本局开始时的筹码（用于计算赢得金额）
                self.initial_stacks = {}
                for seat in seats:
                    self.initial_stacks[seat['uuid']] = seat['stack']
                
                # 清空上一局的底牌记录（使用clear()而不是创建新字典，保持AI玩家的引用）
                self.player_hole_cards.clear()
                self.shared_hole_cards.clear()
                
                # 记录人类玩家的底牌
                human_uuid = self.human_player.uuid
                self.player_hole_cards[human_uuid] = hole_card
                self.shared_hole_cards[human_uuid] = hole_card
                
                # Button 位置轮转（PyPokerEngine 不会自动轮转）
                # 找出所有还有筹码的玩家（淘汰的玩家不参与轮转）
                active_seats = [idx for idx, s in enumerate(seats) if s['stack'] > 0]
                active_player_count = len(active_seats)
                
                # 第一局时，Button在第一个有筹码的玩家
                if round_count == 1:
                    self.current_dealer_btn = active_seats[0] if active_seats else 0
                    self.player_count_for_dealer = active_player_count
                else:
                    # 后续局次，Button 在有筹码的玩家中顺时针移动
                    # 找到当前 dealer 在 active_seats 中的位置
                    try:
                        current_idx_in_active = active_seats.index(self.current_dealer_btn)
                        next_idx_in_active = (current_idx_in_active + 1) % active_player_count
                        self.current_dealer_btn = active_seats[next_idx_in_active]
                    except (ValueError, ZeroDivisionError):
                        # 如果当前 dealer 已被淘汰，从第一个有筹码的玩家开始
                        self.current_dealer_btn = active_seats[0] if active_seats else 0
                    
                    self.player_count_for_dealer = active_player_count
                
                # 开始新一局 - 初始化上下文
                self.current_round_id = round_count
                if self.ai_enabled:
                    round_id_str = f"round_{round_count}"
                    self.strategy_advisor.start_new_round(round_id_str)
                    self.opponent_analyzer.start_new_round(round_id_str)
                    self.board_analyzer.start_new_round(round_id_str)
                
                # 对手建模器开始新局
                self.opponent_modeler.start_new_round()
                
                # 使用我们自己管理的dealer_btn（不使用PyPokerEngine的）
                dealer_btn = self.current_dealer_btn
                
                self.renderer.render_round_start(round_count, hole_card, 
                                                seats, dealer_btn)
            
            elif event_type == "street_start":
                street = event_data['street']
                round_state = event_data['round_state']
                community_cards = round_state.get('community_card', [])
                pot_size = round_state['pot']['main']['amount']
                
                self.renderer.render_street_start(street, community_cards, pot_size)
            
            elif event_type == "game_update":
                action = event_data['action']
                player_name = action['player_uuid']
                
                # 找到玩家名字
                round_state = event_data['round_state']
                for seat in round_state['seats']:
                    if seat['uuid'] == action['player_uuid']:
                        player_name = seat['name']
                        break
                
                is_human = (player_name == "你")
                
                self.renderer.render_player_action(
                    player_name,
                    action['action'],
                    action.get('amount', 0),
                    is_human
                )
            
            elif event_type == "round_result":
                winners = event_data['winners']
                hand_info = event_data['hand_info']
                round_state = event_data['round_state']
                
                # 在摊牌时，从shared_hole_cards获取所有底牌
                # （AI玩家会在receive_round_start时写入）
                final_hole_cards = dict(self.shared_hole_cards)
                
                # 传递初始筹码和玩家底牌以用于展示
                self.renderer.render_round_result(
                    winners, hand_info, round_state, self.initial_stacks, final_hole_cards
                )
                self.renderer.wait_for_continue()
        
        except Exception as e:
            if self.config.DEBUG:
                self.renderer.render_error(f"处理事件时出错: {e}")
                import traceback
                traceback.print_exc()
    
    def _handle_chat(self, question: str, hole_card: list, 
                    round_state: dict) -> str:
        """
        处理聊天请求
        
        Args:
            question: 用户问题
            hole_card: 手牌
            round_state: 回合状态
        
        Returns:
            AI 回复
        """
        if not self.ai_enabled or not self.ai_config.get('enable_chat', True):
            return ("AI 聊天功能未启用。\n"
                    "如需帮助，请输入 'H' 查看命令列表。")
        
        try:
            # 准备游戏上下文
            game_context = {
                "hole_cards": hole_card if hole_card else [],
                "community_cards": round_state.get('community_card', []),
                "street": round_state.get('street', ''),
                "pot_size": round_state.get('pot', {}).get('main', {}).get('amount', 0),
                "stack_size": self._get_my_stack(round_state)
            }
            
            # 调用 ChatAgent
            response = self.chat_agent.chat(question, game_context)
            return response
        
        except Exception as e:
            return f"抱歉，AI 暂时无法回答（{str(e)}）"
    
    def _get_ai_advice(self, valid_actions: list, hole_card: list,
                      round_state: dict) -> Dict[str, Any]:
        """
        获取 AI 建议
        
        Args:
            valid_actions: 可选行动
            hole_card: 手牌
            round_state: 回合状态
        
        Returns:
            AI 建议字典
        """
        try:
            # 提取必要信息
            community_cards = round_state.get('community_card', [])
            street = round_state.get('street', 'preflop')
            pot_size = round_state.get('pot', {}).get('main', {}).get('amount', 0)
            stack_size = self._get_my_stack(round_state)
            
            # 获取玩家位置
            position = self._get_my_position(round_state)
            
            # 计算跟注金额
            call_amount = 0
            for action in valid_actions:
                if action.get('action') == 'call':
                    call_amount = action.get('amount', 0)
                    break
            
            # 获取对手行动（规范化Check/Call）
            opponent_actions = self._get_recent_actions(round_state)
            
            # 获取活跃对手列表
            active_opponents = self._get_active_opponents(round_state)
            
            # 调用策略建议引擎（含对手建模）
            advice = self.strategy_advisor.get_advice(
                hole_cards=hole_card,
                community_cards=community_cards,
                street=street,
                position=position,
                pot_size=pot_size,
                stack_size=stack_size,
                call_amount=call_amount,
                valid_actions=valid_actions,
                opponent_actions=opponent_actions,
                active_opponents=active_opponents
            )
            
            return advice
        
        except Exception as e:
            return {
                "reasoning": f"AI 建议暂时不可用（{str(e)}）",
                "recommended_action": "call"
            }
    
    def _get_my_position(self, round_state: dict) -> str:
        """
        获取玩家位置名称
        
        Args:
            round_state: 回合状态
        
        Returns:
            位置名称（BTN, SB, BB, UTG, MP, CO, HJ等）
        """
        try:
            # 找到玩家的座位索引
            my_uuid = self.human_player.uuid
            my_idx = None
            seats = round_state.get('seats', [])
            
            for idx, seat in enumerate(seats):
                if seat.get('uuid') == my_uuid:
                    my_idx = idx
                    break
            
            if my_idx is None:
                return "Unknown"
            
            # 获取庄位和有筹码的玩家
            dealer_btn = self.current_dealer_btn  # 使用我们管理的Button位置
            active_seats = [idx for idx, s in enumerate(seats) if s['stack'] > 0]
            active_count = len(active_seats)
            
            # 两人对决
            if active_count == 2:
                return "BTN" if my_idx == dealer_btn else "BB"
            
            # 多人游戏：计算位置
            if my_idx == dealer_btn:
                return "BTN"
            
            # 在活跃玩家中找到相对位置
            try:
                dealer_idx_in_active = active_seats.index(dealer_btn)
                my_idx_in_active = active_seats.index(my_idx)
                
                # 计算相对位置（顺时针距离）
                relative_pos = (my_idx_in_active - dealer_idx_in_active) % active_count
                
                if relative_pos == 1:
                    return "SB"
                elif relative_pos == 2:
                    return "BB"
                elif relative_pos == active_count - 1:
                    return "CO"  # Cut-off
                elif relative_pos == active_count - 2:
                    return "HJ"  # Hijack
                elif relative_pos == 3:
                    return "UTG"  # Under the gun
                else:
                    return "MP"  # Middle position
            except ValueError:
                return "Unknown"
        
        except Exception as e:
            if self.config.DEBUG:
                print(f"获取位置失败: {e}")
            return "Unknown"
    
    def _get_my_stack(self, round_state: dict) -> int:
        """获取自己的筹码数"""
        for seat in round_state.get('seats', []):
            if seat.get('name') == "你":
                return seat.get('stack', 1000)
        return 1000
    
    def _get_active_opponents(self, round_state: dict) -> List[str]:
        """获取当前活跃的对手"""
        opponents = []
        for seat in round_state.get('seats', []):
            player_name = seat.get('name', '')
            if player_name != "你" and seat.get('state') != 'folded':
                opponents.append(player_name)
        return opponents
    
    def _record_opponent_action(self, action: Dict, round_state: dict):
        """记录对手行动到建模器"""
        if not hasattr(self, 'opponent_modeler'):
            return
        
        try:
            # 从action中提取信息
            player_uuid = action.get('uuid', '')
            action_type = action.get('action', '')
            amount = action.get('amount', 0)
            
            # 找到对应的玩家名称
            player_name = None
            for seat in round_state.get('seats', []):
                if seat.get('uuid') == player_uuid:
                    player_name = seat.get('name', '')
                    break
            
            if player_name and player_name != "你":
                # 记录到对手建模器
                self.opponent_modeler.record_action(
                    player_name=player_name,
                    action=action_type,
                    amount=amount,
                    street=round_state.get('street', ''),
                    pot_size=round_state.get('pot', {}).get('main', {}).get('amount', 0),
                    community_cards=round_state.get('community_card', [])
                )
        except Exception as e:
            if self.config.DEBUG:
                print(f"记录对手行动失败: {e}")
    
    def _get_recent_actions(self, round_state: dict) -> List[Dict]:
        """获取最近的对手行动（规范化Check/Call）"""
        actions = []
        action_histories = round_state.get('action_histories', {})
        
        # 获取当前街道的行动
        street = round_state.get('street', 'preflop')
        if street in action_histories:
            for action in action_histories[street]:
                # 记录到对手建模器
                self._record_opponent_action(action, round_state)
                
                action_type = action.get('action', '').lower()
                amount = action.get('amount', 0)
                
                # 规范化：将 call 0 转换为 check
                if action_type == 'call' and amount == 0:
                    action_type = 'check'
                
                actions.append({
                    "player": action.get('uuid', ''),
                    "action": action_type,
                    "amount": amount
                })
        
        return actions

