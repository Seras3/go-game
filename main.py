from typing import Set
import arcade
import arcade.gui
from arcade.gui import ui_style, UIToggle
from arcade.gui.manager import UIManager
from enum import Enum
import os

# DIRECTORY :: CONSTANTS
WINDOW_TITLE = 'Adam Adrian Claudiu - GO!'
BACKGROUND_COLOR = arcade.color.DARK_SLATE_BLUE

# DIRECTORY :: ENUMS


class Algorithm(Enum):
    MIN_MAX = 0
    ALPHA_BETA = 1


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class Table(Enum):
    DIM7x7 = 0
    DIM9x9 = 1
    DIM10x10 = 2


class Moves(Enum):
    CNT50 = 0
    CNT100 = 1
    CNT200 = 2


# DIRECTORY :: COMPONENTS


class GameOptions:
    def __init__(self):
        self.vs_ai = False  # if AI is involved
        self.algorithm = Algorithm.MIN_MAX
        self.difficulty = Difficulty.EASY
        self.table = Table.DIM7x7
        self.moves = Moves.CNT50

    def getMap(self):
        return {
            'vs_ai': self.vs_ai,
            'difficulty': self.difficulty,
            'algorithm': self.algorithm,
            'table': self.table,
            'moves': self.moves,
        }


class MyGhostFlatButton(arcade.gui.UIGhostFlatButton):
    def __init__(self, center_x, center_y, text):
        super().__init__(
            text=text,
            center_x=center_x,
            center_y=center_y,
        )

    def on_click(self):
        text = self.text.strip()
        if text == 'Player VS Player':
            window.show_view(SettingsView())
        if text == 'Player VS AI':
            window.show_view(SettingsView(vs_ai=True))
        if text == 'AI VS AI':
            window.show_view(SettingsView(vs_ai=True))
        if text == 'EXIT':
            arcade.close_window()
        if text == 'BACK':
            window.show_view(MenuView())
        if text == 'PLAY':
            window.show_view(GameView())


class MySelectableButton(arcade.gui.UIGhostFlatButton):
    def __init__(self, center_x, center_y, text, option: Enum,
                 view: arcade.View):
        super().__init__(
            text=text,
            center_x=center_x,
            center_y=center_y,
        )
        self.option = option
        self.view = view

    def on_click(self):
        category = str(self.option.__class__.__name__).lower()
        self.view.set_option(category, self.option)


class MyToggler(arcade.gui.UIToggle):
    def __init__(self, center_x, center_y, height, value, view):
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            height=height,
            value=value,
        )
        self.view = view
        Style.set_toggle(self)

    def on_click(self):
        super().on_click()
        self.view.selectedOptions.algorithm = Algorithm(
            int(self.view.buttons['algorithm'].value))


# DIRECTORY :: STYLES


class Style:
    def set_unselected_button(button: MyGhostFlatButton):
        button.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(135, 21, 25),
            bg_color_hover=(135, 21, 25),
            bg_color_press=(122, 21, 24),
            border_color=(135, 21, 25),
            border_color_hover=arcade.color.WHITE,
            border_color_press=arcade.color.WHITE,
        )

    def set_selected_button(button: MyGhostFlatButton):
        button.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            bg_color=(51, 139, 57),
            bg_color_hover=(51, 139, 57),
            bg_color_press=(28, 71, 32),
            border_color=(51, 139, 57),
            border_color_hover=arcade.color.WHITE,
            border_color_press=arcade.color.WHITE,
        )

    def set_toggle(toggle: MyToggler):
        toggle.set_style_attrs(
            color_false=(220, 215, 222),
            bg_color_false=(100, 100, 100),
            color_true=(220, 215, 222),
            bg_color_true=(11, 167, 219),
        )


# DIRECTORY :: VIEWS
class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()

        self.x_slot = self.window.width // 2
        self.y_slot = self.window.height // 8

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(BACKGROUND_COLOR)

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(
            'GO!',
            self.x_slot,
            self.y_slot * 7,
            arcade.color.WHITE,
            align='center',
            anchor_x='center',
            anchor_y='center',
            font_size=40,
            bold=True,
        )

    def setup(self):
        self.ui_manager.purge_ui_elements()

        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' Player VS Player ',
                center_x=self.x_slot,
                center_y=self.y_slot * 5,
            ))
        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' Player VS AI ',
                center_x=self.x_slot,
                center_y=self.y_slot * 4,
            ))
        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' AI VS AI ',
                center_x=self.x_slot,
                center_y=self.y_slot * 3,
            ))

        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' EXIT ',
                center_x=self.x_slot,
                center_y=self.y_slot,
            ))


class SettingsView(arcade.View):
    def __init__(self, vs_ai=False):
        super().__init__()
        self.ui_manager = UIManager()
        self.x_slot = self.window.width // 6
        self.y_slot = self.window.height // 9
        self.selectedOptions = GameOptions()
        self.selectedOptions.vs_ai = vs_ai

        toggler = MyToggler(
            center_x=self.x_slot * 2,
            center_y=self.y_slot * 6,
            height=30,
            value=self.selectedOptions.algorithm.value,
            view=self,
        )

        line_table = 4 if vs_ai else 6
        line_moves = 3 if vs_ai else 5

        self.buttons = {
            'algorithm': toggler,
            'difficulty': self.get_buttons_from_enum(Difficulty, 5),
            'table': self.get_buttons_from_enum(Table, line_table),
            'moves': self.get_buttons_from_enum(Moves, line_moves),
        }

    def get_buttons_from_enum(self, enum, line):
        buttons = []

        for entry in enum:
            name = entry.name.upper()
            if enum != Difficulty:
                name = name[3:]

            button = MySelectableButton(
                text=' ' + name + ' ',
                center_x=self.x_slot * (2 + entry.value),
                center_y=self.y_slot * line,
                option=entry,
                view=self,
            )

            buttons += [button]
        return buttons

    def set_option(self, category, option):
        setattr(self.selectedOptions, category, option)
        self.update_buttons(category)

    def draw_buttons(self, category):
        for index, button in enumerate(self.buttons[category]):
            option = getattr(self.selectedOptions, category)
            if option.value == index:
                Style.set_selected_button(button)
            else:
                Style.set_unselected_button(button)

            self.ui_manager.add_ui_element(button)

    def update_buttons(self, category):
        for index, button in enumerate(self.buttons[category]):
            option = getattr(self.selectedOptions, category)
            if option.value == index:
                Style.set_selected_button(button)
            else:
                Style.set_unselected_button(button)

            button.render()

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(BACKGROUND_COLOR)

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.selectedOptions.algorithm = Algorithm(
                int(self.buttons['algorithm'].value))

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text(
            'Settings',
            self.x_slot * 3,
            self.y_slot * 8,
            arcade.color.WHITE,
            align='left',
            anchor_x='center',
            anchor_y='center',
            font_size=40,
        )

        if self.selectedOptions.vs_ai:
            arcade.draw_text(
                'Algorithm',
                self.x_slot,
                self.y_slot * 6,
                arcade.color.WHITE,
                align='left',
                anchor_x='center',
                anchor_y='center',
                font_size=20,
            )

            algorithms = [' Min-Max ', ' Alpha-Beta ']

            arcade.draw_text(
                algorithms[self.selectedOptions.algorithm.value],
                self.x_slot * 3,
                self.y_slot * 6,
                arcade.color.WHITE,
                align='right',
                anchor_x='center',
                anchor_y='center',
                font_size=20,
            )

            arcade.draw_text(
                'Difficulty',
                self.x_slot,
                self.y_slot * 5,
                arcade.color.WHITE,
                align='left',
                anchor_x='center',
                anchor_y='center',
                font_size=20,
            )

        arcade.draw_text(
            'Table',
            self.x_slot,
            self.y_slot * (4 if self.selectedOptions.vs_ai else 6),
            arcade.color.WHITE,
            align='left',
            anchor_x='center',
            anchor_y='center',
            font_size=20,
        )

        arcade.draw_text(
            'Moves',
            self.x_slot,
            self.y_slot * (3 if self.selectedOptions.vs_ai else 5),
            arcade.color.WHITE,
            align='left',
            anchor_x='center',
            anchor_y='center',
            font_size=20,
        )

    def setup(self):
        self.ui_manager.purge_ui_elements()

        if self.selectedOptions.vs_ai:
            self.ui_manager.add_ui_element(self.buttons['algorithm'])
            self.draw_buttons('difficulty')

        self.draw_buttons('table')
        self.draw_buttons('moves')

        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' BACK ',
                center_x=self.x_slot * 2,
                center_y=self.y_slot,
            ))

        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' PLAY ',
                center_x=self.x_slot * 4,
                center_y=self.y_slot,
            ))


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()

        ## TODO proper grid
        self.x_slot = self.window.width // 2
        self.y_slot = self.window.height // 8

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(BACKGROUND_COLOR)

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(
            'GAME',
            self.x_slot,
            self.y_slot * 7,
            arcade.color.WHITE,
            align='center',
            anchor_x='center',
            anchor_y='center',
            font_size=40,
            bold=True,
        )

    def setup(self):
        self.ui_manager.purge_ui_elements()

        self.ui_manager.add_ui_element(
            MyGhostFlatButton(
                text=' EXIT ',
                center_x=self.x_slot,
                center_y=self.y_slot,
            ))


# MAIN
if __name__ == '__main__':
    window = arcade.Window(title=WINDOW_TITLE)
    window.show_view(MenuView())
    arcade.run()