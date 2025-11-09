"""
对手建模模块
跨局记录和分析对手的打法特点
"""
from typing import Dict, List, Any, Optional
from collections import defaultdict


class OpponentModeler:
    """对手建模器 - 记录和分析对手行为"""
    
    def __init__(self):
        """初始化对手建模器"""
        # 对手档案：{player_name: profile}
        self.opponent_profiles: Dict[str, Dict[str, Any]] = {}
        
        # 当前局的临时记录
        self.current_round_actions: Dict[str, List[Dict]] = defaultdict(list)
    
    def start_new_round(self):
        """开始新一局，清空临时记录"""
        self.current_round_actions.clear()
    
    def record_action(self, 
                     player_name: str, 
                     action: str, 
                     amount: int = 0,
                     street: str = "",
                     pot_size: int = 0,
                     community_cards: List[str] = None):
        """
        记录对手行动
        
        Args:
            player_name: 玩家名称
            action: 行动类型 (fold/call/raise/check)
            amount: 金额
            street: 街道 (preflop/flop/turn/river)
            pot_size: 底池大小
            community_cards: 公共牌
        """
        # 初始化对手档案
        if player_name not in self.opponent_profiles:
            self.opponent_profiles[player_name] = {
                "total_actions": 0,
                "fold_count": 0,
                "call_count": 0,
                "raise_count": 0,
                "check_count": 0,
                "total_bet_amount": 0,
                "aggression_factor": 0.0,  # (raise + bet) / (call + check)
                "vpip": 0.0,  # 主动入池率
                "pfr": 0.0,   # 翻牌前加注率
                "recent_actions": [],
                "tendencies": []
            }
        
        profile = self.opponent_profiles[player_name]
        
        # 记录到当前局
        action_record = {
            "action": action,
            "amount": amount,
            "street": street,
            "pot_size": pot_size,
            "community_cards": community_cards or []
        }
        self.current_round_actions[player_name].append(action_record)
        
        # 更新档案统计
        profile["total_actions"] += 1
        
        if action == "fold":
            profile["fold_count"] += 1
        elif action == "call":
            profile["call_count"] += 1
            profile["total_bet_amount"] += amount
        elif action == "raise":
            profile["raise_count"] += 1
            profile["total_bet_amount"] += amount
        elif action == "check":
            profile["check_count"] += 1
        
        # 保存到最近行动
        profile["recent_actions"].append(action_record)
        if len(profile["recent_actions"]) > 20:
            profile["recent_actions"] = profile["recent_actions"][-20:]
        
        # 更新侵略性因子
        aggressive_actions = profile["raise_count"]
        passive_actions = profile["call_count"] + profile["check_count"]
        if passive_actions > 0:
            profile["aggression_factor"] = aggressive_actions / passive_actions
        else:
            profile["aggression_factor"] = float(aggressive_actions)
    
    def get_opponent_summary(self, player_name: str, detailed: bool = False) -> str:
        """
        获取对手特点总结
        
        Args:
            player_name: 玩家名称
            detailed: 是否返回详细信息
        
        Returns:
            对手特点描述
        """
        if player_name not in self.opponent_profiles:
            return "未知对手（首次遇到）"
        
        profile = self.opponent_profiles[player_name]
        
        if profile["total_actions"] < 5:
            return f"对手信息较少（观察到 {profile['total_actions']} 次行动）"
        
        # 分析打法倾向
        tendencies = []
        
        # 分析侵略性
        if profile["aggression_factor"] > 2.0:
            tendencies.append("非常激进")
        elif profile["aggression_factor"] > 1.0:
            tendencies.append("较为激进")
        elif profile["aggression_factor"] > 0.5:
            tendencies.append("中等侵略性")
        else:
            tendencies.append("被动保守")
        
        # 分析弃牌率
        fold_rate = profile["fold_count"] / profile["total_actions"]
        if fold_rate > 0.7:
            tendencies.append("容易弃牌")
        elif fold_rate < 0.3:
            tendencies.append("不轻易弃牌")
        
        # 分析跟注倾向
        call_rate = profile["call_count"] / profile["total_actions"]
        if call_rate > 0.4:
            tendencies.append("爱跟注")
        
        # 构建总结
        summary_parts = []
        summary_parts.append(f"对手 {player_name}：{', '.join(tendencies)}")
        summary_parts.append(f"（观察到 {profile['total_actions']} 次行动）")
        
        if detailed:
            summary_parts.append(f"\n  - 侵略性因子: {profile['aggression_factor']:.2f}")
            summary_parts.append(f"\n  - 加注率: {profile['raise_count']/profile['total_actions']*100:.1f}%")
            summary_parts.append(f"\n  - 弃牌率: {fold_rate*100:.1f}%")
            
            # 最近3次行动
            recent = profile["recent_actions"][-3:]
            if recent:
                actions_str = ", ".join([f"{a['street']}-{a['action']}" for a in recent])
                summary_parts.append(f"\n  - 最近行动: {actions_str}")
        
        return "".join(summary_parts)
    
    def get_current_round_actions(self, player_name: str) -> List[Dict]:
        """
        获取对手在当前局的行动
        
        Args:
            player_name: 玩家名称
        
        Returns:
            行动列表
        """
        return self.current_round_actions.get(player_name, [])
    
    def get_all_opponents_summary(self) -> str:
        """获取所有对手的简要总结"""
        if not self.opponent_profiles:
            return "暂无对手信息"
        
        summaries = []
        for player_name in self.opponent_profiles.keys():
            summary = self.get_opponent_summary(player_name, detailed=False)
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def analyze_opponent_range(self, 
                               player_name: str, 
                               action: str, 
                               street: str,
                               pot_size: int,
                               bet_amount: int) -> str:
        """
        基于对手历史，分析其可能的手牌范围
        
        Args:
            player_name: 玩家名称
            action: 当前行动
            street: 街道
            pot_size: 底池
            bet_amount: 下注金额
        
        Returns:
            范围分析
        """
        if player_name not in self.opponent_profiles:
            return "对手信息不足，难以判断范围"
        
        profile = self.opponent_profiles[player_name]
        
        # 计算相对下注大小
        bet_to_pot_ratio = bet_amount / pot_size if pot_size > 0 else 0
        
        analysis = []
        
        if action == "raise":
            if profile["aggression_factor"] > 2.0:
                analysis.append("这个对手很激进，加注范围较宽")
                if bet_to_pot_ratio > 0.75:
                    analysis.append("大额加注可能是价值或诈唬")
                else:
                    analysis.append("小额加注可能在试探或持续下注")
            else:
                analysis.append("这个对手较保守，加注通常有货")
                analysis.append("可能持有强牌或强听牌")
        
        elif action == "call":
            if profile["call_count"] / profile["total_actions"] > 0.4:
                analysis.append("这个对手爱跟注，范围较宽")
                analysis.append("可能持有听牌、中等牌力或在设陷阱")
            else:
                analysis.append("这个对手不常跟注")
                analysis.append("此次跟注可能持有边缘牌力或强牌慢打")
        
        elif action == "fold":
            if profile["fold_count"] / profile["total_actions"] > 0.7:
                analysis.append("这个对手容易弃牌")
                analysis.append("可以考虑诈唬施压")
            else:
                analysis.append("这个对手不轻易弃牌")
                analysis.append("本次弃牌说明牌力确实很弱")
        
        return "；".join(analysis) if analysis else "难以判断"
    
    def clear_all(self):
        """清除所有对手档案（用于新游戏）"""
        self.opponent_profiles.clear()
        self.current_round_actions.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_opponents": len(self.opponent_profiles),
            "total_actions_recorded": sum(
                p["total_actions"] for p in self.opponent_profiles.values()
            ),
            "opponents": list(self.opponent_profiles.keys())
        }

