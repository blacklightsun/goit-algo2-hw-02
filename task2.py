from typing import List, Dict

def rod_cutting_memo(length: int, prices: List[int]) -> Dict:
    """
    Знаходить оптимальний спосіб розрізання через мемоізацію

    Args:
        length: довжина стрижня
        prices: список цін, де prices[i] — ціна стрижня довжини i+1

    Returns:
        Dict з максимальним прибутком та списком розрізів
    """

    def recurr_rod_cutting(prices, n, memo={}, cuts={}):
        '''Рекурсивна функція для розрізання стрижня з мемоізацією'''
        if n in memo:
            return memo[n]
        if n == 0:
            return 0

        max_value = float('-inf')
        best_cut = 0
        for i in range(1, n + 1):
            current_value = prices[i - 1] + recurr_rod_cutting(prices, n - i, memo, cuts)
            if current_value > max_value:
                max_value = current_value
                best_cut = i

        memo[n] = max_value
        cuts[n] = best_cut
        return max_value

    def explain_cuts(cuts, n):
        '''Функція для пояснення розрізів'''
        result = []
        while n > 0:
            result.append(cuts[n])
            n -= cuts[n]
        return result


    # Перевірка вхідних даних
    if length != len(prices):
        raise ValueError("Довжина стрижня не відповідає кількості цін")
    if length <= 0:
        raise ValueError("Довжина стрижня повинна бути додатнім числом")
    if not all(isinstance(price, (int, float)) for price in prices):
        raise ValueError("Ціни повинні бути числами")
    if not all(price >= 0 for price in prices):
        raise ValueError("Ціни повинні бути невід'ємними")
    if len(prices) == 0:
        raise ValueError("Список цін не може бути порожнім")
    
    # Ініціалізація словників для мемоізації
    memo = {}
    cuts = {}

    # Виклик рекурсивної функції
    max_profit = recurr_rod_cutting(prices, length, memo, cuts)
    optimal_cuts = explain_cuts(cuts, length)
    
    return {
        "max_profit": max_profit,
        "cuts": optimal_cuts,
        "number_of_cuts": len(optimal_cuts) - 1
    }

def rod_cutting_table(length: int, prices: List[int]) -> Dict:
    """
    Знаходить оптимальний спосіб розрізання через табуляцію

    Args:
        length: довжина стрижня
        prices: список цін, де prices[i] — ціна стрижня довжини i+1

    Returns:
        Dict з максимальним прибутком та списком розрізів
    """

    # Перевірка вхідних даних
    if length != len(prices):
        raise ValueError("Довжина стрижня не відповідає кількості цін")
    if length <= 0:
        raise ValueError("Довжина стрижня повинна бути додатнім числом")
    if not all(isinstance(price, (int, float)) for price in prices):
        raise ValueError("Ціни повинні бути числами")
    if not all(price >= 0 for price in prices):
        raise ValueError("Ціни повинні бути невід'ємними")
    if len(prices) == 0:
        raise ValueError("Список цін не може бути порожнім")

    # масив цін
    value = [0] + prices
    # розмірність робочих таблиць
    shape = len(value)
    # таблиця для зберігання максимальних прибутків
    value_table  = [[0 for _ in range(shape)] for _ in range(shape)]
    # таблиця для зберігання оптимальних розрізів
    cuts_table = [[[] for _ in range(shape)] for _ in range(shape)]

    # розрахунки робочих таблиць
    for i in range(1, shape):
        for j in range(i, shape):

            next_case = j // i * value[i] + value_table[j % i][j % i]
            prev_case = value_table[i - 1][j]
            if next_case > prev_case:
                value_table[i][j] = next_case
                cuts_table[i][j] = [i] * (j // i) + cuts_table[j % i][j % i]
            else:
                value_table[i][j] = prev_case
                cuts_table[i][j] = cuts_table[i - 1][j]

    optimal_cuts = cuts_table[-1][-1]

    return {
        "max_profit": float(value_table[-1][-1]),
        "cuts": optimal_cuts,
        "number_of_cuts": len(optimal_cuts) - 1
    }

def run_tests():
    """Функція для запуску всіх тестів"""
    test_cases = [
        # Тест 1: Базовий випадок
        {
            "length": 5,
            "prices": [2, 5, 7, 8, 10],
            "name": "Базовий випадок"
        },
        # Тест 2: Оптимально не різати
        {
            "length": 3,
            "prices": [1, 3, 8],
            "name": "Оптимально не різати"
        },
        # Тест 3: Всі розрізи по 1
        {
            "length": 4,
            "prices": [3, 5, 6, 7],
            "name": "Рівномірні розрізи"
        }
    ]

    for test in test_cases:
        print(f"\nТест: {test['name']}")
        print(f"Довжина стрижня: {test['length']}")
        print(f"Ціни: {test['prices']}")

        # Тестуємо мемоізацію
        memo_result = rod_cutting_memo(test['length'], test['prices'])
        print("\nРезультат мемоізації:")
        print(f"Максимальний прибуток: {memo_result['max_profit']}")
        print(f"Розрізи: {memo_result['cuts']}")
        print(f"Кількість розрізів: {memo_result['number_of_cuts']}")

        # Тестуємо табуляцію
        table_result = rod_cutting_table(test['length'], test['prices'])
        print("\nРезультат табуляції:")
        print(f"Максимальний прибуток: {table_result['max_profit']}")
        print(f"Розрізи: {table_result['cuts']}")
        print(f"Кількість розрізів: {table_result['number_of_cuts']}")

        print("\nПеревірка пройшла успішно!")

if __name__ == "__main__":
    run_tests()