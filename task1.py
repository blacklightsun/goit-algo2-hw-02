from typing import List, Dict
from dataclasses import dataclass, field

@dataclass
class PrinterConstraints:
    max_volume: float
    max_items: int

@dataclass(order=True)
class PrintJob:
    id: str = field(default=None, compare=False)
    volume: float = field(default=None, compare=False)
    priority: int = field(default=None, compare=False)
    print_time: int = field(default=None, compare=False)

    # Додаткові поля для порівняння (необхідно для сортування)
    priority_for_sort: int = field(init=False, compare=True)
    volume_for_sort: float = field(init=False, compare=True)

    def __post_init__(self):
        '''Критерії для порівнняня об'єктів PrintJob (на більше/менше): спочатку - пріоритет, потім - об'єм фігури.
        Для реалізації цього необхідно змінити порядок пріорітетів: чим більший пріоритет, тим 'більший' PrintJob.
        Для цього створюємо поле priority_for_sort, яке буде від'ємним значенням priority,
        щоб при сортуванні за зростанням спочатку йшли найбільші пріоритети (= найменьші priority_for_sort).
        В dataclass порядок для порівняння визначається порядком полів у класі, помічених для порівняння.
        Тому для порівння/сортування об'ємів фігури створюємо додатковий атрибут volume_for_sort, щоб при порівнянні/сортуванні за зростанням спочатку йшли найменьші об'єми
        та щоб зберігти порядок полів у класі, які передаються в конструктор об'єкта при його створенні (інакше volume буде перед priority_for_sort).'''
        self.priority_for_sort = - self.priority
        self.volume_for_sort = self.volume

@dataclass
class Printer:
    name: str
    constraints: PrinterConstraints
    jobs: List[PrintJob] = field(default_factory=list)

    def add_job(self, job: PrintJob):
        '''Додає завдання на друк до черги, якщо воно відповідає обмеженням принтера'''
        if job.volume > self.constraints.max_volume:
            print(f"Cannot add job {job.id}: max items limit reached.")
            return False
		
        self.jobs.append(job)
        return True
	
    def make_print_queqe(self):
        '''
        Бульбашкове сортування для списку задач. Можна було б реалізувати через метод sort() для списків, 
        але щоб показати порівняння об'єктів PrintJob (більше/менше) реалізуємо сортування за допомогою наочного алгоритму самостійно.
        Сортування відбувається за пріоритетом, а потім за об'ємом фігури (в напрямку зменшення значень обох полів об'єктів).
        '''
        n = len(self.jobs)
		# Проходимо по всіх елементах масиву
        for i in range(n):
			# Останні i елементів вже на своїх місцях
            for j in range(0, n - i - 1):
				# Якщо елемент більший за наступний, міняємо їх місцями
                if self.jobs[j] < self.jobs[j + 1]:
                    self.jobs[j], self.jobs[j + 1] = self.jobs[j + 1], self.jobs[j]



def optimize_printing(print_jobs: List[Dict], constraints: Dict) -> Dict:
    """
    Оптимізує чергу 3D-друку згідно з пріоритетами та обмеженнями принтера

    Args:
        print_jobs: Список завдань на друк
        constraints: Обмеження принтера

    Returns:
        Dict з порядком друку та загальним часом

    Логіка роботи:
        Завдання, які не відповідають обмеженням принтера, не додаються до черги.
        Черга друку формується за пріоритетом та об'ємом фігур - в рамках одного пріорітету в першу чергу друкується найбільша фігура, 
        як найбільш оптимальна (яка займає найбільшу долю можливостей принтера за об'ємом друку та кількостю фігур).
        Якщо є "вільне місце" на принтері (по об'єму друку та кількості фігур), то воно заповнюється наступними завданнями з черги.

    !!! Важливо:
        В умовах ДЗ для test1_jobs очікувана черга друку: ['M1', 'M2', 'M3']. Формально це відповідає обмеженням принтера, 
        але один з ключових етапів жадібного алгоритму - обчислення ефективності кожного елементу черги і обробка елементів у порядку спадання ефективності.
        Це може бути об'єм на одиницю виробу, частку об'єму фігури в загальному об'ємі друку принтера, час друку на одиницю об'єму фігури тощо.
        Очікувана черга друку: ['M1', 'M2', 'M3'] не містить в собі ознак обробки в порядку спадання ефективності за будь-яким показником ефективності.
        Тому моя відповідь ['M2', 'M3', 'M1'] не відповідає очикуваному результату для test1_jobs, але є правильною, а час виконання - відповідає очикуваним.
        Для test2_jobs та test3_jobs результат відповідає очікуваному в умовах ДЗ.
    """
    # ініціалізуємо принтер з обмеженнями
    printer = Printer(
        name="3D Printer",
        constraints=PrinterConstraints(**constraints)
        )

    # Додаємо завдання на друк до принтера. Завдання, які не відповідають обмеженням принтера, не додаються до черги.
    for job in print_jobs:
        printer.add_job(PrintJob(**job))

    # Сортуємо завдання за пріоритетом та об'ємом (за зменшенням завданнь)
    printer.make_print_queqe()

    # ініціалізуємо тимчасові змінні управління чергою друку
    print_order = [] #  список для id завдань у черзі
    total_time = 0 # загальний час друку
    step_time = 0 # час друку для одного кроку (групи завданнь, що другуються одночасно)
    current_free_volume = printer.constraints.max_volume
    current_free_items = printer.constraints.max_items

    # Проходимо по всіх завданнях у відсортованій черзі
    for job in printer.jobs:
        
        # якщо завдання не відповідає поточним обмеженням принтера, то починаємо новий крок друку
        if job.volume > current_free_volume or current_free_items < 1:
            current_free_volume = printer.constraints.max_volume
            current_free_items = printer.constraints.max_items
            total_time += step_time # додаємо час друку поточного кроку до загального часу
            step_time = 0 # скидаємо час друку нового кроку


        print_order.append(job.id)
        # зменшуємо поточний вільний об'єм принтера та кількість завдань, що друкуються одночасно
        current_free_volume -= job.volume
        current_free_items -= 1
        # обираємо максимальний час друку з усіх завдань, що друкуються одночасно
        step_time = job.print_time if job.print_time > step_time else step_time

    # додаємо час друку останнього кроку до загального часу
    total_time += step_time

    return {
        "print_order": print_order,
        "total_time": total_time
    }

# Тестування
def test_printing_optimization():
    # Тест 1: Моделі однакового пріоритету
    test1_jobs = [
        {"id": "M1", "volume": 100, "priority": 1, "print_time": 120},
        {"id": "M2", "volume": 150, "priority": 1, "print_time": 90},
        {"id": "M3", "volume": 120, "priority": 1, "print_time": 150}
    ]

    # Тест 2: Моделі різних пріоритетів
    test2_jobs = [
        {"id": "M1", "volume": 100, "priority": 2, "print_time": 120},  # лабораторна
        {"id": "M2", "volume": 150, "priority": 1, "print_time": 90},  # дипломна
        {"id": "M3", "volume": 120, "priority": 3, "print_time": 150}  # особистий проєкт
    ]

    # Тест 3: Перевищення обмежень об'єму
    test3_jobs = [
        {"id": "M1", "volume": 250, "priority": 1, "print_time": 180},
        {"id": "M2", "volume": 200, "priority": 1, "print_time": 150},
        {"id": "M3", "volume": 180, "priority": 2, "print_time": 120}
    ]

    constraints = {
        "max_volume": 300,
        "max_items": 2
    }

    print("\nТест 1 (однаковий пріоритет):")
    result1 = optimize_printing(test1_jobs, constraints)
    print(f"Порядок друку: {result1['print_order']}")
    print(f"Загальний час: {result1['total_time']} хвилин")

    print("\nТест 2 (різні пріоритети):")
    result2 = optimize_printing(test2_jobs, constraints)
    print(f"Порядок друку: {result2['print_order']}")
    print(f"Загальний час: {result2['total_time']} хвилин")

    print("\nТест 3 (перевищення обмежень):")
    result3 = optimize_printing(test3_jobs, constraints)
    print(f"Порядок друку: {result3['print_order']}")
    print(f"Загальний час: {result3['total_time']} хвилин")

if __name__ == "__main__":
    test_printing_optimization()

