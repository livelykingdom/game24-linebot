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
    if len(values) == 1: return 1 if values[0] == 24 else 0
    total = 0
    values = list(values)
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            a, b = values[i], values[j]
            rest = [values[k] for k in range(len(values)) if k not in (i, j)]
            results = [a+b, a-b, b-a, a*b]
            if b != 0: results.append(Fraction(a, b))
            if a != 0: results.append(Fraction(b, a))
            for result in results:
                if result < 0 or result.denominator != 1: continue
                total += count_solutions(tuple(sorted(rest + [result])))
    return total


def build_difficulty_buckets():
    if not PUZZLES: return
    puzzle_scores = []
    for puzzle in PUZZLES:
        score = count_solutions(tuple(puzzle))
        puzzle_scores.append((puzzle, score))
    puzzle_scores.sort(key=lambda x: x[1], reverse=True)
    total = len(puzzle_scores)
    bucket_size = max(1, total // 5)
    for index, item in enumerate(puzzle_scores):
        level = min(index // bucket_size, 4)
        difficulty_buckets[level].append(item[0])


def get_difficulty_from_score(score):
    return min(score // 20, 4)


def get_next_puzzle(score):
    level = get_difficulty_from_score(score)
    bucket = difficulty_buckets.get(level, [])
    return random.choice(bucket if bucket else PUZZLES)


# =========================================================
# PLAYER DATA
# =========================================================

def create_default_player():
    return {
        "score": 0, "combo": 0, "best_combo": 0,
        "badges": [], "current_puzzle": None, "last_encouragement": ""
    }

players = {}

def save_data():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
    except: pass

def load_data():
    global players
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                players = json.load(f)
    except: players = {}

def get_player(user_id):
    if user_id not in players: players[user_id] = create_default_player()
    return players[user_id]


# =========================================================
# BADGES
# =========================================================

BADGES = [
    {"id": "first", "icon": "🌟", "name": "นักคิดคนแรก"},
    {"id": "master", "icon": "💎", "name": "เซียนเกม 24"},
    {"id": "legend", "icon": "👑", "name": "ตำนานเกม 24"}
]

def update_badges(player):
    new = []
    if player["score"] >= 10 and "first" not in player["badges"]:
        player["badges"].append("first"); new.append("🌟 นักคิดคนแรก")
    if player["score"] >= 50 and "master" not in player["badges"]:
        player["badges"].append("master"); new.append("💎 เซียนเกม 24")
    if player["score"] >= 100 and "legend" not in player["badges"]:
        player["badges"].append("legend"); new.append("👑 ตำนานเกม 24")
    return new


# =========================================================
# SAFE EVAL
# =========================================================

def evaluate_expression(expression, puzzle):
    if len(expression) > 100 or not re.fullmatch(r"[0-9+\-*/()\s]+", expression):
        raise ValueError("Invalid format")
    tree = ast.parse(expression, mode="eval")
    used_numbers = []
    def visit(node):
        if isinstance(node, ast.Expression): return visit(node.body)
        if isinstance(node, ast.Constant):
            used_numbers.append(node.value)
            return Fraction(node.value, 1)
        if isinstance(node, ast.BinOp):
            l, r = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return l + r
            if isinstance(node.op, ast.Sub): return l - r
            if isinstance(node.op, ast.Mult): return l * r
            if isinstance(node.op, ast.Div): return l / r
        raise ValueError("Invalid")
    
    result = visit(tree)
    if sorted(used_numbers) != sorted(puzzle) or result.denominator != 1 or result < 0:
        raise ValueError("Invalid")
    return result


# =========================================================
# MESSAGE HANDLERS
# =========================================================

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    if not signature: abort(400)
    body = request.get_data(as_text=True)
    try: handler.handle(body, signature)
    except InvalidSignatureError: abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    text_lower = text.lower()
    user_id = event.source.user_id
    player = get_player(user_id)

    if text_lower in ["คะแนน", "score"]:
        rank_th, rank_en = get_rank(player["score"])
        reply = f"🏆 คะแนนสะสม: {player['score']}\n🏅 ระดับ: {rank_th} ({rank_en})"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if text_lower in ["ขอโจทย์", "puzzle", "play"]:
        puzzle = get_next_puzzle(player["score"])
        player["current_puzzle"] = puzzle
        save_data()
        nums = " ".join(map(str, puzzle))
        reply = (f"🧩 โจทย์: {nums}\n(Puzzle: {nums})\n\n"
                 f"พิมพ์สมการตอบกลับมาเลยค่ะ (Type your equation)")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if player["current_puzzle"] is None:
        reply = ("สวัสดีค่ะ 🌟 พร้อมลับสมองกันหรือยังคะ?\n\n"
                 "พิมพ์ “ขอโจทย์” เพื่อเริ่มเล่นเกม 24 ค่ะ\n"
                 "พิมพ์ “คะแนน” เพื่อดู Rank และคะแนนนะคะ\n\n"
                 "Hello! 🌟 Ready to sharpen your mind?\n\n"
                 "Type “puzzle” to start playing Game 24.\n"
                 "Type “score” to check your Rank and points.")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    try:
        result = evaluate_expression(text, player["current_puzzle"])
        if result == 24:
            player["score"] += 1
            rank_th, rank_en = get_rank(player["score"])
            new_puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = new_puzzle
            save_data()
            reply = (f"✨ ถูกต้อง! (Correct!)\n"
                     f"🏆 คะแนน: {player['score']} | 🏅 ระดับ: {rank_th} ({rank_en})\n"
                     f"🧩 โจทย์ถัดไป: {' '.join(map(str, new_puzzle))}\n"
                     f"(Next puzzle: {' '.join(map(str, new_puzzle))})")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"😅 ผลลัพธ์คือ {result} ลองใหม่นะคะ!\n(Result is {result}, try again!)"))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ รูปแบบไม่ถูกต้อง ลองใหม่ค่ะ\n(Invalid format, try again)"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)