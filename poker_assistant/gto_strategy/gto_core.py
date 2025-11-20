"""
GTO策略核心引擎
实现基于博弈论最优的德州扑克决策算法
"""
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# 导入类型定义
from .types import GTOContext, GTOResult, FrequencyResult, SizingRecommendation, ActionType, Position, Street


# 为向后兼容保留的旧类型定义
@dataclass
class GTOSituation:
    """GTO情境数据结构（向后兼容）"""
    street: str  # preflop, flop, turn, river
    position: str  # BTN, SB, BB, UTG, MP, CO, HJ
    stack_size: int  # 有效筹码深度
    pot_size: int  # 底池大小
    community_cards: List[str]  # 公共牌
    hole_cards: List[str]  # 手牌
    opponent_actions: List[Dict]  # 对手行动历史
    active_opponents: int  # 活跃对手数量
    
    def to_context(self) -> GTOContext:
        """转换为新的上下文格式"""
        return GTOContext(
            street=self.street,
            position=self.position,
            stack_size=self.stack_size,
            pot_size=self.pot_size,
            community_cards=self.community_cards,
            hole_cards=self.hole_cards,
            opponent_actions=self.opponent_actions,
            active_opponents=self.active_opponents
        )


@dataclass
class GTOAction:
    """GTO行动建议（向后兼容）"""
    action: str  # fold, call, raise
    amount: int  # 建议金额
    frequency: float  # 执行频率
    reasoning: str  # 决策理由
    range_category: str  # 范围分类
    exploit_adjustment: float  # 剥削调整因子
    
    @classmethod
    def from_result(cls, result: GTOResult) -> 'GTOAction':
        """从新的结果格式转换"""
        return cls(
            action=result.action,
            amount=result.amount,
            frequency=result.confidence,
            reasoning=result.reasoning,
            range_category=result.range_analysis.get('range_category', 'unknown'),
            exploit_adjustment=0.0
        )


class GTOCore:
    """GTO策略核心引擎"""
    
    def __init__(self):
        # GTO核心参数
        self.min_raise_factor = 2.0  # 最小加注倍数
        self.max_raise_factor = 4.0  # 最大加注倍数
        self.value_bet_threshold = 0.6  # 价值下注阈值
        self.bluff_threshold = 0.3  # 诈唬阈值
        
        # 加载GTO范围数据
        self.preflop_ranges = self._load_default_preflop_ranges()
        self.postflop_strategies = self._load_default_postflop_strategies()
        self.sizing_charts = self._load_default_sizing_charts()
        
    def _load_default_preflop_ranges(self) -> Dict:
        """加载默认翻牌前范围"""
        return {
            "BTN": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s",
                        "QJs", "QJo", "QTs", "QTo", "Q9s",
                        "JTs", "JTo", "J9s", "J8s",
                        "T9s", "T8s", "T7s",
                        "98s", "97s", "96s",
                        "87s", "86s", "85s",
                        "76s", "75s", "74s",
                        "65s", "64s", "63s",
                        "54s", "53s", "52s",
                        "43s", "42s", "32s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            },
            "CO": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s",
                        "QJs", "QJo", "QTs", "QTo", "Q9s", "Q8s", "Q7s", "Q6s",
                        "JTs", "JTo", "J9s", "J8s", "J7s", "J6s",
                        "T9s", "T8s", "T7s", "T6s",
                        "98s", "97s", "96s",
                        "87s", "86s",
                        "76s", "75s",
                        "65s", "64s",
                        "54s", "53s",
                        "43s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            },
            "HJ": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s", "K8s", "K7s", "K6s", "K5s",
                        "QJs", "QJo", "QTs", "QTo", "Q9s", "Q8s", "Q7s",
                        "JTs", "JTo", "J9s", "J8s", "J7s",
                        "T9s", "T8s", "T7s",
                        "98s", "97s",
                        "87s", "86s",
                        "76s", "75s",
                        "65s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            },
            "MP": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s", "K8s", "K7s",
                        "QJs", "QJo", "QTs", "QTo", "Q9s", "Q8s",
                        "JTs", "JTo", "J9s", "J8s",
                        "T9s", "T8s",
                        "98s", "97s",
                        "87s",
                        "76s",
                        "65s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            },
            "UTG": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s",
                        "QJs", "QJo", "QTs", "QTo",
                        "JTs", "JTo",
                        "T9s",
                        "98s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            },
            "SB": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s",
                        "QJs", "QJo", "QTs", "QTo", "Q9s",
                        "JTs", "JTo", "J9s", "J8s",
                        "T9s", "T8s", "T7s",
                        "98s", "97s",
                        "87s", "86s",
                        "76s", "75s",
                        "65s", "64s",
                        "54s", "53s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            },
            "BB": {
                "open": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                        "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
                        "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s",
                        "QJs", "QJo", "QTs", "QTo", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s",
                        "JTs", "JTo", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s",
                        "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s",
                        "98s", "97s", "96s", "95s", "94s", "93s", "92s",
                        "87s", "86s", "85s", "84s", "83s", "82s",
                        "76s", "75s", "74s", "73s", "72s",
                        "65s", "64s", "63s", "62s",
                        "54s", "53s", "52s",
                        "43s", "42s",
                        "32s"],
                "defend": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                          "AKs", "AKo", "AQs", "AQo", "AJs", "AJo", "ATs", "ATo", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s",
                          "KQs", "KQo", "KJs", "KJo", "KTs", "KTo", "K9s", "K8s", "K7s", "K6s", "K5s", "K4s", "K3s", "K2s",
                          "QJs", "QJo", "QTs", "QTo", "Q9s", "Q8s", "Q7s", "Q6s", "Q5s", "Q4s", "Q3s", "Q2s",
                          "JTs", "JTo", "J9s", "J8s", "J7s", "J6s", "J5s", "J4s", "J3s", "J2s",
                          "T9s", "T8s", "T7s", "T6s", "T5s", "T4s", "T3s", "T2s",
                          "98s", "97s", "96s", "95s", "94s", "93s", "92s",
                          "87s", "86s", "85s", "84s", "83s", "82s",
                          "76s", "75s", "74s", "73s", "72s",
                          "65s", "64s", "63s", "62s",
                          "54s", "53s", "52s",
                          "43s", "42s",
                          "32s"],
                "3bet": ["AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AJs", "KQs"],
                "call_3bet": ["AA", "KK", "QQ", "JJ", "TT", "99", "88", "77", "66", "55", "44", "33", "22",
                             "AKs", "AKo", "AQs", "AQo", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s",
                             "KQs", "KJs", "KTs", "K9s",
                             "QJs", "QTs", "Q9s",
                             "JTs", "J9s", "T9s", "98s", "87s", "76s", "65s", "54s"]
            }
        }
    
    def _load_default_postflop_strategies(self) -> Dict:
        """加载默认翻牌后策略"""
        return {
            "flop": {
                "cbet": {
                    "frequency": 0.65,
                    "sizing": {
                        "dry_board": 0.33,  # 干燥牌面1/3底池
                        "wet_board": 0.75,  # 湿润牌面3/4底池
                        "dynamic_board": 0.55  # 动态牌面半池
                    },
                    "thresholds": {
                        "value_bet": 0.7,
                        "bluff": 0.25,
                        "check_back": 0.4
                    }
                },
                "vs_cbet": {
                    "call_frequency": 0.45,
                    "raise_frequency": 0.12,
                    "fold_frequency": 0.43,
                    "thresholds": {
                        "call": 0.35,
                        "raise": 0.65,
                        "fold": 0.2
                    }
                }
            },
            "turn": {
                "double_barrel": {
                    "frequency": 0.45,
                    "sizing": 0.65,
                    "thresholds": {
                        "value_bet": 0.75,
                        "bluff": 0.3
                    }
                },
                "vs_turn_bet": {
                    "call_frequency": 0.38,
                    "raise_frequency": 0.08,
                    "fold_frequency": 0.54
                }
            },
            "river": {
                "value_bet": {
                    "thin_value_threshold": 0.55,
                    "overbet_threshold": 0.85,
                    "sizing": {
                        "thin_value": 0.55,
                        "standard_value": 0.75,
                        "overbet": 1.25
                    }
                },
                "bluff": {
                    "frequency": 0.3,
                    "blocker_requirement": True,
                    "sizing": 0.75
                }
            }
        }
    
    def _load_default_sizing_charts(self) -> Dict:
        """加载默认下注尺度图表"""
        return {
            "preflop": {
                "open": {
                    "standard": 2.5,  # 2.5BB
                    "deep_stack": 3.0,  # 深筹码
                    "short_stack": 2.0  # 浅筹码
                },
                "3bet": {
                    "ip": 3.0,  # 位置优势
                    "oop": 3.5  # 位置劣势
                },
                "4bet": {
                    "standard": 2.2,  # 2.2倍3bet
                    "allin_threshold": 25  # 25BB以下全下
                }
            },
            "postflop": {
                "value_bet": {
                    "thin": 0.5,
                    "standard": 0.75,
                    "big": 1.0,
                    "overbet": 1.25
                },
                "bluff": {
                    "small": 0.33,
                    "standard": 0.75,
                    "big": 1.0
                },
                "probe": {
                    "small": 0.4,
                    "standard": 0.65
                }
            }
        }
    
    def calculate_gto_action(self, situation: GTOSituation) -> GTOAction:
        """
        计算GTO最优行动
        
        Args:
            situation: 当前情境
            
        Returns:
            GTO行动建议
        """
        if situation.street == 'preflop':
            return self._calculate_preflop_action(situation)
        else:
            return self._calculate_postflop_action(situation)
    
    def _calculate_preflop_action(self, situation: GTOSituation) -> GTOAction:
        """计算翻牌前GTO行动"""
        # 获取当前位置的范围
        position_range = self.preflop_ranges.get(situation.position, self.preflop_ranges['BB'])
        
        # 转换手牌为标准化格式
        hand_string = self._format_hand(situation.hole_cards)
        
        # 分析对手行动
        is_raised = self._is_pot_raised(situation.opponent_actions)
        is_3bet = self._is_3bet_pot(situation.opponent_actions)
        
        # 根据情境选择策略
        if not is_raised:
            # 无人加注，考虑开池
            return self._calculate_open_action(situation, position_range, hand_string)
        elif is_3bet:
            # 面对3bet
            return self._calculate_vs_3bet_action(situation, position_range, hand_string)
        else:
            # 面对单一加注
            return self._calculate_vs_raise_action(situation, position_range, hand_string)
    
    def _calculate_postflop_action(self, situation: GTOSituation) -> GTOAction:
        """计算翻牌后GTO行动"""
        street_strategy = self.postflop_strategies.get(situation.street, self.postflop_strategies['flop'])
        
        # 评估牌力
        hand_strength = self._evaluate_hand_strength(situation.hole_cards, situation.community_cards)
        
        # 评估牌面纹理
        board_texture = self._evaluate_board_texture(situation.community_cards)
        
        # 评估位置优势
        position_advantage = self._evaluate_position_advantage(situation.position)
        
        # 计算GTO频率
        action_frequencies = self._calculate_action_frequencies(
            hand_strength, board_texture, position_advantage, situation, street_strategy
        )
        
        # 选择行动
        return self._select_action_by_frequency(action_frequencies, situation)
    
    def _format_hand(self, hole_cards: List[str]) -> str:
        """将手牌格式化为标准表示"""
        if not hole_cards or len(hole_cards) < 2:
            return ""
        
        card1, card2 = hole_cards[0], hole_cards[1]
        
        # 解析手牌格式，支持多种输入格式
        def parse_card(card):
            """解析单张牌，支持多种格式"""
            if len(card) == 2:
                # 可能是标准格式：'SA' (黑桃A) 或 'AS' (A黑桃)
                # 需要判断哪个是rank，哪个是suit
                char1, char2 = card[0], card[1]
                
                # 如果第一个是A/T/J/Q/K/2-9，则是rank+suit格式
                if char1 in 'ATJQK23456789':
                    return char1, char2  # rank, suit
                # 如果第二个是A/T/J/Q/K/2-9，则是suit+rank格式
                elif char2 in 'ATJQK23456789':
                    return char2, char1  # rank, suit
                else:
                    # 无法判断，默认第一个为suit，第二个为rank
                    return char2, char1
                    
            elif len(card) == 3 and card.startswith('10'):
                # 10的格式：'10D' (方块10)
                return 'T', card[2]  # 10用T表示
            elif len(card) == 3:
                # 其他3字符格式，尝试解析
                # 可能是suit+rank格式：'C2' (梅花2)
                suit, rank = card[0], card[1:]
                if rank in 'ATJQK23456789':
                    return rank, suit
                else:
                    # 反向解析
                    return card[1], card[0]
            else:
                # 默认处理
                return '2', 'S'  # 默认2♠
        
        try:
            rank1, suit1 = parse_card(card1)
            rank2, suit2 = parse_card(card2)
        except:
            # 解析失败，使用默认值
            rank1, suit1 = '2', 'S'
            rank2, suit2 = '3', 'H'
        
        # 排序：高牌在前
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        rank_val1 = ranks.get(rank1, 0)
        rank_val2 = ranks.get(rank2, 0)
        
        if rank_val1 > rank_val2:
            high_rank, low_rank = rank1, rank2
        elif rank_val1 < rank_val2:
            high_rank, low_rank = rank2, rank1
        else:
            # 对子
            return f"{rank1}{rank2}"
        
        # 判断是否同花
        if suit1 == suit2:
            return f"{high_rank}{low_rank}s"
        else:
            return f"{high_rank}{low_rank}o"
    
    def _is_pot_raised(self, opponent_actions: List[Dict]) -> bool:
        """判断底池是否被加注"""
        for action in opponent_actions:
            if action.get('action') == 'raise':
                return True
        return False
    
    def _is_3bet_pot(self, opponent_actions: List[Dict]) -> bool:
        """判断是否是3bet底池"""
        raise_count = sum(1 for action in opponent_actions if action.get('action') == 'raise')
        return raise_count >= 2
    
    def _calculate_open_action(self, situation: GTOSituation, position_range: Dict, hand_string: str) -> GTOAction:
        """计算开池行动"""
        open_range = position_range.get('open', [])
        
        if hand_string in open_range:
            # 在范围内，开池加注
            sizing_chart = self.sizing_charts['preflop']['open']
            
            # 根据筹码深度选择尺度
            if situation.stack_size < 30:  # 浅筹码
                sizing = sizing_chart['short_stack']
            elif situation.stack_size > 150:  # 深筹码
                sizing = sizing_chart['deep_stack']
            else:
                sizing = sizing_chart['standard']
            
            amount = int(situation.pot_size * sizing) if situation.pot_size > 0 else int(sizing * 10)
            
            return GTOAction(
                action='raise',
                amount=amount,
                frequency=1.0,
                reasoning=f"{situation.position}位置开池，手牌{hand_string}在标准范围内",
                range_category='value',
                exploit_adjustment=1.0
            )
        else:
            # 不在范围内，弃牌
            return GTOAction(
                action='fold',
                amount=0,
                frequency=1.0,
                reasoning=f"{situation.position}位置开池，手牌{hand_string}不在标准范围内",
                range_category='fold',
                exploit_adjustment=1.0
            )
    
    def _calculate_vs_raise_action(self, situation: GTOSituation, position_range: Dict, hand_string: str) -> GTOAction:
        """计算面对加注的行动 - 使用频率基础决策"""
        # 获取防守范围
        defend_range = position_range.get('defend', position_range.get('call_3bet', []))
        
        # 评估手牌强度
        hand_strength = self._evaluate_hand_strength(situation.hole_cards, situation.community_cards)
        
        # 评估位置优势
        position_advantage = self._evaluate_position_advantage(situation.position)
        
        # 基础频率（根据是否在防守范围内调整）
        if hand_string in defend_range:
            # 在防守范围内，主要跟注
            base_frequencies = {'fold': 0.15, 'call': 0.70, 'raise': 0.15}
        else:
            # 不在范围内，主要弃牌但保留诈唬
            base_frequencies = {'fold': 0.75, 'call': 0.20, 'raise': 0.05}
        
        # 根据手牌强度调整
        if hand_strength >= 0.7:
            # 强牌，更积极的防守
            base_frequencies['call'] += 0.15
            base_frequencies['fold'] -= 0.15
        elif hand_strength >= 0.5:
            # 中等牌力，标准防守
            pass  # 保持基础频率
        else:
            # 弱牌，更保守
            base_frequencies['fold'] += 0.10
            base_frequencies['call'] -= 0.10
        
        # 根据位置调整
        base_frequencies['raise'] *= (0.8 + 0.4 * position_advantage)
        base_frequencies['fold'] *= (1.2 - 0.4 * position_advantage)
        
        # 标准化频率
        total = sum(base_frequencies.values())
        if total > 0:
            frequencies = {k: v/total for k, v in base_frequencies.items()}
        else:
            frequencies = {'fold': 0.7, 'call': 0.3}
        
        # 根据频率选择行动（保持纯GTO随机性）
        import random
        rand = random.random()
        cumulative = 0.0
        
        for action, frequency in frequencies.items():
            cumulative += frequency
            if rand <= cumulative:
                return self._create_gto_action_by_frequency(action, situation, frequency, hand_string)
        
        # 默认返回最后一个行动
        last_action = list(frequencies.keys())[-1]
        return self._create_gto_action_by_frequency(last_action, situation, frequencies[last_action], hand_string)
    
    # 该方法已撤回 - 保持纯GTO随机性
    # def _enhance_decision_consistency(self, frequencies: Dict[str, float]) -> Dict[str, float]:
    #     """增强决策一致性：让AI更倾向于选择高概率行动"""
    #     # 如果某个行动概率过低（<20%），适当降低其权重
    #     # 同时保持长期统计的GTO特性
    #     
    #     enhanced = frequencies.copy()
    #     
    #     # 找到最高概率的行动
    #     max_action = max(frequencies.items(), key=lambda x: x[1])
    #     max_prob = max_action[1]
    #     
    #     # 如果最高概率>60%，进一步增强它
    #     if max_prob > 0.6:
    #         # 增强最高概率行动10%
    #         enhancement = 0.1
    #         enhanced[max_action[0]] = min(0.95, max_prob + enhancement)
    #         
    #         # 相应减少其他行动的概率
    #         other_actions = [k for k in enhanced.keys() if k != max_action[0]]
    #         if other_actions:
    #             reduction = enhancement / len(other_actions)
    #             for action in other_actions:
    #                 enhanced[action] = max(0.01, enhanced[action] - reduction)
    #     
    #     # 重新标准化
    #     total = sum(enhanced.values())
    #     if total > 0:
    #         enhanced = {k: v/total for k, v in enhanced.items()}
    #     
    #     return enhanced
    
    def _create_gto_action_by_frequency(self, action: str, situation: GTOSituation, frequency: float, hand_string: str) -> GTOAction:
        """根据频率创建GTO行动"""
        if action == 'fold':
            return GTOAction(
                action='fold',
                amount=0,
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择（手牌{hand_string}）",
                range_category='fold',
                exploit_adjustment=1.0
            )
        elif action == 'call':
            return GTOAction(
                action='call',
                amount=situation.pot_size,  # 简化处理
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择（手牌{hand_string}）",
                range_category='defend',
                exploit_adjustment=1.0
            )
        elif action == 'raise':
            # 计算下注尺度
            sizing = self._calculate_optimal_sizing(situation)
            amount = int(situation.pot_size * sizing)
            
            return GTOAction(
                action='raise',
                amount=amount,
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择，尺度{sizing:.2f}底池（手牌{hand_string}）",
                range_category='value' if frequency > 0.5 else 'bluff',
                exploit_adjustment=1.0
            )
        
        # 默认返回弃牌
        return GTOAction(
            action='fold',
            amount=0,
            frequency=1.0,
            reasoning=f"GTO策略：默认{action}（手牌{hand_string}）",
            range_category='fold',
            exploit_adjustment=1.0
        )
    
    def _calculate_vs_3bet_action(self, situation: GTOSituation, position_range: Dict, hand_string: str) -> GTOAction:
        """计算面对3bet的行动"""
        call_3bet_range = position_range.get('call_3bet', [])
        
        if hand_string in call_3bet_range:
            return GTOAction(
                action='call',
                amount=int(situation.pot_size * 0.5),  # 简化处理
                frequency=1.0,
                reasoning=f"{situation.position}位置面对3bet，手牌{hand_string}在跟注范围内",
                range_category='call_3bet',
                exploit_adjustment=1.0
            )
        else:
            return GTOAction(
                action='fold',
                amount=0,
                frequency=1.0,
                reasoning=f"{situation.position}位置面对3bet，手牌{hand_string}不在跟注范围内",
                range_category='fold',
                exploit_adjustment=1.0
            )
    
    def _evaluate_hand_strength(self, hole_cards: List[str], community_cards: List[str]) -> float:
        """评估手牌强度 (0-1)"""
        if not hole_cards or len(hole_cards) < 2:
            return 0.0
        
        # 翻牌前评估基于手牌本身强度
        if not community_cards:
            return self._evaluate_preflop_hand_strength(hole_cards)
        
        # 翻牌后评估结合公共牌
        return self._evaluate_postflop_hand_strength(hole_cards, community_cards)
    
    def _evaluate_preflop_hand_strength(self, hole_cards: List[str]) -> float:
        """评估翻牌前手牌强度 (0-1) - 修复版3"""
        if not hole_cards or len(hole_cards) < 2:
            return 0.0
        
        # 格式化手牌
        card1, card2 = hole_cards[0], hole_cards[1]
        rank1, suit1 = card1[1], card1[0]
        rank2, suit2 = card2[1], card2[0]
        
        # 牌力等级
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        rank_val1 = ranks.get(rank1, 0)
        rank_val2 = ranks.get(rank2, 0)
        
        # 基础强度计算
        base_strength = 0.0
        
        # 对子
        if rank1 == rank2:
            # 对子强度：22=0.55, AA=0.95
            base_strength = 0.55 + (rank_val1 - 2) * 0.40 / 12
            return min(0.95, base_strength)
        
        # 高牌因素
        high_card = max(rank_val1, rank_val2)
        low_card = min(rank_val1, rank_val2)
        
        # 高牌奖励（更合理的奖励体系）
        if high_card == 14:  # A高牌
            high_card_bonus = 0.40
        elif high_card == 13:  # K高牌
            high_card_bonus = 0.32
        elif high_card == 12:  # Q高牌
            high_card_bonus = 0.25
        elif high_card == 11:  # J高牌
            high_card_bonus = 0.18
        elif high_card == 10:  # T高牌
            high_card_bonus = 0.12
        else:
            high_card_bonus = (high_card - 2) / 12 * 0.15
        
        # 间隔惩罚（更合理的惩罚）
        gap = high_card - low_card
        if gap <= 2:  # 连牌或1-gap
            gap_penalty = 0
        elif gap <= 4:  # 2-4 gap
            gap_penalty = gap * 0.02
        else:  # 大间隔
            gap_penalty = gap * 0.03
        
        # 同花奖励（提高奖励）
        suited_bonus = 0.15 if suit1 == suit2 else 0
        
        # 连牌奖励（更精细）
        if gap == 1:  # 连牌
            connector_bonus = 0.10
        elif gap == 2:  # 1-gap
            connector_bonus = 0.06
        elif gap == 3:  # 2-gap
            connector_bonus = 0.03
        else:
            connector_bonus = 0
        
        # 特殊强牌调整（更精确）
        if high_card == 14:  # A高牌
            if gap <= 2:  # AK, AQ, AJ, AT, A9, A8, A7
                high_card_bonus += 0.08
            elif gap <= 4:  # A6, A5, A4, A3
                high_card_bonus += 0.05
        elif high_card == 13 and gap <= 2:  # KQ, KJ, KT
            high_card_bonus += 0.05
        elif high_card == 13 and gap <= 4:  # K9, K8, K7, K6
            high_card_bonus += 0.02  # K高牌即使间隔稍大也还行
        
        # 基础强度（提高基础值）
        base_strength = 0.30 + high_card_bonus - gap_penalty + suited_bonus + connector_bonus
        
        # 确保在合理范围内
        return max(0.20, min(0.90, base_strength))
    
    def _evaluate_postflop_hand_strength(self, hole_cards: List[str], community_cards: List[str]) -> float:
        """评估翻牌后手牌强度 (0-1) - 修复版2"""
        import random

        if not community_cards or len(community_cards) < 3:
            return self._evaluate_preflop_hand_strength(hole_cards)

        # 格式化手牌和公共牌
        card1, card2 = hole_cards[0], hole_cards[1]
        rank1, suit1 = card1[1], card1[0]
        rank2, suit2 = card2[1], card2[0]

        # 牌力等级
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

        rank_val1 = ranks.get(rank1, 0)
        rank_val2 = ranks.get(rank2, 0)

        # 计算组合牌力
        all_cards = community_cards + hole_cards

        # 获取所有牌的点数和花色
        card_ranks = []
        card_suits = []
        for card in all_cards:
            card_rank = card[1]
            card_suit = card[0]
            card_ranks.append(ranks.get(card_rank, 0))
            card_suits.append(card_suit)

        # 首先检查是否有口袋对子（超对子）
        if rank1 == rank2:  # 手牌是对子
            # 检查这个对子是否比牌面所有牌都大（超对子）
            community_max_rank = max([ranks.get(card[1], 0) for card in community_cards])
            if rank_val1 > community_max_rank:  # 超对子！
                if rank_val1 >= 13:  # KK+, 超强超对子
                    return 0.85
                elif rank_val1 >= 12:  # QQ, 强超对子
                    return 0.80
                else:  # JJ-, 中等超对子
                    return 0.75

        # 如果不是超对子，继续正常牌型评估
        card_ranks.sort(reverse=True)

        # 检查是否有牌型
        # 1. 同花
        has_flush = False
        suit_counts = {}
        for suit in card_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
            if suit_counts[suit] >= 5:
                has_flush = True
                break

        # 2. 顺子
        has_straight = False
        unique_ranks = sorted(list(set(card_ranks)), reverse=True)
        if len(unique_ranks) >= 5:
            count = 1
            for i in range(1, len(unique_ranks)):
                if unique_ranks[i-1] - unique_ranks[i] == 1:
                    count += 1
                    if count >= 5:
                        has_straight = True
                        break
                else:
                    count = 1
            # 检查A2345的情况
            if not has_straight and 14 in unique_ranks and 2 in unique_ranks and 3 in unique_ranks and 4 in unique_ranks and 5 in unique_ranks:
                has_straight = True

        # 3. 四条
        has_four_of_a_kind = False
        rank_counts = {}
        for rank in card_ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
            if rank_counts[rank] == 4:
                has_four_of_a_kind = True
                break

        # 4. 葫芦
        has_full_house = False
        three_of_a_kind_rank = None
        for rank, count in rank_counts.items():
            if count >= 3:
                three_of_a_kind_rank = rank
                break
        if three_of_a_kind_rank:
            for rank, count in rank_counts.items():
                if rank != three_of_a_kind_rank and count >= 2:
                    has_full_house = True
                    break

        # 5. 三条
        has_three_of_a_kind = False
        if not has_four_of_a_kind and three_of_a_kind_rank:
            has_three_of_a_kind = True

        # 6. 两对
        has_two_pair = False
        pairs = [rank for rank, count in rank_counts.items() if count >= 2]
        if len(pairs) >= 2:
            has_two_pair = True

        # 7. 一对
        has_one_pair = False
        if not has_two_pair and pairs:
            has_one_pair = True

        # 计算牌力值
        if has_flush and has_straight:
            return 0.95  # 同花顺
        elif has_four_of_a_kind:
            return 0.85  # 四条
        elif has_full_house:
            return 0.75  # 葫芦
        elif has_flush:
            return 0.65  # 同花
        elif has_straight:
            return 0.60  # 顺子
        elif has_three_of_a_kind:
            return 0.50  # 三条
        elif has_two_pair:
            return 0.40  # 两对
        elif has_one_pair:
            return 0.30  # 一对
        else:
            # 高牌
            return 0.15  # 高牌
    
    def _evaluate_board_texture(self, community_cards: List[str]) -> Dict:
        """评估牌面纹理"""
        if not community_cards or len(community_cards) < 3:
            return {'texture': 'dry', 'coordination': 0.2}
        
        # 简化的牌面评估
        coordination = self._calculate_coordination(community_cards)
        
        if coordination > 0.7:
            texture = 'wet'  # 湿润牌面
        elif coordination > 0.4:
            texture = 'dynamic'  # 动态牌面
        else:
            texture = 'dry'  # 干燥牌面
        
        return {
            'texture': texture,
            'coordination': coordination,
            'has_flush_draw': self._has_flush_draw(community_cards),
            'has_straight_draw': self._has_straight_draw(community_cards)
        }
    
    def _calculate_coordination(self, community_cards: List[str]) -> float:
        """计算牌面协调性 (0-1)"""
        if len(community_cards) < 3:
            return 0.0
        
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = []
        card_suits = []
        
        for card in community_cards:
            card_ranks.append(ranks.get(card[1], 0))
            card_suits.append(card[0])
        
        # 顺子威胁评估
        coordination = 0.0
        sorted_ranks = sorted(card_ranks)
        
        for i in range(len(sorted_ranks) - 1):
            gap = sorted_ranks[i+1] - sorted_ranks[i]
            if gap <= 2:
                coordination += 0.3
            elif gap <= 3:
                coordination += 0.15
        
        # 同花威胁评估
        suit_counts = {}
        for suit in card_suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        max_suit_count = max(suit_counts.values()) if suit_counts else 0
        if max_suit_count >= 3:
            coordination += 0.2
        
        return min(1.0, coordination)
    
    def _has_flush_draw(self, community_cards: List[str]) -> bool:
        """检查是否有同花听牌"""
        if len(community_cards) < 3:
            return False
        
        suit_counts = {}
        for card in community_cards:
            suit = card[0]
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        
        return max(suit_counts.values()) >= 3
    
    def _has_straight_draw(self, community_cards: List[str]) -> bool:
        """检查是否有顺子听牌"""
        if len(community_cards) < 3:
            return False
        
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = sorted([ranks.get(card[1], 0) for card in community_cards])
        
        # 检查连续牌
        consecutive_count = 1
        for i in range(len(card_ranks) - 1):
            if card_ranks[i+1] - card_ranks[i] <= 1:
                consecutive_count += 1
                if consecutive_count >= 3:
                    return True
            else:
                consecutive_count = 1
        
        return False
    
    def _evaluate_position_advantage(self, position: str) -> float:
        """评估位置优势 (0-1, 越高越好)"""
        position_scores = {
            'BTN': 1.0,   # 按钮位最优
            'CO': 0.9,    # Cut-off
            'HJ': 0.8,    # Hijack  
            'MP': 0.6,    # Middle position
            'UTG': 0.3,   # Under the gun
            'SB': 0.4,    # 小盲（位置劣势但按钮）
            'BB': 0.2     # 大盲（位置最差）
        }
        return position_scores.get(position, 0.5)
    
    def _calculate_action_frequencies(self, hand_strength: float, board_texture: Dict, 
                                    position_advantage: float, situation: GTOSituation, 
                                    street_strategy: Dict) -> Dict[str, float]:
        """计算行动频率"""
        
        # 基础频率
        frequencies = {
            'fold': 0.0,
            'call': 0.0,
            'raise': 0.0
        }
        
        # 根据牌力调整
        if hand_strength >= 0.8:
            # 超强牌：主要价值下注
            frequencies['raise'] = 0.85
            frequencies['call'] = 0.15
            frequencies['fold'] = 0.0
        elif hand_strength >= 0.6:
            # 强牌：价值下注为主
            frequencies['raise'] = 0.65
            frequencies['call'] = 0.35
            frequencies['fold'] = 0.0
        elif hand_strength >= 0.4:
            # 中等牌：混合策略
            frequencies['raise'] = 0.25
            frequencies['call'] = 0.55
            frequencies['fold'] = 0.20
        elif hand_strength >= 0.25:
            # 边缘牌：防守性跟注或诈唬
            frequencies['raise'] = 0.15
            frequencies['call'] = 0.35
            frequencies['fold'] = 0.50
        else:
            # 弱牌：主要弃牌，偶尔诈唬
            frequencies['raise'] = 0.08
            frequencies['call'] = 0.12
            frequencies['fold'] = 0.80
        
        # 根据牌面纹理调整
        if board_texture['texture'] == 'wet':
            # 湿润牌面：更谨慎
            frequencies['raise'] *= 0.8
            frequencies['fold'] *= 1.2
        elif board_texture['texture'] == 'dry':
            # 干燥牌面：可以更激进
            frequencies['raise'] *= 1.1
            frequencies['fold'] *= 0.9
        
        # 根据对手行动历史调整 - 关键修复
        if situation.opponent_actions:
            # 检查是否有攻击性行动（加注）
            aggressive_actions = [action for action in situation.opponent_actions if action.get('action') == 'raise']
            if aggressive_actions:
                # 面对攻击性下注，弱牌应该更多弃牌
                if hand_strength < 0.40:  # 弱牌
                    frequencies['fold'] *= 1.8  # 显著增加弃牌
                    frequencies['raise'] *= 0.3  # 显著减少加注
                    frequencies['call'] *= 0.6   # 减少跟注
                elif hand_strength < 0.60:  # 中等牌
                    frequencies['fold'] *= 1.4  # 增加弃牌
                    frequencies['raise'] *= 0.7  # 减少加注
                # 强牌保持原有策略
        
        # 根据位置调整
        frequencies['raise'] *= (0.8 + 0.4 * position_advantage)
        frequencies['fold'] *= (1.2 - 0.4 * position_advantage)
        
        # 标准化频率
        total = sum(frequencies.values())
        if total > 0:
            frequencies = {k: v/total for k, v in frequencies.items()}
        
        return frequencies
    
    def _select_action_by_frequency(self, frequencies: Dict[str, float], situation: GTOSituation) -> GTOAction:
        """根据频率选择行动"""
        import random
        
        rand = random.random()
        cumulative = 0.0
        
        for action, frequency in frequencies.items():
            cumulative += frequency
            if rand <= cumulative:
                return self._create_gto_action(action, situation, frequency)
        
        # 默认返回最后一个行动
        last_action = list(frequencies.keys())[-1]
        return self._create_gto_action(last_action, situation, frequencies[last_action])
    
    def _create_gto_action(self, action: str, situation: GTOSituation, frequency: float) -> GTOAction:
        """创建GTO行动 - 修复版"""
        if action == 'fold':
            return GTOAction(
                action='fold',
                amount=0,
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择",
                range_category='fold',
                exploit_adjustment=1.0
            )
        elif action == 'call':
            # 获取需要跟注的金额
            call_amount = situation.call_amount if hasattr(situation, 'call_amount') else situation.pot_size
            return GTOAction(
                action='call',
                amount=call_amount,
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择",
                range_category='defend',
                exploit_adjustment=1.0
            )
        elif action == 'raise':
            # 计算下注尺度 - 使用更精确的逻辑
            if situation.street == 'preflop':
                # 翻牌前使用BB为单位的尺度
                hand_strength = self._evaluate_hand_strength(situation.hole_cards, situation.community_cards)
                if situation.position == 'BTN':
                    sizing = 2.2 if hand_strength >= 0.5 else 2.0
                elif situation.position == 'CO':
                    sizing = 2.3 if hand_strength >= 0.5 else 2.1
                elif situation.position == 'SB':
                    sizing = 3.0 if hand_strength >= 0.6 else 2.5
                else:  # BB, MP, UTG
                    sizing = 2.5 if hand_strength >= 0.6 else 2.2
                amount = int(sizing * 10)  # 假设大盲是10
            else:
                # 翻牌后使用底池比例
                sizing = self._calculate_optimal_sizing(situation)
                amount = int(situation.pot_size * sizing)
            
            return GTOAction(
                action='raise',
                amount=amount,
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择，尺度{sizing:.2f}",
                range_category='value' if frequency > 0.5 else 'bluff',
                exploit_adjustment=1.0
            )
        
        # 默认返回弃牌
        return GTOAction(
            action='fold',
            amount=0,
            frequency=1.0,
            reasoning="GTO策略：默认弃牌",
            range_category='fold',
            exploit_adjustment=1.0
        )
    
    def _calculate_optimal_sizing(self, situation: GTOSituation) -> float:
        """计算最优下注尺度 - 修复版"""
        if situation.street == 'preflop':
            return self.sizing_charts['preflop']['open']['standard']
        
        # 翻牌后根据情境选择尺度
        hand_strength = self._evaluate_hand_strength(situation.hole_cards, situation.community_cards)
        
        if situation.street == 'flop':
            flop_strategy = self.postflop_strategies['flop']
            
            # 根据牌力和牌面选择尺度
            if hand_strength >= 0.7:  # 强牌
                return flop_strategy['cbet']['sizing'].get('standard', 0.75)
            elif hand_strength >= 0.5:  # 中等牌
                return flop_strategy['cbet']['sizing'].get('dry', 0.33)
            else:  # 弱牌/诈唬
                return flop_strategy['cbet']['sizing'].get('dry', 0.33)
        
        # 转牌和河牌 - 根据牌力调整尺度
        if hand_strength >= 0.8:  # 超强牌
            return 0.75  # 大尺度
        elif hand_strength >= 0.6:  # 强牌
            return 0.65  # 标准尺度
        elif hand_strength >= 0.4:  # 中等牌
            return 0.50  # 中等尺度
        else:  # 弱牌/诈唬
            return 0.33  # 小尺度
    
    def calculate_gto_action_new(self, context: GTOContext) -> GTOResult:
        """使用新类型系统的GTO决策方法"""
        try:
            # 转换为旧的GTOSituation格式
            situation = GTOSituation(
                street=context.street,
                position=context.position,
                stack_size=context.stack_size,
                pot_size=context.pot_size,
                community_cards=context.community_cards,
                hole_cards=context.hole_cards,
                opponent_actions=context.opponent_actions,
                active_opponents=context.active_opponents
            )
            
            # 使用现有的GTO逻辑
            gto_action = self.calculate_gto_action(situation)
            
            # 转换为新的结果格式
            frequencies = self._calculate_action_frequencies_new(context)
            sizing_rec = self._calculate_sizing_recommendation_new(context)
            
            return GTOResult(
                action=gto_action.action,
                amount=gto_action.amount,
                confidence=gto_action.frequency,
                reasoning=gto_action.reasoning,
                gto_explanation=f"位置: {context.position}; 街道: {context.street}; 筹码深度: {context.stack_size}BB",
                frequencies=frequencies.action_frequencies,
                sizing_recommendation=sizing_rec,
                range_analysis=self._analyze_range_new(context),
                balance_metrics={'balance_score': 0.5, 'predictability': 0.5, 'exploitability': 0.5},
                exploit_opportunities=[]
            )
            
        except Exception as e:
            # 回退到简单的GTO逻辑
            return self._fallback_gto_result_new(context)
    
    def _calculate_action_frequencies_new(self, context: GTOContext) -> FrequencyResult:
        """计算行动频率（新类型系统） - 修复版2"""
        # 简化实现，直接计算频率
        hand_string = self._format_hand(context.hole_cards)
        hand_strength = self._evaluate_hand_strength(context.hole_cards, context.community_cards)
        
        # 基础频率
        frequencies = {
            'fold': 0.0,
            'call': 0.0,
            'raise': 0.0
        }
        
        # 根据牌力调整 - 更精细的分级
        if hand_strength >= 0.85:
            # 超强牌：主要价值下注
            frequencies['raise'] = 0.90
            frequencies['call'] = 0.10
            frequencies['fold'] = 0.0
        elif hand_strength >= 0.75:
            # 很强牌：价值下注为主
            frequencies['raise'] = 0.75
            frequencies['call'] = 0.25
            frequencies['fold'] = 0.0
        elif hand_strength >= 0.65:
            # 强牌：混合策略
            frequencies['raise'] = 0.55
            frequencies['call'] = 0.45
            frequencies['fold'] = 0.0
        elif hand_strength >= 0.55:
            # 中等偏强：更多跟注
            frequencies['raise'] = 0.35
            frequencies['call'] = 0.65
            frequencies['fold'] = 0.0
        elif hand_strength >= 0.45:
            # 中等牌：标准混合策略
            frequencies['raise'] = 0.20
            frequencies['call'] = 0.60
            frequencies['fold'] = 0.20
        elif hand_strength >= 0.35:
            # 中等偏弱：防守性跟注
            frequencies['raise'] = 0.12
            frequencies['call'] = 0.48
            frequencies['fold'] = 0.40
        elif hand_strength >= 0.25:
            # 边缘牌：主要弃牌但保留诈唬
            frequencies['raise'] = 0.08
            frequencies['call'] = 0.22
            frequencies['fold'] = 0.70
        else:
            # 弱牌：主要弃牌，偶尔诈唬
            frequencies['raise'] = 0.05
            frequencies['call'] = 0.10
            frequencies['fold'] = 0.85
        
        # 根据位置和特殊情况调整
        position_advantage = self._evaluate_position_advantage(context.position)
        
        # 大盲位特殊防守逻辑
        if context.position == 'BB':
            # 大盲位已经投入1BB，需要更宽的防守范围
            if hand_strength >= 0.25:  # 降低防守门槛到0.25
                frequencies['fold'] *= 0.4  # 显著减少弃牌（从0.6改为0.4）
                frequencies['call'] *= 1.5  # 大幅增加跟注
                if hand_strength >= 0.40:  # 降低加注门槛
                    frequencies['raise'] *= 1.3  # 强牌可以更多加注
            else:
                # 即使很弱的牌也要保留一些防守频率
                frequencies['fold'] *= 0.8  # 减少弃牌
                frequencies['call'] *= 1.2  # 增加跟注
        
        # 小盲位面对加注时的防守
        elif context.position == 'SB' and context.opponent_actions:
            # 如果前面有加注，小盲位需要更谨慎
            if any(action.get('action') == 'raise' for action in context.opponent_actions):
                if hand_strength < 0.50:
                    frequencies['fold'] *= 1.2  # 增加弃牌
                    frequencies['raise'] *= 0.8  # 减少加注
        
        # 位置越好，越激进（排除已处理的大盲位）
        if context.position != 'BB':
            if position_advantage >= 0.8:  # BTN
                frequencies['raise'] *= 1.2
                frequencies['fold'] *= 0.8
            elif position_advantage >= 0.6:  # CO
                frequencies['raise'] *= 1.1
                frequencies['fold'] *= 0.9
            elif position_advantage <= 0.3:  # UTG, MP
                frequencies['raise'] *= 0.8  # 更早位置更保守
                frequencies['fold'] *= 1.2  # 更早位置更多弃牌
        
        # 标准化频率
        total = sum(frequencies.values())
        if total > 0:
            frequencies = {k: v/total for k, v in frequencies.items()}
        
        return FrequencyResult(
            action_frequencies=frequencies,
            mixed_strategy=frequencies,
            equilibrium_deviation=0.03,  # 进一步降低偏差
            confidence_level=0.88
        )
    
    def _calculate_sizing_recommendation_new(self, context: GTOContext) -> SizingRecommendation:
        """计算下注尺度建议（新类型系统） - 修复版2"""
        hand_strength = self._evaluate_hand_strength(context.hole_cards, context.community_cards)
        
        # 根据牌力和位置计算推荐尺度
        if hand_strength >= 0.8:
            # 超强牌：大尺度价值下注
            if context.position in ['BTN', 'CO']:
                optimal_sizing = 0.75  # 位置好，可以大尺度
            else:
                optimal_sizing = 0.65   # 位置差，稍微保守
        elif hand_strength >= 0.7:
            # 很强牌：标准价值下注
            optimal_sizing = 0.55
        elif hand_strength >= 0.6:
            # 强牌：中等尺度
            optimal_sizing = 0.45
        elif hand_strength >= 0.5:
            # 中等偏强：小中等尺度
            optimal_sizing = 0.33
        elif hand_strength >= 0.4:
            # 中等牌：小尺度
            optimal_sizing = 0.25
        else:
            # 弱牌/诈唬：最小尺度
            optimal_sizing = 0.20
        
        # 根据街道调整
        if context.street == 'preflop':
            # 翻牌前根据位置和牌力调整
            if context.position == 'BTN':
                optimal_sizing = 2.2 if hand_strength >= 0.5 else 2.0
            elif context.position == 'CO':
                optimal_sizing = 2.3 if hand_strength >= 0.5 else 2.1
            elif context.position == 'SB':
                optimal_sizing = 3.0 if hand_strength >= 0.6 else 2.5
            else:  # BB, MP, UTG
                optimal_sizing = 2.5 if hand_strength >= 0.6 else 2.2
        elif context.street == 'turn':
            optimal_sizing *= 1.1  # 转牌可以稍微大点
        elif context.street == 'river':
            optimal_sizing *= 1.2  # 河牌可以更大
        
        # 根据筹码深度调整 - 防止过度下注
        if context.stack_size < 50:  # 浅筹码
            optimal_sizing = min(optimal_sizing, 0.75 if context.street != 'preflop' else 2.5)
        
        # 确保尺度在合理范围内
        if context.street == 'preflop':
            optimal_sizing = max(2.0, min(4.0, optimal_sizing))  # 翻牌前2-4BB
        else:
            optimal_sizing = max(0.20, min(1.0, optimal_sizing))  # 翻牌后20%-100%底池
        
        return SizingRecommendation(
            optimal_sizing=optimal_sizing,
            min_sizing=optimal_sizing * 0.8,
            max_sizing=optimal_sizing * 1.2,
            explanation=f"基于牌力{hand_strength:.2f}位置{context.position}的GTO推荐：{optimal_sizing:.2f}",
            sizing_type='value' if hand_strength >= 0.6 else 'probe'
        )
    
    def _analyze_range_new(self, context: GTOContext) -> Dict[str, Any]:
        """分析手牌范围（新类型系统）"""
        hand_string = self._format_hand(context.hole_cards)
        
        return {
            'hand': hand_string,
            'position': context.position,
            'street': context.street,
            'in_open_range': self._is_in_open_range(hand_string, context.position),
            'in_defend_range': self._is_in_defend_range(hand_string, context.position),
            'range_strength': self._calculate_range_strength(hand_string, context.position),
            'recommendation': {
                'hand': hand_string,
                'position': context.position,
                'action': 'open' if self._is_in_open_range(hand_string, context.position) else 'fold',
                'is_in_range': self._is_in_open_range(hand_string, context.position),
                'strength': self._calculate_range_strength(hand_string, context.position),
                'recommendation': '在推荐范围内' if self._is_in_open_range(hand_string, context.position) else '不在推荐范围内，建议弃牌',
                'range_size': len(self.preflop_ranges.get(context.position, {}).get('open', []))
            }
        }
    
    def _fallback_gto_result_new(self, context: GTOContext) -> GTOResult:
        """回退GTO结果（新类型系统）"""
        return GTOResult(
            action='call',
            amount=context.call_amount,
            confidence=0.5,
            reasoning='GTO分析失败，使用保守策略',
            gto_explanation='回退到基础策略',
            frequencies={'call': 0.7, 'fold': 0.3},
            sizing_recommendation=SizingRecommendation(
                optimal_sizing=0.5,
                min_sizing=0.3,
                max_sizing=0.7,
                explanation='回退尺度建议',
                sizing_type='mixed'
            ),
            range_analysis={'hand': 'unknown', 'position': context.position, 'recommendation': {'action': 'call'}},
            balance_metrics={'balance_score': 0.5, 'predictability': 0.5, 'exploitability': 0.5},
            exploit_opportunities=[]
        )
    
    def _is_in_open_range(self, hand_string: str, position: str) -> bool:
        """检查手牌是否在开池范围内"""
        position_range = self.preflop_ranges.get(position, {})
        open_range = position_range.get('open', [])
        return hand_string in open_range
    
    def _is_in_defend_range(self, hand_string: str, position: str) -> bool:
        """检查手牌是否在防守范围内"""
        position_range = self.preflop_ranges.get(position, {})
        defend_range = position_range.get('defend', position_range.get('call_3bet', []))
        return hand_string in defend_range
    
    def _calculate_range_strength(self, hand_string: str, position: str) -> float:
        """计算范围强度（0-1）"""
        position_range = self.preflop_ranges.get(position, {})
        open_range = position_range.get('open', [])
        
        if not open_range:
            return 0.0
        
        try:
            hand_index = open_range.index(hand_string)
            return 1.0 - (hand_index / len(open_range))
        except ValueError:
            return 0.0