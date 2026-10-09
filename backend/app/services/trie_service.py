from typing import List, Dict, Any, Optional

class TrieNode:
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end_of_word: bool = False
        self.data: Optional[Dict[str, Any]] = None

class TrieService:
    """
    Service quản lý cấu trúc dữ liệu Trie cho tìm kiếm chính xác và gợi ý (autocomplete).
    Được thiết kế theo đúng chuẩn interface để dễ dàng cắm thuật toán của Hair vào sau này.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, data: Optional[Dict[str, Any]] = None):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.data = data

    def search(self, word: str) -> bool:
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def get_word_data(self, word: str) -> Optional[Dict[str, Any]]:
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return None
            node = node.children[char]
        return node.data if node.is_end_of_word else None

    def get_suggestions(self, prefix: str, limit: int = 5) -> List[str]:
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        suggestions: List[str] = []

        def _dfs(curr_node: TrieNode, current_str: str):
            if len(suggestions) >= limit:
                return
            if curr_node.is_end_of_word:
                suggestions.append(current_str)
            for ch, next_node in sorted(curr_node.children.items()):
                _dfs(next_node, current_str + ch)
                if len(suggestions) >= limit:
                    return

        _dfs(node, prefix.lower())
        return suggestions

    def delete(self, word: str) -> bool:
        def _delete(node: TrieNode, word_str: str, index: int) -> bool:
            if index == len(word_str):
                if not node.is_end_of_word:
                    return False
                node.is_end_of_word = False
                node.data = None
                return len(node.children) == 0

            char = word_str[index]
            if char not in node.children:
                return False

            should_delete_child = _delete(node.children[char], word_str, index + 1)
            if should_delete_child:
                del node.children[char]
                return len(node.children) == 0 and not node.is_end_of_word
            return False

        return _delete(self.root, word.lower(), 0)

# Singleton instance
trie_service = TrieService()
