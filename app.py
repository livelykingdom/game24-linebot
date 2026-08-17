# =========================================================
# MESSAGE HANDLER (ฉบับป้องกันข้อมูลรีเซ็ต)
# =========================================================

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    text_lower = text.lower()
    user_id = event.source.user_id
    player = get_player(user_id)

    prepare_daily_data(player)

    # 1. SCORE
    if text_lower in ["คะแนน", "score"]:
        save_data()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=format_stats(player)))
        return

    # 2. BADGES
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

    # 3. PLAY (ป้องกันไม่ให้ล้างคะแนนเก่าหากผู้เล่นมีคะแนนอยู่แล้ว)
    if text_lower in ["เล่น", "play"]:
        register_activity(player)
        # หากผู้เล่นยังไม่มีโจทย์ปัจจุบัน ค่อยสุ่มโจทย์ใหม่ แต่คะแนนและภารกิจเดิมจะยังอยู่ครบ
        if player.get("current_puzzle") is None:
            puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = puzzle
            player["hint_used"] = False
            save_data()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=format_puzzle_message(player["current_puzzle"], player))
        )
        return

    # 4. BREAK / SKIP
    if text_lower in ["พัก", "break"]:
        player["current_puzzle"] = None
        player["combo"] = 0
        player["hint_used"] = False
        save_data()
        reply = (
            "พักก่อนได้เลยนะคะ 🌷 (Take a break!)\n"
            "ไม่เป็นไรเลยค่ะ พรุ่งนี้หรือเมื่อพร้อมแล้ว กลับมาประลองใหม่ได้เสมอนะคะ\n"
            "พิมพ์ “เล่น” เพื่อเล่นต่อได้เลยค่ะ"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if text_lower in ["ข้าม", "skip"]:
        if player.get("current_puzzle") is not None:
            puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = puzzle
            player["combo"] = 0
            player["hint_used"] = False
            save_data()
            reply = (
                f"🔄 เปลี่ยนโจทย์เรียบร้อยค่ะ! (Puzzle skipped!)\n\n"
                f"{format_puzzle_message(puzzle, player)}"
            )
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            reply = "ยังไม่มีโจทย์ที่กำลังเล่นอยู่ค่ะ พิมพ์ “เล่น” เพื่อเริ่มได้เลยค่ะ"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 5. NO CURRENT PUZZLE
    if player.get("current_puzzle") is None:
        reply = (
            "สวัสดีค่ะ 🌟 พร้อมลับสมองกันหรือยังคะ?\n\n"
            "พิมพ์ “เล่น” เพื่อเริ่มเล่นเกม 24 ค่ะ\n"
            "พิมพ์ “คะแนน” เพื่อดู Rank และคะแนนนะคะ\n"
            "พิมพ์ “เหรียญ” เพื่อดูเหรียญที่สะสมค่ะ"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 6. HINT
    if text_lower in ["คำใบ้", "hint"]:
        puzzle = player.get("current_puzzle")
        hint_msg = make_hint_message(player, puzzle)
        save_data()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=hint_msg))
        return

    # 7. ANSWER (ตรวจคำตอบ)
    puzzle = player["current_puzzle"]

    try:
        result = evaluate_expression(text, puzzle)

        if result == 24:
            player["correct_total"] += 1
            player["daily_correct"] += 1
            
            if player.get("hint_used", False):
                combo_bonus = 0
            else:
                player["combo"] += 1
                player["best_combo"] = max(player["best_combo"], player["combo"])
                combo_bonus = calculate_combo_bonus(player["combo"])

            base_score = 1
            milestone_bonus = 0
            milestone_message = ""

            player["round_correct"] += 1
            if player["round_correct"] == 5:
                milestone_bonus += 2
                milestone_message = "\n\n🎉 จบด่านย่อย 5 ข้อ! (+2 Bonus)"
            elif player["round_correct"] == 10:
                milestone_bonus += 5
                milestone_message = "\n\n🏆 จบด่าน 10 ข้อ! (+5 Bonus)"
                player["round_correct"] = 0

            if player["daily_correct"] == 5:
                milestone_bonus += 2
                milestone_message += "\n\n🎯 ภารกิจวันนี้สำเร็จ! (+2 Bonus)"

            total_gain = base_score + combo_bonus + milestone_bonus
            old_score = player["score"]

            player["score"] += total_gain
            player["daily_score"] += total_gain

            if player["daily_score"] > player["personal_best_daily_score"]:
                player["personal_best_daily_score"] = player["daily_score"]

            new_badges = update_badges(player)
            old_rank = get_rank(old_score)
            rank_th, rank_en = get_rank(player["score"])

            new_puzzle = get_next_puzzle(player["score"])
            player["current_puzzle"] = new_puzzle
            player["hint_used"] = False 
            encouragement = random_message(player, CORRECT_MESSAGES)

            progress_text = get_progress_text(player["score"])

            badge_text = ""
            if new_badges:
                badge_text = "\n\n🎖️ ปลดล็อกเหรียญใหม่! (New Badge Unlocked!)\n" + "\n".join(new_badges)

            reply = (
                f"{encouragement}\n\n"
                f"🎁 +{total_gain} | 🏆 Score: {player['score']}\n"
                f"🏅 {rank_th} ({rank_en}) | 🔥 Combo x{player['combo']}\n"
                f"📅 ภารกิจวันนี้: {player['daily_correct']}/5 ✅ | 🔥 Streak: {player['streak']} วัน (day)\n"
                f"{progress_text}"
                f"{badge_text}"
                f"{milestone_message}\n\n"
                f"🧩 โจทย์ถัดไป (Next puzzle): {' '.join(map(str, new_puzzle))}\n\n"
                f"พิมพ์สมการมาได้เลยนะคะ\n"
                f"Type your equation when you're ready.\n\n"
                f"พิมพ์ “คำใบ้” เพื่อขอคำใบ้, “พัก” เพื่อพักก่อน หรือ “ข้าม” เพื่อเปลี่ยนโจทย์ค่ะ\n"
                f"Type “hint” for a clue, “break” to take a break, or “skip” for a new puzzle."
            )

            save_data()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            return

    except ZeroDivisionError:
        player["combo"] = 0
        save_data()
        reply = "😅 ข้อนี้หารด้วยศูนย์นะคะ (Division by zero)\nลองคิดใหม่อีกครั้งได้เลยค่ะ"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    except ValueError as e:
        player["combo"] = 0
        save_data()
        reason = str(e)
        if "เลขไม่ตรง" in reason:
            reply = f"🔎 ใช้ตัวเลขไม่ตรงกับโจทย์ค่ะ\nโจทย์คือ: {' '.join(map(str, puzzle))}"
        elif "เศษส่วน" in reason:
            reply = "💡 ห้ามเกิดเศษส่วนระหว่างคำนวณค่ะ ลองใหม่นะ"
        elif "ติดลบ" in reason:
            reply = "💡 ห้ามมีค่าติดลบระหว่างคำนวณค่ะ ลองใหม่นะ"
        else:
            reply = "🌱 สมการไม่ถูกต้อง ลองเช็กเครื่องหมายอีกครั้งค่ะ"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    except Exception:
        player["combo"] = 0
        save_data()
        reply = "🌱 สมการยังไม่ถูกต้อง ลองใหม่นะคะ"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # RESULT != 24
    player["combo"] = 0
    save_data()
    encouragement = random_message(player, WRONG_MESSAGES)
    reply = f"{encouragement}\n\nผลลัพธ์คือ {result} ยังไม่ใช่ 24 นะคะ ลองใหม่ได้เลย!"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))