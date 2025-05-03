import json
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from playsound import playsound
import threading
import os
import pygame
from PIL import Image, ImageTk


# Load JSON questions (randomize and select up to 10)
with open("questions.json", "r") as f:
    all_questions = json.load(f)
questions = random.sample(all_questions, min(10, len(all_questions)))

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎉 Creative Quiz App")
        self.root.geometry("500x400")
        self.root.configure(bg="#fffbe6")

        try:
            self.bg_image = Image.open("background.png")
            self.bg_image = ImageTk.PhotoImage(self.bg_image)
        except Exception as e:
            print("Error loading background image:", e)
            # Optionally, load a default image or skip background
            self.bg_image = None

        if self.bg_image:
            self.bg_label = tk.Label(root, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()
        else:
            self.bg_label = tk.Label(root, bg="#fffbe6")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.score = 0
        self.q_index = 0
        self.time_left = 10  # Seconds per question
        self.timer = None
        self.high_score = 0

        # Initialize pygame mixer and play background music
        pygame.mixer.init()
        pygame.mixer.music.load("background_music.mp3")
        pygame.mixer.music.play(-1)

        # Load high score
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read().strip())

        self.title_label = tk.Label(root, text="🧠 Fun Quiz Time! 🏆", font=("Arial", 28, "bold"), bg="#fffbe6", fg="#cc3300")
        self.title_label.pack(pady=10)

        self.emoji_label = tk.Label(root, text="🤓", font=("Arial", 26), bg="#fffbe6")
        self.emoji_label.pack()

        self.image_label = tk.Label(root, bg="#fffbe6")
        self.image_label.pack(pady=10)

        self.question_label = tk.Label(root, text="", font=("Arial", 20), wraplength=450, bg="#fffbe6", fg="#444444")
        self.question_label.pack(pady=20)

        self.options_var = tk.StringVar()
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(root, text="", variable=self.options_var, value="", font=("Arial", 20), bg="#fff0cc", fg="#000066")
            rb.place(x=-300, y=0)
            self.radio_buttons.append(rb)

        self.timer_label = tk.Label(root, text="⏱️ Time: 10s", font=("Arial", 16), fg="blue", bg="#fffbe6")
        self.timer_label.pack(pady=10)
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=len(questions))
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TProgressbar", background="#ffcc00", troughcolor="#fffbe6")
        self.progress.pack(pady=10)

        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 16), bg="#fffbe6", fg="#007700")
        self.score_label.pack(pady=5)

        self.submit_button = tk.Button(root, text="Submit ✅", command=lambda: [self.play_click_sound(), self.check_answer()], bg="#ffd699", fg="#333", font=("Arial", 16, "bold"))
        self.submit_button.pack(pady=10)
        self.music_button = tk.Button(root, text="🔊 Pause Music", command=lambda: [self.play_click_sound(), self.toggle_music()], bg="#ffd699", fg="#333", font=("Arial", 14))
        self.music_button.pack(pady=5)
        def on_enter(e): e.widget.config(bg="#ffe0b3")
        def on_leave(e): e.widget.config(bg="#ffd699")
        self.submit_button.bind("<Enter>", on_enter)
        self.submit_button.bind("<Leave>", on_leave)
        self.music_button.bind("<Enter>", on_enter)
        self.music_button.bind("<Leave>", on_leave)
 
        self.next_question()
        self.credits_label = tk.Label(root, text="Done by Subash, Mahesh and Berlin", font=("Arial", 12, "italic"), bg="#fffbe6", fg="#666666")
        self.credits_label.pack(side="bottom", pady=5)

    def play_click_sound(self):
        threading.Thread(target=playsound, args=("click.mp3",), daemon=True).start()

    def slide_in_option(self, widget, end_x, y, step=10):
        def slide(x):
            if x < end_x:
                widget.place(x=x, y=y)
                self.root.after(10, slide, x + step)
            else:
                widget.place(x=end_x, y=y)
        slide(-300)

    def start_timer(self):
        self.time_left = 10
        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"⏱️ Time: {self.time_left}s")
        if self.time_left > 0:
            self.time_left -= 1
            self.timer = self.root.after(1000, self.update_timer)
        else:
            self.check_answer(timeout=True)

    def animate_question_transition(self, new_text):
        def fade_out(alpha=1.0):
            if alpha > 0:
                self.question_label.config(fg=f"#{int(alpha * 51):02x}{int(alpha * 51):02x}{int(alpha * 51):02x}")
                self.root.after(50, fade_out, alpha - 0.1)
            else:
                self.question_label.config(text=new_text)
                fade_in()

        def fade_in(alpha=0.0):
            if alpha <= 1:
                self.question_label.config(fg=f"#{int(alpha * 51):02x}{int(alpha * 51):02x}{int(alpha * 51):02x}")
                self.root.after(50, fade_in, alpha + 0.1)

        fade_out()

    def next_question(self):
        if self.q_index < len(questions):
            q = questions[self.q_index]
            self.image_label.config(image="")
            self.current_image = None

            if "image" in q:
                self.current_image = tk.PhotoImage(file=q["image"])
                self.image_label.config(image=self.current_image)

            self.animate_question_transition(f"❓ {q['question']}")
            self.options_var.set(None)
            for i, option in enumerate(q['options']):
                self.radio_buttons[i].config(text=option, value=option)
                self.radio_buttons[i].place(x=-300, y=250 + i*40)
                self.slide_in_option(self.radio_buttons[i], end_x=150, y=250 + i*40)
            self.start_timer()
            self.progress["value"] = self.q_index
            self.animate_emoji()
        else:
            self.end_quiz()

    def check_answer(self, timeout=False):
        self.root.after_cancel(self.timer)
        selected = self.options_var.get()
        correct = questions[self.q_index]["answer"]

        if timeout:
            messagebox.showinfo("⏰ Time's Up!", f"Time's up! Correct answer was: {correct}")
            self.play_sound("sound_wrong.mp3")
        elif selected == correct:
            messagebox.showinfo("✅ Correct!", "Nice one!")
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.play_sound("sound_correct.mp3")
        else:
            messagebox.showinfo("❌ Wrong!", f"Oops! The correct answer was: {correct}")
            self.play_sound("sound_wrong.mp3")

        self.q_index += 1
        self.next_question()

    def end_quiz(self):
        messagebox.showinfo("🏁 Quiz Over", f"You scored {self.score} out of {len(questions)}")
        if self.score > self.high_score:
            self.high_score = self.score
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
            messagebox.showinfo("🏆 New High Score!", f"Congratulations! Your new high score is {self.high_score}.")
            self.canvas = tk.Canvas(self.root, width=500, height=400, bg="#fffbe6", highlightthickness=0)
            self.canvas.place(x=0, y=0)
            self.confetti = [self.canvas.create_oval(random.randint(0, 500), random.randint(0, 400), 
                                                       random.randint(5, 15)+10, random.randint(5, 15)+10, 
                                                       fill=random.choice(["red", "green", "blue", "yellow", "orange", "purple"])) 
                             for _ in range(50)]
            self.animate_confetti()
        
        if self.score > len(questions) // 2:
            self.play_sound("victory.mp3")
        else:
            self.play_sound("game_over.mp3")

        self.progress["value"] = len(questions)
        self.root.destroy()

    def animate_confetti(self):
        for dot in self.confetti:
            self.canvas.move(dot, 0, 5)
            x, y, _, _ = self.canvas.coords(dot)
            if y > 400:
                self.canvas.coords(dot, random.randint(0, 500), 0, random.randint(5, 15)+10, random.randint(5, 15)+10)
        self.root.after(100, self.animate_confetti)

    def animate_emoji(self):
        emojis = ["🤓", "🧐", "😄", "🎉"]
        idx = 0

        def update():
            nonlocal idx
            self.emoji_label.config(text=emojis[idx % len(emojis)])
            idx += 1
            if idx < 12:
                self.root.after(150, update)

        update()

    def play_sound(self, filename):
        threading.Thread(target=playsound, args=(filename,), daemon=True).start()

    def toggle_music(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.music_button.config(text="🔈 Play Music")
        else:
            pygame.mixer.music.unpause()
            self.music_button.config(text="🔊 Pause Music")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()