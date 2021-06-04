from typing import Set, Text
import arcade
import arcade.gui
import arcade.sprite
from arcade.gui import ui_style, UIToggle
from arcade.gui.manager import UIManager
from enum import Enum
import os
import copy

from pyglet.window.key import B, S

# DIRECTORY :: CONSTANTS
WINDOW_TITLE = 'Adam Adrian Claudiu - GO!'
BACKGROUND_COLOR = arcade.color.DARK_SLATE_BLUE
BLACK_STONE_PATH = 'assets/black.png'
WHITE_STONE_PATH = 'assets/white.png'
DIRECTIONS_X = (0, 1, 0, -1)
DIRECTIONS_Y = (-1, 0, 1, 0)


# DIRECTORY :: UTIL
def get_path(rel_path):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    return os.path.join(script_dir, rel_path)


class Debugger:
    def print_cluster_stone_matrix(stone_matrix):
        for i in range(len(stone_matrix) - 1, -1, -1):
            print([stone.cluster_id for stone in stone_matrix[i]])

    def print_matrix(matrix, n):
        for i in range(n, -1, -1):
            print([el for el in matrix[i]])

    def print_clusters(clusters):
        for cluster in clusters.values():
            print(cluster.id, cluster.liberties)


class Timer:
    def __init__(self):
        self.time = 0
        self.minutes = 0
        self.seconds = 0

    def increment(self, delta_time):
        self.time += delta_time
        self.minutes = int(self.time // 60)
        self.seconds = int((self.time // 1) % 60)

    def __str__(self):
        repr = f"0{self.minutes}" if self.minutes < 10 else str(self.minutes)
        repr += ':'
        repr += f"0{self.seconds}" if self.seconds < 10 else str(self.seconds)
        return repr


# DIRECTORY :: ENUMS
class Algorithm(Enum):
    MIN_MAX = 0
    ALPHA_BETA = 1


class Border(Enum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 4


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
    EMPTY = 0
    BLACK = 1
    WHITE = 2


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
        if text == 'BACK' or text == 'GO BACK':
            window.show_view(MenuView())
        if text == 'PLAY' or text == 'PLAY AGAIN':
            StoneCluster.uuid = 0
            window.show_view(GameView(self.selected_options))


class PlayerButton(arcade.gui.UIGhostFlatButton):
    def __init__(self, center_x, center_y, text, player, game):
        super().__init__(
            text=text,
            center_x=center_x,
            center_y=center_y,
        )

        self.player = player
        self.game = game

    def on_click(self):
        text = self.text.strip()
        if text == 'RESIGN':
            self.game.should_end = True
            self.player.resign()

        if text == "PASS":
            self.game.table.illegal_stone = None
            self.game.moves_played += 1
            if self.game.moves_played == self.game.available_moves:
                self.game.should_end = True
            else:
                self.game.next_turn()


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
    def __init__(self, stone_type):
        self.name = ""
        self.score = 0
        self.time = Timer()
        self.column_x = 0
        self.has_resigned = False
        self.stone_type = stone_type

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

    def resign(self):
        self.has_resigned = True


class StoneSprite(arcade.sprite.Sprite):
    def __init__(
            self,
            size,
            center_x,
            center_y,
            table_position,  # (0, 0) is  left bottom corner in matrix
            type=StoneType.EMPTY):
        scale = size / 900
        self.type = type
        self.table_position = table_position
        self.cluster_id = None

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


class StoneCluster:
    uuid = 0

    def __init__(self, stone: StoneSprite, liberties: set):
        self.id = StoneCluster.uuid
        self.type = stone.type
        self.stones = set([stone])
        self.liberties = liberties
        StoneCluster.uuid += 1

    def merge(self, cluster):
        for stone in cluster.stones:
            stone.cluster_id = self.id
        self.stones.update(cluster.stones)

    def update_capture_score(self, game):
        if game.turn == game.player1.stone_type:
            game.player1.score += len(self.stones)
        else:
            game.player2.score += len(self.stones)

    def clear_captured_stones(self):
        for stone in self.stones:
            stone.type = StoneType.EMPTY
            stone.cluster_id = None

    def update_liberties(self, table):
        self.liberties = set()
        for stone in self.stones:
            xc, yc = stone.table_position
            self.liberties.update(table.get_stone_liberties(xc, yc))

    def update_liberties_local(self, table, cluster_matrix):
        self.liberties.clear()
        for stone in self.stones:
            xc, yc = stone.table_position
            for i in range(len(DIRECTIONS_X)):
                x = xc + DIRECTIONS_X[i]
                y = yc + DIRECTIONS_Y[i]
                if table.is_valid_position(x,
                                           y) and cluster_matrix[x][y] == None:
                    self.liberties.add((x, y))


class Territory:
    def __init__(self):
        self.visited = set()
        self.colors = set()
        self.borders = set()  # distinct borders (vertex aren't included)

    def is_valid(self):
        return not (len(self.colors) > 1 or len(self.borders) > 1)


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

        self.square_size = self.height // self.nr_rows
        self.stone_size = self.square_size // 2

        self.stone_sprites = arcade.SpriteList()
        self.stone_matrix = []  # list of StoneSprite
        self.clusters = {}
        self.illegal_stone = None  # prevent conflicts

    def setup(self):
        for i in range(self.nr_rows + 1):
            self.stone_matrix.append([])
            for j in range(self.nr_rows + 1):
                center_x = self.start_x + j * self.square_size
                center_y = self.start_y + i * self.square_size
                stone = StoneSprite(self.stone_size,
                                    center_x,
                                    center_y,
                                    table_position=(i, j))
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
    def get_stone_raw_location(self, x, y):
        base_x = x - self.start_x + self.stone_size // 2
        base_y = y - self.start_y + self.stone_size // 2
        return base_y // self.stone_size, base_x // self.stone_size

    # get table location
    def get_stone_location(self, x, y):
        i, j = self.get_stone_raw_location(x, y)
        return i // 2, j // 2

    # get stone from window coordinates
    def get_stone(self, x, y) -> StoneSprite:
        i, j = self.get_stone_raw_location(x, y)
        if i % 2 == 1 or i % 2 == 1:
            return None
        i = i // 2
        j = j // 2
        return self.stone_matrix[i][j]

    # DEBUG PRINT
    def afi_cluster(self):
        for k, v in self.clusters.items():
            print('liberties', k, v.liberties)
            print('stone_ids')
            for stone in v.stones:
                print(stone.cluster_id)

    def update_cluster_liberties(self, clusters):
        for cluster in clusters.values():
            cluster.update_liberties(self)

    def update_cluster_liberties_local(self, clusters, cluster_matrix):
        for cluster in clusters.values():
            cluster.update_liberties_local(self, cluster_matrix)

    def is_vertex(self, i, j):
        return (i, j) in [(0, 0), (0, self.nr_rows), (self.nr_rows, 0),
                          (self.nr_rows, self.nr_rows)]

    def get_visited_borders(self, i, j) -> set():
        if self.is_vertex(i, j):
            return set()

        visited_borders = set()
        for k in range(len(DIRECTIONS_X)):
            x = i + DIRECTIONS_X[k]
            y = j + DIRECTIONS_Y[k]
            if not self.is_valid_position(x, y):
                border = None
                if x < 0:
                    border = Border.BOTTOM
                if x > self.nr_rows:
                    border = Border.TOP
                if y < 0:
                    border = Border.LEFT
                if y > self.nr_rows:
                    border = Border.RIGHT
                visited_borders.add(border)
        return visited_borders

    def try_visit_area(self, i, j, matrix, territory: Territory):
        territory.visited.add((i, j))
        territory.borders.update(self.get_visited_borders(i, j))

        for k in range(len(DIRECTIONS_X)):
            x = i + DIRECTIONS_X[k]
            y = j + DIRECTIONS_Y[k]
            if self.is_valid_position(x, y):
                if matrix[x][y] == StoneType.EMPTY:
                    if (x, y) in territory.visited:
                        continue
                    self.try_visit_area(x, y, matrix, territory)

                matrix[i][j] = matrix[x][y]
                territory.colors.add(matrix[x][y])

    def print_scoring_matrix(self, matrix):
        for i in range(self.nr_rows, -1, -1):
            print([tp.value for tp in matrix[i]])

    def calculate_scores(self, game):
        white_player = game.player1 if game.player1.stone_type == StoneType.WHITE else game.player2
        black_player = game.player2 if white_player == game.player1 else game.player1

        player_by_stone_type = {
            StoneType.WHITE: white_player,
            StoneType.BLACK: black_player
        }

        matrix_types = [[stone.type for stone in row]
                        for row in self.stone_matrix]

        print("INITIAL SCORE TABLE")
        self.print_scoring_matrix(matrix_types)
        print()

        visited_positions = set()
        for i in range(self.nr_rows + 1):
            for j in range(self.nr_rows + 1):
                if matrix_types[i][j] == StoneType.EMPTY and (
                        i, j) not in visited_positions:
                    initial_matrix_types = copy.deepcopy(matrix_types)

                    territory = Territory()
                    self.try_visit_area(i, j, matrix_types, territory)
                    if not territory.is_valid():
                        matrix_types = initial_matrix_types

        print("FINAL SCORE TABLE")
        self.print_scoring_matrix(matrix_types)
        print()

        for i in range(self.nr_rows + 1):
            for j in range(self.nr_rows + 1):
                if matrix_types[i][j] != StoneType.EMPTY:
                    player_by_stone_type[matrix_types[i][j]].score += 1

    def is_valid_move(self, game, i, j) -> bool:
        selected_stone = self.stone_matrix[i][j]
        if selected_stone == self.illegal_stone:
            return False

        selected_stone = copy.deepcopy(selected_stone)
        aux_clusters = copy.deepcopy(self.clusters)
        cluster_matrix = [[stone.cluster_id for stone in row]
                          for row in self.stone_matrix]
        type_matrix = [[stone.type for stone in row]
                       for row in self.stone_matrix]

        xc, yc = selected_stone.table_position
        stone_liberties = self.get_stone_liberties(xc, yc)
        aux_clusters[StoneCluster.uuid - 1] = StoneCluster(
            selected_stone, stone_liberties)

        cluster_matrix[xc][yc] = StoneCluster.uuid - 1
        type_matrix[xc][yc] = game.turn

        # print("[B] TRY_CLUSTERS")
        #  Debugger.print_clusters(self.clusters)

        for i in range(len(DIRECTIONS_X)):
            x = xc + DIRECTIONS_X[i]
            y = yc + DIRECTIONS_Y[i]
            if self.is_valid_position(x, y) and type_matrix[x][y] == game.turn:
                if cluster_matrix[xc][yc] == cluster_matrix[x][y]:
                    continue

                current_cluster = aux_clusters[cluster_matrix[xc][yc]]
                neighbor_cluster = aux_clusters[cluster_matrix[x][y]]

                aux_clusters.pop(current_cluster.id)
                neighbor_cluster.merge(current_cluster)
                for stone in neighbor_cluster.stones:
                    xs, ys = stone.table_position
                    cluster_matrix[xs][ys] = stone.cluster_id

        self.update_cluster_liberties_local(aux_clusters, cluster_matrix)

        StoneCluster.uuid -= 1

        has_caputred = self.try_capture(game, xc, yc, type_matrix,
                                        cluster_matrix, aux_clusters)
        # print("[A] TRY_CLUSTERS")
        # Debugger.print_clusters(self.clusters)

        if has_caputred:
            return True

        return not (len(aux_clusters[cluster_matrix[xc][yc]].liberties) == 0)

    # assert is a valid move calling (is_valid_move) first
    def update_move(self, game, i, j) -> bool:
        self.illegal_stone = None
        selected_stone = self.stone_matrix[i][j]
        selected_stone.type = game.turn

        xc, yc = selected_stone.table_position
        stone_liberties = self.get_stone_liberties(xc, yc)
        self.clusters[StoneCluster.uuid - 1] = StoneCluster(
            selected_stone, stone_liberties)
        selected_stone.cluster_id = StoneCluster.uuid - 1

        # print("[B] IN UPDATE")
        # Debugger.print_cluster_stone_matrix(self.stone_matrix)
        # print("CLUSTERS")
        # Debugger.print_clusters(self.clusters)

        for i in range(len(DIRECTIONS_X)):
            x = xc + DIRECTIONS_X[i]
            y = yc + DIRECTIONS_Y[i]
            if self.is_valid_position(
                    x, y) and self.stone_matrix[x][y].type == game.turn:

                neighbor_stone = self.stone_matrix[x][y]
                neighbor_cluster = self.clusters[neighbor_stone.cluster_id]

                if neighbor_stone.cluster_id == selected_stone.cluster_id:
                    continue

                current_cluster = self.clusters[selected_stone.cluster_id]
                self.clusters.pop(current_cluster.id)
                neighbor_cluster.merge(current_cluster)

        # print("[A] IN UPDATE")
        # Debugger.print_cluster_stone_matrix(self.stone_matrix)
        # print("CLUSTERS")
        # Debugger.print_clusters(self.clusters)
        self.update_cluster_liberties(self.clusters)

        # print("[A] UPD CLUSTER")
        # Debugger.print_cluster_stone_matrix(self.stone_matrix)

        # print("CLUSTERS")
        # Debugger.print_clusters(self.clusters)

        self.capture(game, selected_stone)

        self.update_cluster_liberties(self.clusters)

    # return True if could capture opponent stones
    def try_capture(self, game, xc, yc, type_matrix, cluster_matrix,
                    clusters) -> bool:
        has_captured = False
        opponent_type = game.get_opponent_player().stone_type

        for i in range(len(DIRECTIONS_X)):
            x = xc + DIRECTIONS_X[i]
            y = yc + DIRECTIONS_Y[i]
            if self.is_valid_position(
                    x, y) and type_matrix[x][y] == opponent_type:
                neighbor_cluster = clusters[cluster_matrix[x][y]]

                if len(neighbor_cluster.liberties) == 0:
                    clusters.pop(neighbor_cluster.id)
                    neighbor_cluster.clear_captured_stones()
                    has_captured = True

        return has_captured

    def capture(self, game, selected_stone: StoneSprite) -> bool:
        opponent_type = game.get_opponent_player().stone_type

        xc, yc = selected_stone.table_position
        for i in range(len(DIRECTIONS_X)):
            x = xc + DIRECTIONS_X[i]
            y = yc + DIRECTIONS_Y[i]
            if self.is_valid_position(
                    x, y) and self.stone_matrix[x][y].type == opponent_type:

                neighbor_stone = self.stone_matrix[x][y]
                neighbor_cluster = self.clusters[neighbor_stone.cluster_id]
                if len(neighbor_cluster.liberties) == 0:
                    if len(neighbor_cluster.stones) == 1:
                        self.illegal_stone = next(iter(
                            neighbor_cluster.stones))
                    self.clusters.pop(neighbor_cluster.id)
                    neighbor_cluster.update_capture_score(game)
                    neighbor_cluster.clear_captured_stones()

    def is_valid_position(self, x, y):
        return x >= 0 and x <= self.nr_rows and y >= 0 and y <= self.nr_rows

    def get_stone_liberties(self, xc, yc):
        stone_liberties = set()
        for i in range(len(DIRECTIONS_X)):
            x = xc + DIRECTIONS_X[i]
            y = yc + DIRECTIONS_Y[i]
            if self.is_valid_position(
                    x, y) and self.stone_matrix[x][y].type == StoneType.EMPTY:
                stone_liberties.add((x, y))
        return stone_liberties


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
        self.moves_played = 0
        self.available_moves = int(self.selected_options.moves.name[3:])
        self.winner = None
        self.game_started = False  # True when black make first move

        self.table = Table(
            start_x=int((self.window.width - 500) / 2),
            start_y=int((self.window.height - 500) / 2),
            width=500,
            height=500,
            dimension=selected_options.tabledimension,
        )
        self.player1 = Player(StoneType.BLACK)
        self.player2 = Player(StoneType.WHITE)
        self.cursor = StoneSprite(5, 0, 0, (-1, -1))

        self.turn = StoneType.BLACK  # decide player turn
        self.running = True  # if game is running
        self.should_end = False

        self.player1.column_x = self.table.start_x // 2
        self.player2.column_x = (3 * self.player1.column_x) + self.table.width
        self.player_name_y = 50
        self.player_time_y = 100
        self.player_score_y = 150
        self.player_pass_y = 400
        self.player_resign_y = 500

        p1_buttons = []
        p2_buttons = []

        if self.selected_options.game_type == GameType.PVP:
            self.player1.name = "Player1"
            self.player2.name = "Player2"
            p1_buttons += [
                PlayerButton(
                    self.player1.column_x,
                    self.player_resign_y,
                    " RESIGN ",
                    self.player1,
                    self,
                ),
                PlayerButton(
                    self.player1.column_x,
                    self.player_pass_y,
                    " PASS ",
                    self.player1,
                    self,
                ),
            ]

            p2_buttons += [
                PlayerButton(
                    self.player2.column_x,
                    self.window.height - self.player_resign_y,
                    " RESIGN ",
                    self.player2,
                    self,
                ),
                PlayerButton(
                    self.player2.column_x,
                    self.window.height - self.player_pass_y,
                    " PASS ",
                    self.player2,
                    self,
                ),
            ]

        if self.selected_options.game_type == GameType.PVA:
            self.player1.name = "YOU"
            self.player2.name = "AI"
            p1_buttons += [
                PlayerButton(
                    self.player1.column_x,
                    self.player_resign_y,
                    " RESIGN ",
                    self.player1,
                    self,
                ),
                PlayerButton(
                    self.player1.column_x,
                    self.player_pass_y,
                    " PASS ",
                    self.player1,
                    self,
                ),
            ]

        if self.selected_options.game_type == GameType.AVA:
            self.player1.name = "AI1"
            self.player2.name = "AI2"

        self.player_buttons = {
            StoneType.BLACK: p1_buttons,
            StoneType.WHITE: p2_buttons
        }

        self.end_buttons = {
            'play_again':
            MyGhostFlatButton(text=" PLAY AGAIN ",
                              center_x=320,
                              center_y=270,
                              selected_options=self.selected_options),
            'go_back':
            MyGhostFlatButton(text=" GO BACK ", center_x=500, center_y=270),
        }

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(BACKGROUND_COLOR)

    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.running:
            return

        self.cursor.center_x = x
        self.cursor.center_y = y

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if not self.running:
            return

        if self.table.is_valid_point(x, y):
            selected_stone = self.table.get_stone(x, y)
            if selected_stone == None or selected_stone.type != StoneType.EMPTY:
                return

            i, j = self.table.get_stone_location(x, y)

            # print("ULTIMA MUTAREEEEEEEEEEEEEEEEEE")

            # print("[B] CLUSTER_MATRIX")
            # Debugger.print_cluster_stone_matrix(self.table.stone_matrix)

            # print("[B] CLUSTERS")
            # Debugger.print_clusters(self.table.clusters)

            if self.table.is_valid_move(self, i, j):
                # print("[A] CLUSTER_MATRIX")
                # Debugger.print_cluster_stone_matrix(self.table.stone_matrix)

                # print("[A] CLUSTERS")
                # Debugger.print_clusters(self.table.clusters)

                self.table.update_move(self, i, j)
                self.game_started = True
                self.moves_played += 1
                if self.moves_played == self.available_moves:
                    self.should_end = True
                else:
                    self.next_turn()

    def get_winner(self):
        if self.player1.has_resigned or self.player2.has_resigned:
            return self.player2 if self.player1.has_resigned else self.player1

        self.table.calculate_scores(self)
        if self.player1.score == self.player2.score:
            return None

        return self.player1 if self.player1.score > self.player2.score else self.player2

    def get_current_player(self) -> Player:
        return self.player1 if self.turn == self.player1.stone_type else self.player2

    def get_opponent_player(self) -> Player:
        return self.player2 if self.turn == self.player1.stone_type else self.player1

    def on_update(self, delta_time):
        if self.running and self.game_started:
            self.get_current_player().time.increment(delta_time)
        self.table.stone_sprites.update()
        stones_hit = arcade.check_for_collision_with_list(
            self.cursor, self.table.stone_sprites)

        for stone_row in self.table.stone_matrix:
            for stone in stone_row:
                if stone.type == StoneType.EMPTY:
                    stone.alpha = 0
                    stone.texture = Textures.get_turn_texture(self.turn)
                    if stone in stones_hit:
                        stone.alpha = 150
                else:
                    stone.alpha = 255

    def draw_moves(self):
        arcade.draw_text(
            text=f"MOVES AVAILALBE: {self.available_moves - self.moves_played}",
            start_x=self.window.width / 2,
            start_y=self.window.height - 30,
            color=arcade.color.WHITE,
            font_size=20,
            anchor_x='center',
            anchor_y='center',
            align='center',
        )

    def on_draw(self):
        arcade.start_render()

        self.draw_moves()

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

        self.end_game()

    def end_game(self):
        if self.should_end:
            self.running = False
            self.clear_buttons()
            self.ui_manager.add_ui_element(self.end_buttons['play_again'])
            self.ui_manager.add_ui_element(self.end_buttons['go_back'])
            self.winner = self.get_winner()

        self.should_end = False
        if self.running == False:
            self.draw_end_game(self.winner)

    def setup(self):
        self.ui_manager.purge_ui_elements()
        self.table.setup()
        self.show_buttons()

    def next_turn(self):
        self.clear_buttons()
        self.turn = StoneType.WHITE if self.turn == StoneType.BLACK else StoneType.BLACK
        self.show_buttons()

    def show_buttons(self):
        for button in self.player_buttons[self.turn]:
            self.ui_manager.add_ui_element(button)

    def clear_buttons(self):
        for button in self.player_buttons[self.turn]:
            button.kill()

    def draw_end_game(self, winner):
        text = f"{winner.name} is the WINNER! :) " if winner != None else " Is draw. "

        arcade.draw_rectangle_filled(
            center_x=400,
            center_y=300,
            width=400,
            height=200,
            color=arcade.color.BLACK_LEATHER_JACKET,
        )

        arcade.draw_text(
            text=text,
            start_x=400,
            start_y=350,
            color=arcade.color.WHITE,
            font_size=18,
            align='center',
            anchor_x='center',
            anchor_y='center',
        )


# MAIN
if __name__ == '__main__':
    window = arcade.Window(title=WINDOW_TITLE)
    window.show_view(MenuView())
    arcade.run()