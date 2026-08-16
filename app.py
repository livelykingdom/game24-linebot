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

# ระบุ Secret และ Token ของ LINE Bot
CHANNEL_SECRET = '59244ceb431e36e1b1b27fd5a2cbb7ca'
CHANNEL_ACCESS_TOKEN = 'XYvMjGta0QtKO/zZwykz/RBqmh84ukn2MpIkUfdBtkzrzh9Zt9u8lYv4wQOZ8kBqxn2TGWMOn1vaqLptWUC4M2xncEgdLtM2N+cqy6tU9cr9pZi0BPkoq9hgGIQd+DhqiWd0F3e5hVMg9qrqhMTg+gdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")
SAVE_FILE = "game_data.json"


# =========================================================
# PUZZLES (404 ข้อ)
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
        return "👑 คุณขึ้นถึงระดับสูงสุดแล้วนะคะ!"

    next_score, next_th, _ = next_rank
    remaining = next_score - score

    return (
        f"📈 อีก {remaining} คะแนน "
        f"จะเลื่อนขั้นเป็น «{next_th}» นะคะ"
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

difficulty_buckets = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: []
}


# =========================================================
# PUZZLE SOLVER
# ใช้สำหรับประเมินความยากของโจทย์
# =========================================================

@lru_cache(maxsize=None)
def count_solutions(values):
    """
    นับจำนวนวิธีที่สามารถทำให้ได้ 24
    โดยอนุญาตเฉพาะผลลัพธ์ที่เป็นจำนวนเต็มและไม่ติดลบ
    """
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

    # โจทย์ที่มีหลายวิธีแก้ = โดยทั่วไปง่ายกว่า
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
    {
        "id": "first_correct",
        "icon": "🌟",
        "name": "นักคิดคนแรก",
        "condition": lambda p: p["correct_total"] >= 1
    },
    {
        "id": "combo_5",
        "icon": "🔥",
        "name": "ไฟแรง Combo x5",
        "condition": lambda p: p["best_combo"] >= 5
    },
    {
        "id": "daily_5",
        "icon": "🎯",
        "name": "ภารกิจประจำวัน",
        "condition": lambda p: p["daily_correct"] >= 5
    },
    {
        "id": "score_10",
        "icon": "🏅",
        "name": "นักคิดหน้าใหม่",
        "condition": lambda p: p["score"] >= 10
    },
    {
        "id": "score_50",
        "icon": "💎",
        "name": "เซียนเกม 24",
        "condition": lambda p: p["score"] >= 50
    },
    {
        "id": "score_100",
        "icon": "👑",
        "name": "ตำนานแห่งเกม 24",
        "condition": lambda p: p["score"] >= 100
    },
    {
        "id": "streak_3",
        "icon": "🔥",
        "name": "นักสู้ 3 วัน",
        "condition": lambda p: p["best_streak"] >= 3
    },
    {
        "id": "streak_7",
        "icon": "🌟",
        "name": "7-Day Champion",
        "condition": lambda p: p["best_streak"] >= 7
    }
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
        return "ยังไม่มีเหรียญนะคะ เล่นต่ออีกนิด เดี๋ยวก็ได้เหรียญแรกแล้วค่ะ 🌟"
    return "\n".join(unlocked)


# =========================================================
# ENCOURAGEMENT
# =========================================================

CORRECT_MESSAGES = [
    "✨ ถูกต้องค่ะ! เก่งมากเลยนะคะ",
    "🌟 เยี่ยมมากค่ะ! สมองไวมากเลย",
    "🎯 แม่นมากค่ะ! จับทางโจทย์ได้เก่งจริง ๆ",
    "🧠 เก่งมากนะคะ! คิดได้ยอดเยี่ยมเลย",
    "🔥 สุดยอดค่ะ! วันนี้สมองกำลังร้อนแรงเลย",
    "👏 ถูกต้องค่ะ! ค่อย ๆ เก่งขึ้นทุกข้อเลยนะคะ",
    "🚀 เก่งมากค่ะ! ไปต่อกันอีกข้อเลยนะคะ",
    "💡 คิดได้เฉียบมากค่ะ!",
    "🏆 เยี่ยมเลยค่ะ! อีกนิดเดียวก็ขึ้น Rank ใหม่แล้วนะคะ",
    "🌈 ทำได้แล้วค่ะ! อย่าเพิ่งหยุดนะคะ"
]

WRONG_MESSAGES = [
    "💪 ยังไม่ใช่คำตอบนี้นะคะ แต่ไม่เป็นไร ลองใหม่อีกครั้งค่ะ",
    "🧠 เกือบแล้วค่ะ! ลองจัดกลุ่มตัวเลขใหม่ดูนะคะ",
    "🌱 ไม่เป็นไรเลยค่ะ ความผิดพลาดก็เป็นส่วนหนึ่งของการฝึกนะคะ",
    "✨ ลองมองโจทย์อีกมุมหนึ่งดูนะคะ ใกล้มากแล้วค่ะ",
    "💡 ยังมีทางอื่นอยู่นะคะ ลองเปลี่ยนเครื่องหมายดูค่ะ",
    "👏 อย่าเพิ่งยอมแพ้นะคะ นักคิดเก่ง ๆ ก็ต้องลองหลายทางค่ะ"
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
        f"🏆 คะแนนสะสม: {player['score']} คะแนน\n"
        f"🏅 ระดับ: {rank_th}\n"
        f"🔥 Combo สูงสุด: x{player['best_combo']}\n"
        f"📅 ภารกิจวันนี้: {player['daily_correct']}/5 ข้อ\n"
        f"🔥 Streak: {player['streak']} วัน\n"
        f"⭐ Personal Best วันนี้: {player['personal_best_daily_score']} คะแนน\n"
        f"🎖️ เหรียญ: {len(player['badges'])}/{len(BADGES)}\n\n"
        f"{get_progress_text(player['score'])}"
    )


def format_stats_english(player):
    _, rank_en = get_rank(player["score"])
    return (
        f"🏆 Score: {player['score']}\n"
        f"🏅 Rank: {rank_en}\n"
        f"🔥 Best Combo: x{player['best_combo']}\n"
        f"📅 Daily Mission: {player['daily_correct']}/5\n"
        f"🔥 Streak: {player['streak']} days\n"
        f"⭐ Personal Best: {player['personal_best_daily_score']}\n"
    )


def format_puzzle_message(puzzle, player):
    nums = " ".join(map(str, puzzle))
    difficulty_level = get_difficulty_from_score(player["score"])
    difficulty_en, difficulty_th = DIFFICULTY_NAMES[difficulty_level]
    rank_th, rank_en = get_rank(player["score"])

    return (
        f"🧩 โจทย์มาแล้วค่ะ!\n"
        f"เลขของคุณคือ: {nums}\n\n"
        f"🎯 ระดับโจทย์: {difficulty_en} ({difficulty_th})\n"
        f"🏅 Rank: {rank_th}\n"
        f"🔥 Combo: x{player['combo']}\n\n"
        f"นำเลขทั้ง 4 ตัวมาคำนวณให้ได้ 24 นะคะ\n"
        f"พิมพ์สมการตอบกลับมาได้เลยค่ะ\n\n"
        f"💡 อยากพัก พิมพ์ “ยอมแพ้” ได้นะคะ\n\n"
        f"🧩 Here is your puzzle!\n"
        f"Numbers: {nums}\n"
        f"🎯 Difficulty: {difficulty_en}\n\n"
        f"Type your equation to make 24.\n"
        f"Type “give up” if you need a break."
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
        reply = (
            f"{format_stats(player)}\n\n"
            f"🇬🇧 {format_stats_english(player)}\n"
            f"\nType 'badges' to see your badges."
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # BADGES
    # =====================================================
    if text_lower in ["เหรียญ", "badge", "badges"]:
        save_data()
        reply = (
            f"🎖️ เหรียญความสำเร็จของคุณ\n\n"
            f"{get_badge_text(player)}\n\n"
            f"สะสมต่อไปนะคะ ยังมีเหรียญรอปลดล็อกอีกค่ะ!"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # PUZZLE
    # =====================================================
    if text_lower in ["ขอโจทย์", "puzzle", "play"]:
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
    # GIVE UP
    # =====================================================
    if text_lower in ["ยอมแพ้", "give up", "skip"]:
        player["current_puzzle"] = None
        player["combo"] = 0
        save_data()
        reply = (
            "พักก่อนได้เลยนะคะ 🌷\n"
            "ไม่เป็นไรเลยค่ะ พรุ่งนี้หรือเมื่อพร้อมแล้ว กลับมาประลองใหม่ได้เสมอนะคะ\n\n"
            "💡 ความเก่งเกิดจากการฝึกทีละนิดค่ะ\n\n"
            "พิมพ์ “ขอโจทย์” เพื่อเล่นต่อได้เลยค่ะ"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # =====================================================
    # NO CURRENT PUZZLE
    # =====================================================
    if player["current_puzzle"] is None:
        reply = (
            "สวัสดีค่ะ 🌟\n"
            "พร้อมลับสมองกันหรือยังคะ?\n\n"
            "พิมพ์ “ขอโจทย์” เพื่อเริ่มเล่นเกม 24 ค่ะ\n"
            "พิมพ์ “คะแนน” เพื่อดู Rank และคะแนนนะคะ\n"
            "พิมพ์ “เหรียญ” เพื่อดูเหรียญที่สะสมค่ะ"
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
                    "\n\n🎉 จบด่านย่อย 5 ข้อแล้วค่ะ!\n"
                    "🎁 โบนัสพิเศษ +2 คะแนนนะคะ"
                )
            elif player["round_correct"] == 10:
                milestone_bonus += 5
                milestone_message = (
                    "\n\n🏆 จบด่าน 10 ข้อแล้วค่ะ!\n"
                    "🎁 โบนัสพิเศษ +5 คะแนนนะคะ\n"
                    "🚀 ไปต่อด่านใหม่กันเลยค่ะ!"
                )
                player["round_correct"] = 0

            if player["daily_correct"] == 5:
                milestone_bonus += 2
                milestone_message += (
                    "\n\n🎯 ภารกิจวันนี้สำเร็จแล้วค่ะ!\n"
                    "เก่งมากนะคะ ตอบถูกครบ 5 ข้อแล้ว\n"
                    "🎁 โบนัสภารกิจ +2 คะแนน"
                )
            
            if player["daily_correct"] == 10:
                milestone_bonus += 5
                milestone_message += (
                    "\n\n🌟 วันนี้สุดยอดมากค่ะ!\n"
                    "ตอบถูกครบ 10 ข้อแล้วนะคะ\n"
                    "🎁 โบนัสพิเศษ +5 คะแนน"
                )

            total_gain = base_score + combo_bonus + milestone_bonus
            old_score = player["score"]

            player["score"] += total_gain
            player["daily_score"] += total_gain

            if player["daily_score"] > player["personal_best_daily_score"]:
                player["personal_best_daily_score"] = player["daily_score"]

            new_badges = update_badges(player)
            old_rank = get_rank(old_score)
            new_rank = get_rank(player["score"])
            rank_up = old_rank != new_rank

            new_puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = new_puzzle
            encouragement = random_message(player, CORRECT_MESSAGES)
            rank_th, rank_en = get_rank(player["score"])

            combo_text = ""
            if combo_bonus > 0:
                combo_text = (
                    f"\n🔥 COMBO x{player['combo']}!"
                    f" โบนัส +{combo_bonus} คะแนนค่ะ"
                )

            rank_text = ""
            if rank_up:
                rank_text = (
                    f"\n\n🎉 ยินดีด้วยนะคะ!\n"
                    f"เลื่อนขั้นเป็น 🏅 {rank_th} แล้วค่ะ!\n"
                    f"🇬🇧 {rank_en}"
                )

            badge_text = ""
            if new_badges:
                badge_text = (
                    "\n\n🎖️ ปลดล็อกเหรียญใหม่ค่ะ!\n"
                    + "\n".join(new_badges)
                )

            progress = get_progress_text(player["score"])

            reply = (
                f"{encouragement}\n\n"
                f"✅ คำตอบถูกต้องค่ะ!\n"
                f"🎁 ได้คะแนน +{total_gain}\n"
                f"🏆 คะแนนสะสม: {player['score']}\n"
                f"🏅 ระดับ: {rank_th}\n"
                f"🔥 Combo: x{player['combo']}\n"
                f"📅 ภารกิจวันนี้: {player['daily_correct']}/5\n"
                f"🔥 Streak: {player['streak']} วัน\n"
                f"{progress}"
                f"{combo_text}"
                f"{milestone_message}"
                f"{rank_text}"
                f"{badge_text}"
                f"\n\n"
                f"🧩 โจทย์ถัดไป: {' '.join(map(str, new_puzzle))}\n\n"
                f"พิมพ์สมการมาได้เลยนะคะ หรือพิมพ์ “ยอมแพ้” เพื่อพักค่ะ"
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
            "😅 ข้อนี้หารด้วยศูนย์นะคะ\n"
            "ลองคิดใหม่อีกครั้งได้เลยค่ะ\n\n"
            "💡 Combo ถูกรีเซ็ตแล้ว แต่คะแนนเดิมยังอยู่ค่ะ"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    except ValueError as e:
        player["combo"] = 0
        save_data()
        reason = str(e)

        if "เลขไม่ตรง" in reason:
            reply = (
                "🔎 ลองเช็กตัวเลขอีกครั้งนะคะ\n\n"
                f"โจทย์คือ: {' '.join(map(str, puzzle))}\n\n"
                "ต้องใช้เลขทั้ง 4 ตัวให้ครบ และใช้แต่ละตัวอย่างละครั้งค่ะ"
            )
        elif "เศษส่วน" in reason:
            reply = (
                "💡 เกือบแล้วค่ะ!\n"
                "กติกาของเราคือระหว่างคำนวณห้ามเกิดเศษส่วนนะคะ\n"
                "ลองเปลี่ยนวิธีคำนวณอีกนิดค่ะ"
            )
        elif "ติดลบ" in reason:
            reply = (
                "💡 สมการนี้มีค่าติดลบระหว่างคำนวณค่ะ\n"
                "ลองจัดลำดับการคำนวณใหม่อีกครั้งนะคะ"
            )
        else:
            reply = (
                "🌱 ยังไม่ใช่คำตอบนี้นะคะ\n"
                "ลองคิดใหม่อีกครั้งค่ะ อย่าเพิ่งยอมแพ้นะคะ!\n\n"
                "💡 คำตอบที่ผิดไม่ได้แปลว่าทำไม่ได้ค่ะ"
            )

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    except Exception:
        player["combo"] = 0
        save_data()
        reply = (
            "🌱 สมการนี้ยังไม่ถูกต้องนะคะ\n"
            "ลองเช็กวงเล็บและเครื่องหมายอีกครั้งค่ะ\n\n"
            "💪 ไม่เป็นไรนะคะ ลองใหม่ได้เสมอค่ะ"
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
        f"ผลลัพธ์ของสมการนี้คือ {result}\n"
        f"ยังไม่ใช่ 24 นะคะ\n\n"
        f"ลองเปลี่ยนวิธีจัดตัวเลขดูอีกครั้งค่ะ\n"
        f"💡 ยังไม่เสียคะแนนนะคะ ลองใหม่ได้เลย!"
    )

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)