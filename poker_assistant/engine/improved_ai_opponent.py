"""
改进的AI对手策略 - 使用GTO策略指导
"""
import random
try:
    from pypokerengine.players import BasePokerPlayer
except ImportError:
    # 如果pypokerengine不可用，创建一个基类
    class BasePokerPlayer:
        def __init__(self):
            self.uuid = None
        
        def declare_action(self, valid_actions, hole_card, round_state):
            pass

# 导入GTO策略组件
try:
    from ..gto_strategy.gto_advisor import GTOAdvisor
    from ..gto_strategy.gto_core import GTOSituation
    GTO_AVAILABLE = True
except ImportError:
    GTO_AVAILABLE = False
    GTOAdvisor = None
    GTOSituation = None


class ImprovedAIOpponentPlayer(BasePokerPlayer):
    """
    改进的AI对手玩家 - 带思考过程显示
    """
    
    def __init__(self, difficulty: str = "medium", shared_hole_cards: dict = None, 
                 show_thinking: bool = True, gto_enabled: bool = True):
        super().__init__()
        self.difficulty = difficulty
        self.action_history = []
        self.round_count = 0
        self.hole_cards = []
        self.shared_hole_cards = shared_hole_cards
        self.show_thinking = show_thinking  # 是否显示思考过程
        self.gto_enabled = gto_enabled  # 是否启用GTO策略
        
        # 确保有uuid属性
        if not hasattr(self, 'uuid') or self.uuid is None:
            import uuid as uuid_module
            self.uuid = str(uuid_module.uuid4())
        
        # GTO策略组件
        self.gto_advisor = None
        if GTO_AVAILABLE and gto_enabled:
            try:
                self.gto_advisor = GTOAdvisor()
            except Exception:
                self.gto_advisor = None
        
        # 对手建模数据
        self.opponent_stats = {}
        self.table_dynamics = {
            'avg_pot_size': 0,
            'aggression_level': 'normal',
            'recent_raises': 0
        }
    
    def declare_action(self, valid_actions, hole_card, round_state):
        """决定下一步行动 - 优先使用GTO策略指导"""
        import time
        
        fold_action = valid_actions[0]
        call_action = valid_actions[1]
        raise_action = valid_actions[2]
        
        # 更新桌面动态
        self._update_table_dynamics(round_state)
        
        # 生成思考过程（如果开启显示）
        if self.show_thinking:
            # 先输出空行和AI玩家名字+思考中
            print()
            # 获取AI玩家名字
            ai_name = "AI"
            for seat in round_state.get('seats', []):
                if seat.get('uuid') == self.uuid:
                    ai_name = seat.get('name', 'AI')
                    break
            print(f"🤖 {ai_name} 思考中...")
            
            # 等待2秒
            time.sleep(2)
            
            # 输出思考内容
            thinking_process = self._generate_thinking_process(
                hole_card, round_state, valid_actions
            )
            self._display_thinking(thinking_process)
        else:
            # 即使关闭思考显示，也添加1秒延时让AI决策更自然
            time.sleep(1)
        
        # 优先使用GTO策略（如果启用且可用）
        if self.gto_enabled and self.gto_advisor:
            try:
                gto_action = self._get_gto_advice(valid_actions, hole_card, round_state)
                if gto_action:
                    return gto_action
            except Exception as e:
                print(f"GTO策略失败，使用传统策略: {e}")
        
        # GTO不可用或失败时，回退到传统策略
        # 根据难度选择策略
        if self.difficulty == "easy":
            action, amount = self._improved_easy_strategy(fold_action, call_action, raise_action, 
                                                         hole_card, round_state)
        elif self.difficulty == "hard":
            action, amount = self._improved_hard_strategy(fold_action, call_action, raise_action,
                                                         hole_card, round_state)
        else:  # medium
            action, amount = self._improved_medium_strategy(fold_action, call_action, raise_action,
                                                           hole_card, round_state)
        
        return action, amount
    
    def _generate_thinking_process(self, hole_card, round_state, valid_actions):
        """生成思考过程 - 基于GTO策略结果，包含详细GTO分析和对手手牌猜测"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        call_amount = valid_actions[1]['amount']
        
        # 基础牌力评估（用于显示，不作为决策依据）
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        thinking_steps = []
        
        # 手牌信息展示
        if street == 'preflop':
            card_desc = self._describe_hole_cards(hole_card)
            formatted_cards = self._format_hole_cards_display(hole_card)
            position = self._get_my_position(round_state)
            position_desc = self._describe_position(position, len([p for p in round_state['seats'] if p['stack'] > 0]))
            thinking_steps.append(f"🎯 {formatted_cards} ({card_desc}) - {position_desc}")
        else:
            hand_desc = self._describe_hand_strength(hand_strength, hole_card, round_state.get('community_card', []))
            formatted_cards = self._format_hole_cards_display(hole_card)
            thinking_steps.append(f"🎯 {hand_desc} {formatted_cards}")
        
        # GTO策略分析（优先显示，作为决策依据）
        gto_decision = None
        gto_sizing_info = None
        if self.gto_enabled and self.gto_advisor:
            try:
                gto_analysis = self._get_gto_analysis(hole_card, round_state, valid_actions)
                if gto_analysis:
                    # 获取GTO决策用于最终建议
                    gto_result = self._get_raw_gto_result(hole_card, round_state, valid_actions)
                    if gto_result:
                        gto_decision = gto_result.get('action', '')
                        gto_amount = gto_result.get('amount', 0)
                        gto_confidence = gto_result.get('confidence', 0)
                        
                        # 提取频率分布信息
                        frequencies = gto_result.get('frequencies', {})
                        sizing_rec = gto_result.get('sizing_recommendation', {})
                        
                        # 构建GTO分析字符串，频率分布单独一行
                        gto_info = f"🧠 GTO策略: {gto_decision} ${gto_amount} (置信度: {gto_confidence:.0%})"
                        
                        # 添加频率分布（新行显示）
                        if frequencies:
                            freq_parts = []
                            for action, freq in frequencies.items():
                                if freq > 0.01:  # 只显示大于1%的频率
                                    bar_length = int(freq * 20)  # 20个字符的进度条
                                    bar = "█" * bar_length + "░" * (20 - bar_length)
                                    freq_parts.append(f"{action}: {freq:.0%} [{bar}]")
                            if freq_parts:
                                gto_info += f"\n📊 频率分布: {' | '.join(freq_parts)}"
                        
                        # 添加尺度建议信息（稍后会在赔率行显示）
                        if sizing_rec and isinstance(sizing_rec, dict):
                            optimal_sizing = sizing_rec.get('optimal_sizing', 0)
                            if optimal_sizing > 0:
                                gto_sizing_info = f"💰 尺度建议: {optimal_sizing:.0%} 底池"
                        
                        thinking_steps.append(f"{gto_info}")
            except Exception as e:
                # GTO分析失败时仍显示基础信息，但不作为决策依据
                pass
        
        # 底池信息（只在有跟注时显示）
        if call_amount > 0 and pot > 0:
            pot_odds = call_amount / (pot + call_amount)
            pot_info = f"💰 底池${pot}，跟注${call_amount}，赔率{pot_odds:.1%}"
            
            # 在赔率行末尾添加尺度建议
            if gto_sizing_info:
                pot_info += f" | {gto_sizing_info}"
            
            thinking_steps.append(pot_info)
        
        # 对手手牌猜测（仅针对人类玩家）
        active_opponents = self._get_active_opponents(round_state)
        if active_opponents > 0:
            hand_guess = self._guess_opponent_hands(round_state, street)
            if hand_guess:
                thinking_steps.append(f"🔍 {hand_guess}")
        
        # 基于GTO策略的最终决策建议
        if gto_decision:
            if gto_decision == 'raise':
                thinking_steps.append("💡 GTO建议: 积极进攻，价值下注")
            elif gto_decision == 'call':
                thinking_steps.append("💡 GTO建议: 控制底池，谨慎跟注")
            elif gto_decision == 'fold':
                thinking_steps.append("💡 GTO建议: 放弃底池，保存筹码")
            else:
                thinking_steps.append(f"💡 GTO建议: 执行{gto_decision}行动")
        else:
            # GTO不可用时，使用传统建议作为备选
            if hand_strength >= 0.7:
                thinking_steps.append("💡 传统建议: 强牌，考虑价值下注")
            elif hand_strength >= 0.4:
                thinking_steps.append("💡 传统建议: 中等牌力，谨慎行动")
            else:
                thinking_steps.append("💡 传统建议: 弱牌，考虑弃牌")
        
        return "\n".join(thinking_steps)
    
    def _format_action(self, action, amount):
        """格式化行动显示"""
        action_names = {
            'fold': '🚫 弃牌',
            'call': '✅ 跟注',
            'raise': '📈 加注'
        }
        
        action_text = action_names.get(action, action)
        if amount > 0:
            return f"{action_text} ${amount}"
        else:
            return action_text
    
    def _get_active_opponents(self, round_state):
        """获取活跃对手数量（排除已弃牌玩家）"""
        seats = round_state.get('seats', [])
        return sum(1 for seat in seats 
                   if seat.get('stack', 0) > 0 
                   and seat.get('uuid') != self.uuid 
                   and seat.get('state', 'participating') == 'participating')
    
    def _format_hole_cards_display(self, hole_card):
        """格式化手牌显示，像玩家手牌一样渲染"""
        if not hole_card or len(hole_card) < 2:
            return ""
        
        # 导入卡片工具函数
        try:
            from poker_assistant.utils.card_utils import format_card, get_card_color
            
            # 格式化两张牌
            card1 = format_card(hole_card[0])
            card2 = format_card(hole_card[1])
            
            # 获取颜色
            color1 = get_card_color(hole_card[0])
            color2 = get_card_color(hole_card[1])
            
            # 创建格式化字符串（使用Unicode符号）
            return f"{card1} {card2}"
            
        except ImportError:
            # 如果无法导入，使用简单格式
            return f"{hole_card[0]} {hole_card[1]}"
    
    def _display_thinking(self, thinking_text):
        """显示思考过程 - 精简版"""
        if thinking_text:
            print(f"{thinking_text}")
    
    def _display_decision(self, action, amount, hole_card, round_state):
        """显示最终决策 - 精简版"""
        action_names = {
            'fold': '🚫 弃牌',
            'call': '✅ 跟注',
            'raise': '📈 加注'
        }
        
        action_text = action_names.get(action, action)
        if amount > 0:
            print(f"🎯 {action_text} ${amount}")
        else:
            print(f"🎯 {action_text}")
    
    def _describe_hole_cards(self, hole_card):
        """描述手牌"""
        if not hole_card or len(hole_card) < 2:
            return "无效手牌"
        
        # 提取牌面信息
        card1, card2 = hole_card[0], hole_card[1]
        rank1, rank2 = card1[1], card2[1]
        suit1, suit2 = card1[0], card2[0]
        
        # 是否对子
        if rank1 == rank2:
            rank_names = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T'}
            rank_name = rank_names.get(rank1, rank1)
            return f"对子 {rank_name}{rank_name}"
        
        # 是否同花
        suited = "同花" if suit1 == suit2 else "不同花"
        
        # 高牌
        ranks = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
        
        high_card = max(ranks.get(rank1, 0), ranks.get(rank2, 0))
        low_card = min(ranks.get(rank1, 0), ranks.get(rank2, 0))
        
        # 连牌判断
        gap = high_card - low_card
        if gap == 1:
            connector = "连牌"
        elif gap <= 3:
            connector = "近似连牌"
        else:
            connector = "不连牌"
        
        return f"{suited} {connector}"
    
    def _describe_hand_strength(self, strength, hole_card, community_card):
        """描述牌力"""
        if strength >= 0.8:
            return "极强牌力"
        elif strength >= 0.6:
            return "强牌"
        elif strength >= 0.4:
            return "中等牌力"
        elif strength >= 0.2:
            return "弱牌"
        else:
            return "极弱牌力"
    
    def _describe_position(self, position, total_players):
        """描述位置"""
        if total_players <= 2:
            return "单挑位置"
        
        if position == 0:
            return "按钮位(最佳)"
        elif position == 1:
            return "小盲位"
        elif position == 2:
            return "大盲位"
        elif position >= total_players - 2:
            return "靠后位置"
        else:
            return "靠前位置"
    
    def _analyze_opponents_simple(self, round_state):
        """简化对手分析 - 只分析活跃玩家"""
        # 获取活跃对手数量
        active_opponents = self._get_active_opponents(round_state)
        
        if active_opponents == 0:
            return ""
        
        # 如果只有1个活跃对手，简化分析
        if active_opponents == 1:
            return "1个活跃对手"
        
        # 分析活跃对手的下注行为
        opponent_analysis = self._analyze_opponent_betting_patterns(round_state)
        
        # 专门分析玩家（你）的行为（只分析活跃玩家）
        player_analysis = self._analyze_player_behavior(round_state)
        
        result = f"{active_opponents}个活跃对手{opponent_analysis}"
        if player_analysis:
            result += f"\n🎯 玩家分析: {player_analysis}"
        
        return result
    
    def _analyze_player_behavior(self, round_state):
        """专门分析玩家（你）的行为模式"""
        action_histories = round_state.get('action_histories', {})
        street = round_state['street']
        
        if not action_histories or street not in action_histories:
            return ""
        
        # 找到玩家的UUID（通过名称"你"识别）
        player_uuid = None
        for seat in round_state['seats']:
            # 假设玩家名称是"你"
            if seat.get('name') == '你':
                player_uuid = seat['uuid']
                break
        
        if not player_uuid or player_uuid == self.uuid:
            return ""
        
        # 收集玩家在所有街道的行为
        player_actions = []
        player_total_invested = 0
        
        for street_name, actions in action_histories.items():
            if not isinstance(actions, list):
                continue
                
            for action in actions:
                if isinstance(action, dict) and 'action' in action and 'uuid' in action:
                    if action['uuid'] == player_uuid:
                        action_type = action['action'].lower()
                        amount = action.get('amount', 0)
                        
                        # 排除盲注相关行动
                        if street_name == 'preflop' and amount <= 20 and action_type in ['call', 'raise']:
                            continue  # 排除小盲注和补盲注
                        
                        player_actions.append({
                            'street': street_name,
                            'action': action_type,
                            'amount': amount
                        })
                        player_total_invested += amount
        
        if not player_actions:
            return "暂无有意义行动"
        
        # 分析玩家行为模式
        analysis_parts = []
        
        # 统计行为类型
        aggressive_actions = sum(1 for a in player_actions if a['action'] in ['raise', 'allin'])
        call_actions = sum(1 for a in player_actions if a['action'] == 'call')
        fold_actions = sum(1 for a in player_actions if a['action'] == 'fold')
        total_meaningful_actions = len(player_actions)
        
        if total_meaningful_actions == 0:
            return "暂无有意义行动"
        
        # 计算激进度
        aggression_factor = aggressive_actions / total_meaningful_actions if total_meaningful_actions > 0 else 0
        
        # 分析激进度
        if aggression_factor >= 0.6:
            analysis_parts.append("激进型")
        elif aggression_factor >= 0.3:
            analysis_parts.append("平衡型")
        else:
            analysis_parts.append("保守型")
        
        # 分析当前街道的行为
        current_street_actions = [a for a in player_actions if a['street'] == street]
        if current_street_actions:
            last_action = current_street_actions[-1]
            
            if last_action['action'] == 'raise':
                if last_action['amount'] >= 100:
                    analysis_parts.append("当前街道大加注")
                else:
                    analysis_parts.append("当前街道加注")
            elif last_action['action'] == 'call':
                analysis_parts.append("当前街道跟注")
            elif last_action['action'] == 'allin':
                analysis_parts.append("当前街道全押")
        
        # 基于行为猜测手牌范围
        if aggression_factor >= 0.6:  # 激进玩家
            if player_total_invested >= 200:
                analysis_parts.append("可能持有强牌或诈唬")
            else:
                analysis_parts.append("范围较宽，可能包含诈唬")
        elif aggression_factor <= 0.2:  # 保守玩家
            if aggressive_actions > 0:
                analysis_parts.append("可能持有强牌")
            else:
                analysis_parts.append("多为中等强度牌")
        else:  # 平衡型玩家
            analysis_parts.append("标准范围")
        
        return "，".join(analysis_parts) if analysis_parts else "暂无分析"
    
    def _analyze_opponent_betting_patterns(self, round_state):
        """分析对手下注模式"""
        action_histories = round_state.get('action_histories', {})
        street = round_state['street']
        
        if not action_histories or street not in action_histories:
            return ""
        
        analysis_parts = []
        
        # 分析当前街道的对手行为
        current_street_actions = action_histories[street]
        if not isinstance(current_street_actions, list):
            return ""
        
        # 获取活跃对手（未弃牌的玩家）
        seats = round_state.get('seats', [])
        active_uuids = {seat['uuid'] for seat in seats if seat.get('state', 'participating') == 'participating' and seat['uuid'] != self.uuid}
        
        # 统计对手行为（只统计活跃玩家）
        opponent_actions = {}
        for action in current_street_actions:
            if isinstance(action, dict) and 'action' in action and 'uuid' in action:
                uuid = action['uuid']
                # 只分析活跃的对手
                if uuid != self.uuid and uuid in active_uuids:
                    if uuid not in opponent_actions:
                        opponent_actions[uuid] = []
                    opponent_actions[uuid].append(action['action'].lower())
        
        # 分析每个对手的行为模式
        aggressive_count = 0
        passive_count = 0
        total_opponents = len(opponent_actions)
        
        for uuid, actions in opponent_actions.items():
            if not actions:
                continue
                
            # 计算激进程度
            aggressive_actions = sum(1 for a in actions if a in ['raise', 'allin'])
            total_actions = len(actions)
            aggression_rate = aggressive_actions / total_actions
            
            if aggression_rate >= 0.5:
                aggressive_count += 1
            elif aggression_rate <= 0.2:
                passive_count += 1
        
        # 生成分析结果
        if aggressive_count > 0:
            analysis_parts.append(f"{aggressive_count}个激进")
        if passive_count > 0:
            analysis_parts.append(f"{passive_count}个保守")
        
        if analysis_parts:
            return "，" + "，".join(analysis_parts)
        
        return ""
    
    def _guess_opponent_hands(self, round_state, street):
        """猜测对手手牌范围 - 仅针对人类玩家，排除AI对手"""
        action_histories = round_state.get('action_histories', {})
        community_cards = round_state.get('community_card', [])
        
        if not action_histories or street not in action_histories:
            return ""
        
        guesses = []
        
        # 分析当前街道的行动
        current_actions = action_histories[street]
        if not isinstance(current_actions, list):
            return ""
        
        # 按对手分组分析
        opponent_actions = {}
        for action in current_actions:
            if isinstance(action, dict) and 'action' in action and 'uuid' in action:
                uuid = action['uuid']
                if uuid != self.uuid:  # 只分析对手
                    if uuid not in opponent_actions:
                        opponent_actions[uuid] = []
                    opponent_actions[uuid].append(action)
        
        # 获取活跃对手（未弃牌的玩家）
        seats = round_state.get('seats', [])
        active_uuids = {seat['uuid'] for seat in seats if seat.get('state', 'participating') == 'participating' and seat['uuid'] != self.uuid}
        
        # 分析每个对手的手牌范围（只分析活跃的人类玩家，跳过AI对手）
        for uuid, actions in opponent_actions.items():
            if not actions:
                continue
            
            # 跳过已弃牌的玩家
            if uuid not in active_uuids:
                continue
            
            # 获取对手名字和类型
            opponent_name = "对手"
            is_human = False
            for seat in round_state['seats']:
                if seat['uuid'] == uuid:
                    opponent_name = seat['name']
                    # 判断是否为人类玩家（名字不包含"AI_"）
                    is_human = not opponent_name.startswith('AI_')
                    break
            
            # 只分析人类玩家，跳过AI对手
            if not is_human:
                continue
            
            # 分析下注模式（排除盲注）
            meaningful_actions = []
            total_invested = 0
            
            for action in actions:
                action_type = action['action'].lower()
                amount = action.get('amount', 0)
                
                # 排除盲注相关行动
                if street == 'preflop' and amount <= 20 and action_type in ['call', 'raise']:
                    continue  # 排除小盲注和补盲注
                
                meaningful_actions.append(action)
                total_invested += amount
            
            if not meaningful_actions:
                continue
            
            # 基于有意义的行动进行猜测
            has_raise = any(a['action'].lower() == 'raise' for a in meaningful_actions)
            has_allin = any(a['action'].lower() == 'allin' for a in meaningful_actions)
            
            # 根据行为猜测手牌强度
            if has_allin:
                guess = "超强牌(AA,KK,AK)"
            elif has_raise:
                if total_invested > 100:
                    guess = "强牌(对子+，AQ+)"
                else:
                    guess = "中等牌(对子，KQ)"
            elif total_invested > 0:
                guess = "边缘牌(高牌，同花连牌)"
            else:
                guess = "弱牌或投机牌"
            
            guesses.append(f"{opponent_name}: {guess}")
        
        # 分析翻牌前的行动（更重要）
        if 'preflop' in action_histories and street != 'preflop':
            preflop_actions = action_histories['preflop']
            if isinstance(preflop_actions, list):
                preflop_guesses = []
                for action in preflop_actions:
                    if isinstance(action, dict) and 'action' in action and 'uuid' in action:
                        uuid = action['uuid']
                        if uuid != self.uuid and uuid not in [g.split(':')[0] for g in guesses]:
                            # 获取对手信息
                            opponent_name = "对手"
                            is_human = False
                            for seat in round_state['seats']:
                                if seat['uuid'] == uuid:
                                    opponent_name = seat['name']
                                    is_human = not opponent_name.startswith('AI_')
                                    break
                            
                            # 只分析人类玩家
                            if not is_human:
                                continue
                            
                            action_type = action['action'].lower()
                            amount = action.get('amount', 0)
                            
                            # 排除盲注
                            if amount <= 20 and action_type in ['call', 'raise']:
                                continue
                            
                            if action_type == 'raise':
                                if amount >= 100:  # 大加注
                                    preflop_guesses.append(f"翻牌前大加注: 强牌范围")
                                else:
                                    preflop_guesses.append(f"翻牌前加注: 中等强度")
                
                if preflop_guesses:
                    guesses.extend(preflop_guesses[:2])  # 限制数量
        
        # 根据公共牌调整猜测
        if community_cards:
            board_analysis = self._analyze_board_for_opponent_range(community_cards)
            if board_analysis:
                guesses.append(f"牌面分析: {board_analysis}")
        
        if guesses:
            return "；".join(guesses[:3])  # 限制显示数量
        
        return ""
    
    def _analyze_board_for_opponent_range(self, community_cards):
        """根据公共牌分析对手可能的手牌范围"""
        if len(community_cards) < 3:
            return ""
        
        # 评估牌面协调性
        coordination = self._assess_board_coordination(community_cards)
        
        if coordination > 0.7:
            return "协调牌面，对手可能击中强牌"
        elif coordination < 0.3:
            return "干燥牌面，对手多为高牌"
        else:
            return "中性牌面，对手范围较宽"
    
    def _improved_easy_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """改进的简单策略 - 更精细的决策"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 评估牌力
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self._get_position_factor(round_state)
        
        # 调整后的牌力阈值
        adjusted_strength = hand_strength * position_factor
        
        # 获取当前筹码量
        my_stack = self._get_my_stack(round_state)
        
        if street == 'preflop':
            # 翻牌前更精细的起手牌要求
            if adjusted_strength >= 0.85:
                # 超强牌（AA, KK, AK等）
                if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                    # 根据筹码深度调整下注大小
                    if my_stack > pot * 20:  # 深筹码
                        amount = max(raise_action['amount']['min'], int(pot * 0.8))
                    else:  # 浅筹码
                        amount = max(raise_action['amount']['min'], int(pot * 0.6))
                    return raise_action['action'], amount
                elif random.random() < 0.2:  # 20%概率慢打
                    return call_action['action'], call_action['amount']
                return call_action['action'], call_action['amount']
                
            elif adjusted_strength >= 0.7:
                # 强牌但非超强
                if call_action['amount'] <= pot * 0.15 and random.random() < 0.8:
                    return call_action['action'], call_action['amount']
                elif raise_action['amount']['min'] != -1 and random.random() < 0.3:
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif adjusted_strength >= 0.5:
                # 中等牌力
                if call_action['amount'] <= pot * 0.08 and position_factor >= 1.0:
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 差牌
                if call_action['amount'] == 0:  # 免费看牌
                    return call_action['action'], call_action['amount']
                # 偶尔偷盲（10%）
                elif (position_factor >= 1.1 and call_action['amount'] <= pot * 0.05 and 
                      random.random() < 0.1):
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            # 根据牌力和公共牌协调性综合判断
            board_coordination = self._assess_board_coordination(round_state.get('community_card', []))
            
            # 调整牌力评估
            effective_strength = adjusted_strength
            if board_coordination > 0.7:  # 协调的牌面
                effective_strength *= 0.9  # 降低牌力评估
            elif board_coordination < 0.3:  # 不协调的牌面
                effective_strength *= 1.1  # 提高牌力评估
            
            if effective_strength >= 0.8:
                # 强牌，价值下注
                if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                    bet_size = self._calculate_value_bet_size(hand_strength, pot, raise_action)
                    return raise_action['action'], bet_size
                elif random.random() < 0.8:  # 80%概率至少跟注
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.55:
                # 中等强牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.2 and hand_strength >= 0.4:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif pot_odds <= 0.3 and hand_strength >= 0.45:  # 赔率合适
                    if random.random() < 0.7:
                        return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and 
                      random.random() < 0.2 and pot_odds <= 0.25):  # 偶尔半诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.4))
                    return raise_action['action'], amount
                
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.35:
                # 边缘牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.15 and hand_strength >= 0.25:  # 赔率很好才跟注
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.1 and 
                      pot_odds <= 0.2):  # 10%概率诈唬
                    amount = max(raise_action['amount']['min'], int(pot * 0.35))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 极低概率诈唬（8%）
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.08 and 
                      pot_odds <= 0.25):
                    amount = max(raise_action['amount']['min'], int(pot * 0.3))
                    return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
    
    def _improved_medium_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """改进的中等策略 - 更智能的对手建模和情境判断"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 获取当前筹码量
        my_stack = self._get_my_stack(round_state)
        
        # 评估牌力
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self._get_position_factor(round_state)
        
        # 对手倾向
        opponent_tendency = self._analyze_opponent_tendency(round_state)
        
        # 公共牌协调性
        board_coordination = self._assess_board_coordination(round_state.get('community_card', []))
        
        # 调整后的牌力阈值
        adjusted_strength = hand_strength * position_factor * opponent_tendency
        
        # 根据牌面调整牌力评估
        if street != 'preflop':
            if board_coordination > 0.7:  # 协调牌面，降低牌力
                adjusted_strength *= 0.85
            elif board_coordination < 0.3:  # 不协调牌面，提高牌力
                adjusted_strength *= 1.15
        
        if street == 'preflop':
            # 基于位置和对手倾向调整起手牌要求
            if adjusted_strength >= 0.8:
                # 超强牌
                if opponent_tendency > 1.2:  # 对手激进
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        # 深筹码时更大加注
                        if my_stack > pot * 15:
                            amount = max(raise_action['amount']['min'], int(pot * 0.9))
                        else:
                            amount = max(raise_action['amount']['min'], int(pot * 0.7))
                        return raise_action['action'], amount
                else:  # 对手保守
                    if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                        amount = max(raise_action['amount']['min'], int(pot * 0.6))
                        return raise_action['action'], amount
                
                # 偶尔慢打
                if random.random() < 0.2:
                    return call_action['action'], call_action['amount']
                return call_action['action'], call_action['amount']
                
            elif adjusted_strength >= 0.65:
                # 强牌
                if call_action['amount'] <= pot * 0.12 and position_factor >= 1.0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.4 and 
                      opponent_tendency < 1.1):  # 对保守对手加注
                    amount = max(raise_action['amount']['min'], int(pot * 0.5))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif adjusted_strength >= 0.5:
                # 中等牌力
                if (call_action['amount'] <= pot * 0.08 and 
                    (position_factor >= 1.0 or opponent_tendency < 1.0)):
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.15 and 
                      position_factor >= 1.1):  # 位置好时偶尔偷盲
                    amount = self._calculate_value_bet_size(hand_strength * 0.5, pot, raise_action, round_state)
                    return raise_action['action'], amount
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 差牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 位置好时偶尔偷盲（8%）
                elif (position_factor >= 1.1 and call_action['amount'] <= pot * 0.04 and 
                      random.random() < 0.08):
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            # 根据牌面纹理和对手类型调整策略
            effective_strength = adjusted_strength
            
            if effective_strength >= 0.8:
                # 超强牌
                if opponent_tendency > 1.2:  # 对手激进，可以大注
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength * 1.1, pot, raise_action, round_state)
                        return raise_action['action'], bet_size
                else:  # 对手保守，标准价值下注
                    if random.random() < 0.6 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength, pot, raise_action, round_state)
                        return raise_action['action'], bet_size
                
                # 80%概率至少跟注
                if random.random() < 0.8:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.6:
                # 强牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.25 and hand_strength >= 0.5:  # 赔率合适
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.35 and hand_strength >= 0.55 and 
                      opponent_tendency < 1.0):  # 对保守对手放宽
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.3 and 
                      pot_odds <= 0.3):  # 半诈唬
                    amount = self._calculate_value_bet_size(hand_strength * 0.8, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.4:
                # 中等牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.2 and hand_strength >= 0.35:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.25 and hand_strength >= 0.4 and 
                      position_factor >= 1.0):  # 位置好
                    if random.random() < 0.8:
                        return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.2 and 
                      pot_odds <= 0.25 and position_factor >= 1.05):  # 位置好时半诈唬
                    amount = self._calculate_value_bet_size(hand_strength * 0.7, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.25:
                # 边缘牌力
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.15 and hand_strength >= 0.25:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.15 and 
                      pot_odds <= 0.2 and opponent_tendency > 1.1):  # 对激进对手诈唬
                    amount = self._calculate_value_bet_size(hand_strength * 0.6, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 对激进对手偶尔诈唬（12%）
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.12 and 
                      opponent_tendency > 1.2 and pot_odds <= 0.2):
                    amount = self._calculate_value_bet_size(hand_strength * 0.5, pot, raise_action, round_state)
                    return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
        
        # 默认返回弃牌（安全保底）
        return fold_action['action'], fold_action['amount']
    
    def _improved_hard_strategy(self, fold_action, call_action, raise_action, hole_card, round_state):
        """改进的困难策略 - 最智能的决策"""
        street = round_state['street']
        pot = round_state['pot']['main']['amount']
        
        # 获取当前筹码量
        my_stack = self._get_my_stack(round_state)
        
        # 评估牌力
        hand_strength = self._evaluate_real_hand_strength(hole_card, round_state.get('community_card', []))
        
        # 位置因子
        position_factor = self._get_position_factor(round_state)
        
        # 对手倾向
        opponent_tendency = self._analyze_opponent_tendency(round_state)
        
        # 公共牌协调性
        board_coordination = self._assess_board_coordination(round_state.get('community_card', []))
        
        # 调整后的牌力阈值
        adjusted_strength = hand_strength * position_factor * opponent_tendency
        
        # 根据牌面调整牌力评估
        if street != 'preflop':
            if board_coordination > 0.7:  # 协调牌面，降低牌力
                adjusted_strength *= 0.8
            elif board_coordination < 0.3:  # 不协调牌面，提高牌力
                adjusted_strength *= 1.2
        
        if street == 'preflop':
            # 基于位置和对手倾向调整起手牌要求
            if adjusted_strength >= 0.85:
                # 超强牌
                if opponent_tendency > 1.3:  # 对手很激进
                    if random.random() < 0.8 and raise_action['amount']['min'] != -1:
                        # 深筹码时更大加注
                        if my_stack > pot * 12:
                            amount = max(raise_action['amount']['min'], int(pot * 1.0))
                        else:
                            amount = max(raise_action['amount']['min'], int(pot * 0.8))
                        return raise_action['action'], amount
                else:  # 对手保守
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        amount = max(raise_action['amount']['min'], int(pot * 0.7))
                        return raise_action['action'], amount
                
                # 偶尔慢打
                if random.random() < 0.15:
                    return call_action['action'], call_action['amount']
                return call_action['action'], call_action['amount']
                
            elif adjusted_strength >= 0.7:
                # 强牌
                if call_action['amount'] <= pot * 0.15 and position_factor >= 1.0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.5 and 
                      opponent_tendency < 1.1):  # 对保守对手加注
                    amount = max(raise_action['amount']['min'], int(pot * 0.6))
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif adjusted_strength >= 0.55:
                # 中等牌力
                if (call_action['amount'] <= pot * 0.1 and 
                    (position_factor >= 1.0 or opponent_tendency < 1.0)):
                    return call_action['action'], call_action['amount']
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.25 and 
                      position_factor >= 1.1):  # 位置好时偷盲
                    amount = self._calculate_value_bet_size(hand_strength * 0.6, pot, raise_action, round_state)
                    return raise_action['action'], amount
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 差牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 位置好时偶尔偷盲（12%）
                elif (position_factor >= 1.1 and call_action['amount'] <= pot * 0.05 and 
                      random.random() < 0.12):
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
        
        else:  # 翻牌后
            # 根据牌面纹理和对手类型调整策略
            effective_strength = adjusted_strength
            
            # 检查是否只有高牌（没有成牌）
            actual_strength = self._evaluate_actual_hand_strength(hole_card, round_state.get('community_card', []))
            has_made_hand = actual_strength >= 0.4  # 是否有成牌（对子及以上）
            
            if effective_strength >= 0.85 and has_made_hand:
                # 超强牌且有成牌
                if opponent_tendency > 1.3:  # 对手很激进
                    if random.random() < 0.8 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength * 1.2, pot, raise_action, round_state)
                        return raise_action['action'], bet_size
                else:  # 对手保守
                    if random.random() < 0.7 and raise_action['amount']['min'] != -1:
                        bet_size = self._calculate_value_bet_size(hand_strength * 1.1, pot, raise_action, round_state)
                        return raise_action['action'], bet_size
                
                # 85%概率至少跟注
                if random.random() < 0.85:
                    return call_action['action'], call_action['amount']
                return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.85 and not has_made_hand:
                # 高牌被高估，实际上只有高牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                # 只有高牌时，只在赔率很好或免费看牌时跟注
                if pot_odds <= 0.15 or call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                
            elif effective_strength >= 0.65 and has_made_hand:
                # 强牌且有成牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.3 and hand_strength >= 0.55:  # 赔率合适
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.4 and hand_strength >= 0.6 and 
                      opponent_tendency < 1.0):  # 对保守对手放宽
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.4 and 
                      pot_odds <= 0.35):  # 半诈唬
                    amount = self._calculate_value_bet_size(hand_strength * 0.8, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.65 and not has_made_hand:
                # 中等强度但只有高牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                # 只有高牌时，只在赔率很好或免费看牌时跟注
                if pot_odds <= 0.2 or call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.45 and has_made_hand:
                # 中等牌力且有成牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.25 and hand_strength >= 0.4:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (pot_odds <= 0.3 and hand_strength >= 0.45 and 
                      position_factor >= 1.0):  # 位置好
                    if random.random() < 0.8:
                        return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.3 and 
                      pot_odds <= 0.3 and position_factor >= 1.05):  # 位置好时半诈唬
                    amount = self._calculate_value_bet_size(hand_strength * 0.7, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.45 and not has_made_hand:
                # 中等强度但只有高牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                # 只有高牌时，只在赔率很好或免费看牌时跟注
                if pot_odds <= 0.15 or call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.3 and has_made_hand:
                # 边缘牌力但有成牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                if pot_odds <= 0.2 and hand_strength >= 0.3:  # 赔率很好
                    return call_action['action'], call_action['amount']
                elif (raise_action['amount']['min'] != -1 and random.random() < 0.2 and 
                      pot_odds <= 0.25 and opponent_tendency > 1.2):  # 对激进对手诈唬
                    amount = self._calculate_value_bet_size(hand_strength * 0.6, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            elif effective_strength >= 0.3 and not has_made_hand:
                # 边缘牌力且只有高牌
                pot_odds = call_action['amount'] / (pot + call_action['amount'])
                
                # 只有高牌时，只在赔率很好或免费看牌时跟注
                if pot_odds <= 0.15 or call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                else:
                    return fold_action['action'], fold_action['amount']
                    
            else:
                # 弱牌
                if call_action['amount'] == 0:
                    return call_action['action'], call_action['amount']
                # 只有高牌时，降低诈唬频率
                elif (not has_made_hand and 
                      raise_action['amount']['min'] != -1 and random.random() < 0.1 and 
                      opponent_tendency > 1.2 and pot_odds <= 0.2):
                    # 高牌诈唬要更谨慎（10%概率）
                    amount = self._calculate_value_bet_size(hand_strength * 0.4, pot, raise_action, round_state)
                    return raise_action['action'], amount
                elif (has_made_hand and 
                      raise_action['amount']['min'] != -1 and random.random() < 0.15 and 
                      opponent_tendency > 1.2 and pot_odds <= 0.25):
                    # 有成牌时可以稍微激进一些（15%概率）
                    amount = self._calculate_value_bet_size(hand_strength * 0.6, pot, raise_action, round_state)
                    return raise_action['action'], amount
                return fold_action['action'], fold_action['amount']
    
    def _evaluate_real_hand_strength(self, hole_card, community_card):
        """评估真实牌力（0-1）- 修复高牌高估问题"""
        if not hole_card or len(hole_card) < 2:
            return 0.0
        
        # 基础牌力评估（仅基于手牌）
        base_strength = self._evaluate_hand_simple(hole_card, community_card)
        
        # 如果有公共牌，进行更精确评估
        if community_card and len(community_card) >= 3:
            # 评估实际牌力，而不是仅仅基于手牌
            actual_strength = self._evaluate_actual_hand_strength(hole_card, community_card)
            
            # 如果实际牌力远低于基础牌力，说明高牌被高估了
            if actual_strength < base_strength * 0.7:
                return actual_strength
            
            # 考虑公共牌协调性
            board_coordination = self._assess_board_coordination(community_card)
            
            # 协调的公共牌降低牌力（更危险）
            if board_coordination > 0.7:
                actual_strength *= 0.85
            elif board_coordination < 0.3:
                actual_strength *= 1.1
            
            return min(1.0, actual_strength)
        
        return min(1.0, base_strength)
    
    def _get_position_factor(self, round_state):
        """获取位置因子"""
        my_position = self._get_my_position(round_state)
        dealer_btn = round_state['dealer_btn']
        total_players = len([p for p in round_state['seats'] if p['stack'] > 0])
        
        # 位置评估（越靠后越好）
        if my_position == dealer_btn:
            return 1.15  # BTN位置最佳
        elif (my_position - dealer_btn) % total_players <= 2:
            return 1.05  # 靠后位置
        else:
            return 0.95  # 靠前位置
    
    def _analyze_opponent_tendency(self, round_state):
        """分析对手倾向（更智能）- 排除盲注影响"""
        action_histories = round_state.get('action_histories', {})
        
        total_actions = 0
        aggressive_actions = 0
        call_actions = 0
        fold_actions = 0
        
        # 分析所有街道的行动
        for street, street_actions in action_histories.items():
            if isinstance(street_actions, list):
                for action in street_actions:
                    if isinstance(action, dict) and 'action' in action:
                        # 只统计其他玩家的行动
                        if action.get('uuid') != self.uuid:
                            action_type = action['action'].lower()
                            amount = action.get('amount', 0)
                            
                            # 排除盲注相关行动
                            if street == 'preflop' and amount <= 20 and action_type in ['call', 'raise']:
                                continue  # 排除小盲注和补盲注
                            
                            total_actions += 1
                            
                            if action_type in ['raise', 'allin']:
                                aggressive_actions += 1
                            elif action_type == 'call':
                                call_actions += 1
                            elif action_type == 'fold':
                                fold_actions += 1
        
        if total_actions == 0:
            return 1.0
        
        # 计算激进因子（0-1）
        aggression_factor = aggressive_actions / total_actions if total_actions > 0 else 0.5
        
        # 计算弃牌率
        fold_rate = fold_actions / total_actions if total_actions > 0 else 0
        
        # 根据对手类型返回调整因子
        if aggression_factor > 0.5:  # 非常激进
            return 0.85  # 更谨慎
        elif aggression_factor > 0.35:  # 激进
            return 0.9
        elif aggression_factor < 0.15:  # 非常保守
            return 1.2  # 可以更激进
        elif aggression_factor < 0.25:  # 保守
            return 1.1
        else:  # 正常
            return 1.0
    
    def _calculate_value_bet_size(self, hand_strength, pot, raise_action, round_state=None):
        """计算价值下注大小（更智能和情境化）"""
        min_raise = raise_action['amount']['min']
        max_raise = raise_action['amount']['max']
        
        # 获取当前筹码深度信息
        my_stack = self._get_my_stack(round_state) if round_state else 1000
        
        # 计算筹码深度（以当前底池为基准）
        stack_depth = my_stack / pot if pot > 0 else 20
        
        # 获取街道信息
        street = round_state.get('street', 'preflop') if round_state else 'preflop'
        
        # 获取对手倾向
        opponent_tendency = self._analyze_opponent_tendency(round_state) if round_state else 1.0
        
        # 获取位置因子
        position_factor = self._get_position_factor(round_state) if round_state else 1.0
        
        # 根据牌力、筹码深度、街道和位置决定下注比例
        if hand_strength >= 0.9:  # 极强牌
            if stack_depth > 20:  # 深筹码
                if street == 'preflop':
                    bet_ratio = random.uniform(0.8, 1.0)  # 翻牌前可以更激进
                else:
                    bet_ratio = random.uniform(0.7, 0.9)  # 翻牌后控制底池
            elif stack_depth < 5:  # 浅筹码
                bet_ratio = random.uniform(0.9, 1.0)  # 可以更激进
            else:  # 中等筹码
                bet_ratio = random.uniform(0.8, 1.0)
                
        elif hand_strength >= 0.8:  # 强牌
            if stack_depth > 20:
                if street == 'preflop':
                    bet_ratio = random.uniform(0.7, 0.9)
                else:
                    bet_ratio = random.uniform(0.6, 0.8)  # 翻牌后更谨慎
            elif stack_depth < 5:
                bet_ratio = random.uniform(0.8, 0.9)
            else:
                bet_ratio = random.uniform(0.65, 0.85)
                
        elif hand_strength >= 0.65:  # 中等强牌
            if stack_depth > 20:
                if street == 'preflop':
                    bet_ratio = random.uniform(0.5, 0.7)
                else:
                    bet_ratio = random.uniform(0.4, 0.6)  # 深筹码时更保守
            elif stack_depth < 5:
                bet_ratio = random.uniform(0.6, 0.8)  # 浅筹码时可以更大
            else:
                bet_ratio = random.uniform(0.5, 0.7)
                
        elif hand_strength >= 0.5:  # 中等牌
            if stack_depth > 20:
                if street == 'preflop':
                    bet_ratio = random.uniform(0.4, 0.6)
                else:
                    bet_ratio = random.uniform(0.3, 0.5)  # 翻牌后小价值下注
            elif stack_depth < 5:
                bet_ratio = random.uniform(0.5, 0.7)  # 浅筹码时可以更大
            else:
                bet_ratio = random.uniform(0.4, 0.6)
                
        else:  # 边缘牌（半诈唬）
            if stack_depth > 20:
                bet_ratio = random.uniform(0.2, 0.4)  # 深筹码时小注诈唬
            elif stack_depth < 5:
                bet_ratio = random.uniform(0.4, 0.6)  # 浅筹码时更大诈唬
            else:
                bet_ratio = random.uniform(0.3, 0.5)
        
        # 根据对手倾向调整下注大小
        if opponent_tendency > 1.2:  # 对手激进，可以稍微加大下注
            bet_ratio *= 1.1
        elif opponent_tendency < 0.9:  # 对手保守，可以稍微减小下注
            bet_ratio *= 0.9
        
        # 根据位置调整下注大小
        if position_factor >= 1.1:  # 位置好，可以稍微加大下注
            bet_ratio *= 1.05
        elif position_factor <= 0.95:  # 位置差，稍微减小下注
            bet_ratio *= 0.95
        
        # 根据街道调整下注大小
        if street == 'river':  # 河牌圈，价值下注可以更精确
            if hand_strength >= 0.8:
                bet_ratio *= 1.1  # 强牌在河牌可以更大下注
            else:
                bet_ratio *= 0.9  # 边缘牌在河牌要谨慎
        elif street == 'turn':  # 转牌圈，适中下注
            bet_ratio *= 1.0
        elif street == 'flop':  # 翻牌圈，可以稍微大一些
            if hand_strength >= 0.7:
                bet_ratio *= 1.05
        
        # 确保下注比例在合理范围内
        bet_ratio = max(0.2, min(1.0, bet_ratio))  # 限制在20%-100%之间
        
        bet_size = int(pot * bet_ratio)
        
        # 确保在允许范围内，并添加一些随机性避免过于机械化
        if bet_size < min_raise:
            # 如果必须最小加注，考虑是否值得加注
            if hand_strength >= 0.6:  # 只有较强的牌才进行最小加注
                return min_raise
            else:
                return 0  # 选择跟注或弃牌
        elif bet_size > max_raise:
            return max_raise
        else:
            # 添加小幅随机性（±10%）让下注看起来更自然
            random_factor = random.uniform(0.9, 1.1)
            final_bet = int(bet_size * random_factor)
            
            # 确保仍然在范围内
            final_bet = max(min_raise, min(max_raise, final_bet))
            
            # 对于强牌，确保下注足够大以获取价值
            if hand_strength >= 0.8 and final_bet < pot * 0.5:
                final_bet = max(final_bet, int(pot * 0.5))
            
            # 避免过于机械化的下注金额，使用更自然的数字
            if final_bet > 100:
                # 让下注金额更自然（比如195而不是200，385而不是400）
                remainder = final_bet % 50
                if remainder < 15:
                    final_bet -= remainder
                elif remainder > 35:
                    final_bet += (50 - remainder)
            
            return final_bet
    
    def _evaluate_actual_hand_strength(self, hole_card, community_card):
        """评估实际牌力（考虑公共牌后的真实强度）"""
        if not hole_card or len(hole_card) < 2 or not community_card or len(community_card) < 3:
            return self._evaluate_hand_simple(hole_card, community_card)
        
        # 合并所有牌
        all_cards = hole_card + community_card
        
        # 评估实际牌力
        actual_strength = self._assess_hand_strength(all_cards)
        
        return actual_strength
    
    def _assess_hand_strength(self, all_cards):
        """评估手牌强度（基于所有牌）"""
        if len(all_cards) < 5:
            return self._evaluate_hand_simple(all_cards[:2], all_cards[2:])
        
        # 提取点数和花色
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = []
        card_suits = []
        
        for card in all_cards:
            rank = card[1]
            suit = card[0]
            card_ranks.append(ranks.get(rank, 0))
            card_suits.append(suit)
        
        # 统计每个点数和花色的数量
        rank_counts = {}
        suit_counts = {}
        
        for rank in card_ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        for suit in card_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        # 评估牌力
        strength = 0.0
        
        # 1. 检查同花
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        if max_suit_count >= 5:
            strength = 0.8  # 同花
        elif max_suit_count == 4:
            strength = 0.3  # 4张同花
        elif max_suit_count == 3:
            strength = 0.1  # 3张同花
        
        # 2. 检查顺子可能性
        unique_ranks = sorted(set(card_ranks))
        straight_potential = 0
        
        for i in range(len(unique_ranks) - 2):
            if unique_ranks[i+2] - unique_ranks[i] <= 4:
                straight_potential += 0.1
        
        strength += min(0.3, straight_potential)
        
        # 3. 检查对子和三条
        max_rank_count = max(rank_counts.values()) if rank_counts else 0
        if max_rank_count >= 3:
            strength = max(strength, 0.7)  # 三条
        elif max_rank_count == 2:
            # 计算对子数量
            pair_count = sum(1 for count in rank_counts.values() if count == 2)
            if pair_count >= 2:
                strength = max(strength, 0.6)  # 两对
            else:
                strength = max(strength, 0.4)  # 一对
        
        # 4. 高牌评估（如果没有其他牌力）
        if strength < 0.2:
            # 评估高牌强度
            high_cards = sorted(card_ranks, reverse=True)[:3]  # 取最高的3张牌
            avg_high_card = sum(high_cards) / len(high_cards)
            
            # 高牌强度（基于平均高牌点数）
            if avg_high_card >= 12:  # Q以上
                strength = 0.25
            elif avg_high_card >= 10:  # T以上
                strength = 0.2
            else:
                strength = 0.15
        
        return min(1.0, strength)
    
    def _has_showdown_value(self, hand_strength, round_state):
        """判断是否有摊牌价值"""
        # 简化判断：牌力超过阈值且有希望赢
        return hand_strength >= 0.3
    
    def _get_my_stack(self, round_state):
        """获取我的筹码量"""
        for seat in round_state['seats']:
            if seat['uuid'] == self.uuid:
                return seat.get('stack', 0)
        return 0
    
    def _assess_board_coordination(self, community_card):
        """评估公共牌协调性（更精确）"""
        if not community_card or len(community_card) < 3:
            return 0.5
        
        # 评估顺子可能性
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = []
        for card in community_card:
            rank = card[1]
            card_ranks.append(ranks.get(rank, 0))
        
        card_ranks.sort()
        
        # 检查顺子可能性
        straight_danger = 0
        for i in range(len(card_ranks) - 2):
            if card_ranks[i+2] - card_ranks[i] <= 4:  # 3张牌在5个连续等级内
                straight_danger += 0.2
        
        # 检查同花可能性
        suit_counts = {}
        for card in community_card:
            suit = card[0]
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        flush_danger = max(suit_counts.values()) / len(community_card) if suit_counts else 0
        
        # 综合评估：0.0-1.0，越高表示牌面越协调（越危险）
        coordination = min(1.0, (straight_danger + flush_danger) / 2)
        
        return coordination
    
    def _get_gto_advice(self, valid_actions, hole_card, round_state):
        """
        获取GTO策略建议
        """
        if not self.gto_advisor:
            return None
        
        try:
            # 准备GTO需要的参数
            street = round_state['street']
            position = self._get_position_name(round_state)
            stack_size = self._get_my_stack(round_state)
            pot_size = round_state['pot']['main']['amount']
            community_cards = round_state.get('community_card', [])
            
            # 计算跟注金额
            call_amount = 0
            for action in valid_actions:
                if action.get('action') == 'call':
                    call_amount = action.get('amount', 0)
                    break
            
            # 提取对手行动历史
            opponent_actions = self._extract_opponent_actions(round_state)
            
            # 获取活跃对手
            active_opponents = []
            for seat in round_state.get('seats', []):
                if seat.get('uuid') != self.uuid and seat.get('state') == 'participating':
                    active_opponents.append(seat.get('name', ''))
            
            # 获取GTO建议
            gto_result = self.gto_advisor.get_gto_advice(
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
            
            if gto_result:
                # 转换GTO建议为行动
                action_type = gto_result['action']
                amount = gto_result.get('amount', 0)
                
                # 映射到可用行动
                if action_type == 'fold':
                    fold_action = next((a for a in valid_actions if a['action'] == 'fold'), None)
                    if fold_action:
                        return fold_action['action'], fold_action['amount']
                
                elif action_type == 'call':
                    call_action = next((a for a in valid_actions if a['action'] == 'call'), None)
                    if call_action:
                        return call_action['action'], call_action['amount']
                
                elif action_type == 'raise':
                    raise_action = next((a for a in valid_actions if a['action'] == 'raise'), None)
                    if raise_action and raise_action['amount']['min'] != -1:
                        # 使用GTO建议的金额，但要确保在有效范围内
                        gto_amount = max(amount, raise_action['amount']['min'])
                        gto_amount = min(gto_amount, raise_action['amount']['max'])
                        return raise_action['action'], int(gto_amount)
            
            return None
            
        except Exception as e:
            print(f"GTO策略获取失败: {e}")
            return None
    
    def _get_position_name(self, round_state):
        """获取位置名称"""
        position_idx = self._get_my_position(round_state)
        total_players = len([s for s in round_state['seats'] if s['stack'] > 0])
        
        if total_players <= 2:
            return "BTN" if position_idx == 0 else "BB"
        
        dealer_btn = round_state['dealer_btn']
        small_blind_pos = round_state['small_blind_pos'] 
        big_blind_pos = round_state['big_blind_pos']
        
        if position_idx == dealer_btn:
            return "BTN"
        elif position_idx == small_blind_pos:
            return "SB"
        elif position_idx == big_blind_pos:
            return "BB"
        elif position_idx == (dealer_btn - 1) % len(round_state['seats']):
            return "CO"
        elif position_idx == (dealer_btn - 2) % len(round_state['seats']):
            return "HJ"
        else:
            return "MP"
    
    def _extract_opponent_actions(self, round_state):
        """提取对手行动历史"""
        actions = []
        action_histories = round_state.get('action_histories', {})
        
        for street, street_actions in action_histories.items():
            if street_actions:
                for action in street_actions:
                    if action.get('uuid') != self.uuid:
                        actions.append({
                            'street': street,
                            'action': action.get('action'),
                            'amount': action.get('amount', 0)
                        })
        
        return actions
    
    def _get_raw_gto_result(self, hole_card, round_state, valid_actions):
        """获取原始GTO结果，用于思考过程分析"""
        if not self.gto_advisor:
            return None
        
        try:
            # 准备GTO需要的参数
            street = round_state['street']
            position = self._get_position_name(round_state)
            stack_size = self._get_my_stack(round_state)
            pot_size = round_state['pot']['main']['amount']
            community_cards = round_state.get('community_card', [])
            
            # 计算跟注金额
            call_amount = 0
            for action in valid_actions:
                if action.get('action') == 'call':
                    call_amount = action.get('amount', 0)
                    break
            
            # 提取对手行动历史
            opponent_actions = self._extract_opponent_actions(round_state)
            
            # 获取活跃对手
            active_opponents = []
            for seat in round_state.get('seats', []):
                if seat.get('uuid') != self.uuid and seat.get('state') == 'participating':
                    active_opponents.append(seat.get('name', ''))
            
            # 获取GTO建议
            return self.gto_advisor.get_gto_advice(
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
            
        except Exception as e:
            return None
    
    def _get_gto_analysis(self, hole_card, round_state, valid_actions):
        """获取GTO策略分析文本 - 增强版，显示更多详细信息"""
        try:
            # 准备GTO需要的参数
            street = round_state['street']
            position = self._get_position_name(round_state)
            stack_size = self._get_my_stack(round_state)
            pot_size = round_state['pot']['main']['amount']
            community_cards = round_state.get('community_card', [])
            
            # 计算跟注金额
            call_amount = 0
            for action in valid_actions:
                if action.get('action') == 'call':
                    call_amount = action.get('amount', 0)
                    break
            
            # 提取对手行动历史
            opponent_actions = self._extract_opponent_actions(round_state)
            
            # 获取活跃对手
            active_opponents = []
            for seat in round_state.get('seats', []):
                if seat.get('uuid') != self.uuid and seat.get('state') == 'participating':
                    active_opponents.append(seat.get('name', ''))
            
            # 获取GTO建议
            gto_result = self.gto_advisor.get_gto_advice(
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
            
            if gto_result:
                # 提取关键信息生成详细的GTO分析
                action = gto_result['action']
                amount = gto_result.get('amount', 0)
                confidence = gto_result.get('confidence', 0)
                reasoning = gto_result.get('reasoning', '')
                frequencies = gto_result.get('frequencies', {})
                sizing_recommendation = gto_result.get('sizing_recommendation', {})
                range_analysis = gto_result.get('range_analysis', {})
                
                # 生成详细的GTO分析文本
                gto_parts = []
                
                # 1. 主要策略建议
                main_action = f"🎯 GTO策略: {action}"
                if amount > 0:
                    main_action += f" ${amount}"
                if confidence > 0:
                    main_action += f" (置信度: {int(confidence * 100)}%)"
                gto_parts.append(main_action)
                
                # 2. 频率分析（如果有）
                if frequencies:
                    freq_text = "📊 频率分布:"
                    for action_type, freq in frequencies.items():
                        if isinstance(freq, (int, float)):
                            percentage = int(freq * 100)
                            bar = "█" * (percentage // 10) + "░" * (10 - percentage // 10)
                            freq_text += f" {action_type}: {percentage}% [{bar}]"
                    gto_parts.append(freq_text)
                
                # 3. 尺度建议（如果有）
                if sizing_recommendation and isinstance(sizing_recommendation, dict):
                    optimal = sizing_recommendation.get('optimal_sizing', 0)
                    if optimal > 0:
                        pot_percentage = int(optimal * 100)
                        gto_parts.append(f"💰 尺度建议: {pot_percentage}% 底池")
                
                # 4. 范围分析（如果有）
                if range_analysis and isinstance(range_analysis, dict):
                    hand_strength = range_analysis.get('range_strength', 0)
                    in_range = range_analysis.get('in_open_range', False)
                    if hand_strength > 0:
                        strength_text = f"🎴 牌力评估: {int(hand_strength * 100)}%"
                        if in_range:
                            strength_text += " (在标准范围内)"
                        gto_parts.append(strength_text)
                
                # 5. 关键理由
                if reasoning:
                    # 提取理由中的核心信息
                    lines = reasoning.strip().split('\n')
                    key_points = []
                    for line in lines:
                        line = line.strip()
                        if line.startswith('•') and len(key_points) < 3:
                            key_points.append(line.replace('•', '').strip())
                        elif '理由:' in line and len(key_points) < 3:
                            reason_text = line.split('理由:')[1].strip()
                            if reason_text and len(reason_text) < 100:
                                key_points.append(reason_text)
                    
                    if key_points:
                        gto_parts.append(f"💡 核心逻辑: {'; '.join(key_points)}")
                
                return " | ".join(gto_parts)
            
            return None
            
        except Exception as e:
            # GTO分析失败时返回None，不影响整体思考过程
            return None
    
    def _update_table_dynamics(self, round_state):
        """更新桌面动态"""
        # 统计最近的加注情况
        street = round_state['street']
        action_histories = round_state.get('action_histories', {})
        
        if street in action_histories:
            recent_raises = sum(1 for action in action_histories[street] 
                              if action.get('action', '').lower() == 'raise')
            self.table_dynamics['recent_raises'] = recent_raises
    
    def _get_my_position(self, round_state):
        """获取自己的位置索引"""
        for idx, seat in enumerate(round_state['seats']):
            if seat['uuid'] == self.uuid:
                return idx
        return 0
    
    def _evaluate_hand_simple(self, hole_card, community_card):
        """保留原有的简单评估作为基础"""
        if not hole_card or len(hole_card) < 2:
            return 0.0
        
        # 提取点数
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card1_rank = ranks.get(hole_card[0][1], 0)
        card2_rank = ranks.get(hole_card[1][1], 0)
        
        # 是否对子
        is_pair = (card1_rank == card2_rank)
        
        # 是否同花
        is_suited = (hole_card[0][0] == hole_card[1][0])
        
        # 高牌
        high_card = max(card1_rank, card2_rank)
        low_card = min(card1_rank, card2_rank)
        
        # 基础评分
        score = 0.0
        
        if is_pair:
            # 对子
            score = 0.5 + (card1_rank / 28.0)  # AA=1.0, 22=0.54
        else:
            # 非对子
            score = (high_card + low_card) / 28.0
            
            # 同花加成
            if is_suited:
                score += 0.1
            
            # 连牌加成
            if abs(card1_rank - card2_rank) <= 3:
                score += 0.05
            
            # 高牌加成
            if high_card >= 12:  # Q 或更大
                score += 0.1
        
        return min(1.0, score)
    
    # 保留原有的消息处理方法
    def receive_game_start_message(self, game_info):
        self.round_count = 0
    
    def receive_round_start_message(self, round_count, hole_card, seats):
        self.round_count = round_count
        self.hole_cards = hole_card
        
        # 修复：将底牌记录到共享字典中，用于摊牌显示
        if self.shared_hole_cards is not None:
            self.shared_hole_cards[self.uuid] = hole_card
    
    def receive_street_start_message(self, street, round_state):
        pass
    
    def receive_game_update_message(self, action, round_state):
        pass
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        pass