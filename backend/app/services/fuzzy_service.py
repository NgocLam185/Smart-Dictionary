from typing import List, Dict, Any

class FuzzySearchService:
    """
    Service tìm kiếm gần đúng dựa trên khoảng cách Levenshtein (Task Laam-08).
    Được cấu trúc theo chuẩn interface để dễ dàng cắm thuật toán của Hiuss vào sau này.
    """
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # deletion
                        dp[i][j - 1],      # insertion
                        dp[i - 1][j - 1]   # substitution
                    )
        return dp[m][n]

    def search(self, query: str, candidates: List[str], max_distance: int = 2, limit: int = 5) -> List[Dict[str, Any]]:
        query = query.strip().lower()
        results = []

        for candidate in candidates:
            dist = self.levenshtein_distance(query, candidate.lower())
            if dist <= max_distance:
                results.append({"word": candidate, "distance": dist})

        results.sort(key=lambda x: (x["distance"], len(x["word"])))
        return results[:limit]

# Singleton instance
fuzzy_service = FuzzySearchService()
