# -*- coding: utf-8 -*-
import pygame
import sys
import random

pygame.init()

# ----- ПАРАМЕТРЫ ОКНА -----
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Поле чудес – угадай слово!")

clock = pygame.time.Clock()

# ----- ШРИФТЫ -----
FONT_BIG = pygame.font.Font(None, 64)
FONT_MED = pygame.font.Font(None, 40)
FONT_SMALL = pygame.font.Font(None, 28)

# ----- СЛОВА И ВОПРОСЫ -----
WORDS_DATA = [
    {"word": "КОМПЬЮТЕР", "question": "Как называется основное устройство для обработки информации?"},
    {"word": "ПРОГРАММА", "question": "Как называется набор команд, который выполняет компьютер?"},
    {"word": "АЛГОРИТМ", "question": "Как называется точная последовательность действий для решения задачи?"},
    {"word": "ИНФОРМАТИКА", "question": "Как называется наука об информации и способах её обработки?"},
    {"word": "ПРОЦЕССОР", "question": "Как называется «мозг» компьютера, который выполняет все вычисления?"},
    {"word": "КЛАВИАТУРА", "question": "Как называется устройство для ввода текста и команд?"},
    {"word": "МОНИТОР", "question": "Как называется устройство для вывода изображения?"},
    {"word": "СЕТЬ", "question": "Как называется система, объединяющая несколько компьютеров?"},
    {"word": "БАЗА", "question": "Коротко: как называется хранилище структурированных данных? (одно слово)"},
    {"word": "ФАЙЛ", "question": "Как называется именованная область на диске для хранения данных?"},
    {"word": "УСТРОЙСТВО", "question": "Общее название любой физической части компьютера?"},
    {"word": "КОД", "question": "Как одним словом называют текст программы?"},
]

# ----- ЦВЕТА -----
WHITE = (255, 255, 255)
LIGHT = (200, 200, 255)
BG = (30, 30, 60)
BUTTON_BG = (60, 60, 100)

# ----- КНОПКА "НАЧАТЬ ЗАНОВО" -----
BUTTON_WIDTH, BUTTON_HEIGHT = 260, 50
RESTART_BUTTON_RECT = pygame.Rect(
    (WIDTH - BUTTON_WIDTH) // 2,
    HEIGHT - 100,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)

# ----- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ СОСТОЯНИЯ -----
word = ""
question = ""
guessed_letters = set()
wrong_letters = set()
attempts_left = 0
game_over = False
message = ""

difficulty = "medium"   # "easy" / "medium" / "hard"
total_score = 0
guessed_words = []      # список угаданных слов

# Таймер (в секундах)
round_time_limit = 60
round_start_ticks = 0   # время начала раунда (в миллисекундах)

# ----- ЗВУКИ -----
def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except Exception:
        return None

correct_sound = load_sound("correct.wav")  # правильная буква
wrong_sound = load_sound("wrong.wav")      # неправильная буква
win_sound = load_sound("win.wav")          # победа
lose_sound = load_sound("lose.wav")        # поражение (ошибки/время)


# ====== ПРОСТЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======
def get_attempts_for_word(w):
    """Сколько ошибок можно сделать для данного слова при текущей сложности."""
    length = len(w)
    if difficulty == "easy":
        factor = 3.0
    elif difficulty == "medium":
        factor = 2.0
    else:  # "hard"
        factor = 1.5
    return max(1, int(round(length * factor)))


def get_points_for_word(w):
    """Сколько очков даём за слово при текущей сложности."""
    base = len(w) * 10
    if difficulty == "easy":
        factor = 1.0
    elif difficulty == "medium":
        factor = 1.5
    else:  # "hard"
        factor = 2.0
    return int(base * factor)


def start_new_round():
    """Начать новый раунд: новое слово и вопрос, обнулить состояние для этого слова."""
    global word, question, guessed_letters, wrong_letters, attempts_left
    global game_over, message, round_start_ticks

    data = random.choice(WORDS_DATA)
    word = data["word"]
    question = data["question"]
    guessed_letters = set()
    wrong_letters = set()
    attempts_left = get_attempts_for_word(word)
    game_over = False
    message = ""

    # фиксируем время старта раунда
    round_start_ticks = pygame.time.get_ticks()


def change_difficulty():
    """Переключить сложность по кругу: Лёгкий → Средний → Сложный → Лёгкий..."""
    global difficulty, attempts_left, game_over, message

    if difficulty == "easy":
        difficulty = "medium"
    elif difficulty == "medium":
        difficulty = "hard"
    else:
        difficulty = "easy"

    # Если игра ещё идёт, пересчитаем лимит ошибок под новый режим
    if not game_over:
        max_attempts = get_attempts_for_word(word)
        used_mistakes = len(wrong_letters)
        attempts_left = max(0, max_attempts - used_mistakes)
        if attempts_left <= 0:
            game_over = True
            message = f"К сожалению, вы проиграли. Загаданное слово: {word}"
            if lose_sound:
                lose_sound.play()


def draw():
    """Отрисовать весь экран."""
    screen.fill(BG)

    # Заголовок
    title = FONT_BIG.render("Поле чудес", True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 40)))

    # Вопрос
    q_text = "Вопрос: " + question
    q_surf = FONT_SMALL.render(q_text, True, LIGHT)
    screen.blit(q_surf, q_surf.get_rect(midtop=(WIDTH // 2, 90)))

    # Слово (с подчёркиваниями)
    display = ""
    for ch in word:
        if ch in guessed_letters:
            display += ch + " "
        else:
            display += "_ "
    word_surf = FONT_BIG.render(display.strip(), True, WHITE)
    screen.blit(word_surf, word_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10)))

    # Осталось ошибок
    attempts_text = f"Осталось ошибок: {attempts_left}"
    attempts_surf = FONT_MED.render(attempts_text, True, WHITE)
    screen.blit(attempts_surf, (40, 130))

    # Неверные буквы
    if wrong_letters:
        wrong_text = "Неверные буквы: " + " ".join(sorted(wrong_letters))
    else:
        wrong_text = "Неверных букв нет"
    wrong_surf = FONT_SMALL.render(wrong_text, True, LIGHT)
    screen.blit(wrong_surf, (40, 180))

    # Режим сложности
    if difficulty == "easy":
        diff_text = "Режим: Лёгкий"
    elif difficulty == "medium":
        diff_text = "Режим: Средний"
    else:
        diff_text = "Режим: Сложный"
    diff_surf = FONT_SMALL.render(diff_text, True, WHITE)
    screen.blit(diff_surf, (40, 220))

    # Очки
    score_text = f"Очки: {total_score}"
    score_surf = FONT_SMALL.render(score_text, True, WHITE)
    screen.blit(score_surf, (40, 260))

    # Таймер
    now = pygame.time.get_ticks()
    elapsed_sec = (now - round_start_ticks) // 1000
    remaining = round_time_limit - elapsed_sec
    if remaining < 0:
        remaining = 0
    timer_text = f"Время: {remaining} с"
    timer_surf = FONT_SMALL.render(timer_text, True, WHITE)
    screen.blit(timer_surf, (WIDTH - 200, 130))

    # Список угаданных слов
    header = FONT_SMALL.render("Угаданные слова:", True, WHITE)
    screen.blit(header, (WIDTH - 260, 180))
    y = 210
    for w in guessed_words:
        w_surf = FONT_SMALL.render(w, True, LIGHT)
        screen.blit(w_surf, (WIDTH - 260, y))
        y += 24

    # Подсказка по управлению
    instr = (
        "Введите русские буквы. TAB – сменить режим. "
        "ПРОБЕЛ или кнопка – начать новый раунд."
    )
    instr_surf = FONT_SMALL.render(instr, True, WHITE)
    screen.blit(instr_surf, instr_surf.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

    # Кнопка "Начать заново"
    pygame.draw.rect(screen, BUTTON_BG, RESTART_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, LIGHT, RESTART_BUTTON_RECT, width=2, border_radius=10)
    btn_text = FONT_MED.render("Начать заново", True, WHITE)
    screen.blit(btn_text, btn_text.get_rect(center=RESTART_BUTTON_RECT.center))

    # Сообщение о конце игры
    if game_over and message:
        msg_surf = FONT_MED.render(message, True, WHITE)
        screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))


# ====== ОСНОВНАЯ ПРОГРАММА ======
def main():
    global total_score, attempts_left, game_over, message

    pygame.key.start_text_input()

    # первый раунд
    start_new_round()

    running = True
    while running:
        clock.tick(60)

        # --- проверяем таймер ---
        if not game_over:
            now = pygame.time.get_ticks()
            elapsed_sec = (now - round_start_ticks) // 1000
            if elapsed_sec >= round_time_limit:
                game_over = True
                if message == "":
                    message = f"Время вышло! Загаданное слово: {word}"
                if lose_sound:
                    lose_sound.play()

        for event in pygame.event.get():
            # Закрываем окно
            if event.type == pygame.QUIT:
                running = False

            # Клавиши
            if event.type == pygame.KEYDOWN:
                # TAB – смена сложности
                if event.key == pygame.K_TAB:
                    change_difficulty()

                # ПРОБЕЛ – новый раунд (сложность и очки сохраняются)
                elif event.key == pygame.K_SPACE:
                    start_new_round()

            # Клик по кнопке "Начать заново"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if RESTART_BUTTON_RECT.collidepoint(event.pos):
                    start_new_round()

            # Ввод букв (русская раскладка)
            if event.type == pygame.TEXTINPUT and not game_over:
                text = event.text
                for ch in text:
                    letter = ch.upper()

                    # только буквы
                    if not letter.isalpha():
                        continue

                    # уже вводили такую
                    if letter in guessed_letters or letter in wrong_letters:
                        continue

                    # правильная буква
                    if letter in word:
                        guessed_letters.add(letter)
                        if correct_sound:
                            correct_sound.play()

                        # проверяем, все ли буквы угаданы
                        all_found = True
                        for wch in word:
                            if wch not in guessed_letters:
                                all_found = False
                                break

                        if all_found:
                            game_over = True
                            message = "Победа! Вы угадали слово!"
                            total_score += get_points_for_word(word)
                            guessed_words.append(word)
                            if win_sound:
                                win_sound.play()
                    else:
                        # неправильная буква
                        wrong_letters.add(letter)
                        attempts_left -= 1
                        if wrong_sound:
                            wrong_sound.play()

                        if attempts_left <= 0 and not game_over:
                            game_over = True
                            message = f"К сожалению, вы проиграли. Загаданное слово: {word}"
                            if lose_sound:
                                lose_sound.play()

        draw()
        pygame.display.flip()

    pygame.key.stop_text_input()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
