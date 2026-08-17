import os
import re
import ast
import json
import random
from fractions import Fraction
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functools import lru_cache

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


# =========================================================
# APP / LINE
# =========================================================

app = Flask(__name__)

CHANNEL_SECRET = '59244ceb431e36e1b1b27fd5a2cbb7ca'
CHANNEL_ACCESS_TOKEN = 'XYvMjGta0QtKO/zZwykz/RBqmh84ukn2MpIkUfdBtkzrzh9Zt9u8lYv4wQOZ8kBqxn2TGWMOn1vaqLptWUC4M2xncEgdLtM2N+cqy6tU9cr9pZi0BPkoq9hgGIQd+DhqiWd0F3e5hVMg9qrqhMTg+gdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")
SAVE_FILE = "game_data.json"


# =========================================================
# PUZZLES (ครบถ้วน 404 ข้อ)
# =========================================================

PUZZLES = [
    [1, 1, 1, 8], [1, 1, 2, 6], [1, 1, 2, 7], [1, 1, 2, 8], [1, 1, 2, 9], [1, 1, 3, 4], [1, 1, 3, 5], [1, 1, 3, 6], [1, 1, 3, 7], [1, 1, 3, 8], 
    [1, 1, 3, 9], [1, 1, 4, 4], [1, 1, 4, 5], [1, 1, 4, 6], [1, 1, 4, 7], [1, 1, 4, 8], [1, 1, 4, 9], [1, 1, 5, 5], [1, 1, 5, 6], [1, 1, 5, 7], 
    [1, 1, 5, 8], [1, 1, 6, 6], [1, 1, 6, 8], [1, 1, 6, 9], [1, 1, 8, 8], [1, 2, 2, 4], [1, 2, 2, 5], [1, 2, 2, 6], [1, 2, 2, 7], [1, 2, 2, 8], 
    [1, 2, 2, 9], [1, 2, 3, 3], [1, 2, 3, 4], [1, 2, 3, 5], [1, 2, 3, 6], [1, 2, 3, 7], [1, 2, 3, 8], [1, 2, 3, 9], [1, 2, 4, 4], [1, 2, 4, 5], 
    [1, 2, 4, 6], [1, 2, 4, 7], [1, 2, 4, 8], [1, 2, 4, 9], [1, 2, 5, 5], [1, 2, 5, 6], [1, 2, 5, 7], [1, 2, 5, 8], [1, 2, 5, 9], [1, 2, 6, 6], 
    [1, 2, 6, 7], [1, 2, 6, 8], [1, 2, 6, 9], [1, 2, 7, 7], [1, 2, 7, 8], [1, 2, 7, 9], [1, 2, 8, 8], [1, 2, 8, 9], [1, 3, 3, 3], [1, 3, 3, 4], 
    [1, 3, 3, 5], [1, 3, 3, 6], [1, 3, 3, 7], [1, 3, 3, 8], [1, 3, 3, 9], [1, 3, 4, 4], [1, 3, 4, 5], [1, 3, 4, 6], [1, 3, 4, 7], [1, 3, 4, 8], 
    [1, 3, 4, 9], [1, 3, 5, 6], [1, 3, 5, 7], [1, 3, 5, 8], [1, 3, 5, 9], [1, 3, 6, 6], [1, 3, 6, 7], [1, 3, 6, 8], [1, 3, 6, 9], [1, 3, 7, 7], 
    [1, 3, 7, 8], [1, 3, 7, 9], [1, 3, 8, 8], [1, 3, 8, 9], [1, 3, 9, 9], [1, 4, 4, 4], [1, 4, 4, 5], [1, 4, 4, 6], [1, 4, 4, 7], [1, 4, 4, 8], 
    [1, 4, 4, 9], [1, 4, 5, 5], [1, 4, 5, 6], [1, 4, 5, 7], [1, 4, 5, 8], [1, 4, 5, 9], [1, 4, 6, 6], [1, 4, 6, 7], [1, 4, 6, 8], [1, 4, 6, 9], 
    [1, 4, 7, 7], [1, 4, 7, 8], [1, 4, 7, 9], [1, 4, 8, 8], [1, 4, 8, 9], [1, 5, 5, 5], [1, 5, 5, 6], [1, 5, 5, 9], [1, 5, 6, 6], [1, 5, 6, 7], 
    [1, 5, 6, 8], [1, 5, 6, 9], [1, 5, 7, 8], [1, 5, 7, 9], [1, 5, 8, 8], [1, 5, 8, 9], [1, 5, 9, 9], [1, 6, 6, 6], [1, 6, 6, 8], [1, 6, 6, 9], 
    [1, 6, 7, 9], [1, 6, 8, 8], [1, 6, 8, 9], [1, 6, 9, 9], [1, 7, 7, 9], [1, 7, 8, 8], [1, 7, 8, 9], [1, 7, 9, 9], [1, 8, 8, 8], [1, 8, 8, 9], 
    [2, 2, 2, 3], [2, 2, 2, 4], [2, 2, 2, 5], [2, 2, 2, 7], [2, 2, 2, 8], [2, 2, 2, 9], [2, 2, 3, 3], [2, 2, 3, 4], [2, 2, 3, 5], [2, 2, 3, 6], 
    [2, 2, 3, 7], [2, 2, 3, 8], [2, 2, 3, 9], [2, 2, 4, 4], [2, 2, 4, 5], [2, 2, 4, 6], [2, 2, 4, 7], [2, 2, 4, 8], [2, 2, 4, 9], [2, 2, 5, 5], 
    [2, 2, 5, 6], [2, 2, 5, 7], [2, 2, 5, 8], [2, 2, 5, 9], [2, 2, 6, 6], [2, 2, 6, 7], [2, 2, 6, 8], [2, 2, 6, 9], [2, 2, 7, 7], [2, 2, 7, 8], 
    [2, 2, 8, 8], [2, 2, 8, 9], [2, 3, 3, 3], [2, 3, 3, 5], [2, 3, 3, 6], [2, 3, 3, 7], [2, 3, 3, 8], [2, 3, 3, 9], [2, 3, 4, 4], [2, 3, 4, 5], 
    [2, 3, 4, 6], [2, 3, 4, 7], [2, 3, 4, 8], [2, 3, 4, 9], [2, 3, 5, 5], [2, 3, 5, 6], [2, 3, 5, 7], [2, 3, 5, 8], [2, 3, 5, 9], [2, 3, 6, 6], 
    [2, 3, 6, 7], [2, 3, 6, 8], [2, 3, 6, 9], [2, 3, 7, 7], [2, 3, 7, 8], [2, 3, 7, 9], [2, 3, 8, 8], [2, 3, 8, 9], [2, 3, 9, 9], [2, 4, 4, 4], 
    [2, 4, 4, 5], [2, 4, 4, 6], [2, 4, 4, 7], [2, 4, 4, 8], [2, 4, 4, 9], [2, 4, 5, 5], [2, 4, 5, 6], [2, 4, 5, 7], [2, 4, 5, 8], [2, 4, 5, 9], 
    [2, 4, 6, 6], [2, 4, 6, 7], [2, 4, 6, 8], [2, 4, 6, 9], [2, 4, 7, 7], [2, 4, 7, 8], [2, 4, 7, 9], [2, 4, 8, 8], [2, 4, 8, 9], [2, 4, 9, 9], 
    [2, 5, 5, 7], [2, 5, 5, 8], [2, 5, 5, 9], [2, 5, 6, 6], [2, 5, 6, 7], [2, 5, 6, 8], [2, 5, 6, 9], [2, 5, 7, 7], [2, 5, 7, 8], [2, 5, 7, 9], 
    [2, 5, 8, 8], [2, 5, 8, 9], [2, 6, 6, 6], [2, 6, 6, 7], [2, 6, 6, 8], [2, 6, 6, 9], [2, 6, 7, 8], [2, 6, 7, 9], [2, 6, 8, 8], [2, 6, 8, 9], 
    [2, 6, 9, 9], [2, 7, 7, 8], [2, 7, 8, 8], [2, 7, 8, 9], [2, 8, 8, 8], [2, 8, 8, 9], [2, 8, 9, 9], [3, 3, 3, 3], [3, 3, 3, 4], [3, 3, 3, 5], 
    [3, 3, 3, 6], [3, 3, 3, 7], [3, 3, 3, 8], [3, 3, 3, 9], [3, 3, 4, 4], [3, 3, 4, 5], [3, 3, 4, 6], [3, 3, 4, 7], [3, 3, 4, 8], [3, 3, 4, 9], 
    [3, 3, 5, 5], [3, 3, 5, 6], [3, 3, 5, 7], [3, 3, 5, 9], [3, 3, 6, 6], [3, 3, 6, 7], [3, 3, 6, 8], [3, 3, 6, 9], [3, 3, 7, 7], [3, 3, 7, 8], 
    [3, 3, 7, 9], [3, 3, 8, 8], [3, 3, 8, 9], [3, 3, 9, 9], [3, 4, 4, 4], [3, 4, 4, 5], [3, 4, 4, 6], [3, 4, 4, 7], [3, 4, 4, 8], [3, 4, 4, 9], 
    [3, 4, 5, 5], [3, 4, 5, 6], [3, 4, 5, 7], [3, 4, 5, 8], [3, 4, 5, 9], [3, 4, 6, 6], [3, 4, 6, 8], [3, 4, 6, 9], [3, 4, 7, 7], [3, 4, 7, 8], 
    [3, 4, 7, 9], [3, 4, 8, 9], [3, 4, 9, 9], [3, 5, 5, 6], [3, 5, 5, 7], [3, 5, 5, 8], [3, 5, 5, 9], [3, 5, 6, 6], [3, 5, 6, 7], [3, 5, 6, 8], 
    [3, 5, 6, 9], [3, 5, 7, 8], [3, 5, 7, 9], [3, 5, 8, 8], [3, 5, 8, 9], [3, 5, 9, 9], [3, 6, 6, 6], [3, 6, 6, 7], [3, 6, 6, 8], [3, 6, 6, 9], 
    [3, 6, 7, 7], [3, 6, 7, 8], [3, 6, 7, 9], [3, 6, 8, 8], [3, 6, 8, 9], [3, 6, 9, 9], [3, 7, 7, 7], [3, 7, 7, 8], [3, 7, 7, 9], [3, 7, 8, 8], 
    [3, 7, 8, 9], [3, 7, 9, 9], [3, 8, 8, 8], [3, 8, 8, 9], [3, 8, 9, 9], [3, 9, 9, 9], [4, 4, 4, 4], [4, 4, 4, 5], [4, 4, 4, 6], [4, 4, 4, 7], 
    [4, 4, 4, 8], [4, 4, 4, 9], [4, 4, 5, 5], [4, 4, 5, 6], [4, 4, 5, 7], [4, 4, 5, 8], [4, 4, 6, 8], [4, 4, 6, 9], [4, 4, 7, 7], [4, 4, 7, 8], 
    [4, 4, 7, 9], [4, 4, 8, 8], [4, 4, 8, 9], [4, 5, 5, 5], [4, 5, 5, 6], [4, 5, 5, 7], [4, 5, 5, 8], [4, 5, 5, 9], [4, 5, 6, 6], [4, 5, 6, 7], 
    [4, 5, 6, 8], [4, 5, 6, 9], [4, 5, 7, 7], [4, 5, 7, 8], [4, 5, 7, 9], [4, 5, 8, 8], [4, 5, 8, 9], [4, 5, 9, 9], [4, 6, 6, 6], [4, 6, 6, 7], 
    [4, 6, 6, 8], [4, 6, 6, 9], [4, 6, 7, 7], [4, 6, 7, 8], [4, 6, 7, 9], [4, 6, 8, 8], [4, 6, 8, 9], [4, 6, 9, 9], [4, 7, 7, 7], [4, 7, 7, 8], 
    [4, 7, 8, 8], [4, 7, 8, 9], [4, 7, 9, 9], [4, 8, 8, 8], [4, 8, 8, 9], [4, 8, 9, 9], [5, 5, 5, 5], [5, 5, 5, 6], [5, 5, 5, 9], [5, 5, 6, 6], 
    [5, 5, 6, 7], [5, 5, 6, 8], [5, 5, 7, 7], [5, 5, 7, 8], [5, 5, 8, 8], [5, 5, 8, 9], [5, 5, 9, 9], [5, 6, 6, 6], [5, 6, 6, 7], [5, 6, 6, 8], 
    [5, 6, 6, 9], [5, 6, 7, 7], [5, 6, 7, 8], [5, 6, 7, 9], [5, 6, 8, 8], [5, 6, 8, 9], [5, 6, 9, 9], [5, 7, 7, 9], [5, 7, 8, 8], [5, 7, 8, 9], 
    [5, 8, 8, 8], [5, 8, 8, 9], [6, 6, 6, 6], [6, 6, 6, 8], [6, 6, 6, 9], [6, 6, 7, 9], [6, 6, 8, 8], [6, 6, 8, 9], [6, 7, 8, 9], [6, 7, 9, 9], 
    [6, 8, 8, 8], [6, 8, 8, 9], [6, 8, 9, 9], [7, 8, 8, 9]
]


# =========================================================
# RANK
# =========================================================

RANKS = {
    0: ("ผู้เริ่มต้น", "Beginner"),
    10: ("นักคิดหน้าใหม่", "Rookie"),
    20: ("นักคิดคล่องแคล่ว", "Thinker"),
    30: ("นักคิดสายฟ้า", "Speed Mind"),
    40: ("นักล่าเลข 24", "Number Hunter"),
    50: ("เซียนเกม 24", "24 Master"),
    60: ("นักรบสมองเพชร", "Brain Warrior"),
    70: ("ราชันย์นักคิด", "Mind King"),
    80: ("ปรมาจารย์เกม 24", "24 Grandmaster"),
    90: ("อัจฉริยะคณิต", "Math Genius"),
    100: ("ตำนานแห่งเกม 24", "24 Legend"),
}


def get_rank(score):
    current = RANKS[0]
    for threshold in sorted(RANKS.keys()):
        if score >= threshold:
            current = RANKS[threshold]
    return current


def get_next_rank(score):
    thresholds = sorted(RANKS.keys())
    for threshold in thresholds:
        if score < threshold:
            th, en = RANKS[threshold]
            return threshold, th, en
    return None


def get_progress_text(score):
    next_rank = get_next_rank(score)
    if not next_rank:
        return "👑 คุณขึ้นถึงระดับสูงสุดแล้วนะคะ! (You've reached the highest rank!)"

    next_score, next_th, next_en = next_rank
    remaining = next_score - score

    return (
        f"อีก {remaining} คะแนน จะเลื่อนขั้นเป็น {next_th}\n"
        f"📈 {remaining} more point{'s' if remaining > 1 else ''} to {next_en}"
    )


# =========================================================
# DIFFICULTY
# =========================================================

DIFFICULTY_NAMES = {
    0: ("🌱 Easy", "ง่าย"),
    1: ("🌿 Normal", "ปกติ"),
    2: ("🔥 Challenge", "ท้าทาย"),
    3: ("⚡ Expert", "ยาก"),
    4: ("👑 Master", "ระดับปรมาจารย์"),
}

difficulty_buckets = {0: [], 1: [], 2: [], 3: [], 4: []}


# =========================================================
# PUZZLE SOLVER
# =========================================================

@lru_cache(maxsize=None)
def count_solutions(values):
    values = tuple(sorted(values))
    if len(values) == 1:
        return 1 if values[0] == 24 else 0

    total = 0
    values = list(values)

    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            a = values[i]
            b = values[j]
            rest = [
                values[k]
                for k in range(len(values))
                if k not in (i, j)
            ]

            results = [
                a + b,
                a - b,
                b - a,
                a * b
            ]

            if b != 0:
                results.append(Fraction(a, b))
            if a != 0:
                results.append(Fraction(b, a))

            for result in results:
                if result < 0:
                    continue
                if result.denominator != 1:
                    continue
                new_values = rest + [result]
                total += count_solutions(tuple(sorted(new_values)))

    return total


def build_difficulty_buckets():
    if not PUZZLES:
        return

    puzzle_scores = []
    for puzzle in PUZZLES:
        score = count_solutions(tuple(puzzle))
        puzzle_scores.append((puzzle, score))

    puzzle_scores.sort(key=lambda x: x[1], reverse=True)
    total = len(puzzle_scores)
    bucket_size = max(1, total // 5)

    difficulty_buckets[0].clear()
    difficulty_buckets[1].clear()
    difficulty_buckets[2].clear()
    difficulty_buckets[3].clear()
    difficulty_buckets[4].clear()

    for index, item in enumerate(puzzle_scores):
        if index < bucket_size:
            level = 0
        elif index < bucket_size * 2:
            level = 1
        elif index < bucket_size * 3:
            level = 2
        elif index < bucket_size * 4:
            level = 3
        else:
            level = 4

        difficulty_buckets[level].append(item[0])


def get_difficulty_from_score(score):
    if score < 20:
        return 0
    elif score < 40:
        return 1
    elif score < 60:
        return 2
    elif score < 80:
        return 3
    else:
        return 4


def get_next_puzzle(score):
    level = get_difficulty_from_score(score)
    bucket = difficulty_buckets.get(level, [])
    if not bucket:
        bucket = PUZZLES
    return random.choice(bucket)


# =========================================================
# PLAYER DATA
# =========================================================

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")
SAVE_FILE = "game_data.json"

def create_default_player():
    return {
        "score": 0,
        "combo": 0,
        "best_combo": 0,
        "correct_total": 0,
        "daily_date": "",
        "daily_correct": 0,
        "daily_score": 0,
        "last_active_date": "",
        "streak": 0,
        "best_streak": 0,
        "round_correct": 0,
        "personal_best_daily_score": 0,
        "badges": [],
        "current_puzzle": None,
        "last_encouragement": ""
    }


players = {}


# =========================================================
# SAVE / LOAD
# =========================================================

def save_data():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)


def load_data():
    global players
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                players = json.load(f)
    except Exception as e:
        print("Load error:", e)
        players = {}


def get_player(user_id):
    if user_id not in players:
        players[user_id] = create_default_player()
    return players[user_id]


# =========================================================
# DATE / STREAK / DAILY MISSION
# =========================================================

def today_str():
    return datetime.now(BANGKOK_TZ).date().isoformat()


def yesterday_str():
    return (
        datetime.now(BANGKOK_TZ).date() - timedelta(days=1)
    ).isoformat()


def prepare_daily_data(player):
    today = today_str()
    if player["daily_date"] != today:
        if player["daily_score"] > player["personal_best_daily_score"]:
            player["personal_best_daily_score"] = player["daily_score"]
        player["daily_date"] = today
        player["daily_correct"] = 0
        player["daily_score"] = 0


def register_activity(player):
    today = today_str()
    prepare_daily_data(player)

    if player["last_active_date"] == today:
        return False

    if player["last_active_date"] == yesterday_str():
        player["streak"] += 1
    else:
        player["streak"] = 1

    player["best_streak"] = max(player["best_streak"], player["streak"])
    player["last_active_date"] = today

    return True


# =========================================================
# BADGES
# =========================================================

BADGES = [
    {"id": "first_correct", "icon": "🌟", "name": "นักคิดคนแรก (First Thinker)", "condition": lambda p: p["correct_total"] >= 1},
    {"id": "combo_5", "icon": "🔥", "name": "ไฟแรง Combo x5 (On Fire x5)", "condition": lambda p: p["best_combo"] >= 5},
    {"id": "daily_5", "icon": "🎯", "name": "ภารกิจประจำวัน (Daily Achiever)", "condition": lambda p: p["daily_correct"] >= 5},
    {"id": "score_10", "icon": "🏅", "name": "นักคิดหน้าใหม่ (Rookie)", "condition": lambda p: p["score"] >= 10},
    {"id": "score_50", "icon": "💎", "name": "เซียนเกม 24 (24 Master)", "condition": lambda p: p["score"] >= 50},
    {"id": "score_100", "icon": "👑", "name": "ตำนานแห่งเกม 24 (24 Legend)", "condition": lambda p: p["score"] >= 100},
    {"id": "streak_3", "icon": "🔥", "name": "นักสู้ 3 วัน (3-Day Streak)", "condition": lambda p: p["best_streak"] >= 3},
    {"id": "streak_7", "icon": "🌟", "name": "7-Day Champion", "condition": lambda p: p["best_streak"] >= 7}
]


def update_badges(player):
    new_badges = []
    for badge in BADGES:
        if badge["id"] in player["badges"]:
            continue
        if badge["condition"](player):
            player["badges"].append(badge["id"])
            new_badges.append(f'{badge["icon"]} {badge["name"]}')
    return new_badges


def get_badge_text(player):
    unlocked = []
    for badge in BADGES:
        if badge["id"] in player["badges"]:
            unlocked.append(f'{badge["icon"]} {badge["name"]}')
    if not unlocked:
        return "ยังไม่มีเหรียญ (No badges yet) 🌟\nเล่นต่ออีกนิดเดี๋ยวก็ได้แล้วค่ะ (Keep playing!)"
    return "\n".join(unlocked)


# =========================================================
# ENCOURAGEMENT
# =========================================================

CORRECT_MESSAGES = [
    "✅ ถูกต้องค่ะ! Correct!\n✨ คิดได้เฉียบมากค่ะ! Very sharp thinking!",
    "✅ ถูกต้องค่ะ! Correct!\n🌟 เยี่ยมมากค่ะ! สมองไวมากเลย Excellent!",
    "✅ ถูกต้องค่ะ! Correct!\n🎯 แม่นมากค่ะ! จับทางโจทย์ได้เก่งจริง ๆ Spot on!",
    "✅ ถูกต้องค่ะ! Correct!\n🧠 เก่งมากนะคะ! คิดได้ยอดเยี่ยมเลย Brilliant!",
    "✅ ถูกต้องค่ะ! Correct!\n🔥 สุดยอดค่ะ! วันนี้สมองกำลังร้อนแรงเลย Awesome!",
    "✅ ถูกต้องค่ะ! Correct!\n🚀 ทำได้เยี่ยมมาก! ไปลุยข้อต่อไปกันเลย Great job!",
    "✅ ถูกต้องค่ะ! Correct!\n💡 คิดได้เฉียบขาดและรวดเร็วมาก Smart and quick thinking!",
    "✅ ถูกต้องค่ะ! Correct!\n🏆 สุดยอดนักคิด! เก่งมากๆ เลยค่ะ Absolute math star!"
]

WRONG_MESSAGES = [
    "💪 ยังไม่ใช่คำตอบนี้นะคะ ลองใหม่อีกครั้งค่ะ\n💪 Not quite, try again!",
    "🧠 เกือบแล้วค่ะ! ลองจัดกลุ่มตัวเลขใหม่ดูนะคะ\n🧠 Almost! Try grouping the numbers differently.",
    "🌱 ไม่เป็นไรเลยค่ะ ลองคิดอีกมุมดูนะคะ\n🌱 It's okay, try looking from another angle.",
    "✨ ใกล้ความจริงแล้วค่ะ ลองสลับเครื่องหมายดูนะคะ\n✨ So close! Try swapping operators.",
]


def random_message(player, messages):
    available = [
        m for m in messages
        if m != player["last_encouragement"]
    ]
    if not available:
        available = messages
    message = random.choice(available)
    player["last_encouragement"] = message
    return message


# =========================================================
# HINT GENERATOR (สร้างคำใบ้เบื้องต้น 1 ขั้นตอน)
# =========================================================

def get_hint(puzzle):
    # มองหาคู่เลขที่คูณหรือบวกกันแล้วลงตัวเพื่อเป็นไกด์ไลน์เบื้องต้น
    p = sorted(puzzle)
    return (
        f"💡 คำใบ้ค่ะ\n"
        f"ลองมองหาคู่ตัวเลขจากชุดนี้ ({' '.join(map(str, puzzle))}) "
        f"ที่ทำให้ออกมาเป็นผลลัพธ์ง่ายๆ เช่น 6×4, 8×3 หรือ 12×2 ดูก่อนนะคะ\n\n"
        f"💡 Hint\n"
        f"Try looking for a pair of numbers from ({' '.join(map(str, puzzle))}) "
        f"that can make a helpful intermediate number like 6×4, 8×3, or 12×2."
    )


# =========================================================
# SAFE EQUATION EVALUATOR
# =========================================================

def evaluate_expression(expression, puzzle):
    if len(expression) > 100:
        raise ValueError("สมการยาวเกินไปค่ะ")
    if not re.fullmatch(r"[0-9+\-*/()\s]+", expression):
        raise ValueError("ใช้เฉพาะตัวเลขและ + - * / ( ) เท่านั้นค่ะ")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise ValueError("รูปแบบสมการไม่ถูกต้องค่ะ")

    used_numbers = []

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)

        if isinstance(node, ast.Constant):
            if not isinstance(node.value, int):
                raise ValueError("ใช้เฉพาะจำนวนเต็มนะคะ")
            used_numbers.append(node.value)
            value = Fraction(node.value, 1)
            if value < 0:
                raise ValueError("ห้ามมีค่าติดลบนะคะ")
            return value

        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            right = visit(node.right)

            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError
                result = left / right
            else:
                raise ValueError("มีเครื่องหมายที่ไม่อนุญาตค่ะ")

            if result < 0:
                raise ValueError("สมการมีค่าติดลบค่ะ")
            if result.denominator != 1:
                raise ValueError("ระหว่างคำนวณห้ามมีเศษส่วนนะคะ")

            return result

        raise ValueError("ไม่สามารถใช้รูปแบบนี้ได้นะคะ")

    result = visit(tree)

    if sorted(used_numbers) != sorted(puzzle):
        raise ValueError("ใช้เลขไม่ตรงกับโจทย์ค่ะ")
    if len(used_numbers) != 4:
        raise ValueError("ต้องใช้เลขให้ครบทั้ง 4 ตัวนะคะ")

    return result


# =========================================================
# SCORE / COMBO
# =========================================================

def calculate_combo_bonus(combo):
    if combo >= 10:
        return 5
    if combo >= 5:
        return 2
    if combo >= 3:
        return 1
    return 0


# =========================================================
# HELPERS
# =========================================================

def format_stats(player):
    rank_th, rank_en = get_rank(player["score"])
    return (
        f"🏆 คะแนนสะสม (Score): {player['score']}\n"
        f"🏅 ระดับ (Rank): {rank_th} ({rank_en})\n"
        f"🔥 Combo สูงสุด (Best Combo): x{player['best_combo']}\n"
        f"📅 ภารกิจวันนี้ (Daily Mission): {player['daily_correct']}/5\n"
        f"🔥 Streak: {player['streak']} วัน (days)\n"
        f"⭐ Personal Best: {player['personal_best_daily_score']}\n"
        f"🎖️ เหรียญ (Badges): {len(player['badges'])}/{len(BADGES)}\n\n"
        f"{get_progress_text(player['score'])}\n\n"
        f"พิมพ์ 'เล่น' หรือ 'Play' เพื่อเริ่มเกม (Type 'play' to continue)\n"
        f"พิมพ์ 'เหรียญ' เพื่อดูเหรียญที่ได้ (Type 'badges' to see your badges)"
    )


def format_puzzle_message(puzzle, player):
    nums = " ".join(map(str, puzzle))
    rank_th, rank_en = get_rank(player["score"])

    return (
        f"🧩 โจทย์ถัดไป (Next puzzle): {nums}\n\n"
        f"🏅 Rank: {rank_th} ({rank_en}) | 🔥 Combo x{player['combo']}\n\n"
        f"พิมพ์สมการมาได้เลยนะคะ\n"
        f"Type your equation when you're ready.\n\n"
        f"พิมพ์ “คำใบ้” เพื่อขอความช่วยเหลือ, “พักก่อน” เพื่อพัก หรือ “ข้าม” เพื่อเปลี่ยนโจทย์ค่ะ\n"
        f"Type “hint” for a clue, “break” to take a break, or “skip” to change the puzzle."
    )


# =========================================================
# INIT
# =========================================================

load_data()
build_difficulty_buckets()


# =========================================================
# CALLBACK
# =========================================================

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    if not signature:
        abort(400)
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# =========================================================
# MESSAGE HANDLER
# =========================================================

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    text_lower = text.lower()
    user_id = event.source.user_id
    player = get_player(user_id)

    prepare_daily_data(player)

    # =====================================================
    # SCORE
    # =====================================================
    if text_lower in ["คะแนน", "score"]:
        save_data()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=format_stats(player)))
        return

    # =====================================================
    # BADGES
    # =====================================================
    if text_lower in ["เหรียญ", "badge", "badges"]:
        save_data()
        reply = (
            f"🎖️ เหรียญความสำเร็จของคุณ (Your Badges)\n\n"
            f"{get_badge_text(player)}\n\n"
            f"สะสมต่อไปนะคะ ยังมีเหรียญรอปลดล็อกอีกค่ะ!\n"
            f"(Keep playing to unlock more!)"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # PLAY
    # =====================================================
    if text_lower in ["เล่น", "play"]:
        register_activity(player)
        puzzle = get_next_puzzle(player["score"])
        player["current_puzzle"] = puzzle
        save_data()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=format_puzzle_message(puzzle, player))
        )
        return

    # =====================================================
    # HINT
    # =====================================================
    if text_lower in ["คำใบ้", "hint"]:
        if player["current_puzzle"] is not None:
            reply = get_hint(player["current_puzzle"])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ยังไม่มีโจทย์ที่เล่นอยู่ค่ะ พิมพ์ 'เล่น' เพื่อเริ่มเกมก่อนนะคะ"))
        return

    # =====================================================
    # BREAK / SKIP
    # =====================================================
    if text_lower in ["พักก่อน", "break"]:
        player["current_puzzle"] = None
        player["combo"] = 0
        save_data()
        reply = (
            "พักก่อนได้เลยนะคะ 🌷 (Take a break!)\n"
            "ไม่เป็นไรเลยค่ะ พรุ่งนี้หรือเมื่อพร้อมแล้ว กลับมาประลองใหม่ได้เสมอนะคะ\n\n"
            "พิมพ์ “เล่น” หรือ “Play” เพื่อเล่นต่อได้เลยค่ะ\n"
            "(Type “play” to play again.)"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if text_lower in ["ข้าม", "skip"]:
        if player["current_puzzle"] is not None:
            puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = puzzle
            player["combo"] = 0  # รีเซ็ตคอมโบเมื่อข้าม
            save_data()
            reply = (
                f"🔄 เปลี่ยนโจทย์เรียบร้อยค่ะ! (Puzzle skipped!)\n\n"
                f"{format_puzzle_message(puzzle, player)}"
            )
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            reply = "ยังไม่มีโจทย์ที่กำลังเล่นอยู่ค่ะ พิมพ์ “เล่น” หรือ “Play” เพื่อเริ่มได้เลยค่ะ"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # NO CURRENT PUZZLE
    # =====================================================
    if player["current_puzzle"] is None:
        reply = (
            "สวัสดีค่ะ 🌟 พร้อมลับสมองกันหรือยังคะ?\n\n"
            "พิมพ์ “เล่น” เพื่อเริ่มเล่นเกม 24 ค่ะ\n"
            "พิมพ์ “คะแนน” เพื่อดู Rank และคะแนนนะคะ\n"
            "พิมพ์ “เหรียญ” เพื่อดูเหรียญที่สะสมค่ะ\n\n"
            "Hello! 🌟 Ready to sharpen your mind?\n\n"
            "Type “play” to start playing Game 24.\n"
            "Type “score” to check your Rank and points.\n"
            "Type “badges” to view your collected badges."
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # ANSWER
    # =====================================================
    puzzle = player["current_puzzle"]

    try:
        result = evaluate_expression(text, puzzle)

        # =================================================
        # CORRECT
        # =================================================
        if result == 24:
            player["correct_total"] += 1
            player["daily_correct"] += 1
            player["combo"] += 1

            player["best_combo"] = max(player["best_combo"], player["combo"])
            player["round_correct"] += 1

            base_score = 1
            combo_bonus = calculate_combo_bonus(player["combo"])
            milestone_bonus = 0
            milestone_message = ""

            if player["round_correct"] == 5:
                milestone_bonus += 2
                milestone_message = (
                    "\n\n🎉 จบด่านย่อย 5 ข้อ! (5 Puzzles Cleared!)\n"
                    "🎁 โบนัส (Bonus): +2"
                )
            elif player["round_correct"] == 10:
                milestone_bonus += 5
                milestone_message = (
                    "\n\n🏆 จบด่าน 10 ข้อ! (10 Puzzles Cleared!)\n"
                    "🎁 โบนัสพิเศษ (Special Bonus): +5\n"
                    "🚀 ไปต่อด่านใหม่กันเลยค่ะ! (Next stage!)"
                )
                player["round_correct"] = 0

            if player["daily_correct"] == 5:
                milestone_bonus += 2
                milestone_message += (
                    "\n\n🎯 ภารกิจวันนี้สำเร็จ! (Daily Mission Completed!)\n"
                    "🎁 โบนัส (Bonus): +2"
                )
            
            if player["daily_correct"] == 10:
                milestone_bonus += 5
                milestone_message += (
                    "\n\n🌟 วันนี้สุดยอดมากค่ะ! (You are amazing today!)\n"
                    "🎁 โบนัส (Bonus): +5"
                )

            total_gain = base_score + combo_bonus + milestone_bonus

            player["score"] += total_gain
            player["daily_score"] += total_gain

            if player["daily_score"] > player["personal_best_daily_score"]:
                player["personal_best_daily_score"] = player["daily_score"]

            update_badges(player)
            rank_th, rank_en = get_rank(player["score"])

            new_puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = new_puzzle
            encouragement = random_message(player, CORRECT_MESSAGES)

            progress = get_progress_text(player["score"])

            reply = (
                f"{encouragement}\n\n"
                f"🎁 +{total_gain} | 🏆 Score: {player['score']}\n"
                f"🏅 {rank_th} ({rank_en}) | 🔥 Combo x{player['combo']}\n"
                f"📅 ภารกิจวันนี้: {player['daily_correct']}/5 ✅ | 🔥 Streak: {player['streak']} วัน (day)\n"
                f"{progress}\n"
                f"{milestone_message}\n\n"
                f"🧩 โจทย์ถัดไป (Next puzzle): {' '.join(map(str, new_puzzle))}\n\n"
                f"พิมพ์สมการมาได้เลยนะคะ\n"
                f"Type your equation when you're ready.\n\n"
                f"พิมพ์ “คำใบ้” เพื่อขอความช่วยเหลือ, “พักก่อน” เพื่อพัก หรือ “ข้าม” เพื่อเปลี่ยนโจทย์ค่ะ\n"
                f"Type “hint” for a clue, “break” to take a break, or “skip” to change the puzzle."
            )

            save_data()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            return

    # =====================================================
    # WRONG / INVALID
    # =====================================================
    except ZeroDivisionError:
        player["combo"] = 0
        save_data()
        reply = (
            "😅 ข้อนี้หารด้วยศูนย์นะคะ (Division by zero is not allowed)\n"
            "ลองคิดใหม่อีกครั้งได้เลยค่ะ (Please try again)\n\n"
            "💡 Combo ถูกรีเซ็ตแล้ว แต่คะแนนเดิมยังอยู่ค่ะ (Combo reset, but score remains)"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    except ValueError as e:
        player["combo"] = 0
        save_data()
        reason = str(e)

        if "เลขไม่ตรง" in reason:
            reply = (
                "🔎 ลองเช็กตัวเลขอีกครั้งนะคะ (Please check the numbers again)\n\n"
                f"โจทย์คือ (Puzzle): {' '.join(map(str, puzzle))}\n\n"
                "ต้องใช้เลขทั้ง 4 ตัวให้ครบ และใช้แต่ละตัวอย่างละครั้งค่ะ\n"
                "(Must use all 4 numbers exactly once)"
            )
        elif "เศษส่วน" in reason:
            reply = (
                "💡 เกือบแล้วค่ะ! (Close!)\n"
                "กติกาคือระหว่างคำนวณห้ามเกิดเศษส่วนนะคะ\n"
                "(Fractions are not allowed during calculation)\n"
                "ลองเปลี่ยนวิธีคำนวณอีกนิดค่ะ (Try a different approach)"
            )
        elif "ติดลบ" in reason:
            reply = (
                "💡 สมการนี้มีค่าติดลบระหว่างคำนวณค่ะ\n"
                "(Negative values are not allowed during calculation)\n"
                "ลองจัดลำดับการคำนวณใหม่อีกครั้งนะคะ (Please rearrange your equation)"
            )
        else:
            reply = (
                "🌱 ยังไม่ใช่คำตอบนี้นะคะ (Not quite!)\n"
                "ลองคิดใหม่อีกครั้งค่ะ อย่าเพิ่งยอมแพ้นะคะ!\n"
                "(Try again, don't give up!)\n\n"
                "💡 คำตอบที่ผิดไม่ได้แปลว่าทำไม่ได้ค่ะ (Wrong answers are stepping stones!)"
            )

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    except Exception:
        player["combo"] = 0
        save_data()
        reply = (
            "🌱 สมการนี้ยังไม่ถูกต้องนะคะ (Invalid equation format)\n"
            "ลองเช็กวงเล็บและเครื่องหมายอีกครั้งค่ะ (Please check parentheses and operators)\n\n"
            "💪 ไม่เป็นไรนะคะ ลองใหม่ได้เสมอค่ะ (You can always try again)"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # RESULT != 24
    # =====================================================
    player["combo"] = 0
    save_data()
    encouragement = random_message(player, WRONG_MESSAGES)

    reply = (
        f"{encouragement}\n\n"
        f"ผลลัพธ์ของสมการนี้คือ {result} (The result is {result})\n"
        f"ยังไม่ใช่ 24 นะคะ (It's not 24 yet)\n\n"
        f"ลองเปลี่ยนวิธีจัดตัวเลขดูอีกครั้งค่ะ (Try rearranging the numbers)\n"
        f"💡 ยังไม่เสียคะแนนนะคะ ลองใหม่ได้เลย! (No points lost, try again!)"
    )

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)