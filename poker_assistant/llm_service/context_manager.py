"""
上下文管理器
管理对话历史和上下文信息
"""
from typing import List, Dict, Any, Optional
from collections import deque
import json


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_history: int = 10, max_tokens: int = 6000):
        """
        初始化上下文管理器
        
        Args:
            max_history: 最大保留的对话轮数
            max_tokens: 最大token数（粗略估算）
        """
        self.max_history = max_history
        self.max_tokens = max_tokens
        
        # 对话历史 (deque 自动限制长度)
        self.conversation_history: deque = deque(maxlen=max_history)
        
        # 游戏上下文
        self.game_context: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str):
        """
        添加消息到历史
        
        Args:
            role: 角色 ('user', 'assistant', 'system')
            content: 消息内容
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str):
        """添加助手消息"""
        self.add_message("assistant", content)
    
    def add_system_message(self, content: str):
        """添加系统消息"""
        self.add_message("system", content)
    
    def get_messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        获取消息列表
        
        Args:
            include_system: 是否包含系统消息
        
        Returns:
            消息列表
        """
        if include_system:
            return list(self.conversation_history)
        else:
            return [
                msg for msg in self.conversation_history 
                if msg["role"] != "system"
            ]
    
    def update_game_context(self, context_data: Dict[str, Any]):
        """
        更新游戏上下文
        
        Args:
            context_data: 上下文数据
        """
        self.game_context.update(context_data)
    
    def get_game_context(self) -> Dict[str, Any]:
        """获取游戏上下文"""
        return self.game_context.copy()
    
    def get_game_context_string(self) -> str:
        """
        获取游戏上下文的字符串表示
        
        Returns:
            格式化的上下文字符串
        """
        if not self.game_context:
            return "（当前没有进行中的牌局）"
        
        parts = []
        
        # 手牌
        if "hole_cards" in self.game_context:
            hole_cards = self.game_context["hole_cards"]
            parts.append(f"你的手牌: {', '.join(hole_cards)}")
        
        # 公共牌
        if "community_cards" in self.game_context:
            community_cards = self.game_context["community_cards"]
            if community_cards:
                parts.append(f"公共牌: {', '.join(community_cards)}")
        
        # 街道
        if "street" in self.game_context:
            street_names = {
                'preflop': '翻牌前',
                'flop': '翻牌',
                'turn': '转牌',
                'river': '河牌'
            }
            street = self.game_context["street"]
            street_cn = street_names.get(street, street)
            parts.append(f"当前阶段: {street_cn}")
        
        # 底池
        if "pot_size" in self.game_context:
            pot = self.game_context["pot_size"]
            parts.append(f"底池: ${pot}")
        
        # 筹码
        if "stack_size" in self.game_context:
            stack = self.game_context["stack_size"]
            parts.append(f"你的筹码: ${stack}")
        
        return "\n".join(parts)
    
    def compress_context(self, target_tokens: Optional[int] = None) -> List[Dict[str, str]]:
        """
        压缩上下文（当token数过多时）
        
        Args:
            target_tokens: 目标token数
        
        Returns:
            压缩后的消息列表
        """
        target = target_tokens or self.max_tokens
        
        messages = list(self.conversation_history)
        
        # 简单的压缩策略：保留最近的消息
        # 粗略估算：中文约2个字符=1个token
        estimated_tokens = sum(len(msg["content"]) / 2 for msg in messages)
        
        if estimated_tokens <= target:
            return messages
        
        # 保留系统消息和最近的对话
        system_messages = [msg for msg in messages if msg["role"] == "system"]
        other_messages = [msg for msg in messages if msg["role"] != "system"]
        
        # 从后往前保留消息，直到达到token限制
        compressed = system_messages.copy()
        current_tokens = sum(len(msg["content"]) / 2 for msg in system_messages)
        
        for msg in reversed(other_messages):
            msg_tokens = len(msg["content"]) / 2
            if current_tokens + msg_tokens <= target:
                compressed.insert(len(system_messages), msg)
                current_tokens += msg_tokens
            else:
                break
        
        return compressed
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history.clear()
    
    def clear_game_context(self):
        """清除游戏上下文"""
        self.game_context.clear()
    
    def clear_all(self):
        """清除所有上下文"""
        self.clear_history()
        self.clear_game_context()
    
    def save_to_dict(self) -> Dict[str, Any]:
        """
        保存为字典（用于序列化）
        
        Returns:
            包含所有上下文的字典
        """
        return {
            "conversation_history": list(self.conversation_history),
            "game_context": self.game_context,
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """
        从字典加载（用于反序列化）
        
        Args:
            data: 包含上下文的字典
        """
        if "conversation_history" in data:
            self.conversation_history.clear()
            for msg in data["conversation_history"]:
                self.conversation_history.append(msg)
        
        if "game_context" in data:
            self.game_context = data["game_context"]
    
    def get_summary(self) -> str:
        """
        获取上下文摘要
        
        Returns:
            摘要字符串
        """
        summary_parts = []
        
        summary_parts.append(f"对话轮数: {len(self.conversation_history)}")
        
        if self.game_context:
            summary_parts.append("游戏上下文: 已设置")
        else:
            summary_parts.append("游戏上下文: 未设置")
        
        # 估算token数
        estimated_tokens = sum(
            len(msg["content"]) / 2 
            for msg in self.conversation_history
        )
        summary_parts.append(f"估算tokens: {int(estimated_tokens)}")
        
        return " | ".join(summary_parts)


class ConversationSession:
    """会话管理器（用于管理多个独立的对话会话）"""
    
    def __init__(self):
        self.sessions: Dict[str, ContextManager] = {}
        self.current_session_id: Optional[str] = None
    
    def create_session(self, session_id: str) -> ContextManager:
        """创建新会话"""
        context = ContextManager()
        self.sessions[session_id] = context
        self.current_session_id = session_id
        return context
    
    def get_session(self, session_id: str) -> Optional[ContextManager]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_current_session(self) -> Optional[ContextManager]:
        """获取当前会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None
    
    def switch_session(self, session_id: str) -> bool:
        """切换会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return True
        return False
    
    def delete_session(self, session_id: str):
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None

