# -------------------- Libraries --------------------
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.config import Config
import json
import os
import sys

# Set fullscreen mode and dark blue background
Config.set('graphics', 'fullscreen', 'auto')
Window.clearcolor = (29 / 255, 43 / 255, 83 / 255, 1)

# Save file path - Kullanıcı dizininde sakla
if getattr(sys, 'frozen', False):
    # EXE olarak çalışıyorsa
    base_path = os.path.dirname(sys.executable)
else:
    # Python olarak çalışıyorsa
    base_path = os.path.dirname(os.path.abspath(__file__))

SAVE_FILE = os.path.join(base_path, 'game_save.json')

# Eğer save dosyası yoksa, boş bir dosya oluştur
if not os.path.exists(SAVE_FILE):
    empty_save = {
        'money': 0,
        'rig_count': 0,
        'rig_price': 50,
        'gpu_price': 100,
        'base_income': 1,
        'passive_income_multiplier': 1,
        'level': 0,
        'initial_rig_price_per_level': [50],
        'initial_gpu_price_per_level': [100],
        'rigs': []
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(empty_save, f)

# Resource path function for PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class LevelUpPopup(Popup):
    def __init__(self, game, **kwargs):
        super(LevelUpPopup, self).__init__(**kwargs)
        self.game = game
        self.title = "Congratulations! New Level"
        self.size_hint = (0.8, 0.4)
        self.auto_dismiss = False

        # Popup background with rounded corners
        with self.canvas.before:
            Color(29 / 255, 43 / 255, 83 / 255, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(size=self.update_rect, pos=self.update_rect)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        message = Label(
            text=f"Level Up! New Level: {self.game.level + 2}",
            font_size=20,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(message)

        level_up_button = Button(
            text="Proceed to New Level",
            size_hint=(1, 0.3),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        level_up_button.bind(on_press=self.level_up)
        layout.add_widget(level_up_button)

        self.content = layout

    def level_up(self, instance):
        self.game.level_up()
        self.dismiss()

    def update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MarketMenu(Popup):
    def __init__(self, game, **kwargs):
        super(MarketMenu, self).__init__(**kwargs)
        self.game = game
        self.title = "Market"
        self.size_hint = (0.8, 0.6)
        self.auto_dismiss = False

        # Popup background with rounded corners
        with self.canvas.before:
            Color(29 / 255, 43 / 255, 83 / 255, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(size=self.update_rect, pos=self.update_rect)

        # Market menu content
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # 2x Passive Income button
        self.passive_income_button = Button(
            text="2x Passive Income",
            size_hint=(1, 0.3),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.passive_income_button.bind(on_press=self.activate_passive_income)
        layout.add_widget(self.passive_income_button)

        # Close button
        close_button = Button(
            text="Close",
            size_hint=(1, 0.2),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        close_button.bind(on_press=self.dismiss)
        layout.add_widget(close_button)

        self.content = layout

    def activate_passive_income(self, instance):
        # Activate 2x passive income multiplier
        self.game.passive_income_multiplier = 2
        self.game.update_money_label()

        # Reset multiplier after 1 minute
        Clock.schedule_once(self.reset_passive_income, 60)

    def reset_passive_income(self, dt):
        # Reset passive income multiplier
        self.game.passive_income_multiplier = 1
        self.game.update_money_label()

    def update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RigWidget(BoxLayout):
    def __init__(self, game, base_income, **kwargs):
        super(RigWidget, self).__init__(**kwargs)
        self.game = game
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = Window.height * 0.1

        # Dark gray background
        with self.canvas.before:
            Color(47 / 255, 47 / 255, 47 / 255, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(size=self.update_rect, pos=self.update_rect)

        # Rig image
        self.rig_image = Image(
            source=resource_path('rig2.png'),
            size_hint=(None, None),
            size=(Window.width * 0.15, Window.height * 0.1)
        )
        self.add_widget(self.rig_image)

        # GPU image (initially hidden)
        self.gpu_image = Image(
            source=resource_path('gpu.png'),
            size_hint=(None, None),
            size=(Window.width * 0.15, Window.height * 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            opacity=0
        )
        self.add_widget(self.gpu_image)

        # Buy GPU button
        self.buy_gpu_button = Button(
            text=f"Buy GPU ({self.game.format_number(self.game.gpu_price)})",
            size_hint=(None, None),
            size=(Window.width * 0.3, Window.height * 0.05),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.buy_gpu_button.bind(on_press=self.buy_gpu)

        # Button with rounded corners
        with self.buy_gpu_button.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.button_rect = RoundedRectangle(
                size=self.buy_gpu_button.size,
                pos=self.buy_gpu_button.pos,
                radius=[15]
            )

        self.buy_gpu_button.bind(size=self.update_button_rect, pos=self.update_button_rect)
        self.add_widget(self.buy_gpu_button)

        # Income properties
        self.has_gpu = False
        self.base_income = base_income
        self.income = self.base_income

    def buy_gpu(self, instance):
        if self.game.money >= self.game.gpu_price:
            self.game.money -= self.game.gpu_price
            self.game.update_money_label()
            self.has_gpu = True
            self.income = self.base_income * 2
            self.gpu_image.opacity = 1
            self.remove_widget(self.rig_image)
            self.buy_gpu_button.disabled = True
            self.buy_gpu_button.background_color = (0.6, 0.6, 0.6, 1)

            # Increase GPU price
            self.game.gpu_price = int(self.game.gpu_price * 1.5)
            self.game.update_gpu_button_text()

            # Update button text
            self.buy_gpu_button.text = "GPU PURCHASED!"

    def update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_button_rect(self, instance, value):
        self.button_rect.pos = self.buy_gpu_button.pos
        self.button_rect.size = self.buy_gpu_button.size

class ClickerGame(FloatLayout):
    def __init__(self, **kwargs):
        super(ClickerGame, self).__init__(**kwargs)

        # Game variables
        self.money = 0
        self.rig_count = 0
        self.rig_price = 50
        self.gpu_price = 100
        self.base_income = 1
        self.passive_income_rate = 0
        self.passive_income_multiplier = 1

        # Level and max rigs variables
        self.level = 0
        self.current_max_rigs = 10

        # Initial prices per level
        self.initial_rig_price_per_level = [50]
        self.initial_gpu_price_per_level = [100]

        # UI components
        self.money_label = Label(
            text=f"Money: {self.format_number(self.money)} TL",
            font_size=Window.height * 0.03,
            size_hint=(None, None),
            size=(Window.width * 0.3, Window.height * 0.05),
            pos_hint={'x': 0.01, 'top': 0.99}
        )
        self.rig_label = Label(
            text=f"Rig Count: {self.rig_count}/{self.current_max_rigs}",
            font_size=Window.height * 0.03,
            size_hint=(None, None),
            size=(Window.width * 0.3, Window.height * 0.05),
            pos_hint={'x': 0.01, 'top': 0.94}
        )
        self.passive_income_label = Label(
            text=f"Passive Income: {self.format_number(self.passive_income_rate)} TL/s",
            font_size=Window.height * 0.03,
            size_hint=(None, None),
            size=(Window.width * 0.4, Window.height * 0.05),
            pos_hint={'right': 0.99, 'top': 0.99}
        )
        self.level_label = Label(
            text=f"Level: {self.level + 1}",
            font_size=Window.height * 0.03,
            size_hint=(None, None),
            size=(Window.width * 0.3, Window.height * 0.05),
            pos_hint={'right': 0.99, 'top': 0.94}
        )
        
        self.add_widget(self.money_label)
        self.add_widget(self.rig_label)
        self.add_widget(self.passive_income_label)
        self.add_widget(self.level_label)

        # Button layout
        self.button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            spacing=10
        )

        # Market button
        self.market_button = Button(
            text="Market",
            font_size=Window.height * 0.025,
            size_hint=(0.25, 1),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.market_button.bind(on_press=self.open_market)

        # Button with rounded corners
        with self.market_button.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.button_rect_market = RoundedRectangle(
                size=self.market_button.size,
                pos=self.market_button.pos,
                radius=[15]
            )

        self.market_button.bind(size=self.update_button_rect_market, pos=self.update_button_rect_market)
        self.button_layout.add_widget(self.market_button)

        # Level up button
        self.level_up_button = Button(
            text="Level\nUp",
            font_size=Window.height * 0.025,
            size_hint=(0.25, 1),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.level_up_button.bind(on_press=self.check_level_up)

        # Button with rounded corners
        with self.level_up_button.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.button_rect_level_up = RoundedRectangle(
                size=self.level_up_button.size,
                pos=self.level_up_button.pos,
                radius=[15]
            )
        self.level_up_button.bind(size=self.update_button_rect_level_up, pos=self.update_button_rect_level_up)
        self.button_layout.add_widget(self.level_up_button)

        # Buy rig button
        self.buy_rig_button = Button(
            text=f"Buy Rig\n({self.format_number(self.rig_price)})",
            font_size=Window.height * 0.025,
            size_hint=(0.25, 1),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.buy_rig_button.bind(on_press=self.buy_rig)

        # Button with rounded corners
        with self.buy_rig_button.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.button_rect_rig = RoundedRectangle(
                size=self.buy_rig_button.size,
                pos=self.buy_rig_button.pos,
                radius=[15]
            )
        self.buy_rig_button.bind(size=self.update_button_rect_rig, pos=self.update_button_rect_rig)
        self.button_layout.add_widget(self.buy_rig_button)

        self.add_widget(self.button_layout)

        # Click button
        self.click_button = Button(
            text="Earn Money!",
            font_size=Window.height * 0.03,
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.20},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        self.click_button.bind(on_press=self.earn_money)

        # Button with rounded corners
        with self.click_button.canvas.before:
            Color(0.2, 0.6, 1, 1)
            self.button_rect_click = RoundedRectangle(
                size=self.click_button.size,
                pos=self.click_button.pos,
                radius=[15]
            )
        self.click_button.bind(size=self.update_button_rect_click, pos=self.update_button_rect_click)
        self.add_widget(self.click_button)

        # Rig list with ScrollView and GridLayout
        self.rig_frame = GridLayout(
            cols=1,
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        self.rig_frame.bind(minimum_height=self.rig_frame.setter('height'))

        self.scroll_view = ScrollView(
            size_hint=(1, None),
            size=(Window.width, Window.height * 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        self.scroll_view.add_widget(self.rig_frame)
        self.add_widget(self.scroll_view)

        # Passive income mechanism
        Clock.schedule_interval(self.passive_income, 1)

        # Load saved game
        self.load_game()

    def save_game(self):
        # Save game state
        game_state = {
            'money': self.money,
            'rig_count': self.rig_count,
            'rig_price': self.rig_price,
            'gpu_price': self.gpu_price,
            'base_income': self.base_income,
            'passive_income_multiplier': self.passive_income_multiplier,
            'level': self.level,
            'initial_rig_price_per_level': self.initial_rig_price_per_level,
            'initial_gpu_price_per_level': self.initial_gpu_price_per_level,
            'rigs': []
        }

        # Save each rig's state
        for rig_widget in self.rig_frame.children:
            rig_state = {
                'has_gpu': rig_widget.has_gpu,
                'base_income': rig_widget.base_income,
                'income': rig_widget.income
            }
            game_state['rigs'].append(rig_state)

        # Save to JSON file
        with open(SAVE_FILE, 'w') as f:
            json.dump(game_state, f)

    def load_game(self):
        # Initialize game_state with default values
        game_state = {
            'money': 0,
            'rig_count': 0,
            'rig_price': 50,
            'gpu_price': 100,
            'base_income': 1,
            'passive_income_multiplier': 1,
            'level': 0,
            'initial_rig_price_per_level': [50],
            'initial_gpu_price_per_level': [100],
            'rigs': []
        }

        if os.path.exists(SAVE_FILE):
            # Load saved data
            with open(SAVE_FILE, 'r') as f:
                try:
                    loaded_state = json.load(f)
                    # Update game_state with loaded data
                    game_state.update(loaded_state)
                except json.JSONDecodeError:
                    # If file is corrupted, use default values
                    pass

        # Restore game state
        self.money = game_state.get('money', 0)
        self.rig_count = game_state.get('rig_count', 0)
        self.rig_price = game_state.get('rig_price', 50)
        self.gpu_price = game_state.get('gpu_price', 100)
        self.base_income = game_state.get('base_income', 1)
        self.passive_income_multiplier = game_state.get('passive_income_multiplier', 1)
        self.level = game_state.get('level', 0)
        self.initial_rig_price_per_level = game_state.get('initial_rig_price_per_level', [50])
        self.initial_gpu_price_per_level = game_state.get('initial_gpu_price_per_level', [100])
        self.current_max_rigs = self.calculate_max_rigs()

        # Restore rigs
        for rig_state in game_state.get('rigs', []):
            rig_widget = RigWidget(self, base_income=rig_state['base_income'])
            rig_widget.has_gpu = rig_state['has_gpu']
            rig_widget.income = rig_state['income']
            if rig_widget.has_gpu:
                rig_widget.gpu_image.opacity = 1
                rig_widget.remove_widget(rig_widget.rig_image)
                rig_widget.buy_gpu_button.disabled = True
                rig_widget.buy_gpu_button.background_color = (0.6, 0.6, 0.6, 1)
                rig_widget.buy_gpu_button.text = "GPU PURCHASED!"
            self.rig_frame.add_widget(rig_widget)

        # Update UI
        self.update_money_label()
        self.rig_label.text = f"Rig Count: {self.rig_count}/{self.current_max_rigs}"
        self.buy_rig_button.text = f"Buy Rig\n({self.format_number(self.rig_price)})"
        self.level_label.text = f"Level: {self.level + 1}"

    def calculate_max_rigs(self):
        # Calculate max rigs per level (1.5x increase)
        return int(10 * (1.5 ** self.level))

    def earn_money(self, instance):
        self.money += 1
        self.update_money_label()

    def buy_rig(self, instance):
        if self.money >= self.rig_price and self.rig_count < self.current_max_rigs:
            self.money -= self.rig_price
            self.rig_count += 1
            self.rig_price = int(self.rig_price * 1.5)
            self.base_income *= 1.25
        
            self.update_money_label()
            self.rig_label.text = f"Rig Count: {self.rig_count}/{self.current_max_rigs}"
            self.buy_rig_button.text = f"Buy Rig\n({self.format_number(self.rig_price)})"
        
            # Add new rig with current base_income
            self.rig_frame.add_widget(RigWidget(self, base_income=self.base_income))

            # Enable level up button when max rigs reached
            if self.rig_count >= self.current_max_rigs:
                self.level_up_button.disabled = False

    def check_level_up(self, instance):
        # Check if all GPUs are purchased
        if self.all_gpus_purchased():
            self.open_level_up_popup()
        else:
            # Show warning if not all GPUs are purchased
            self.show_warning_popup("Buy All GPUs!", "You must purchase all GPUs to level up.")

    def all_gpus_purchased(self):
        # Check if all rigs have GPUs
        for rig_widget in self.rig_frame.children:
            if not rig_widget.has_gpu:
                return False
        return True

    def show_warning_popup(self, title, message):
        # Create warning popup
        warning_popup = Popup(
            title=title,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        # Popup background with rounded corners
        with warning_popup.canvas.before:
            Color(29 / 255, 43 / 255, 83 / 255, 1)
            warning_popup.rect = RoundedRectangle(size=warning_popup.size, pos=warning_popup.pos, radius=[15])
        warning_popup.bind(size=self.update_warning_popup_rect, pos=self.update_warning_popup_rect)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(Label(text=message, font_size=20, color=(1, 1, 1, 1)))
        close_button = Button(
            text="Close",
            size_hint=(1, 0.3),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        close_button.bind(on_press=warning_popup.dismiss)
        layout.add_widget(close_button)
        warning_popup.content = layout
        warning_popup.open()

    def update_warning_popup_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def open_level_up_popup(self):
        # Open level up popup
        level_up_popup = LevelUpPopup(self)
        level_up_popup.open()

    def level_up(self):
        self.level += 1
        # Calculate new initial rig price (5x previous level's initial price)
        previous_level_initial_price = self.initial_rig_price_per_level[self.level - 1]
        new_initial_price = previous_level_initial_price * 5
        self.initial_rig_price_per_level.append(new_initial_price)
        self.rig_price = new_initial_price

        # Calculate new initial GPU price (5x previous level's initial price)
        previous_level_initial_gpu_price = self.initial_gpu_price_per_level[self.level - 1]
        new_initial_gpu_price = previous_level_initial_gpu_price * 5
        self.initial_gpu_price_per_level.append(new_initial_gpu_price)
        self.gpu_price = new_initial_gpu_price

        # Other updates
        self.current_max_rigs = self.calculate_max_rigs()
        self.rig_count = 0
        self.rig_frame.clear_widgets()
        self.rig_label.text = f"Rig Count: {self.rig_count}/{self.current_max_rigs}"
        self.buy_rig_button.text = f"Buy Rig\n({self.format_number(self.rig_price)})"
        self.level_label.text = f"Level: {self.level + 1}"
        self.level_up_button.disabled = True

    def passive_income(self, dt):
        total_income = sum(rig.income for rig in self.rig_frame.children)
        self.money += total_income * self.passive_income_multiplier
        self.passive_income_rate = total_income * self.passive_income_multiplier
        self.update_money_label()

    def update_money_label(self):
        self.money_label.text = f"Money: {self.format_number(self.money)} TL"
        self.passive_income_label.text = f"Passive Income: {self.format_number(self.passive_income_rate)} TL/s"

    def format_number(self, number):
        # Format number with k, m, b suffixes
        if number >= 1_000_000_000:
            return f"{round(number / 1_000_000_000, 1)}b"
        elif number >= 1_000_000:
            return f"{round(number / 1_000_000, 1)}m"
        elif number >= 1_000:
            return f"{round(number / 1_000, 1)}k"
        else:
            return f"{round(number, 1)}"

    def open_market(self, instance):
        # Open market menu
        market_menu = MarketMenu(self)
        market_menu.open()

    def update_button_rect_market(self, instance, value):
        self.button_rect_market.pos = self.market_button.pos
        self.button_rect_market.size = self.market_button.size

    def update_button_rect_level_up(self, instance, value):
        self.button_rect_level_up.pos = self.level_up_button.pos
        self.button_rect_level_up.size = self.level_up_button.size

    def update_button_rect_rig(self, instance, value):
        self.button_rect_rig.pos = self.buy_rig_button.pos
        self.button_rect_rig.size = self.buy_rig_button.size

    def update_button_rect_click(self, instance, value):
        self.button_rect_click.pos = self.click_button.pos
        self.button_rect_click.size = self.click_button.size

    def update_gpu_button_text(self):
        # Update GPU buy button texts
        for rig_widget in self.rig_frame.children:
            if not rig_widget.has_gpu:
                rig_widget.buy_gpu_button.text = f"Buy GPU ({self.format_number(self.gpu_price)})"

class ClickerGameApp(App):
    def build(self):
        return ClickerGame()

    def on_stop(self):
        # Save game state when app closes
        self.root.save_game()

if __name__ == "__main__":
    app = ClickerGameApp()
    app.run()