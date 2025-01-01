import pygame
import sys
import time
import random

# --- 全局常量与变量 ---

# 窗口大小
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750

# 棋盘大小与坐标区域
BOARD_WIDTH = 700
BOARD_HEIGHT = 700

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 半透明按钮背景颜色（RGBA，最后一个值为透明度）
BUTTON_BG_COLOR = (128, 128, 128, 150)  # 灰色，约60%透明
BUTTON_HOVER_COLOR = (255, 0, 0, 150)  # 红色，约60%透明

# 棋盘网格
GRID_SIZE = 25
CELL_SIZE = BOARD_WIDTH // GRID_SIZE  # 每格像素宽度

# 游戏状态
game_state = "menu"  # 可取 "menu" or "playing"
current_player = 1  # 1=黑棋(玩家), 2=白棋(AI)
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
winner = None
game_ended = False
game_over = False

# 历史战绩
history = []

# AI相关
ai_thinking = False
ai_move_time = 0
AI_DELAY = 1  # 模拟AI思考延迟

# 难度列表（含新难度）
difficulties = ["Common", "Medium", "Hard"]
selected_difficulty = "Common"  # 默认难度

# 新增：AI最后一手的落子坐标(行,列)
ai_last_move = None

# --- 初始化Pygame ---
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("五子棋 - 人机对战（低智版）")
clock = pygame.time.Clock()

# 字体
font_small = pygame.font.SysFont("Microsoft YaHei", 18)
font_medium = pygame.font.SysFont("Microsoft YaHei", 24, bold=True)
font_large = pygame.font.SysFont("Microsoft YaHei", 40, bold=True)


# --- 函数定义 ---
def restart_game():
    """重新开始游戏(清空棋盘、历史等)，保留当前难度，不退回菜单"""
    global board, current_player, winner, game_ended
    global ai_thinking, ai_move_time, history, ai_last_move
    board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    current_player = 1
    winner = None
    game_ended = False
    ai_thinking = False
    ai_move_time = 0
    history = []
    ai_last_move = None  # 重置AI最后一手
    print("游戏已重置，继续对局")


def quit_game():
    """退出游戏"""
    global game_over
    game_over = True


def draw_menu():
    """绘制初始菜单界面"""
    screen.fill(GRAY)
    title_text = font_large.render("五子棋 - 人机对战（低智版）", True, RED)
    screen.blit(
        title_text,
        (
            SCREEN_WIDTH // 2 - title_text.get_width() // 2,
            100,
        ),
    )

    # “难度选择：” 文字
    diff_choice_text = font_medium.render("难度选择：", True, BLUE)
    screen.blit(
        diff_choice_text,
        (
            SCREEN_WIDTH // 2 - diff_choice_text.get_width() // 2,
            200,
        ),
    )

    # 难度按钮
    button_width = 120
    button_height = 50
    gap = 25
    total_width = 3 * button_width + 3 * gap
    start_x = SCREEN_WIDTH // 2 - total_width // 2
    start_y = 250

    for i, diff in enumerate(difficulties):
        x = start_x + i * (button_width + gap)
        y = start_y
        draw_button(
            diff,
            x,
            y,
            button_width,
            button_height,
            (150, 150, 150),
            (255, 0, 0),
            lambda d=diff: set_difficulty(d),
            transparent=False,
        )

    # “开始游戏”按钮
    start_game_btn_w = 200
    start_game_btn_h = 60
    start_game_x = SCREEN_WIDTH // 2 - start_game_btn_w // 2
    start_game_y = 400
    draw_button(
        "开始游戏",
        start_game_x,
        start_game_y,
        start_game_btn_w,
        start_game_btn_h,
        (150, 150, 150),
        (0, 128, 255),
        start_game,
        transparent=False,
    )

    # 当前选择难度
    diff_text = font_medium.render(f"当前难度：{selected_difficulty}", True, BLUE)
    screen.blit(
        diff_text,
        (
            SCREEN_WIDTH // 2 - diff_text.get_width() // 2,
            500,
        ),
    )


def set_difficulty(diff):
    """设置难度"""
    global selected_difficulty
    selected_difficulty = diff
    print(f"难度已设置为: {diff}")


def start_game():
    """点击“开始游戏”按钮后，进入对局状态"""
    global game_state
    restart_game()
    game_state = "playing"
    print(f"开始游戏，当前难度为: {selected_difficulty}")


def draw_button(text, x, y, w, h, color, hover_color, action=None, transparent=False):
    """
    绘制按钮并检测点击
    :param transparent: 若为 True，则使用半透明绘制
    """
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    btn_rect = pygame.Rect(x, y, w, h)

    # 判定鼠标是否在按钮范围内
    if btn_rect.collidepoint(mouse):
        bg_color = hover_color
        if click[0] == 1 and action:
            action()
    else:
        bg_color = color

    if transparent:
        # 绘制半透明按钮
        button_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        button_surface.fill(bg_color)  # RGBA
        screen.blit(button_surface, (x, y))
    else:
        # 普通不透明按钮
        pygame.draw.rect(screen, bg_color, btn_rect)

    # 绘制文字
    txt_surf = font_medium.render(text, True, WHITE)
    txt_rect = txt_surf.get_rect(center=btn_rect.center)
    screen.blit(txt_surf, txt_rect)


def draw_board():
    """绘制棋盘和网格"""
    pygame.draw.rect(screen, GRAY, (0, 0, BOARD_WIDTH, BOARD_HEIGHT))
    for i in range(GRID_SIZE):
        # 垂直线
        start_x = i * CELL_SIZE
        pygame.draw.line(screen, BLACK, (start_x, 0), (start_x, BOARD_HEIGHT), 1)
        # 水平线
        start_y = i * CELL_SIZE
        pygame.draw.line(screen, BLACK, (0, start_y), (BOARD_WIDTH, start_y), 1)


def draw_pieces():
    """绘制棋子，并对AI最新落子做标识"""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            piece = board[i][j]
            center_x = i * CELL_SIZE + CELL_SIZE // 2
            center_y = j * CELL_SIZE + CELL_SIZE // 2

            if piece == 1:
                # 黑棋
                pygame.draw.circle(
                    screen, BLACK, (center_x, center_y), CELL_SIZE // 2 - 2
                )
            elif piece == 2:
                # 白棋
                pygame.draw.circle(
                    screen, WHITE, (center_x, center_y), CELL_SIZE // 2 - 2
                )

                # 如果这颗白棋是AI刚刚下的那一子，则额外绘制一个红色圆环标识
                if ai_last_move is not None and (i, j) == ai_last_move:
                    pygame.draw.circle(
                        screen,
                        RED,
                        (center_x, center_y),
                        CELL_SIZE // 2 - 2,
                        width=2,  # 圆环边框宽度
                    )


def highlight_square():
    """根据鼠标位置高亮方格"""
    if current_player == 1 and not game_ended:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # 仅在棋盘区域内才执行
        if 0 <= mouse_x < BOARD_WIDTH and 0 <= mouse_y < BOARD_HEIGHT:
            row = mouse_x // CELL_SIZE
            col = mouse_y // CELL_SIZE
            rect_x = row * CELL_SIZE
            rect_y = col * CELL_SIZE
            pygame.draw.rect(screen, BLACK, (rect_x, rect_y, CELL_SIZE, CELL_SIZE), 3)


def display_info():
    """显示顶部文字信息：当前玩家、难度等"""
    if current_player == 1:
        player_text = "黑棋"
    else:
        player_text = "白棋 (AI)"
    txt = font_small.render(
        f"当前玩家: {player_text}   难度: {selected_difficulty}", True, RED
    )
    screen.blit(txt, (10, 10))


def display_history():
    """在右侧(700,0)-(900,800)区域显示历史战绩"""
    pygame.draw.rect(
        screen, WHITE, (BOARD_WIDTH, 0, SCREEN_WIDTH - BOARD_WIDTH, SCREEN_HEIGHT)
    )
    pygame.draw.rect(
        screen, BLACK, (BOARD_WIDTH, 0, SCREEN_WIDTH - BOARD_WIDTH, SCREEN_HEIGHT), 2
    )

    title = font_medium.render("对局记录", True, BLACK)
    screen.blit(title, (BOARD_WIDTH + 10, 10))

    recent_moves = history[-20:]  # 显示最近20步
    for idx, entry in enumerate(recent_moves):
        player = "黑棋" if entry["player"] == 1 else "白棋"
        move = entry["move"]
        move_txt = f"{len(history)-len(recent_moves)+idx+1}. {player} -> ({move[0]}, {move[1]})"
        text = font_small.render(move_txt, True, BLACK)
        screen.blit(text, (BOARD_WIDTH + 10, 50 + idx * 20))


def add_to_history(player, move):
    """将移动添加到历史中"""
    history.append({"player": player, "move": move})


def check_winner(board, player):
    """检查是否五连珠"""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if board[x][y] == player:
                # 横向
                if y <= GRID_SIZE - 5 and all(
                    board[x][y + k] == player for k in range(5)
                ):
                    return True
                # 纵向
                if x <= GRID_SIZE - 5 and all(
                    board[x + k][y] == player for k in range(5)
                ):
                    return True
                # 主对角线
                if (
                    x <= GRID_SIZE - 5
                    and y <= GRID_SIZE - 5
                    and all(board[x + k][y + k] == player for k in range(5))
                ):
                    return True
                # 副对角线
                if (
                    x <= GRID_SIZE - 5
                    and y >= 4
                    and all(board[x + k][y - k] == player for k in range(5))
                ):
                    return True
    return False


def heuristic_score(board, player):
    """简单启发式评分函数"""
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    score = 0
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] != player:
                continue
            for d in directions:
                count = 1
                for k in range(1, 5):
                    nx = i + d[0] * k
                    ny = j + d[1] * k
                    if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                        break
                    if board[nx][ny] == player:
                        count += 1
                    else:
                        break
                if count == 2:
                    score += 10
                elif count == 3:
                    score += 100
                elif count == 4:
                    score += 1000
                elif count >= 5:
                    score += 100000
    return score


def ai_move():
    """AI 落子逻辑"""
    global current_player, winner, game_ended
    global ai_thinking, ai_move_time, ai_last_move  # 注意声明

    diff = selected_difficulty

    # Common：略微攻防
    if diff == "Common":
        move = ai_move_heuristic(1.0, 1.1)
    # Medium：更强调进攻(1.5 : 1.2)
    elif diff == "Medium":
        move = ai_move_heuristic(1.5, 1.2)
    # Hard：更加强调进攻(2.0 : 1.3)
    elif diff == "Hard":
        move = ai_move_heuristic(2.0, 1.3)
    else:
        move = ai_move_random()

    if not move:
        return

    board[move[0]][move[1]] = 2  # 白棋
    ai_last_move = (move[0], move[1])  # 记录AI最后一手
    add_to_history(2, move)

    # 检查是否胜利
    if check_winner(board, 2):
        winner = 2
        game_ended = True
    else:
        # 切回黑棋
        current_player = 1
        ai_thinking = False
        ai_move_time = 0


def ai_move_random():
    """AI随机落子"""
    empty_cells = [
        (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if board[x][y] == 0
    ]
    if not empty_cells:
        return None
    return random.choice(empty_cells)


def ai_move_heuristic(attack_factor=1.0, defend_factor=1.1):
    """使用启发式评分，考虑进攻和防守"""
    best_score = -float("inf")
    best_moves = []
    empty_cells = [
        (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if board[x][y] == 0
    ]
    if not empty_cells:
        return None

    for x, y in empty_cells:
        # AI落子分数
        board[x][y] = 2
        score_ai = heuristic_score(board, 2)
        # 玩家潜在分数
        board[x][y] = 1
        score_player = heuristic_score(board, 1)
        # 还原为空
        board[x][y] = 0

        # 综合分数：更注重进攻(attack_factor) 和 防守(defend_factor)
        total_score = attack_factor * score_ai + defend_factor * score_player
        if total_score > best_score:
            best_score = total_score
            best_moves = [(x, y)]
        elif abs(total_score - best_score) < 1e-9:
            best_moves.append((x, y))

    return random.choice(best_moves)


# --- 主循环 ---

while not game_over:
    clock.tick(60)  # FPS限制
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

        # 菜单状态时只响应按钮点击
        if game_state == "menu":
            pass

        # 对局状态
        elif game_state == "playing":
            if not game_ended:
                # 玩家下子
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and current_player == 1
                    and not ai_thinking
                ):
                    mx, my = pygame.mouse.get_pos()
                    if 0 <= mx < BOARD_WIDTH and 0 <= my < BOARD_HEIGHT:
                        row = mx // CELL_SIZE
                        col = my // CELL_SIZE
                        if board[row][col] == 0:
                            board[row][col] = 1
                            add_to_history(1, (row, col))
                            # 如果玩家形成五连珠
                            if check_winner(board, 1):
                                winner = 1
                                game_ended = True
                            else:
                                # 切换到 AI
                                current_player = 2
                                ai_thinking = True
                                ai_move_time = time.time() + AI_DELAY
            else:
                # 对局结束后，处理“重新开始”或“退出游戏”按钮点击
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass

    # --- 绘制逻辑 ---
    screen.fill(GRAY)

    if game_state == "menu":
        draw_menu()
    else:
        # 绘制棋盘
        draw_board()
        draw_pieces()
        highlight_square()

        # 右侧历史战绩
        display_history()

        # 顶部文字（当前玩家、难度）
        display_info()

        # 若AI正在思考，则显示提示 + 等待时机落子
        if current_player == 2 and ai_thinking and not game_ended:
            # 显示“AI 正在思考...”文字
            thinking_txt = font_medium.render("AI 正在思考...", True, BLUE)
            screen.blit(
                thinking_txt,
                (
                    BOARD_WIDTH // 2 - thinking_txt.get_width() // 2,
                    BOARD_HEIGHT // 2 - thinking_txt.get_height() // 2,
                ),
            )

            now = time.time()
            if now >= ai_move_time:
                ai_move()

        # 如果对局已结束，显示胜者并绘制半透明按钮
        if game_ended and winner is not None:
            if winner == 1:
                text = font_large.render("黑棋 获胜!", True, RED)
            else:
                text = font_large.render("白棋 (AI) 获胜!", True, RED)
            screen.blit(
                text,
                (
                    BOARD_WIDTH // 2 - text.get_width() // 2,
                    BOARD_HEIGHT // 2 - text.get_height() // 2,
                ),
            )

            # 半透明按钮
            btn_w = 150
            btn_h = 50
            space = 20

            x_restart = BOARD_WIDTH // 2 - btn_w - space // 2
            y_restart = BOARD_HEIGHT // 2 + 60
            draw_button(
                "重新开始",
                x_restart,
                y_restart,
                btn_w,
                btn_h,
                BUTTON_BG_COLOR,
                BUTTON_HOVER_COLOR,
                restart_game,
                transparent=True,
            )

            x_quit = BOARD_WIDTH // 2 + space // 2
            y_quit = BOARD_HEIGHT // 2 + 60
            draw_button(
                "退出游戏",
                x_quit,
                y_quit,
                btn_w,
                btn_h,
                BUTTON_BG_COLOR,
                BUTTON_HOVER_COLOR,
                quit_game,
                transparent=True,
            )

    pygame.display.flip()

pygame.quit()
sys.exit()
