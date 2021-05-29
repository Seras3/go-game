from typing import Set, Text
import arcade
import arcade.gui
import arcade.sprite
from arcade.gui import ui_style, UIToggle
from arcade.gui.manager import UIManager
from enum import Enum
import os

# DIRECTORY :: CONSTANTS
WINDOW_TITLE = 'Adam Adrian Claudiu - GO!'
BACKGROUND_COLOR = arcade.color.DARK_SLATE_BLUE
BLACK_STONE_PATH = 'assets/black.png'
WHITE_STONE_PATH = 'assets/white.png'


# DIRECTORY :: UTIL
def get_path(rel_path):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    return os.path.join(script_dir, rel_path)


# DIRECTORY :: ENUMS
class Algorithm(Enum):
    MIN_MAX = 0
    ALPHA_BETA = 1


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class TableDimension(Enum):
    DIM7x7 = 0
    DIM9x9 = 1
    DIM10x10 = 2


class Moves(Enum):
    CNT50 = 0
    CNT100 = 1
    CNT200 = 2


class GameType(Enum):
    PVP = 0
    PVA = 1
    AVA = 2


class StoneType(Enum):
    BLACK = 0
    WHITE = 1


# DIRECTORY :: COMPONENTS


class GameOptions:
    def __init__(self):
        self.game_type = GameType.PVP
        self.algorithm = Algorithm.MIN_MAX
        self.difficulty = Difficulty.EASY
        self.tabledimension = TableDimension.DIM7x7
        self.moves = Moves.CNT50

    def getMap(self):
        return {
            'game_type': self.game_type,
            'difficulty': self.difficulty,
            'algorithm': self.algorithm,
            'tabledimension': self.tabledimension,
            'moves': self.moves,
        }

    def is_versus_ai(self):
        return self.game_type in [GameType.PVA, GameType.AVA]


class MyGhostFlatButton(arcade.gui.UIGhostFlatButton):
    def __init__(self, center_x, center_y, text, selected_options=None):
        super().__init__(
            text=text,
            center_x=center_x,
            center_y=center_y,
        )

        self.selected_options = selected_options

    def on_click(self):
        text = self.text.strip()
        if text == 'Player VS Player':
            window.show_view(SettingsView(GameType.PVP))
        if text == 'Player VS AI':
            window.show_view(SettingsView(GameType.PVA))
        if text == 'AI VS AI':
            window.show_view(SettingsView(GameType.AVA))
        if text == 'EXIT':
            arcade.close_window()
        if text == 'BACK':
            window.show_view(MenuView())
        if text == 'PLAY':
            window.show_view(GameView(self.selected_options))


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
        self.view.selected_options.algorithm = Algorithm(
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


class Textures:
    black_stone = arcade.load_texture(BLACK_STONE_PATH)
    white_stone = arcade.load_texture(WHITE_STONE_PATH)

    def get_turn_texture(turn):
        return Textures.black_stone if turn == StoneType.BLACK else Textures.white_stone


# DIRECTORY :: MODELS


class Player:
    def __init__(self, name="", score=0, time=0, column_x=0):
        self.name = name
        self.score = score
        self.time = time
        self.column_x = column_x

    def draw(self, name_y, score_y, time_y, name_color):
        self.draw_name(name_y, name_color)
        self.draw_time(time_y)
        self.draw_score(score_y)

    def draw_name(self, start_y, color):
        arcade.draw_text(
            self.name,
            start_x=self.column_x,
            start_y=start_y,
            color=color,
            font_size=20,
            anchor_x='center',
            anchor_y='center',
            align='center',
        )

    def draw_score(self, start_y):
        arcade.draw_text(
            f"SCORE: {self.score}",
            start_x=self.column_x,
            start_y=start_y,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_x='center',
            anchor_y='center',
            align='center',
        )

    def draw_time(self, start_y):
        arcade.draw_text(
            f"TIME: {self.time}",
            start_x=self.column_x,
            start_y=start_y,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_x='center',
            anchor_y='center',
            align='center',
        )


class StoneSprite(arcade.sprite.Sprite):
    def __init__(self, size, center_x, center_y, type=None):
        scale = size / 900
        self.type = type

        super().__init__(
            filename=get_path('assets/white.png'),
            scale=scale,
            center_x=center_x,
            center_y=center_y,
        )

    def assign_type(self, type: StoneType):
        self.type = type
        if type == StoneType.BLACK:
            self.texture = Textures.black_stone
        else:
            self.texture = Textures.white_stone
        self.alpha = 255


class Table:
    def __init__(self, start_x, start_y, width, height,
                 dimension: TableDimension):
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height

        if dimension == TableDimension.DIM7x7:
            self.nr_rows = 7
        if dimension == TableDimension.DIM9x9:
            self.nr_rows = 9
        if dimension == TableDimension.DIM10x10:
            self.nr_rows = 10

        self.matrix = [[0 for _ in range(self.nr_rows + 1)]
                       for _ in range(self.nr_rows + 1)]

        self.square_size = self.height // self.nr_rows
        self.stone_size = self.square_size // 2

        self.stone_sprites = arcade.SpriteList()
        self.stone_matrix = []  # list of StoneSprite

    def setup(self):
        for i in range(self.nr_rows + 1):
            self.stone_matrix.append([])
            for j in range(self.nr_rows + 1):
                center_x = self.start_x + j * self.square_size
                center_y = self.start_y + i * self.square_size
                stone = StoneSprite(self.stone_size, center_x, center_y)
                self.stone_sprites.append(stone)
                self.stone_matrix[i].append(stone)

    def draw(self):
        for i in range(self.nr_rows):
            for j in range(self.nr_rows):
                center_x = self.start_x + i * self.square_size + self.square_size // 2
                center_y = self.start_y + j * self.square_size + self.square_size // 2
                arcade.draw_rectangle_outline(
                    center_x=center_x,
                    center_y=center_y,
                    width=self.square_size,
                    height=self.square_size,
                    color=arcade.color.WHITE,
                )

    def is_valid_point(self, x, y):
        if x < self.start_x - self.stone_size / 2:
            return False
        if x > self.start_x + self.width + self.stone_size / 2:
            return False
        if y < self.start_y - self.stone_size / 2:
            return False
        if y > self.start_y + self.height + self.stone_size / 2:
            return False
        return True

    # positions with odd coeficients are miss clicks
    def get_stone_location(self, x, y):
        base_x = x - self.start_x + self.stone_size // 2
        base_y = y - self.start_y + self.stone_size // 2
        return base_y // self.stone_size, base_x // self.stone_size

    def get_stone(self, x, y) -> StoneSprite:
        i, j = self.get_stone_location(x, y)
        if i % 2 == 1 or i % 2 == 1:
            return None
        i = i // 2
        j = j // 2
        return self.stone_matrix[i][j]


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
    def __init__(self, game_type):
        super().__init__()
        self.ui_manager = UIManager()
        self.x_slot = self.window.width // 6
        self.y_slot = self.window.height // 9
        self.selected_options = GameOptions()
        self.selected_options.game_type = game_type

        toggler = MyToggler(
            center_x=self.x_slot * 2,
            center_y=self.y_slot * 6,
            height=30,
            value=self.selected_options.algorithm.value,
            view=self,
        )

        line_table = 4 if self.selected_options.is_versus_ai() else 6
        line_moves = 3 if self.selected_options.is_versus_ai() else 5

        self.buttons = {
            'algorithm':
            toggler,
            'difficulty':
            self.get_buttons_from_enum(Difficulty, 5),
            'tabledimension':
            self.get_buttons_from_enum(TableDimension, line_table),
            'moves':
            self.get_buttons_from_enum(Moves, line_moves),
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
        setattr(self.selected_options, category, option)
        self.update_buttons(category)

    def draw_buttons(self, category):
        for index, button in enumerate(self.buttons[category]):
            option = getattr(self.selected_options, category)
            if option.value == index:
                Style.set_selected_button(button)
            else:
                Style.set_unselected_button(button)

            self.ui_manager.add_ui_element(button)

    def update_buttons(self, category):
        for index, button in enumerate(self.buttons[category]):
            option = getattr(self.selected_options, category)
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
            self.selected_options.algorithm = Algorithm(
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

        if self.selected_options.is_versus_ai():
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
                algorithms[self.selected_options.algorithm.value],
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
            self.y_slot * (4 if self.selected_options.is_versus_ai() else 6),
            arcade.color.WHITE,
            align='left',
            anchor_x='center',
            anchor_y='center',
            font_size=20,
        )

        arcade.draw_text(
            'Moves',
            self.x_slot,
            self.y_slot * (3 if self.selected_options.is_versus_ai() else 5),
            arcade.color.WHITE,
            align='left',
            anchor_x='center',
            anchor_y='center',
            font_size=20,
        )

    def setup(self):
        self.ui_manager.purge_ui_elements()

        if self.selected_options.is_versus_ai():
            self.ui_manager.add_ui_element(self.buttons['algorithm'])
            self.draw_buttons('difficulty')

        self.draw_buttons('tabledimension')
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
                selected_options=self.selected_options,
            ))


class GameView(arcade.View):
    def __init__(self, selected_options: GameOptions):
        super().__init__()
        self.ui_manager = UIManager()

        self.selected_options = selected_options

        self.table = Table(
            start_x=int((self.window.width - 500) / 2),
            start_y=int((self.window.height - 500) / 2),
            width=500,
            height=500,
            dimension=selected_options.tabledimension,
        )
        self.player1 = Player()
        self.player2 = Player()
        self.cursor = StoneSprite(5, 0, 0)

        self.turn = StoneType.BLACK

        self.player1.column_x = self.table.start_x // 2
        self.player2.column_x = (3 * self.player1.column_x) + self.table.width
        self.player_name_y = 50
        self.player_time_y = 100
        self.player_score_y = 150

        if self.selected_options.game_type == GameType.PVP:
            self.player1.name = "Player1"
            self.player2.name = "Player2"

        if self.selected_options.game_type == GameType.PVA:
            self.player1.name = "YOU"
            self.player2.name = "AI"

        if self.selected_options.game_type == GameType.AVA:
            self.player1.name = "AI1"
            self.player2.name = "AI2"

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(BACKGROUND_COLOR)

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_mouse_motion(self, x, y, dx, dy):
        self.cursor.center_x = x
        self.cursor.center_y = y

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.table.is_valid_point(x, y):
            selected_stone = self.table.get_stone(x, y)
            if selected_stone == None or selected_stone.type != None:
                return

            selected_stone.type = self.turn
            self.next_turn()

    def on_update(self, delta_time):
        self.table.stone_sprites.update()
        stones_hit = arcade.check_for_collision_with_list(
            self.cursor, self.table.stone_sprites)

        for stone_row in self.table.stone_matrix:
            for stone in stone_row:
                if stone.type == None:
                    stone.alpha = 0
                    stone.texture = Textures.get_turn_texture(self.turn)
                    if stone in stones_hit:
                        stone.alpha = 150
                else:
                    stone.alpha = 255

    def on_draw(self):
        arcade.start_render()

        self.player1.draw(
            self.player_name_y,
            self.player_score_y,
            self.player_time_y,
            arcade.color.AQUA,
        )

        if self.turn == StoneType.BLACK:
            Textures.black_stone.draw_sized(self.player1.column_x, 300, 50, 50)
        else:
            Textures.white_stone.draw_sized(self.player2.column_x, 300, 50, 50)

        self.player2.draw(
            self.window.height - self.player_name_y,
            self.window.height - self.player_time_y,
            self.window.height - self.player_score_y,
            arcade.color.PINK,
        )

        self.table.draw()
        self.table.stone_sprites.draw()

    def setup(self):
        self.ui_manager.purge_ui_elements()
        self.table.setup()

    def next_turn(self):
        self.turn = StoneType.WHITE if self.turn == StoneType.BLACK else StoneType.BLACK


# MAIN
if __name__ == '__main__':
    window = arcade.Window(title=WINDOW_TITLE)
    window.show_view(MenuView())
    arcade.run()