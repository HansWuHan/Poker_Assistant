"""
GTO策略包 - 基于博弈论最优策略的德州扑克决策引擎

提供理论最优的扑克策略，包括：
- 起手牌范围管理
- 下注尺度优化  
- 平衡范围构建
- 频率基础决策

模块结构：
- core: GTO核心算法
- advisor: GTO策略顾问
- calculator: 频率计算器
- optimizer: 尺度优化器
- manager: 范围管理器
"""

# 核心组件
from .gto_core import GTOCore, GTOSituation, GTOAction
from .gto_advisor import GTOAdvisor

# 工具组件
from .frequency_calculator import FrequencyCalculator
from .sizing_optimizer import SizingOptimizer
from .range_manager import RangeManager

# 类型定义
from .types import GTOContext, GTOResult, FrequencyResult, SizingRecommendation

__all__ = [
    # 核心组件
    'GTOCore',
    'GTOSituation', 
    'GTOAction',
    'GTOAdvisor',
    
    # 工具组件
    'FrequencyCalculator',
    'SizingOptimizer', 
    'RangeManager',
    
    # 类型定义
    'GTOContext',
    'GTOResult',
    'FrequencyResult',
    'SizingRecommendation'
]