import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode
import random
import json
import os
from datetime import datetime

class ModernButton(tk.Canvas):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text, command, width=120, height=40, 
                 bg_color="#6366f1", hover_color="#4f46e5", text_color="white"):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, relief="flat", cursor="hand2")
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        
        self.draw_button()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw_button(self, color=None):
        self.delete("all")
        color = color or self.bg_color
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        radius = 12
        
        # Draw rounded rectangle: main rect + 4 corner circles
        self.create_rectangle(radius, 0, w-radius, h, fill=color, outline="")
        self.create_rectangle(0, radius, w, h-radius, fill=color, outline="")
        self.create_oval(0, 0, radius*2, radius*2, fill=color, outline="")
        self.create_oval(w-radius*2, 0, w, radius*2, fill=color, outline="")
        self.create_oval(0, h-radius*2, radius*2, h, fill=color, outline="")
        self.create_oval(w-radius*2, h-radius*2, w, h, fill=color, outline="")
        
        self.create_text(w//2, h//2, text=self.text, fill=self.text_color,
                        font=("Segoe UI", 10, "bold"))
        
    def on_enter(self, e):
        self.draw_button(self.hover_color)
    
    def on_leave(self, e):
        self.draw_button(self.bg_color)
    
    def on_click(self, e):
        if self.command:
            self.command()

class AutoclickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Ultra Autoclicker Pro")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        
        # Stop clicking before any UI changes to prevent freeze
        self.clicking = False
        self.click_thread = None
        self.action_type = tk.StringVar(value="mouse")
        self.mouse_button = tk.StringVar(value="left")
        self.keyboard_key = tk.StringVar(value="enter")
        self.toggle_key_str = tk.StringVar(value="F6")
        self.toggle_key_obj = Key.f6
        self.cps_var = tk.StringVar(value="1000")
        self.delay_var = tk.StringVar(value="0.001")
        self.randomize_var = tk.BooleanVar(value=False)
        self.click_location = tk.StringVar(value="current")
        self.click_count = 0
        self.start_time = None
        self.listener = None
        self.capturing_hotkey = False
        
        # Premium color scheme - Modern gradient dark theme
        self.bg_gradient_start = "#0f0c29"
        self.bg_gradient_end = "#302b63"
        self.card_bg = "#1a1a2e"
        self.accent_primary = "#6366f1"
        self.accent_secondary = "#8b5cf6"
        self.success_color = "#10b981"
        self.danger_color = "#ef4444"
        self.text_primary = "#ffffff"
        self.text_secondary = "#a0a0a0"
        
        self.root.configure(bg=self.bg_gradient_start)
        self.setup_ui()
        self.start_keyboard_listener()
        self.load_settings()
        
    def setup_ui(self):
        # Header with gradient effect
        header = tk.Frame(self.root, bg=self.bg_gradient_start, height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="⚡ ULTRA AUTOCLICKER PRO",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_gradient_start,
            fg=self.accent_primary
        )
        title_label.pack(pady=20)
        
        subtitle = tk.Label(
            header,
            text="Professional Automation Tool",
            font=("Segoe UI", 10),
            bg=self.bg_gradient_start,
            fg=self.text_secondary
        )
        subtitle.pack()
        
        # Main container with scroll
        main_container = tk.Frame(self.root, bg=self.bg_gradient_start)
        main_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Action Type Card
        self.create_card(main_container, "Action Type", 0)
        type_frame = tk.Frame(self.cards[0], bg=self.card_bg)
        type_frame.pack(pady=10)
        
        mouse_btn = ModernButton(
            type_frame, "🖱️ Mouse", 
            lambda: self.set_action_type("mouse"),
            width=140, height=45, bg_color=self.accent_primary
        )
        mouse_btn.pack(side="left", padx=10)
        
        keyboard_btn = ModernButton(
            type_frame, "⌨️ Keyboard",
            lambda: self.set_action_type("keyboard"),
            width=140, height=45, bg_color=self.accent_secondary
        )
        keyboard_btn.pack(side="left", padx=10)
        
        # Mouse Options Card
        self.mouse_card = self.create_card(main_container, "Mouse Settings", 1)
        self.setup_mouse_options()
        
        # Keyboard Options Card
        self.keyboard_card = self.create_card(main_container, "Keyboard Settings", 2)
        self.setup_keyboard_options()
        
        # Advanced Settings Card
        self.create_card(main_container, "Advanced Settings", 3)
        self.setup_advanced_settings()
        
        # Statistics Card
        self.stats_card = self.create_card(main_container, "Statistics", 4)
        self.setup_statistics()
        
        # Control Panel
        self.create_control_panel(main_container)
        
        self.update_ui_state()
        
    def create_card(self, parent, title, index):
        """Create a modern card container"""
        if not hasattr(self, 'cards'):
            self.cards = []
        
        card = tk.Frame(parent, bg=self.card_bg, relief="flat", bd=0)
        card.pack(fill="x", pady=8)
        
        # Card header
        header = tk.Frame(card, bg=self.card_bg, height=35)
        header.pack(fill="x", padx=15, pady=(15, 5))
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.card_bg,
            fg=self.text_primary,
            anchor="w"
        )
        title_label.pack(side="left")
        
        # Content frame
        content = tk.Frame(card, bg=self.card_bg)
        content.pack(fill="x", padx=15, pady=(0, 15))
        
        if len(self.cards) <= index:
            self.cards.append(content)
        else:
            self.cards[index] = content
            
        return content
    
    def setup_mouse_options(self):
        """Setup mouse-specific options"""
        mouse_frame = self.mouse_card
        
        # Button selection
        btn_frame = tk.Frame(mouse_frame, bg=self.card_bg)
        btn_frame.pack(fill="x", pady=5)
        
        tk.Label(btn_frame, text="Button:", font=("Segoe UI", 10),
                bg=self.card_bg, fg=self.text_primary).pack(side="left", padx=5)
        
        for text, value in [("Left", "left"), ("Right", "right"), ("Middle", "middle")]:
            rb = tk.Radiobutton(
                btn_frame, text=text, variable=self.mouse_button, value=value,
                font=("Segoe UI", 9), bg=self.card_bg, fg=self.text_primary,
                selectcolor=self.accent_primary, activebackground=self.card_bg,
                activeforeground=self.text_primary
            )
            rb.pack(side="left", padx=15)
        
        # Click location
        loc_frame = tk.Frame(mouse_frame, bg=self.card_bg)
        loc_frame.pack(fill="x", pady=5)
        
        tk.Label(loc_frame, text="Location:", font=("Segoe UI", 10),
                bg=self.card_bg, fg=self.text_primary).pack(side="left", padx=5)
        
        for text, value in [("Current Position", "current"), ("Fixed Position", "fixed")]:
            rb = tk.Radiobutton(
                loc_frame, text=text, variable=self.click_location, value=value,
                font=("Segoe UI", 9), bg=self.card_bg, fg=self.text_primary,
                selectcolor=self.accent_primary, activebackground=self.card_bg,
                activeforeground=self.text_primary
            )
            rb.pack(side="left", padx=15)
    
    def setup_keyboard_options(self):
        """Setup keyboard-specific options"""
        kb_frame = self.keyboard_card
        
        key_frame = tk.Frame(kb_frame, bg=self.card_bg)
        key_frame.pack(fill="x", pady=5)
        
        tk.Label(key_frame, text="Key:", font=("Segoe UI", 10),
                bg=self.card_bg, fg=self.text_primary).pack(side="left", padx=5)
        
        keys = ["enter", "space", "tab", "backspace", "a", "b", "c", "d", "e", "f", 
                "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", 
                "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", 
                "6", "7", "8", "9", "up", "down", "left", "right"]
        
        self.key_combo = ttk.Combobox(
            key_frame, textvariable=self.keyboard_key, values=keys,
            state="readonly", width=18, font=("Segoe UI", 10)
        )
        self.key_combo.pack(side="left", padx=10)
        self.key_combo.current(0)
    
    def setup_advanced_settings(self):
        """Setup advanced configuration"""
        adv_frame = self.cards[3]
        
        # CPS/APS Control
        cps_frame = tk.Frame(adv_frame, bg=self.card_bg)
        cps_frame.pack(fill="x", pady=8)
        
        tk.Label(cps_frame, text="Speed (CPS/APS):", font=("Segoe UI", 10),
                bg=self.card_bg, fg=self.text_primary, width=18, anchor="w").pack(side="left")
        
        cps_entry = tk.Entry(cps_frame, textvariable=self.cps_var, 
                            font=("Segoe UI", 10), width=10, relief="flat", bd=2)
        cps_entry.pack(side="left", padx=5)
        
        tk.Label(cps_frame, text="(1-10000)", font=("Segoe UI", 9),
                bg=self.card_bg, fg=self.text_secondary).pack(side="left", padx=5)
        
        # Delay Control
        delay_frame = tk.Frame(adv_frame, bg=self.card_bg)
        delay_frame.pack(fill="x", pady=8)
        
        tk.Label(delay_frame, text="Delay (seconds):", font=("Segoe UI", 10),
                bg=self.card_bg, fg=self.text_primary, width=18, anchor="w").pack(side="left")
        
        delay_entry = tk.Entry(delay_frame, textvariable=self.delay_var,
                              font=("Segoe UI", 10), width=10, relief="flat", bd=2)
        delay_entry.pack(side="left", padx=5)
        
        # Randomization
        rand_frame = tk.Frame(adv_frame, bg=self.card_bg)
        rand_frame.pack(fill="x", pady=8)
        
        cb = tk.Checkbutton(
            rand_frame, text="Human-like Randomization (±20%)",
            variable=self.randomize_var, font=("Segoe UI", 10),
            bg=self.card_bg, fg=self.text_primary,
            selectcolor=self.accent_primary, activebackground=self.card_bg,
            activeforeground=self.text_primary
        )
        cb.pack(side="left")
        
        # Hotkey Capture
        hotkey_frame = tk.Frame(adv_frame, bg=self.card_bg)
        hotkey_frame.pack(fill="x", pady=8)
        
        tk.Label(hotkey_frame, text="Toggle Hotkey:", font=("Segoe UI", 10),
                bg=self.card_bg, fg=self.text_primary, width=18, anchor="w").pack(side="left")
        
        self.hotkey_label = tk.Label(
            hotkey_frame, text="F6", font=("Segoe UI", 10, "bold"),
            bg=self.accent_primary, fg="white", width=8, relief="flat"
        )
        self.hotkey_label.pack(side="left", padx=5)
        
        capture_btn = ModernButton(
            hotkey_frame, "Capture", self.capture_hotkey,
            width=80, height=30, bg_color=self.accent_secondary
        )
        capture_btn.pack(side="left", padx=5)
    
    def setup_statistics(self):
        """Setup statistics display"""
        stats_frame = self.stats_card
        
        self.stats_text = tk.Text(
            stats_frame, height=4, font=("Consolas", 10),
            bg="#0a0a0a", fg=self.success_color, relief="flat",
            wrap="word", state="disabled"
        )
        self.stats_text.pack(fill="x", pady=5)
        
        self.update_statistics()
    
    def create_control_panel(self, parent):
        """Create main control panel"""
        control_frame = tk.Frame(parent, bg=self.bg_gradient_start)
        control_frame.pack(fill="x", pady=15)
        
        # Status indicator
        status_container = tk.Frame(control_frame, bg=self.bg_gradient_start)
        status_container.pack(pady=10)
        
        self.status_indicator = tk.Canvas(
            status_container, width=20, height=20,
            highlightthickness=0, bg=self.bg_gradient_start
        )
        self.status_indicator.pack(side="left", padx=10)
        self.status_indicator.create_oval(5, 5, 15, 15, fill=self.danger_color, outline="")
        
        self.status_label = tk.Label(
            status_container, text="STOPPED",
            font=("Segoe UI", 14, "bold"), bg=self.bg_gradient_start,
            fg=self.danger_color
        )
        self.status_label.pack(side="left")
        
        # Main toggle button
        self.toggle_btn = ModernButton(
            control_frame, "▶ START",
            self.toggle_clicking, width=200, height=50,
            bg_color=self.success_color, hover_color="#059669"
        )
        self.toggle_btn.pack(pady=10)
        
        # Info text
        info = tk.Label(
            control_frame,
            text=f"Press {self.toggle_key_str.get()} to toggle | ESC to exit",
            font=("Segoe UI", 9), bg=self.bg_gradient_start,
            fg=self.text_secondary
        )
        info.pack(pady=5)
    
    def set_action_type(self, action_type):
        """Safely switch action type - stops clicking first"""
        if self.clicking:
            self.toggle_clicking()  # Stop first
        
        self.action_type.set(action_type)
        self.update_ui_state()
    
    def update_ui_state(self):
        """Update UI based on current action type"""
        if self.action_type.get() == "mouse":
            self.mouse_card.pack(fill="x", pady=8)
            self.keyboard_card.pack_forget()
        else:
            self.mouse_card.pack_forget()
            self.keyboard_card.pack(fill="x", pady=8)
    
    def capture_hotkey(self):
        """Capture a new hotkey"""
        self.capturing_hotkey = True
        self.hotkey_label.config(text="Press any key...", bg=self.danger_color)
        
        def capture_thread():
            def on_press(key):
                if self.capturing_hotkey:
                    try:
                        if hasattr(key, 'name'):
                            key_name = key.name.upper()
                        else:
                            key_name = key.char.upper() if key.char else str(key).upper()
                        
                        self.root.after(0, lambda: self.set_hotkey(key, key_name))
                        return False
                    except:
                        pass
            
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()
        
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def set_hotkey(self, key_obj, key_name):
        """Set the captured hotkey"""
        self.toggle_key_obj = key_obj
        self.toggle_key_str.set(key_name)
        self.hotkey_label.config(text=key_name, bg=self.accent_primary)
        self.capturing_hotkey = False
        self.save_settings()
    
    def get_key_from_string(self, key_str):
        """Convert string to pynput Key or KeyCode"""
        key_map = {
            "enter": Key.enter, "space": Key.space, "tab": Key.tab,
            "backspace": Key.backspace, "delete": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
        }
        
        if key_str.lower() in key_map:
            return key_map[key_str.lower()]
        elif len(key_str) == 1:
            return KeyCode.from_char(key_str.lower())
        return KeyCode.from_char(key_str.lower())
    
    def calculate_delay(self):
        """Calculate delay with optional randomization"""
        try:
            cps = float(self.cps_var.get())
            if cps <= 0:
                cps = 1000
            base_delay = 1.0 / cps
        except:
            base_delay = 0.001
        
        if self.randomize_var.get():
            variation = random.uniform(-0.2, 0.2)
            delay = base_delay * (1 + variation)
            return max(0.0001, delay)
        return base_delay
    
    def action_loop(self):
        """Main action loop with advanced features"""
        if self.action_type.get() == "mouse":
            mouse_controller = mouse.Controller()
            button_map = {
                "left": mouse.Button.left,
                "right": mouse.Button.right,
                "middle": mouse.Button.middle
            }
            button = button_map[self.mouse_button.get()]
            
            # Get initial position if fixed
            if self.click_location.get() == "fixed":
                initial_pos = mouse_controller.position
            
            while self.clicking:
                if self.click_location.get() == "fixed":
                    mouse_controller.position = initial_pos
                
                mouse_controller.click(button)
                self.click_count += 1
                self.root.after(0, self.update_statistics)
                time.sleep(self.calculate_delay())
        else:
            keyboard_controller = keyboard.Controller()
            key = self.get_key_from_string(self.keyboard_key.get())
            
            while self.clicking:
                keyboard_controller.press(key)
                keyboard_controller.release(key)
                self.click_count += 1
                self.root.after(0, self.update_statistics)
                time.sleep(self.calculate_delay())
    
    def toggle_clicking(self):
        """Toggle clicking on/off"""
        if not self.clicking:
            self.clicking = True
            self.click_count = 0
            self.start_time = time.time()
            self.click_thread = threading.Thread(target=self.action_loop, daemon=True)
            self.click_thread.start()
            
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(5, 5, 15, 15, fill=self.success_color, outline="")
            self.status_label.config(text="RUNNING", fg=self.success_color)
            self.toggle_btn.text = "⏸ STOP"
            self.toggle_btn.bg_color = self.danger_color
            self.toggle_btn.hover_color = "#dc2626"
            self.toggle_btn.draw_button(self.danger_color)
        else:
            self.clicking = False
            self.status_indicator.delete("all")
            self.status_indicator.create_oval(5, 5, 15, 15, fill=self.danger_color, outline="")
            self.status_label.config(text="STOPPED", fg=self.danger_color)
            self.toggle_btn.text = "▶ START"
            self.toggle_btn.bg_color = self.success_color
            self.toggle_btn.hover_color = "#059669"
            self.toggle_btn.draw_button(self.success_color)
            self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        
        if self.start_time and self.clicking:
            elapsed = time.time() - self.start_time
            cps = self.click_count / elapsed if elapsed > 0 else 0
            stats = f"Actions: {self.click_count:,} | Time: {elapsed:.1f}s | Rate: {cps:.1f} CPS/APS"
        elif self.click_count > 0:
            stats = f"Last Session: {self.click_count:,} actions"
        else:
            stats = "Ready to start..."
        
        self.stats_text.insert("1.0", stats)
        self.stats_text.config(state="disabled")
    
    def on_key_press(self, key):
        """Handle keyboard shortcuts"""
        try:
            if self.capturing_hotkey:
                return
            
            if key == self.toggle_key_obj:
                self.root.after(0, self.toggle_clicking)
            elif key == Key.esc:
                self.root.after(0, self.on_closing)
                return False
        except:
            pass
    
    def start_keyboard_listener(self):
        """Start listening for keyboard shortcuts"""
        def listener_thread():
            with keyboard.Listener(on_press=self.on_key_press) as listener:
                self.listener = listener
                listener.join()
        
        thread = threading.Thread(target=listener_thread, daemon=True)
        thread.start()
    
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "action_type": self.action_type.get(),
            "mouse_button": self.mouse_button.get(),
            "keyboard_key": self.keyboard_key.get(),
            "cps": self.cps_var.get(),
            "delay": self.delay_var.get(),
            "randomize": self.randomize_var.get(),
            "click_location": self.click_location.get()
        }
        try:
            with open("autoclicker_settings.json", "w") as f:
                json.dump(settings, f)
        except:
            pass
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("autoclicker_settings.json"):
                with open("autoclicker_settings.json", "r") as f:
                    settings = json.load(f)
                    self.action_type.set(settings.get("action_type", "mouse"))
                    self.mouse_button.set(settings.get("mouse_button", "left"))
                    self.keyboard_key.set(settings.get("keyboard_key", "enter"))
                    self.cps_var.set(settings.get("cps", "1000"))
                    self.delay_var.set(settings.get("delay", "0.001"))
                    self.randomize_var.set(settings.get("randomize", False))
                    self.click_location.set(settings.get("click_location", "current"))
                    self.update_ui_state()
        except:
            pass
    
    def on_closing(self):
        """Handle window closing"""
        self.clicking = False
        self.save_settings()
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoclickerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
