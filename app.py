import re
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

CHANNEL_SECRET = '59244ceb431e36e1b1b27fd5a2cbb7ca'
CHANNEL_ACCESS_TOKEN = 'XYvMjGta0QtKO/zZwykz/RBqmh84ukn2MpIkUfdBtkzrzh9Zt9u8lYv4wQOZ8kBqxn2TGWMOn1vaqLptWUC4M2xncEgdLtM2N+cqy6tU9cr9pZi0BPkoq9hgGIQd+DhqiWd0F3e5hVMg9qrqhMTg+gdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ตัวแปรสำหรับจดจำสถานะของผู้เล่น
user_puzzles = {}
user_scores = {}
user_langs = {} # เก็บภาษาที่ผู้ใช้เลือก (th หรือ en)

# ฐานข้อมูลโจทย์เกม 24 (404 ข้อ)
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

def get_rank(score):
    if score >= 100: return "24 Legend ตำนานแห่งเกม 24"
    if score >= 90: return "Math Genius อัจฉริยะคณิต"
    if score >= 80: return "24 Grandmaster ปรมาจารย์เกม 24"
    if score >= 70: return "Mind King ราชันย์นักคิด"
    if score >= 60: return "Brain Warrior นักรบสมองเพชร"
    if score >= 50: return "24 Master เซียนเกม 24"
    if score >= 40: return "Number Hunter นักล่าเลข 24"
    if score >= 30: return "Speed Mind นักคิดสายฟ้า"
    if score >= 20: return "Thinker นักคิดคล่องแคล่ว"
    if score >= 10: return "Rookie นักคิดหน้าใหม่"
    return "Beginner ผู้เริ่มต้น"

def check_level_up(score):
    ranks = {
        10: "Rookie นักคิดหน้าใหม่",
        20: "Thinker นักคิดคล่องแคล่ว",
        30: "Speed Mind นักคิดสายฟ้า",
        40: "Number Hunter นักล่าเลข 24",
        50: "24 Master เซียนเกม 24",
        60: "Brain Warrior นักรบสมองเพชร",
        70: "Mind King ราชันย์นักคิด",
        80: "24 Grandmaster ปรมาจารย์เกม 24",
        90: "Math Genius อัจฉริยะคณิต",
        100: "24 Legend ตำนานแห่งเกม 24"
    }
    return ranks.get(score, None)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    text_lower = text.lower()
    user_id = event.source.user_id

    # สร้างคะแนนเริ่มต้นให้ผู้ใช้
    if user_id not in user_scores:
        user_scores[user_id] = 0

    # ตรวจจับภาษาที่ผู้ใช้ถนัดจากคำสั่ง
    if text_lower in ["ขอโจทย์", "ยอมแพ้", "คะแนน"]:
        user_langs[user_id] = 'th'
    elif text_lower in ["puzzle", "play", "give up", "skip", "score"]:
        user_langs[user_id] = 'en'
        
    lang = user_langs.get(user_id, 'th')
    current_rank = get_rank(user_scores[user_id])

    # 1. เช็กคะแนน (Score)
    if text_lower in ["คะแนน", "score"]:
        score = user_scores[user_id]
        if lang == 'th':
            reply = f"🏆 คะแนนสะสม: {score} คะแนน\n🏅 ยศปัจจุบัน: {current_rank}\n\nพิมพ์ 'ขอโจทย์' เพื่อเล่นต่อได้เลยจ้า!"
        else:
            reply = f"🏆 Your Score: {score}\n🏅 Current Rank: {current_rank}\n\nType 'puzzle' to continue!"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 2. เริ่มขอโจทย์ (Puzzle)
    if text_lower in ["ขอโจทย์", "puzzle", "play"]:
        puzzle = random.choice(PUZZLES)
        user_puzzles[user_id] = puzzle
        nums_str = " ".join(map(str, puzzle))
        
        if lang == 'th':
            reply = (f"โจทย์มาแล้วจ้า! 🎉\nเลขของคุณคือ: {nums_str}\n\n"
                     f"พิมพ์สมการที่ได้ 24 ตอบกลับมาได้เลยค่ะ (เช่น (8+4)*(4-2))\n"
                     f"พิมพ์ 'ยอมแพ้' เพื่อพักก่อน หรือพิมพ์ 'คะแนน' เพื่อดูแต้ม")
        else:
            reply = (f"Here is your puzzle! 🎉\nNumbers: {nums_str}\n\n"
                     f"Type the equation to get 24 (e.g., (8+4)*(4-2))\n"
                     f"Type 'give up' to skip, or 'score' to check points.")
                     
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 3. ขอยอมแพ้ (Give up)
    if text_lower in ["ยอมแพ้", "give up", "skip"]:
        if user_id in user_puzzles:
            del user_puzzles[user_id]
            
        if lang == 'th':
            reply = "พักก่อนเนอะ ✌️ ถ้าพร้อมประลองความไวเมื่อไหร่ พิมพ์ 'ขอโจทย์' มาได้เลยนะคะ!"
        else:
            reply = "Taking a break! ✌️ When you're ready to play again, just type 'puzzle'!"
            
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 4. กำลังตอบคำถาม
    if user_id in user_puzzles:
        puzzle = user_puzzles[user_id]
        
        if not re.match(r'^[0-9+\-*/() \.]+$', text):
            msg = "❌ พิมพ์เฉพาะตัวเลขและเครื่องหมาย +, -, *, /, ( ) เท่านั้นนะคะ" if lang == 'th' else "❌ Please use only numbers and math symbols +, -, *, /, ( )"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
            return

        nums_in_text = sorted([int(n) for n in re.findall(r'\d+', text)])
        sorted_puzzle = sorted(puzzle)
        
        if nums_in_text != sorted_puzzle:
            msg = f"❌ ใช้ตัวเลขไม่ตรงกับโจทย์ค่ะ\nโจทย์ข้อนี้คือ: {' '.join(map(str, puzzle))}" if lang == 'th' else f"❌ You didn't use the correct numbers.\nYour puzzle is: {' '.join(map(str, puzzle))}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
            return

        try:
            result = eval(text)
            if result == 24:
                # ตอบถูก -> บวกคะแนน
                user_scores[user_id] += 1
                current_score = user_scores[user_id]
                rank_name = get_rank(current_score)
                level_up_name = check_level_up(current_score)
                
                # สุ่มข้อใหม่ทันที
                new_puzzle = random.choice(PUZZLES)
                user_puzzles[user_id] = new_puzzle
                nums_str = " ".join(map(str, new_puzzle))
                
                if lang == 'th':
                    reply = f"✨ ถูกต้องค่ะ! เก่งมาก ✨\n🏆 คะแนน: {current_score} | 🏅 ยศ: {rank_name}\n"
                    if level_up_name:
                        reply += f"🎉 ยินดีด้วย! เลื่อนขั้นเป็นแร้งค์ [ {level_up_name} ] แล้ว! 🎉\n"
                    reply += f"\nลุยกันต่อเลย! เลขข้อต่อไปคือ: {nums_str}\n(พิมพ์สมการเหมือนเดิม หรือพิมพ์ 'ยอมแพ้' เพื่อพักก่อนนะคะ)"
                else:
                    reply = f"✨ Correct! Great job ✨\n🏆 Score: {current_score} | 🏅 Rank: {rank_name}\n"
                    if level_up_name:
                        reply += f"🎉 Congratulations! You've ranked up to [ {level_up_name} ]! 🎉\n"
                    reply += f"\nNext puzzle: {nums_str}\n(Type your equation, or 'give up' to take a break)"
                    
            else:
                reply = f"😅 ยังไม่ถูกจ้า ผลลัพธ์ที่ได้คือ {result} ลองพยายามใหม่นะ!" if lang == 'th' else f"😅 Not quite! Your result is {result}. Try again!"
                
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            
        except ZeroDivisionError:
            msg = "❌ ระวังด้วยจ้า ห้ามหารด้วยศูนย์นะ ลองใหม่ๆ" if lang == 'th' else "❌ Be careful, division by zero is not allowed. Try again!"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        except Exception:
            msg = "❌ รูปแบบสมการไม่ถูกต้องค่ะ ลองเช็กการใส่วงเล็บอีกครั้งนะคะ" if lang == 'th' else "❌ Invalid equation format. Please check your parentheses and symbols."
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
            
    else:
        # 5. กรณีพิมพ์คำอื่นๆ นอกเหนือจากคำสั่ง
        reply = ("พิมพ์ 'ขอโจทย์' เพื่อเริ่มเล่นเกม 24 หรือพิมพ์ 'คะแนน' เพื่อดูแต้มสะสมได้เลยค่ะ 🧮\n"
                 "(Type 'puzzle' to play, or 'score' to check your rank!)")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=5000)