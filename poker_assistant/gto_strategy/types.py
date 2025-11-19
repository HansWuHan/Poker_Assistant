"""
GTO策略类型定义

定义GTO策略相关的数据结构和类型
"""

from typing import Dict, List, Any, Optional, NamedTuple, Union
from dataclasses import dataclass


@dataclass
class GTOContext:
    """GTO决策上下文"""
    street: str
    position: str
    stack_size: int
    pot_size: int
    community_cards: List[str]
    hole_cards: List[str]
    opponent_actions: List[Dict[str, Any]]
    active_opponents: int
    call_amount: int = 0
    valid_actions: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.valid_actions is None:
            self.valid_actions = []


@dataclass 
class GTOResult:
    """GTO策略结果"""
    action: str
    amount: int
    confidence: float
    reasoning: str
    gto_explanation: str
    frequencies: Dict[str, float]
    sizing_recommendation: 'SizingRecommendation'
    range_analysis: Dict[str, Any]
    balance_metrics: Dict[str, float]
    exploit_opportunities: List[str]
    
    def __post_init__(self):
        # 确保所有字段都有默认值
        if not hasattr(self, 'balance_metrics'):
            self.balance_metrics = {'balance_score': 0.5, 'predictability': 0.5, 'exploitability': 0.5}
        if not hasattr(self, 'exploit_opportunities'):
            self.exploit_opportunities = []


@dataclass
class FrequencyResult:
    """频率分析结果"""
    action_frequencies: Dict[str, float]
    mixed_strategy: Dict[str, float]
    equilibrium_deviation: float
    confidence_level: float
    
    def get_primary_action(self) -> str:
        """获取主要行动（频率最高的）"""
        if not self.action_frequencies:
            return "fold"
        return max(self.action_frequencies.items(), key=lambda x: x[1])[0]
    
    def get_action_probability(self, action: str) -> float:
        """获取特定行动的概率"""
        return self.action_frequencies.get(action, 0.0)


@dataclass
class SizingRecommendation:
    """下注尺度建议"""
    optimal_sizing: float  # 百分比，如 2.5 表示 250% 底池
    min_sizing: float
    max_sizing: float
    explanation: str
    sizing_type: str  # 'value', 'bluff', 'mixed', 'probe'
    
    def get_absolute_amount(self, pot_size: int) -> int:
        """获取绝对下注金额"""
        return int(pot_size * self.optimal_sizing)
    
    def is_valid_sizing(self, amount: int, pot_size: int) -> bool:
        """检查下注金额是否在推荐范围内"""
        min_amount = int(pot_size * self.min_sizing)
        max_amount = int(pot_size * self.max_sizing)
        return min_amount <= amount <= max_amount


@dataclass
class RangeSpecification:
    """范围规格定义"""
    position: str
    street: str
    stack_depth: str  # 'deep', 'medium', 'short'
    hand_categories: List[str]  # ['pairs', 'suited_connectors', 'broadways', ...]
    minimum_strength: float  # 0.0 - 1.0
    
    def matches_situation(self, position: str, street: str, stack_size: int, 
                         pot_size: int) -> bool:
        """检查是否匹配当前情况"""
        if self.position != position or self.street != street:
            return False
            
        # 计算筹码深度
        stack_depth = self._calculate_stack_depth(stack_size, pot_size)
        return stack_depth == self.stack_depth
    
    def _calculate_stack_depth(self, stack_size: int, pot_size: int) -> str:
        """计算筹码深度分类"""
        if pot_size == 0:
            return 'deep'
        
        spr = stack_size / pot_size
        if spr > 15:
            return 'deep'
        elif spr > 6:
            return 'medium'
        else:
            return 'short'


@dataclass
class BoardAnalysis:
    """牌面分析结果"""
    texture: str  # 'dry', 'wet', 'dynamic', 'static'
    coordination: float  # 0.0 - 1.0，协调性
    draw_heaviness: float  # 0.0 - 1.0，听牌密度
    premium_hands: List[str]  # 可能的强牌组合
    
    def is_dry(self) -> bool:
        """是否为干燥牌面"""
        return self.texture == 'dry' and self.draw_heaviness < 0.3
    
    def is_wet(self) -> bool:
        """是否为湿润牌面"""
        return self.texture == 'wet' or self.draw_heaviness > 0.6


# 枚举类型定义
class ActionType:
    """行动类型常量"""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "allin"


class Position:
    """位置常量"""
    UTG = "UTG"
    MP = "MP"
    HJ = "HJ"
    CO = "CO"
    BTN = "BTN"
    SB = "SB"
    BB = "BB"


class Street:
    """街道常量"""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


# 工具函数
def validate_gto_result(result: GTOResult) -> bool:
    """验证GTO结果的有效性"""
    if not result.action or result.confidence < 0 or result.confidence > 1:
        return False
    
    if not result.frequencies or sum(result.frequencies.values()) <= 0:
        return False
    
    return True


def merge_frequency_results(results: List[FrequencyResult]) -> FrequencyResult:
    """合并多个频率分析结果"""
    if not results:
        return FrequencyResult({}, {}, 0.0, 0.0)
    
    # 简单的平均值合并策略
    merged_frequencies = {}
    total_confidence = 0.0
    
    for result in results:
        total_confidence += result.confidence_level
        for action, freq in result.action_frequencies.items():
            if action not in merged_frequencies:
                merged_frequencies[action] = 0.0
            merged_frequencies[action] += freq * result.confidence_level
    
    # 标准化
    if total_confidence > 0:
        for action in merged_frequencies:
            merged_frequencies[action] /= total_confidence
    
    return FrequencyResult(
        action_frequencies=merged_frequencies,
        mixed_strategy=merged_frequencies,
        equilibrium_deviation=sum(r.equilibrium_deviation for r in results) / len(results),
        confidence_level=total_confidence / len(results)
    )