"""
扑克牌工具模块
提供扑克牌显示、解析等工具函数
"""
from typing import List, Tuple


# 花色映射
SUIT_SYMBOLS = {
    'S': '♠',  # Spades
    'H': '♥',  # Hearts
    'D': '♦',  # Diamonds
    'C': '♣',  # Clubs
}

# 牌面映射
RANK_NAMES = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    'T': '10', 'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
}


def format_card(card: str) -> str:
    """
    格式化扑克牌显示
    
    Args:
        card: 牌的字符串表示，如 'SA' (黑桃A), 'H2' (红心2)
    
    Returns:
        格式化后的字符串，如 'A♠', '2♥'
    """
    if not card or len(card) != 2:
        return card
    
    suit = card[0]  # 花色
    rank = card[1]  # 点数
    
    suit_symbol = SUIT_SYMBOLS.get(suit, suit)
    rank_name = RANK_NAMES.get(rank, rank)
    
    return f"{rank_name}{suit_symbol}"


def format_cards(cards: List[str]) -> str:
    """
    格式化多张扑克牌显示
    
    Args:
        cards: 牌的列表
    
    Returns:
        格式化后的字符串，如 'A♠ K♥'
    """
    if not cards:
        return ""
    return " ".join([format_card(card) for card in cards])


def parse_card(formatted_card: str) -> str:
    """
    将格式化的牌还原为原始格式
    
    Args:
        formatted_card: 格式化的牌，如 'A♠'
    
    Returns:
        原始格式，如 'SA'
    """
    # 反向映射
    reverse_suits = {v: k for k, v in SUIT_SYMBOLS.items()}
    reverse_ranks = {v: k for k, v in RANK_NAMES.items()}
    
    # 提取点数和花色
    if len(formatted_card) >= 2:
        if len(formatted_card) == 3:  # 如 '10♠'
            rank = formatted_card[:2]
            suit = formatted_card[2]
        else:  # 如 'A♠'
            rank = formatted_card[0]
            suit = formatted_card[1]
        
        original_rank = reverse_ranks.get(rank, rank[0] if rank == '10' else rank)
        original_suit = reverse_suits.get(suit, suit)
        
        return f"{original_suit}{original_rank}"
    
    return formatted_card


def get_card_color(card: str) -> str:
    """
    获取牌的颜色（用于终端显示）
    
    Args:
        card: 牌的字符串表示
    
    Returns:
        Rich库支持的颜色名称
    """
    if not card or len(card) < 2:
        return 'white'
    
    suit = card[0]
    if suit in ['H', 'D']:  # 红心♥、方片♦ - 红色
        return 'bright_red'
    return 'blue'  # 黑桃♠、梅花♣ - 蓝色（在白色背景上比黑色更清晰）


def sort_cards(cards: List[str]) -> List[str]:
    """
    对扑克牌进行排序
    
    Args:
        cards: 牌的列表
    
    Returns:
        排序后的牌列表（按点数从大到小）
    """
    rank_order = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10, 
                  '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2}
    
    def card_key(card: str) -> int:
        if len(card) >= 2:
            rank = card[1]
            return rank_order.get(rank, 0)
        return 0
    
    return sorted(cards, key=card_key, reverse=True)


def describe_hand_strength(hand_info: dict) -> str:
    """
    描述手牌强度
    
    Args:
        hand_info: PyPokerEngine 返回的手牌信息
    
    Returns:
        手牌强度的中文描述
    """
    if not hand_info or 'hand' not in hand_info:
        return "未知"
    
    hand_rank_names = {
        'highcard': '高牌',
        'onepair': '一对',
        'twopair': '两对',
        'threecard': '三条',
        'straight': '顺子',
        'flush': '同花',
        'fullhouse': '葫芦',
        'fourcard': '四条',
        'straightflush': '同花顺',
    }
    
    hand_name = hand_info['hand']['hand']
    return hand_rank_names.get(hand_name, hand_name)


def format_action(action: str, amount: int = 0) -> str:
    """
    格式化行动显示
    
    Args:
        action: 行动类型 ('fold', 'call', 'raise')
        amount: 金额
    
    Returns:
        格式化后的行动描述
    """
    action_names = {
        'fold': '弃牌',
        'call': '跟注',
        'raise': '加注',
        'allin': '全下',
    }
    
    action_cn = action_names.get(action.lower(), action)
    
    if amount > 0:
        return f"{action_cn} ${amount}"
    return action_cn


def format_chips(amount: int) -> str:
    """
    格式化筹码显示
    
    Args:
        amount: 筹码数量
    
    Returns:
        格式化后的字符串
    """
    # 确保amount是整数，避免小数显示
    amount = int(round(amount))
    if amount >= 1000:
        return f"${amount:,}"
    return f"${amount}"


def get_position_name(position: int, player_count: int) -> str:
    """
    获取位置名称
    
    Args:
        position: 位置索引（0 为按钮位）
        player_count: 玩家总数
    
    Returns:
        位置名称
    """
    if player_count <= 2:
        return "BTN" if position == 0 else "BB"
    
    if position == 0:
        return "BTN"
    elif position == 1:
        return "SB"
    elif position == 2:
        return "BB"
    elif position == player_count - 1:
        return "CO"
    elif position == player_count - 2:
        return "HJ"
    else:
        return f"MP{position - 2}"


def get_street_name(street: str) -> str:
    """
    获取街道名称的中文
    
    Args:
        street: 街道名称 ('preflop', 'flop', 'turn', 'river')
    
    Returns:
        中文名称
    """
    street_names = {
        'preflop': '翻牌前',
        'flop': '翻牌',
        'turn': '转牌',
        'river': '河牌',
    }
    return street_names.get(street.lower(), street)

