import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CarAnimation:
    def __init__(self, csv_file):
        # Загружаем данные маршрута с скоростями
        self.route_data = pd.read_csv(csv_file)
        self.total_points = len(self.route_data)
        
        # Проверяем наличие колонок (ОБНОВЛЕНО)
        required_columns = ['shirota', 'dolgota', 'current_speed']
        for col in required_columns:
            if col not in self.route_data.columns:
                raise ValueError(f"CSV файл должен содержать колонку '{col}'")
        
        print(f"✅ Загружено {self.total_points} точек маршрута")
        
        # Инициализация фигуры
        self.fig = plt.figure(figsize=(14, 8))
        self.fig.patch.set_facecolor('#2C3E50')
        
        # Создаем сетку
        grid = plt.GridSpec(2, 2, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Основной график маршрута
        self.ax_map = self.fig.add_subplot(grid[:, 0])
        self.ax_map.set_facecolor('#34495E')
        
        # Панель данных
        self.ax_data = self.fig.add_subplot(grid[0, 1])
        self.ax_data.set_facecolor('#34495E')
        self.ax_data.axis('off')
        
        # Область для кнопок
        self.ax_buttons = self.fig.add_subplot(grid[1, 1])
        self.ax_buttons.set_facecolor('#34495E')
        self.ax_buttons.axis('off')
        
        # Инициализация переменных анимации
        self.current_point = 0
        self.is_playing = False
        self.animation = None
        
        # Реальные метрики
        self.total_distance_km = 0
        self.total_time_seconds = 0
        self.start_time = datetime.now()
        
        # Настройка графиков и кнопок
        self.setup_plots()
        self.setup_buttons()
    
    def setup_plots(self):
        """Настройка внешнего вида графиков"""
        print("🗺️ Настройка графиков...")
        
        # Основной график маршрута
        self.ax_map.set_xlabel('Долгота', color='white', fontsize=12)
        self.ax_map.set_ylabel('Широта', color='white', fontsize=12)
        self.ax_map.tick_params(colors='white')
        
        # Отрисовываем весь маршрут
        self.ax_map.plot(self.route_data['dolgota'], self.route_data['shirota'], 
                        'gray', alpha=0.5, linewidth=2, label='Маршрут')
        
        # Движущаяся точка
        self.car_point, = self.ax_map.plot([], [], 'ro', markersize=10, 
                                          markerfacecolor='red', markeredgecolor='white', 
                                          markeredgewidth=2, label='Автомобиль')
        
        # Пройденный путь
        self.traveled_line, = self.ax_map.plot([], [], 'cyan', linewidth=3, 
                                              alpha=0.8, label='Пройдено')
        
        self.ax_map.legend(facecolor='#2C3E50', edgecolor='white', labelcolor='white')
        self.ax_map.grid(True, alpha=0.3)
    
    def setup_buttons(self):
        """Создание кнопок управления"""
        print("🎮 Настройка кнопок управления...")
        
        # Кнопка Старт
        self.btn_start = Button(
            plt.axes([0.75, 0.15, 0.1, 0.05]), 
            'СТАРТ',
            color='#27AE60',
            hovercolor='#2ECC71'
        )
        self.btn_start.on_clicked(self.start_animation)
        
        # Кнопка Стоп
        self.btn_stop = Button(
            plt.axes([0.86, 0.15, 0.1, 0.05]), 
            'СТОП',
            color='#E74C3C',
            hovercolor='#EC7063'
        )
        self.btn_stop.on_clicked(self.stop_animation)
        
        # Кнопка Сброс
        self.btn_reset = Button(
            plt.axes([0.75, 0.08, 0.21, 0.05]), 
            'СБРОС',
            color='#3498DB',
            hovercolor='#5DADE2'
        )
        self.btn_reset.on_clicked(self.reset_animation)
    
    def calculate_distance_between_points(self, point1, point2):
        """Расчет расстояния между двумя точками в метрах"""
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Упрощенный расчет расстояния
        R = 6371000  # Радиус Земли в метрах
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def get_can_data(self, point_index):
        """Получение CAN-данных из CSV с реальным расчетом времени и расстояния"""
        # Получаем скорость из CSV (ОБНОВЛЕНО)
        current_speed = float(self.route_data['current_speed'].iloc[point_index])
        
        # Получаем оптимальную скорость если есть в данных
        optimal_speed = float(self.route_data['optimal_speed'].iloc[point_index]) if 'optimal_speed' in self.route_data.columns else current_speed
        optimal_fuel = float(self.route_data['optimal_fuel_consumption'].iloc[point_index]) if 'optimal_fuel_consumption' in self.route_data.columns else 0
        
        # Расчет пройденного расстояния
        if point_index > 0:
            # Координаты предыдущей и текущей точек
            prev_lat = float(self.route_data['shirota'].iloc[point_index - 1])
            prev_lon = float(self.route_data['dolgota'].iloc[point_index - 1])
            curr_lat = float(self.route_data['shirota'].iloc[point_index])
            curr_lon = float(self.route_data['dolgota'].iloc[point_index])
            
            # Расстояние между точками в метрах
            segment_distance_m = self.calculate_distance_between_points(
                (prev_lat, prev_lon), (curr_lat, curr_lon)
            )
            
            # Добавляем к общему расстоянию
            self.total_distance_km += segment_distance_m / 1000
            
            # Расчет времени на основе скорости из CSV
            if current_speed > 0 and segment_distance_m > 0:
                # Время = расстояние / скорость
                time_for_segment_hours = (segment_distance_m / 1000) / current_speed
                time_for_segment_seconds = time_for_segment_hours * 3600
                self.total_time_seconds += time_for_segment_seconds
        
        # Расчет расхода топлива (рассчитываем на основе скорости)
        if current_speed <= 0:
            fuel_consumption = 0.8  # холостой ход
        elif current_speed < 30:
            fuel_consumption = 8.0 + (current_speed / 10)
        elif current_speed < 60:
            fuel_consumption = 7.0 + (current_speed / 20)
        else:
            fuel_consumption = 9.0 + (current_speed / 30)
        
        fuel_consumption = max(0.8, min(15.0, fuel_consumption))
        
        # Общее время в пути
        total_time = timedelta(seconds=self.total_time_seconds)
        
        # Прогресс по маршруту
        route_progress = (point_index / self.total_points) * 100
        
        return {
            'speed': current_speed,
            'optimal_speed': optimal_speed,
            'optimal_fuel': optimal_fuel,
            'fuel': round(fuel_consumption, 1),
            'fuel_saving': fuel_consumption - optimal_fuel if optimal_fuel > 0 else 0,
            'distance': round(self.total_distance_km, 2),
            'time_elapsed': total_time,
            'progress': route_progress
        }
    
    def create_data_panel(self, can_data):
        """Создание панели с данными включая оптимальные параметры"""
        self.ax_data.clear()
        self.ax_data.set_facecolor('#34495E')
        self.ax_data.axis('off')
        
        # Заголовок
        self.ax_data.text(0.5, 0.95, 'ДАННЫЕ В РЕАЛЬНОМ ВРЕМЕНИ', 
                         ha='center', va='top', color='white', 
                         fontsize=14, fontweight='bold', transform=self.ax_data.transAxes)
        
        # Основные данные
        y_pos = 0.80
        line_height = 0.12
        
        # Форматируем время
        time_str = str(can_data['time_elapsed']).split('.')[0]
        if len(time_str.split(':')) == 2:
            time_str = "00:" + time_str
        
        data_items = [
            ('ПРОЙДЕНО', f"{can_data['distance']} км"),
            ('ВРЕМЯ', time_str),
            ('ПРОГРЕСС', f"{can_data['progress']:.1f}%"),
            ('ТЕКУЩАЯ СКОРОСТЬ', f"{can_data['speed']} км/ч"),
            ('ОПТИМАЛЬНАЯ СКОРОСТЬ', f"{can_data['optimal_speed']} км/ч"),
            ('ТЕКУЩИЙ РАСХОД', f"{can_data['fuel']} л/100км"),
            ('ОПТИМАЛЬНЫЙ РАСХОД', f"{can_data['optimal_fuel']:.1f} л/100км"),
            ('ЭКОНОМИЯ', f"{can_data['fuel_saving']:.1f} л/100км")
        ]
        
        for label, value in data_items:
            # Метка
            self.ax_data.text(0.05, y_pos, label, color='#BDC3C7', 
                             fontsize=9, fontweight='bold', transform=self.ax_data.transAxes)
            # Значение
            color = '#3498DB' if 'ОПТИМАЛЬ' not in label and 'ЭКОНОМИЯ' not in label else '#27AE60'
            self.ax_data.text(0.05, y_pos - 0.04, value, color=color, 
                             fontsize=11, fontweight='bold', transform=self.ax_data.transAxes)
            y_pos -= line_height
        
        # Добавляем рамку
        rect = FancyBboxPatch((0.02, 0.02), 0.96, 0.93, 
                             boxstyle="round,pad=0.02", 
                             linewidth=2, edgecolor='#3498DB', 
                             facecolor='none', transform=self.ax_data.transAxes)
        self.ax_data.add_patch(rect)
    
    def animate(self, frame):
        """Функция анимации - вызывается для каждого кадра"""
        if not self.is_playing:
            return self.car_point, self.traveled_line
            
        if self.current_point >= self.total_points:
            self.stop_animation()
            return self.car_point, self.traveled_line
        
        try:
            # Текущие координаты
            current_lon = float(self.route_data['dolgota'].iloc[self.current_point])
            current_lat = float(self.route_data['shirota'].iloc[self.current_point])
            
            # Обновляем позицию автомобиля
            self.car_point.set_data([current_lon], [current_lat])
            
            # Обновляем пройденный путь
            traveled_lons = [float(x) for x in self.route_data['dolgota'].iloc[:self.current_point + 1]]
            traveled_lats = [float(x) for x in self.route_data['shirota'].iloc[:self.current_point + 1]]
            self.traveled_line.set_data(traveled_lons, traveled_lats)
            
            # Получаем CAN-данные из CSV с реальными расчетами
            can_data = self.get_can_data(self.current_point)
            
            # Обновляем панель данных
            self.create_data_panel(can_data)
            
            # Увеличиваем счетчик точки
            self.current_point += 1
            
            # Принудительно обновляем отображение
            self.fig.canvas.draw_idle()
            
        except Exception as e:
            print(f"Ошибка в анимации: {e}")
            self.stop_animation()
        
        return self.car_point, self.traveled_line
    
    def start_animation(self, event=None):
        """Запуск анимации"""
        if not self.is_playing:
            self.is_playing = True
            print("▶️ Анимация запущена")
            
            # Если анимация еще не создана, создаем ее
            if self.animation is None:
                self.animation = FuncAnimation(
                    self.fig, 
                    self.animate, 
                    frames=self.total_points,
                    interval=50,  # Более быстрая анимация
                    blit=False, 
                    repeat=False,
                    cache_frame_data=False
                )
    
    def stop_animation(self, event=None):
        """Остановка анимации"""
        if self.is_playing:
            self.is_playing = False
            print("⏹️ Анимация остановлена")
    
    def reset_animation(self, event=None):
        """Сброс анимации"""
        self.stop_animation()
        self.current_point = 0
        self.total_distance_km = 0
        self.total_time_seconds = 0
        self.start_time = datetime.now()
        
        print("🔄 Анимация сброшена")
        
        # Сбрасываем позицию автомобиля
        if len(self.route_data) > 0:
            start_lon = float(self.route_data['dolgota'].iloc[0])
            start_lat = float(self.route_data['shirota'].iloc[0])
            self.car_point.set_data([start_lon], [start_lat])
            self.traveled_line.set_data([], [])
        
        # Обновляем панель данных начальными значениями
        initial_data = self.get_can_data(0)
        self.create_data_panel(initial_data)
        
        # Принудительно обновляем отображение
        self.fig.canvas.draw_idle()
    
    def show(self):
        """Показать анимацию"""
        print("🚀 Запуск интерфейса анимации...")
        
        # Устанавливаем начальное состояние
        self.reset_animation()
        
        # Добавляем информацию о управлении
        plt.figtext(0.02, 0.02, "Управление: СТАРТ - запуск, СТОП - пауза, СБРОС - начало", 
                   color='white', fontsize=10)
        
        plt.show()

# Использование
if __name__ == "__main__":
    # Укажи путь к своему CSV файлу с скоростями
    csv_file = "маршрут_1_скорости.csv"  # Замени на свой файл
    
    try:
        print("🎬 ЗАПУСК АНИМАЦИИ МАРШРУТА")
        print("=" * 50)
        
        car_animation = CarAnimation(csv_file)
        car_animation.show()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Проверь:")
        print("1. Что файл CSV существует и доступен")
        print("2. Что в CSV есть колонки: 'shirota', 'dolgota', 'current_speed'")
        print("3. Что данные в колонках корректные числа")
        print("4. Что установлены библиотеки: matplotlib, pandas, numpy")
        print(f"5. Путь к файлу: {csv_file}")