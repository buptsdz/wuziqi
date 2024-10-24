# 更新后的 Pygame 五子棋游戏代码，包括轮流放置棋子的逻辑
import pygame
import sys
import time

# 初始化Pygame
pygame.init()
pygame.font.init()
# 设置窗口大小和标题
size = width, height = 640, 640
screen = pygame.display.set_mode(size)
pygame.display.set_caption("五子棋")

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# 设置棋盘大小
grid_size = 20
board = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
current_player = 1  # 当前玩家，1为黑棋，2为白棋
# 定义黑棋和白棋的当前位置
black_position = [grid_size // 2, grid_size // 2]
white_position = [grid_size // 2, grid_size // 2]


def draw_board():
    """绘制棋盘"""
    for i in range(grid_size):
        pygame.draw.line(
            screen,
            BLACK,
            (i * width // grid_size, 0),
            (i * width // grid_size, height),
            1,
        )
        pygame.draw.line(
            screen,
            BLACK,
            (0, i * height // grid_size),
            (width, i * height // grid_size),
            1,
        )


def draw_pieces():
    """绘制棋子"""
    for i in range(grid_size):
        for j in range(grid_size):
            if board[i][j] == 1:
                pygame.draw.circle(
                    screen,
                    BLACK,
                    (
                        i * width // grid_size + width // (grid_size * 2),
                        j * height // grid_size + height // (grid_size * 2),
                    ),
                    width // (grid_size * 2) - 2,
                )
            elif board[i][j] == 2:
                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        i * width // grid_size + width // (grid_size * 2),
                        j * height // grid_size + height // (grid_size * 2),
                    ),
                    width // (grid_size * 2) - 2,
                )


def show_current_player():
    """显示当前玩家"""
    font = pygame.font.SysFont("Microsoft YaHei", 18)
    text = font.render(
        f"当前玩家: {'黑棋' if current_player == 1 else '白棋'}", True, RED
    )
    screen.blit(text, (10, 10))


def check_winner(board, player):
    """检查是否有玩家获胜"""
    # 检查所有行、列以及两个对角线
    for i in range(grid_size):
        for j in range(grid_size):
            if board[i][j] == player:
                # 检查行
                if j <= grid_size - 5 and all(
                    board[i][j + k] == player for k in range(5)
                ):
                    return True
                # 检查列
                if i <= grid_size - 5 and all(
                    board[i + k][j] == player for k in range(5)
                ):
                    return True
                # 检查对角线
                if (
                    i <= grid_size - 5
                    and j <= grid_size - 5
                    and all(board[i + k][j + k] == player for k in range(5))
                ):
                    return True
                # 检查反对角线
                if (
                    i <= grid_size - 5
                    and j >= 4
                    and all(board[i + k][j - k] == player for k in range(5))
                ):
                    return True
    return False


def highlight_square(screen, x, y):
    """高亮显示鼠标所在的格子，根据当前玩家显示不同的高亮颜色"""
    row = x // (width // grid_size)
    col = y // (height // grid_size)

    # 根据当前玩家选择高亮颜色
    if current_player == 1:
        highlight_color = BLACK  # 黑棋玩家的高亮颜色
    else:
        highlight_color = WHITE  # 白棋玩家的高亮颜色

    pygame.draw.rect(
        screen,
        highlight_color,
        (
            row * width // grid_size,
            col * height // grid_size,
            width // grid_size,
            height // grid_size,
        ),
        3,
    )


def draw_button(screen, text, x, y, width, height, color, hover_color, action=None):
    """绘制半透明按钮并检查是否被点击"""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # 创建一个支持透明度的 Surface
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # 设置按钮颜色和透明度
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        button_surface.fill(hover_color + (120,))  # 半透明的悬停颜色
        if click[0] == 1 and action is not None:
            action()
    else:
        button_surface.fill(color + (80,))  # 半透明的普通颜色

    # 在按钮 Surface 上绘制文本
    font = pygame.font.SysFont("Microsoft YaHei", 22, bold=True)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = (width // 2, height // 2)
    button_surface.blit(text_surf, text_rect)

    # 将按钮 Surface 绘制到屏幕上
    screen.blit(button_surface, (x, y))


def restart_game():
    """重置游戏状态以重新开始"""
    global board, current_player, winner, game_over, game_ended
    board = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    current_player = 1
    winner = None
    game_over = False
    game_ended = False


def quit_game():
    """退出游戏"""
    global game_over
    game_over = True


# 游戏主循环
game_over = False
game_ended = False
winner = None
button_font = pygame.font.SysFont("Microsoft YaHei", 20)
last_click_time = 0
while not game_over:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

        if event.type == pygame.MOUSEBUTTONDOWN and not winner:
            row = mouse_x // (width // grid_size)
            col = mouse_y // (height // grid_size)
            # 如果该格子为空，则放置棋子并切换玩家
            if board[row][col] == 0:
                board[row][col] = current_player
                if check_winner(board, current_player):
                    winner = current_player
                    game_ended = True
                    last_click_time = time.time()
                current_player = 1 if current_player == 2 else 2

    screen.fill(GRAY)
    draw_board()
    draw_pieces()
    show_current_player()
    highlight_square(screen, mouse_x, mouse_y)

    if game_ended:
        font = pygame.font.SysFont("Microsoft YaHei", 40, bold=True)
        win_text = font.render(
            f"{'黑棋' if winner == 1 else '白棋'} 获胜！",
            True,
            RED,
        )
        screen.blit(
            win_text,
            (
                width // 2 - win_text.get_width() // 2,
                height // 2 - win_text.get_height() // 2,
            ),
        )
        # 绘制重新开始和退出游戏的按钮
        current_time = time.time()
        if current_time - last_click_time > 0.25:
            draw_button(
                screen,
                "重新开始",
                width // 2 - 100,
                height // 2 + 30,
                200,
                40,
                GRAY,
                RED,
                restart_game,
            )
            draw_button(
                screen,
                "退出游戏",
                width // 2 - 100,
                height // 2 + 80,
                200,
                40,
                GRAY,
                RED,
                quit_game,
            )
    pygame.display.flip()

pygame.quit()
sys.exit()
