"""
游戏状态管理模块
管理游戏的完整状态信息
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlayerState:
    """玩家状态"""
    uuid: str
    name: str
    stack: int
    state: str  # 'participating', 'folded', 'allin'
    hole_cards: List[str] = field(default_factory=list)
    position: int = 0
    is_human: bool = False


@dataclass
class ActionRecord:
    """行动记录"""
    player_name: str
    action: str  # 'fold', 'call', 'raise', 'allin'
    amount: int
    street: str  # 'preflop', 'flop', 'turn', 'river'
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RoundState:
    """回合状态"""
    round_count: int
    street: str  # 'preflop', 'flop', 'turn', 'river'
    community_cards: List[str] = field(default_factory=list)
    pot_size: int = 0
    dealer_btn: int = 0
    small_blind_pos: int = 1
    big_blind_pos: int = 2
    small_blind_amount: int = 5
    big_blind_amount: int = 10
    action_histories: List[ActionRecord] = field(default_factory=list)


class GameState:
    """游戏状态管理器"""
    
    def __init__(self, player_count: int = 6, initial_stack: int = 1000):
        self.player_count = player_count
        self.initial_stack = initial_stack
        self.players: List[PlayerState] = []
        self.current_round: Optional[RoundState] = None
        self.round_history: List[RoundState] = []
        self.game_started = False
    
    def add_player(self, uuid: str, name: str, is_human: bool = False):
        """添加玩家"""
        player = PlayerState(
            uuid=uuid,
            name=name,
            stack=self.initial_stack,
            state='participating',
            position=len(self.players),
            is_human=is_human
        )
        self.players.append(player)
    
    def get_player_by_uuid(self, uuid: str) -> Optional[PlayerState]:
        """通过 UUID 获取玩家"""
        for player in self.players:
            if player.uuid == uuid:
                return player
        return None
    
    def get_player_by_name(self, name: str) -> Optional[PlayerState]:
        """通过名字获取玩家"""
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def get_human_player(self) -> Optional[PlayerState]:
        """获取人类玩家"""
        for player in self.players:
            if player.is_human:
                return player
        return None
    
    def update_player_stack(self, uuid: str, stack: int):
        """更新玩家筹码"""
        player = self.get_player_by_uuid(uuid)
        if player:
            player.stack = stack
    
    def update_player_state(self, uuid: str, state: str):
        """更新玩家状态"""
        player = self.get_player_by_uuid(uuid)
        if player:
            player.state = state
    
    def set_player_hole_cards(self, uuid: str, hole_cards: List[str]):
        """设置玩家手牌"""
        player = self.get_player_by_uuid(uuid)
        if player:
            player.hole_cards = hole_cards
    
    def start_new_round(self, round_count: int, dealer_btn: int, 
                       small_blind: int, big_blind: int):
        """开始新回合"""
        self.current_round = RoundState(
            round_count=round_count,
            street='preflop',
            dealer_btn=dealer_btn,
            small_blind_amount=small_blind,
            big_blind_amount=big_blind
        )
        
        # 计算盲注位置
        if self.player_count == 2:
            # 两人局：庄位是小盲，另一人是大盲
            self.current_round.small_blind_pos = dealer_btn
            self.current_round.big_blind_pos = (dealer_btn + 1) % self.player_count
        else:
            # 多人局：庄位下一位是小盲，再下一位是大盲
            self.current_round.small_blind_pos = (dealer_btn + 1) % self.player_count
            self.current_round.big_blind_pos = (dealer_btn + 2) % self.player_count
    
    def update_street(self, street: str):
        """更新当前街道"""
        if self.current_round:
            self.current_round.street = street
    
    def update_community_cards(self, cards: List[str]):
        """更新公共牌"""
        if self.current_round:
            self.current_round.community_cards = cards
    
    def update_pot(self, pot_size: int):
        """更新底池"""
        if self.current_round:
            self.current_round.pot_size = pot_size
    
    def record_action(self, player_name: str, action: str, amount: int):
        """记录玩家行动"""
        if self.current_round:
            action_record = ActionRecord(
                player_name=player_name,
                action=action,
                amount=amount,
                street=self.current_round.street
            )
            self.current_round.action_histories.append(action_record)
    
    def finish_round(self):
        """结束当前回合"""
        if self.current_round:
            self.round_history.append(self.current_round)
            self.current_round = None
    
    def get_active_players(self) -> List[PlayerState]:
        """获取仍在游戏中的玩家"""
        return [p for p in self.players if p.state == 'participating']
    
    def get_player_position_name(self, player: PlayerState) -> str:
        """获取玩家位置名称"""
        if not self.current_round:
            return ""
        
        player_idx = self.players.index(player)
        
        if self.player_count == 2:
            return "BTN" if player_idx == self.current_round.dealer_btn else "BB"
        
        if player_idx == self.current_round.dealer_btn:
            return "BTN"
        elif player_idx == self.current_round.small_blind_pos:
            return "SB"
        elif player_idx == self.current_round.big_blind_pos:
            return "BB"
        else:
            # 计算相对位置
            distance = (player_idx - self.current_round.dealer_btn) % self.player_count
            if distance == self.player_count - 1:
                return "CO"
            elif distance == self.player_count - 2:
                return "HJ"
            else:
                return f"MP"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "player_count": self.player_count,
            "initial_stack": self.initial_stack,
            "players": [
                {
                    "uuid": p.uuid,
                    "name": p.name,
                    "stack": p.stack,
                    "state": p.state,
                    "position": p.position,
                    "is_human": p.is_human
                }
                for p in self.players
            ],
            "current_round": {
                "round_count": self.current_round.round_count,
                "street": self.current_round.street,
                "community_cards": self.current_round.community_cards,
                "pot_size": self.current_round.pot_size,
                "dealer_btn": self.current_round.dealer_btn,
            } if self.current_round else None,
        }

