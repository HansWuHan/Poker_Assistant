"""
范围管理器 - 管理GTO起手牌范围和范围分析
"""
import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class RangeCategory:
    """范围分类"""
    name: str
    hands: Set[str]
    frequency: float
    description: str


class RangeManager:
    """GTO范围管理器"""
    
    def __init__(self):
        # 标准52张牌
        self.suits = ['S', 'H', 'D', 'C']  # 黑桃, 红桃, 方块, 梅花
        self.ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        # 加载预定义范围
        self.preflop_ranges = self._initialize_preflop_ranges()
        self.postflop_ranges = self._initialize_postflop_ranges()
        
        # 范围分析缓存
        self.range_cache = {}
        
    def _initialize_preflop_ranges(self) -> Dict:
        """初始化翻牌前范围"""
        return {
            'BTN': {
                'open': self._generate_btn_open_range(),
                '3bet': self._generate_btn_3bet_range(),
                'call_3bet': self._generate_btn_call_3bet_range()
            },
            'CO': {
                'open': self._generate_co_open_range(),
                '3bet': self._generate_co_3bet_range(),
                'call_3bet': self._generate_co_call_3bet_range()
            },
            'HJ': {
                'open': self._generate_hj_open_range(),
                '3bet': self._generate_hj_3bet_range(),
                'call_3bet': self._generate_hj_call_3bet_range()
            },
            'MP': {
                'open': self._generate_mp_open_range(),
                '3bet': self._generate_mp_3bet_range(),
                'call_3bet': self._generate_mp_call_3bet_range()
            },
            'UTG': {
                'open': self._generate_utg_open_range(),
                '3bet': self._generate_utg_3bet_range(),
                'call_3bet': self._generate_utg_call_3bet_range()
            },
            'SB': {
                'open': self._generate_sb_open_range(),
                '3bet': self._generate_sb_3bet_range(),
                'call_3bet': self._generate_sb_call_3bet_range()
            },
            'BB': {
                'defend': self._generate_bb_defend_range(),
                '3bet': self._generate_bb_3bet_range(),
                'call_3bet': self._generate_bb_call_3bet_range()
            }
        }
    
    def _initialize_postflop_ranges(self) -> Dict:
        """初始化翻牌后范围"""
        return {
            'value_bet': self._generate_value_bet_range(),
            'bluff': self._generate_bluff_range(),
            'check_back': self._generate_check_back_range(),
            'call': self._generate_call_range(),
            'fold': self._generate_fold_range()
        }
    
    def _generate_btn_open_range(self) -> Set[str]:
        """生成按钮位开池范围 (约50%范围)"""
        # 按钮位可以玩很宽的范围
        premium_pairs = ['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
        
        # 同花牌
        suited_aces = ['A2s', 'A3s', 'A4s', 'A5s', 'A6s', 'A7s', 'A8s', 'A9s', 'ATs', 'AJs', 'AQs', 'AKs']
        suited_kings = ['K2s', 'K3s', 'K4s', 'K5s', 'K6s', 'K7s', 'K8s', 'K9s', 'KTs', 'KJs', 'KQs']
        suited_queens = ['Q2s', 'Q3s', 'Q4s', 'Q5s', 'Q6s', 'Q7s', 'Q8s', 'Q9s', 'QTs', 'QJs']
        suited_jacks = ['J2s', 'J3s', 'J4s', 'J5s', 'J6s', 'J7s', 'J8s', 'J9s', 'JTs']
        suited_tens = ['T2s', 'T3s', 'T4s', 'T5s', 'T6s', 'T7s', 'T8s', 'T9s']
        suited_misc = ['987s', '876s', '765s', '654s', '543s', '432s', '32s']
        
        # 不同花牌
        offsuit_aces = ['A2o', 'A3o', 'A4o', 'A5o', 'A6o', 'A7o', 'A8o', 'A9o', 'ATo', 'AJo', 'AQo', 'AKo']
        offsuit_kings = ['K9o', 'KTo', 'KJo', 'KQo']
        offsuit_queens = ['Q9o', 'QTo', 'QJo']
        offsuit_jacks = ['J9o', 'JTo']
        offsuit_tens = ['T9o']
        
        return set(premium_pairs + suited_aces + suited_kings + suited_queens + 
                  suited_jacks + suited_tens + suited_misc + 
                  offsuit_aces + offsuit_kings + offsuit_queens + offsuit_jacks + offsuit_tens)
    
    def _generate_btn_3bet_range(self) -> Set[str]:
        """生成按钮位3bet范围 (约8%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs', 'AJs', 'KQs'}
    
    def _generate_btn_call_3bet_range(self) -> Set[str]:
        """生成按钮位跟注3bet范围 (约25%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_utg_open_range(self) -> Set[str]:
        """生成UTG开池范围 (约15%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KTs',
                'QJs', 'QTs',
                'JTs', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_utg_3bet_range(self) -> Set[str]:
        """生成UTG3bet范围 (约5%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'AKs', 'AKo', 'AQs'}
    
    def _generate_utg_call_3bet_range(self) -> Set[str]:
        """生成UTG跟注3bet范围 (约15%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_sb_open_range(self) -> Set[str]:
        """生成小盲开池范围 (约35%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s',
                'QJs', 'QJo', 'QTs', 'QTo', 'Q9s',
                'JTs', 'JTo', 'J9s', 'J8s',
                'T9s', 'T8s', 'T7s',
                '98s', '97s',
                '87s', '86s',
                '76s', '75s',
                '65s', '64s',
                '54s', '53s'}
    
    def _generate_sb_3bet_range(self) -> Set[str]:
        """生成小盲3bet范围 (约8%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs', 'AJs', 'KQs'}
    
    def _generate_sb_call_3bet_range(self) -> Set[str]:
        """生成小盲跟注3bet范围 (约20%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_bb_defend_range(self) -> Set[str]:
        """生成大盲防守范围 (约45%范围)"""
        # 大盲需要防守更宽的范围
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',
                'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s',
                'QJs', 'QJo', 'QTs', 'QTo', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s',
                'JTs', 'JTo', 'J9s', 'J8s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s',
                'T9s', 'T8s', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s',
                '98s', '97s', '96s', '95s', '94s', '93s', '92s',
                '87s', '86s', '85s', '84s', '83s', '82s',
                '76s', '75s', '74s', '73s', '72s',
                '65s', '64s', '63s', '62s',
                '54s', '53s', '52s',
                '43s', '42s',
                '32s'}
    
    def _generate_bb_3bet_range(self) -> Set[str]:
        """生成大盲3bet范围 (约8%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs', 'AJs', 'KQs'}
    
    def _generate_bb_call_3bet_range(self) -> Set[str]:
        """生成大盲跟注3bet范围 (约25%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_co_open_range(self) -> Set[str]:
        """生成CO开池范围 (约30%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s',
                'QJs', 'QJo', 'QTs', 'QTo', 'Q9s',
                'JTs', 'JTo', 'J9s', 'J8s',
                'T9s', 'T8s', 'T7s',
                '98s', '97s', '96s',
                '87s', '86s', '85s',
                '76s', '75s', '74s',
                '65s', '64s', '63s',
                '54s', '53s', '52s',
                '43s', '42s', '32s'}
    
    def _generate_co_3bet_range(self) -> Set[str]:
        """生成CO3bet范围 (约7%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs', 'AJs', 'KQs'}
    
    def _generate_co_call_3bet_range(self) -> Set[str]:
        """生成CO跟注3bet范围 (约20%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_hj_open_range(self) -> Set[str]:
        """生成HJ开池范围 (约25%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s',
                'QJs', 'QJo', 'QTs', 'QTo', 'Q9s',
                'JTs', 'JTo', 'J9s', 'J8s',
                'T9s', 'T8s', 'T7s',
                '98s', '97s', '96s',
                '87s', '86s', '85s',
                '76s', '75s', '74s',
                '65s', '64s', '63s',
                '54s', '53s'}
    
    def _generate_hj_3bet_range(self) -> Set[str]:
        """生成HJ3bet范围 (约6%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs', 'AJs'}
    
    def _generate_hj_call_3bet_range(self) -> Set[str]:
        """生成HJ跟注3bet范围 (约18%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_mp_open_range(self) -> Set[str]:
        """生成MP开池范围 (约20%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KTs', 'K9s',
                'QJs', 'QJo', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', 'T8s', '98s', '97s', '87s', '86s', '76s', '75s', '65s', '64s', '54s'}
    
    def _generate_mp_3bet_range(self) -> Set[str]:
        """生成MP3bet范围 (约5%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', 'AKo', 'AQs'}
    
    def _generate_mp_call_3bet_range(self) -> Set[str]:
        """生成MP跟注3bet范围 (约15%范围)"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KJs', 'KTs', 'K9s',
                'QJs', 'QTs', 'Q9s',
                'JTs', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_value_bet_range(self) -> Set[str]:
        """生成价值下注范围"""
        # 这取决于具体的牌面，这里只是一个示例
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo'}
    
    def _generate_bluff_range(self) -> Set[str]:
        """生成诈唬范围"""
        # 好的诈唬牌通常有阻断效应
        return {'A5s', 'A4s', 'A3s', 'A2s', 'K9s', 'Q9s', 'J9s', 'T9s', '98s', '87s', '76s', '65s', '54s'}
    
    def _generate_check_back_range(self) -> Set[str]:
        """生成过牌范围"""
        return {'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s'}
    
    def _generate_call_range(self) -> Set[str]:
        """生成跟注范围"""
        return {'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                'AKs', 'AKo', 'AQs', 'AQo', 'AJs', 'AJo', 'ATs', 'ATo', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s',
                'KQs', 'KQo', 'KJs', 'KJo', 'KTs', 'KTo', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s',
                'QJs', 'QJo', 'QTs', 'QTo', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s',
                'JTs', 'JTo', 'J9s', 'J8s', 'J7s', 'J6s',
                'T9s', 'T8s', 'T7s', 'T6s',
                '98s', '97s', '96s', '95s',
                '87s', '86s', '85s', '84s',
                '76s', '75s', '74s',
                '65s', '64s', '63s',
                '54s', '53s', '52s',
                '43s', '42s',
                '32s'}
    
    def _generate_fold_range(self) -> Set[str]:
        """生成弃牌范围"""
        # 理论上任何牌都可以弃牌，这里表示弱牌
        return {'72o', '72s', '82o', '82s', '92o', '92s', 'T2o', 'T2s', 'J2o', 'J2s', 'Q2o', 'Q2s', 'K2o'}
    
    def get_range_for_situation(self, position: str, action: str, street: str = 'preflop') -> Set[str]:
        """
        获取特定情境下的范围
        
        Args:
            position: 位置
            action: 行动 (open, 3bet, call_3bet, defend)
            street: 街道
            
        Returns:
            手牌范围集合
        """
        if street == 'preflop':
            position_ranges = self.preflop_ranges.get(position, {})
            return position_ranges.get(action, set())
        else:
            return self.postflop_ranges.get(action, set())
    
    def is_hand_in_range(self, hand: str, range_set: Set[str]) -> bool:
        """
        检查手牌是否在范围内
        
        Args:
            hand: 手牌 (如 "AKs")
            range_set: 范围集合
            
        Returns:
            是否在范围内
        """
        return hand in range_set
    
    def get_range_strength(self, hand: str, range_set: Set[str]) -> float:
        """
        获取手牌在范围内的强度
        
        Args:
            hand: 手牌
            range_set: 范围集合
            
        Returns:
            强度值 (0-1)
        """
        if hand not in range_set:
            return 0.0
        
        # 简化的强度计算
        # 这里可以根据具体的手牌强度进行更复杂的计算
        if hand in ['AA', 'KK', 'QQ', 'JJ', 'AKs', 'AKo']:
            return 1.0
        elif hand in ['TT', '99', '88', 'AQs', 'AQo', 'AJs', 'KQs']:
            return 0.9
        elif hand in ['77', '66', '55', 'AJs', 'ATs', 'KJs', 'QJs']:
            return 0.8
        elif hand in ['44', '33', '22', 'A9s', 'A8s', 'KJs', 'KTs', 'QJs', 'QTs']:
            return 0.7
        else:
            return 0.5
    
    def get_range_advice(self, hand: str, position: str, action: str, street: str = 'preflop') -> Dict:
        """
        获取范围建议
        
        Args:
            hand: 手牌
            position: 位置
            action: 行动
            street: 街道
            
        Returns:
            建议字典
        """
        range_set = self.get_range_for_situation(position, action, street)
        is_in_range = self.is_hand_in_range(hand, range_set)
        strength = self.get_range_strength(hand, range_set)
        
        if is_in_range:
            if strength >= 0.8:
                recommendation = "强牌，推荐价值下注"
            elif strength >= 0.6:
                recommendation = "中等强度，可以玩"
            else:
                recommendation = "边缘牌，谨慎游戏"
        else:
            recommendation = "不在推荐范围内，建议弃牌"
        
        return {
            'hand': hand,
            'position': position,
            'action': action,
            'is_in_range': is_in_range,
            'strength': strength,
            'recommendation': recommendation,
            'range_size': len(range_set)
        }
    
    def calculate_range_vs_range_equity(self, hero_range: Set[str], villain_range: Set[str]) -> float:
        """
        计算范围对范围的胜率
        
        Args:
            hero_range: 我方范围
            villain_range: 对手范围
            
        Returns:
            平均胜率
        """
        if not hero_range or not villain_range:
            return 0.5
        
        # 简化的胜率计算
        # 在实际应用中，这里应该使用更复杂的蒙特卡洛模拟
        total_equity = 0.0
        count = 0
        
        for hero_hand in hero_range:
            for villain_hand in villain_range:
                # 避免相同的牌
                if not self._hands_conflict(hero_hand, villain_hand):
                    equity = self._estimate_hand_vs_hand_equity(hero_hand, villain_hand)
                    total_equity += equity
                    count += 1
        
        return total_equity / count if count > 0 else 0.5
    
    def _hands_conflict(self, hand1: str, hand2: str) -> bool:
        """检查两手牌是否有冲突（有相同的牌）"""
        # 简化的冲突检测
        # 这里应该实现更完整的逻辑
        return False
    
    def _estimate_hand_vs_hand_equity(self, hand1: str, hand2: str) -> float:
        """估算手牌对局胜率"""
        # 简化的胜率估算
        # 这里应该使用更精确的算法
        strength1 = self.get_range_strength(hand1, {hand1})
        strength2 = self.get_range_strength(hand2, {hand2})
        
        if strength1 + strength2 > 0:
            return strength1 / (strength1 + strength2)
        return 0.5
    
    def get_range_categories(self, range_set: Set[str]) -> Dict[str, RangeCategory]:
        """
        将范围分解为不同类别
        
        Args:
            range_set: 范围集合
            
        Returns:
            分类字典
        """
        categories = {}
        
        # 对子
        pairs = {hand for hand in range_set if len(hand) == 2 and hand[0] == hand[1]}
        if pairs:
            categories['pairs'] = RangeCategory(
                name='对子',
                hands=pairs,
                frequency=len(pairs) / len(range_set),
                description='口袋对子'
            )
        
        # 同花牌
        suited = {hand for hand in range_set if len(hand) == 4 and hand[2] == 's'}
        if suited:
            categories['suited'] = RangeCategory(
                name='同花',
                hands=suited,
                frequency=len(suited) / len(range_set),
                description='同花牌'
            )
        
        # 不同花牌
        offsuit = {hand for hand in range_set if len(hand) == 4 and hand[2] == 'o'}
        if offsuit:
            categories['offsuit'] = RangeCategory(
                name='不同花',
                hands=offsuit,
                frequency=len(offsuit) / len(range_set),
                description='不同花牌'
            )
        
        return categories