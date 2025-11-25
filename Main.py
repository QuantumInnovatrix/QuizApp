import tkinter as tk
from tkinter import messagebox, ttk
import random
import requests
import html
import threading
import json

class QuizGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Quiz Master")
        self.root.geometry("1000x750")
        self.root.configure(bg="#0a0e27")
        self.root.resizable(False, False)
        
        # Gradient background
        self.canvas = tk.Canvas(self.root, width=1000, height=750, bg="#0a0e27", highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.create_gradient_bg()

        self.main_frame = tk.Frame(self.root, bg="#0a0e27")
        self.main_frame.place(x=0, y=0, width=1000, height=750)

        # API Configuration
        self.api_url = "https://opentdb.com/api.php"
        self.categories_url = "https://opentdb.com/api_category.php"
        
        # Categories mapping
        self.categories = {
            "General Knowledge": 9,
            "Science & Nature": 17,
            "Computers": 18,
            "Mathematics": 19,
            "Sports": 21,
            "Geography": 22,
            "History": 23,
            "Animals": 27,
            "Vehicles": 28,
            "Video Games": 15,
            "Mixed Categories": "mixed"
        }
        
        # Difficulty levels
        self.difficulties = ["Easy", "Medium", "Hard", "Mixed"]

        # Game state
        self.questions = []
        self.score = 0                # total points (may be > number of questions)
        self.correct_count = 0        # number of correctly answered questions (0..n)
        self.current_question = 0
        self.selected_answer = tk.IntVar()
        self.time_left = 30
        self.timer_running = False
        self.timer_id = None
        self.total_time = 0
        self.total_timer_id = None
        self.streak = 0
        self.best_streak = 0
        self.high_score = 0          # stored as best correct_count (not points)
        self.answered_questions = []
        self.selected_category = tk.StringVar(value="Computers")
        self.selected_difficulty = tk.StringVar(value="Mixed")
        self.question_count = tk.IntVar(value=10)
        
        # Load saved stats
        self.load_stats()
        
        self.create_start_screen()

    def create_gradient_bg(self):
        """Create gradient background"""
        for i in range(750):
            r = int(10 + (30 - 10) * (i / 750))
            g = int(14 + (40 - 14) * (i / 750))
            b = int(39 + (60 - 39) * (i / 750))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 1000, i, fill=color)

    def load_stats(self):
        """Load saved statistics"""
        try:
            with open('quiz_stats.json', 'r') as f:
                stats = json.load(f)
                # high_score stored as best correct_count
                self.high_score = stats.get('high_score', 0)
                self.best_streak = stats.get('best_streak', 0)
        except:
            pass

    def save_stats(self):
        """Save statistics"""
        try:
            with open('quiz_stats.json', 'w') as f:
                json.dump({
                    'high_score': self.high_score,
                    'best_streak': self.best_streak
                }, f)
        except:
            pass

    def create_start_screen(self):
        """Create the start screen with settings"""
        self.clear_screen()

        # Title with shadow
        title_shadow = tk.Label(
            self.main_frame,
            text="🎓 QUIZ MASTER PRO 🎓",
            font=("Arial", 42, "bold"),
            bg="#0a0e27",
            fg="#1a1f45"
        )
        title_shadow.place(x=152, y=52)
        
        title_label = tk.Label(
            self.main_frame,
            text="🎓 QUIZ MASTER PRO 🎓",
            font=("Arial", 42, "bold"),
            bg="#0a0e27",
            fg="#00f5ff"
        )
        title_label.pack(pady=50)

        # Settings frame
        settings_frame = tk.Frame(self.main_frame, bg="#162447", bd=3, relief="raised")
        settings_frame.pack(pady=20, padx=150, fill="x")
        
        tk.Label(
            settings_frame,
            text="⚙️ QUIZ SETTINGS",
            font=("Arial", 18, "bold"),
            bg="#162447",
            fg="#00f5ff"
        ).pack(pady=15)

        # Category selection
        cat_frame = tk.Frame(settings_frame, bg="#162447")
        cat_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            cat_frame,
            text="📚 Category:",
            font=("Arial", 13, "bold"),
            bg="#162447",
            fg="#ffffff"
        ).pack(side="left", padx=10)
        
        category_menu = ttk.Combobox(
            cat_frame,
            textvariable=self.selected_category,
            values=list(self.categories.keys()),
            state="readonly",
            font=("Arial", 11),
            width=25
        )
        category_menu.pack(side="left", padx=10)

        # Difficulty selection
        diff_frame = tk.Frame(settings_frame, bg="#162447")
        diff_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            diff_frame,
            text="🎯 Difficulty:",
            font=("Arial", 13, "bold"),
            bg="#162447",
            fg="#ffffff"
        ).pack(side="left", padx=10)
        
        difficulty_menu = ttk.Combobox(
            diff_frame,
            textvariable=self.selected_difficulty,
            values=self.difficulties,
            state="readonly",
            font=("Arial", 11),
            width=25
        )
        difficulty_menu.pack(side="left", padx=10)

        # Question count
        count_frame = tk.Frame(settings_frame, bg="#162447")
        count_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(
            count_frame,
            text="📝 Questions:",
            font=("Arial", 13, "bold"),
            bg="#162447",
            fg="#ffffff"
        ).pack(side="left", padx=10)
        
        count_spinbox = tk.Spinbox(
            count_frame,
            from_=5,
            to=20,
            textvariable=self.question_count,
            font=("Arial", 11),
            width=10,
            state="readonly"
        )
        count_spinbox.pack(side="left", padx=10)
        
        tk.Label(
            count_frame,
            text="(5-20)",
            font=("Arial", 10),
            bg="#162447",
            fg="#888888"
        ).pack(side="left")

        # Stats display
        stats_frame = tk.Frame(self.main_frame, bg="#1e3a5f", bd=2, relief="groove")
        stats_frame.pack(pady=20, padx=150, fill="x")
        
        tk.Label(
            stats_frame,
            text=f"🏆 High Score: {self.high_score}",
            font=("Arial", 14, "bold"),
            bg="#1e3a5f",
            fg="#ffd700"
        ).pack(pady=8)
        
        tk.Label(
            stats_frame,
            text=f"🔥 Best Streak: {self.best_streak}",
            font=("Arial", 14, "bold"),
            bg="#1e3a5f",
            fg="#ff6b6b"
        ).pack(pady=8)

        # Start button
        start_btn = tk.Button(
            self.main_frame,
            text="▶ START QUIZ",
            font=("Arial", 20, "bold"),
            bg="#00ff88",
            fg="#0a0e27",
            activebackground="#00dd77",
            activeforeground="#0a0e27",
            bd=0,
            padx=60,
            pady=20,
            cursor="hand2",
            command=self.fetch_questions_and_start
        )
        start_btn.pack(pady=25)
        
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#00dd77", font=("Arial", 21, "bold")))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg="#00ff88", font=("Arial", 20, "bold")))

        # Info
        tk.Label(
            self.main_frame,
            text="📡 Questions loaded dynamically from Open Trivia Database",
            font=("Arial", 10),
            bg="#0a0e27",
            fg="#888888"
        ).pack(pady=5)
        
        tk.Label(
            self.main_frame,
            text="⏱️ 30 seconds per question | 🎯 Build streaks for bonus points!",
            font=("Arial", 11),
            bg="#0a0e27",
            fg="#aaaaaa"
        ).pack(pady=5)

    def show_loading_screen(self, message="Loading questions..."):
        """Show loading screen"""
        self.clear_screen()
        
        tk.Label(
            self.main_frame,
            text="⏳",
            font=("Arial", 60),
            bg="#0a0e27",
            fg="#00f5ff"
        ).pack(pady=150)
        
        tk.Label(
            self.main_frame,
            text=message,
            font=("Arial", 20),
            bg="#0a0e27",
            fg="#ffffff"
        ).pack(pady=20)
        
        # Animated loading bar
        self.loading_bar = tk.Canvas(self.main_frame, width=400, height=30, bg="#162447", highlightthickness=0)
        self.loading_bar.pack(pady=20)
        
        self.animate_loading()

    def animate_loading(self, pos=0):
        """Animate loading bar"""
        # guard in case loading was cancelled
        if not hasattr(self, 'loading_animation') or not self.loading_animation:
            return
        self.loading_bar.delete("all")
        self.loading_bar.create_rectangle(0, 0, pos % 400, 30, fill="#00f5ff", outline="")
        self.root.after(20, lambda: self.animate_loading(pos + 5))

    def fetch_questions_and_start(self):
        """Fetch questions from API and start quiz"""
        self.loading_animation = True
        self.show_loading_screen()
        
        # Fetch in background thread
        thread = threading.Thread(target=self.fetch_questions)
        thread.daemon = True
        thread.start()

    def fetch_questions(self):
        """Fetch questions from API"""
        try:
            # Build API URL
            category_id = self.categories[self.selected_category.get()]
            difficulty = self.selected_difficulty.get().lower()
            amount = self.question_count.get()
            
            params = {
                "amount": amount,
                "type": "multiple"
            }
            
            if category_id != "mixed":
                params["category"] = category_id
            
            if difficulty != "mixed":
                params["difficulty"] = difficulty
            
            # Make API request
            response = requests.get(self.api_url, params=params, timeout=10)
            data = response.json()
            
            if data.get("response_code") == 0:
                self.questions = self.parse_questions(data["results"])
                random.shuffle(self.questions)
                self.root.after(0, self.start_quiz)
            else:
                self.root.after(0, lambda: self.show_error("Not enough questions available for these settings. Try different options."))
                
        except requests.exceptions.RequestException:
            self.root.after(0, lambda: self.show_error("Network error! Please check your internet connection."))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error loading questions: {str(e)}"))

    def parse_questions(self, api_results):
        """Parse API results into question format"""
        questions = []
        for item in api_results:
            options = [html.unescape(item["correct_answer"])] + [html.unescape(opt) for opt in item["incorrect_answers"]]
            random.shuffle(options)
            
            questions.append({
                "question": html.unescape(item["question"]),
                "options": options,
                "answer": options.index(html.unescape(item["correct_answer"])),
                "difficulty": item.get("difficulty", "Mixed").capitalize(),
                "category": html.unescape(item.get("category", "General"))
            })
        
        return questions

    def show_error(self, message):
        """Show error and return to start"""
        self.loading_animation = False
        messagebox.showerror("❌ Error", message)
        self.create_start_screen()

    def start_quiz(self):
        """Start the quiz"""
        self.loading_animation = False
        # Stop loading animation guard
        if hasattr(self, 'loading_animation'):
            self.loading_animation = False

        self.score = 0
        self.correct_count = 0
        self.current_question = 0
        self.total_time = 0
        self.streak = 0
        self.answered_questions = []
        self.start_total_timer()
        self.show_question()

    def clear_screen(self):
        """Clear the screen"""
        # cancel any timers safely
        if getattr(self, 'timer_id', None):
            try:
                self.root.after_cancel(self.timer_id)
            except:
                pass
            self.timer_id = None
        if getattr(self, 'total_timer_id', None):
            try:
                self.root.after_cancel(self.total_timer_id)
            except:
                pass
            self.total_timer_id = None
        self.timer_running = False
        for widget in list(self.main_frame.winfo_children()):
            widget.destroy()

    def start_timer(self):
        """Start question timer"""
        self.time_left = 30
        self.timer_running = True
        self.update_timer()

    def start_total_timer(self):
        """Start total time tracker"""
        # reset
        self.total_time = 0
        self.update_total_timer()

    def update_total_timer(self):
        """Update total time"""
        self.total_time += 1
        self.total_timer_id = self.root.after(1000, self.update_total_timer)

    def update_timer(self):
        """Update countdown timer"""
        if self.timer_running and self.time_left > 0:
            self.timer_label.config(text=f"⏱️ {self.time_left}s")
            if self.time_left <= 10:
                self.timer_label.config(fg="#ff4d4d", font=("Arial", 14, "bold"))
            elif self.time_left <= 20:
                self.timer_label.config(fg="#ffa500")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.timer_running and self.time_left == 0:
            self.timer_running = False
            self.streak = 0
            messagebox.showwarning("⏰ Time's Up!", "Time expired! Your streak has been reset.")
            self.current_question += 1
            self.show_question()

    def show_question(self):
        """Display current question"""
        self.clear_screen()
        self.selected_answer.set(-1)

        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]

            # Progress bar
            progress_frame = tk.Frame(self.main_frame, bg="#0a0e27")
            progress_frame.pack(fill="x", padx=20, pady=15)

            progress_bar_bg = tk.Canvas(progress_frame, width=960, height=25, bg="#162447", highlightthickness=0)
            progress_bar_bg.pack()
            
            progress = ((self.current_question) / len(self.questions)) * 960
            progress_bar_bg.create_rectangle(0, 0, progress, 25, fill="#00f5ff", outline="")
            
            progress_text = f"{self.current_question}/{len(self.questions)}"
            progress_bar_bg.create_text(480, 12, text=progress_text, fill="#ffffff", font=("Arial", 11, "bold"))

            # Info bar
            info_frame = tk.Frame(self.main_frame, bg="#162447", bd=2, relief="solid")
            info_frame.pack(fill="x", padx=20, pady=10)

            tk.Label(
                info_frame,
                text=f"Question {self.current_question + 1}",
                font=("Arial", 13, "bold"),
                bg="#162447",
                fg="#ffffff",
                padx=10,
                pady=5
            ).pack(side="left")

            # Category badge
            tk.Label(
                info_frame,
                text=f"📁 {q.get('category', 'General')}",
                font=("Arial", 11),
                bg="#162447",
                fg="#aaaaaa",
                padx=10
            ).pack(side="left")

            # Difficulty badge
            difficulty_colors = {"Easy": "#00ff88", "Medium": "#ffa500", "Hard": "#ff4d4d"}
            tk.Label(
                info_frame,
                text=f"📌 {q['difficulty']}",
                font=("Arial", 12, "bold"),
                bg="#162447",
                fg=difficulty_colors.get(q['difficulty'], "#ffffff"),
                padx=10
            ).pack(side="left")

            tk.Label(
                info_frame,
                text=f"💯 Points: {self.score}",
                font=("Arial", 13, "bold"),
                bg="#162447",
                fg="#00ff88",
                padx=10
            ).pack(side="right")

            if self.streak > 0:
                tk.Label(
                    info_frame,
                    text=f"🔥 {self.streak}",
                    font=("Arial", 13, "bold"),
                    bg="#162447",
                    fg="#ff6b6b",
                    padx=10
                ).pack(side="right")

            self.timer_label = tk.Label(
                info_frame,
                text=f"⏱️ 30s",
                font=("Arial", 13, "bold"),
                bg="#162447",
                fg="#00ff00",
                padx=10,
                pady=5
            )
            self.timer_label.pack(side="right")

            # Question box
            question_frame = tk.Frame(self.main_frame, bg="#1e3a5f", bd=3, relief="ridge")
            question_frame.pack(pady=20, padx=50, fill="x")
            
            tk.Label(
                question_frame,
                text=q["question"],
                font=("Arial", 16, "bold"),
                bg="#1e3a5f",
                fg="#ffffff",
                wraplength=860,
                justify="center",
                padx=25,
                pady=25
            ).pack()

            # Options
            options_frame = tk.Frame(self.main_frame, bg="#0a0e27")
            options_frame.pack(pady=10)

            for i, option in enumerate(q["options"]):
                btn = tk.Radiobutton(
                    options_frame,
                    text=f"{chr(65+i)}) {option}",
                    variable=self.selected_answer,
                    value=i,
                    font=("Arial", 13),
                    bg="#1e3a5f",
                    fg="#ffffff",
                    selectcolor="#0f2642",
                    activebackground="#2a4f7d",
                    activeforeground="#00f5ff",
                    indicator=0,
                    width=70,
                    padx=20,
                    pady=15,
                    cursor="hand2",
                    borderwidth=2,
                    relief="raised"
                )
                btn.pack(pady=6)
                
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2a4f7d", relief="sunken"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1e3a5f", relief="raised"))

            # Submit button
            submit_btn = tk.Button(
                self.main_frame,
                text="✓ SUBMIT ANSWER",
                font=("Arial", 16, "bold"),
                bg="#00ff88",
                fg="#0a0e27",
                activebackground="#00dd77",
                activeforeground="#0a0e27",
                bd=0,
                padx=50,
                pady=15,
                cursor="hand2",
                command=self.check_answer
            )
            submit_btn.pack(pady=20)
            
            submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg="#00dd77"))
            submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg="#00ff88"))

            self.start_timer()
        else:
            self.show_results()

    def check_answer(self):
        """Check if answer is correct"""
        if self.selected_answer.get() == -1:
            self.show_inline_message("⚠️ No Selection", "Please select an answer before submitting!", "#ffa500")
            return

        # stop timer for this question
        self.timer_running = False
        if getattr(self, 'timer_id', None):
            try:
                self.root.after_cancel(self.timer_id)
            except:
                pass
            self.timer_id = None

        correct_answer = self.questions[self.current_question]["answer"]
        time_bonus = max(0, self.time_left // 5)

        if self.selected_answer.get() == correct_answer:
            # increment correct_count (used for final score display)
            self.correct_count += 1

            # keep the points system as you designed
            self.streak += 1
            points = 1 + time_bonus + (self.streak // 3)
            self.score += points

            self.best_streak = max(self.best_streak, self.streak)

            message = f"✨ Points earned: {points}"
            if time_bonus > 0:
                message += f" | ⚡ Speed bonus: +{time_bonus}"
            if self.streak > 2:
                message += f" | 🔥 Streak: {self.streak} in a row!"

            self.show_answer_feedback(True, message)

        else:
            # wrong answer: reset streak, don't change correct_count
            self.streak = 0
            correct_option = self.questions[self.current_question]["options"][correct_answer]
            message = f"Correct answer: {chr(65+correct_answer)}) {correct_option} | 💔 Streak reset!"
            self.show_answer_feedback(False, message)

    def show_inline_message(self, title, message, color):
        """Show inline message without dialog box"""
        msg_frame = tk.Frame(self.main_frame, bg=color, bd=3, relief="raised")
        msg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(
            msg_frame,
            text=title,
            font=("Arial", 18, "bold"),
            bg=color,
            fg="#0a0e27",
            padx=30,
            pady=10
        ).pack()
        
        tk.Label(
            msg_frame,
            text=message,
            font=("Arial", 14),
            bg=color,
            fg="#0a0e27",
            padx=30,
            pady=10
        ).pack()
        
        self.root.after(1600, msg_frame.destroy)

    def show_answer_feedback(self, is_correct, message):
        """Show answer feedback in the window"""
        # Create overlay
        overlay = tk.Frame(self.main_frame, bg="#000000")
        overlay.place(x=0, y=0, width=1000, height=750)
        overlay.configure(bg="#0a0e27")
        
        if is_correct:
            icon = "✓"
            title = "CORRECT!"
            bg_color = "#00ff88"
            icon_color = "#00ff88"
        else:
            icon = "✗"
            title = "INCORRECT"
            bg_color = "#ff4d4d"
            icon_color = "#ff4d4d"
        
        # Icon
        tk.Label(
            overlay,
            text=icon,
            font=("Arial", 100, "bold"),
            bg="#0a0e27",
            fg=icon_color
        ).pack(pady=80)
        
        # Title
        tk.Label(
            overlay,
            text=title,
            font=("Arial", 40, "bold"),
            bg="#0a0e27",
            fg=bg_color
        ).pack(pady=20)
        
        # Message frame
        msg_frame = tk.Frame(overlay, bg="#162447", bd=3, relief="raised")
        msg_frame.pack(pady=30, padx=100)
        
        tk.Label(
            msg_frame,
            text=message,
            font=("Arial", 16),
            bg="#162447",
            fg="#ffffff",
            padx=40,
            pady=30,
            wraplength=800,
            justify="center"
        ).pack()
        
        # Continue button
        continue_btn = tk.Button(
            overlay,
            text="CONTINUE ➜",
            font=("Arial", 18, "bold"),
            bg=bg_color,
            fg="#0a0e27",
            activebackground=bg_color,
            activeforeground="#0a0e27",
            bd=0,
            padx=50,
            pady=18,
            cursor="hand2",
            command=lambda: self.continue_after_feedback(overlay)
        )
        continue_btn.pack(pady=30)
        
        # Hover effect
        continue_btn.bind("<Enter>", lambda e: continue_btn.config(bg="#ffffff"))
        continue_btn.bind("<Leave>", lambda e: continue_btn.config(bg=bg_color))
        
    def continue_after_feedback(self, overlay):
        """Continue to next question after feedback"""
        overlay.destroy()
        self.current_question += 1
        self.show_question()

    def show_results(self):
        """Show final results"""
        self.clear_screen()
        
        total_questions = len(self.questions)

        # update high score if correct_count is higher
        if self.correct_count > self.high_score:
            self.high_score = self.correct_count
            self.save_stats()

        percentage = (self.correct_count / total_questions) * 100 if total_questions > 0 else 0
        minutes = self.total_time // 60
        seconds = self.total_time % 60

        # Performance evaluation based on percentage (correct_count)
        if percentage >= 90:
            performance = "🌟 OUTSTANDING! 🌟"
            perf_color = "#ffd700"
        elif percentage >= 70:
            performance = "🎯 EXCELLENT! 🎯"
            perf_color = "#00ff88"
        elif percentage >= 50:
            performance = "👍 GOOD JOB! 👍"
            perf_color = "#00d4ff"
        else:
            performance = "💪 KEEP TRYING! 💪"
            perf_color = "#ff6b6b"

        tk.Label(
            self.main_frame,
            text="🎉 Quiz Completed! 🎉",
            font=("Arial", 40, "bold"),
            bg="#0a0e27",
            fg="#00f5ff"
        ).pack(pady=30)

        tk.Label(
            self.main_frame,
            text=performance,
            font=("Arial", 24, "bold"),
            bg="#0a0e27",
            fg=perf_color
        ).pack(pady=10)

        # Results frame
        results_frame = tk.Frame(self.main_frame, bg="#162447", bd=4, relief="groove")
        results_frame.pack(pady=20, padx=120)

        tk.Label(
            results_frame,
            text=f"Final Score: {self.correct_count}/{total_questions}",
            font=("Arial", 26, "bold"),
            bg="#162447",
            fg="#ffd700",
            padx=40,
            pady=8
        ).pack()

        tk.Label(
            results_frame,
            text=f"Points Earned: {self.score}",
            font=("Arial", 20, "bold"),
            bg="#162447",
            fg="#00ff88",
            padx=40,
            pady=6
        ).pack()

        tk.Label(
            results_frame,
            text=f"Accuracy: {percentage:.1f}%",
            font=("Arial", 18),
            bg="#162447",
            fg="#ffffff",
            padx=40,
            pady=6
        ).pack()

        tk.Label(
            results_frame,
            text=f"⏱️ Time: {minutes}m {seconds}s",
            font=("Arial", 17),
            bg="#162447",
            fg="#ffffff",
            padx=40,
            pady=6
        ).pack()

        tk.Label(
            results_frame,
            text=f"🔥 Best Streak: {self.best_streak}",
            font=("Arial", 17),
            bg="#162447",
            fg="#ff6b6b",
            padx=40,
            pady=8
        ).pack()

        # Buttons
        btn_frame = tk.Frame(self.main_frame, bg="#0a0e27")
        btn_frame.pack(pady=20)

        play_again_btn = tk.Button(
            btn_frame,
            text="🔄 PLAY AGAIN",
            font=("Arial", 18, "bold"),
            bg="#00ff88",
            fg="#0a0e27",
            padx=40,
            pady=12,
            bd=0,
            cursor="hand2",
            command=self.create_start_screen
        )
        play_again_btn.pack(side="left", padx=12)
        
        play_again_btn.bind("<Enter>", lambda e: play_again_btn.config(bg="#00dd77"))
        play_again_btn.bind("<Leave>", lambda e: play_again_btn.config(bg="#00ff88"))

        exit_btn = tk.Button(
            btn_frame,
            text="❌ EXIT",
            font=("Arial", 18, "bold"),
            bg="#ff4d4d",
            fg="#0a0e27",
            padx=40,
            pady=12,
            bd=0,
            cursor="hand2",
            command=self.root.quit
        )
        exit_btn.pack(side="left", padx=12)
        
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg="#dd3333"))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg="#ff4d4d"))


if __name__ == "__main__":
    root = tk.Tk()
    game = QuizGame(root)
    root.mainloop()