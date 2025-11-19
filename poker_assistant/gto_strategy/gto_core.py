"""
GTO策略核心引擎
实现基于博弈论最优的德州扑克决策算法
"""
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class GTOSituation:
    """GTO情境数据结构"""
    street: str  # preflop, flop, turn, river
    position: str  # BTN, SB, BB, UTG, MP, CO, HJ
    stack_size: int  # 有效筹码深度
    pot_size: int  # 底池大小
    community_cards: List[str]  # 公共牌
    hole_cards: List[str]  # 手牌
    opponent_actions: List[Dict]  # 对手行动历史
    active_opponents: int  # 活跃对手数量


@dataclass
class GTOAction:
    """GTO行动建议"""
    action: str  # fold, call, raise
    amount: int  # 建议金额
    frequency: float  # 执行频率
    reasoning: str  # 决策理由
    range_category: str  # 范围分类
    exploit_adjustment: float  # 剥削调整因子


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
        rank1, suit1 = card1[1], card1[0]
        rank2, suit2 = card2[1], card2[0]
        
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
        """计算面对加注的行动"""
        defend_range = position_range.get('defend', position_range.get('call_3bet', []))
        
        if hand_string in defend_range:
            # 在防守范围内，跟注
            return GTOAction(
                action='call',
                amount=situation.pot_size,  # 简化处理
                frequency=1.0,
                reasoning=f"{situation.position}位置防守，手牌{hand_string}在防守范围内",
                range_category='defend',
                exploit_adjustment=1.0
            )
        else:
            # 不在范围内，弃牌
            return GTOAction(
                action='fold',
                amount=0,
                frequency=1.0,
                reasoning=f"{situation.position}位置防守，手牌{hand_string}不在防守范围内",
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
        # 简化实现：基于现有逻辑
        if not community_cards:
            return 0.5  # 翻牌前中性评估
        
        # 这里可以集成更复杂的牌力评估
        # 暂时返回一个基于牌型的简单评估
        return 0.6
    
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
        """创建GTO行动"""
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
            return GTOAction(
                action='call',
                amount=situation.pot_size,  # 简化处理
                frequency=frequency,
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择",
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
                reasoning=f"GTO策略：基于频率分析，{action}是最优选择，尺度{sizing:.2f}底池",
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
        """计算最优下注尺度"""
        if situation.street == 'preflop':
            return self.sizing_charts['preflop']['open']['standard']
        
        # 翻牌后根据情境选择尺度
        if situation.street == 'flop':
            flop_strategy = self.postflop_strategies['flop']
            
            # 简化逻辑：根据筹码深度和底池大小选择
            if situation.stack_size > situation.pot_size * 10:  # 深筹码
                return flop_strategy['cbet']['sizing'].get('standard', 0.75)
            else:  # 浅筹码
                return flop_strategy['cbet']['sizing'].get('dry', 0.33)
        
        # 转牌和河牌使用标准尺度
        return 0.65  # 2/3底池作为默认值