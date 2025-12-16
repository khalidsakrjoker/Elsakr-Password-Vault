"""
Elsakr Password Vault - Premium Edition
Complete password management: generate, analyze, store, and organize passwords.
Modern Dark Theme with Premium UI - Security First
"""

import os
import sys
import json
import string
import secrets
import hashlib
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    from zxcvbn import zxcvbn
    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False

from PIL import Image, ImageTk


class Colors:
    """Premium dark theme colors."""
    BG_DARK = "#0a0a0f"
    BG_CARD = "#12121a"
    BG_CARD_HOVER = "#1a1a25"
    BG_INPUT = "#1e1e2e"
    
    PRIMARY = "#8b5cf6"  # Purple
    PRIMARY_HOVER = "#a78bfa"
    PRIMARY_DARK = "#7c3aed"
    
    SECONDARY = "#22d3ee"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a1a1aa"
    TEXT_MUTED = "#71717a"
    
    BORDER = "#27272a"
    BORDER_FOCUS = "#8b5cf6"
    
    # Password strength colors
    STRENGTH_WEAK = "#ef4444"
    STRENGTH_FAIR = "#f59e0b"
    STRENGTH_GOOD = "#22d3ee"
    STRENGTH_STRONG = "#10b981"


class PremiumButton(tk.Canvas):
    """Custom premium button."""
    
    def __init__(self, parent, text, command=None, width=200, height=45, 
                 primary=True, color=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=Colors.BG_CARD, highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.primary = primary
        self.custom_color = color
        self.hovered = False
        self.enabled = True
        
        self.draw_button()
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw_button(self):
        self.delete("all")
        
        if not self.enabled:
            bg_color = Colors.BG_INPUT
            text_color = Colors.TEXT_MUTED
        elif self.custom_color:
            bg_color = self.custom_color
            text_color = Colors.TEXT_PRIMARY
        elif self.primary:
            bg_color = Colors.PRIMARY_HOVER if self.hovered else Colors.PRIMARY
            text_color = Colors.TEXT_PRIMARY
        else:
            bg_color = Colors.BG_CARD_HOVER if self.hovered else Colors.BG_INPUT
            text_color = Colors.TEXT_SECONDARY
        
        radius = 10
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                  radius, fill=bg_color, outline="")
        self.create_text(self.width//2, self.height//2, 
                        text=self.text, fill=text_color,
                        font=("Segoe UI Semibold", 11))
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        if self.enabled:
            self.hovered = True
            self.draw_button()
            self.config(cursor="hand2")
        
    def on_leave(self, event):
        self.hovered = False
        self.draw_button()
        
    def on_click(self, event):
        if self.command and self.enabled:
            self.command()
            
    def set_enabled(self, enabled):
        self.enabled = enabled
        self.draw_button()


class PremiumCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_CARD, **kwargs)
        self.config(highlightbackground=Colors.BORDER, highlightthickness=1)


class PasswordGenerator:
    """Password generation logic."""
    
    @staticmethod
    def generate(length=16, uppercase=True, lowercase=True, digits=True, 
                 symbols=True, exclude_ambiguous=False, exclude_chars=""):
        chars = ""
        
        if uppercase:
            chars += string.ascii_uppercase
        if lowercase:
            chars += string.ascii_lowercase
        if digits:
            chars += string.digits
        if symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
        if exclude_ambiguous:
            ambiguous = "0O1lI"
            chars = ''.join(c for c in chars if c not in ambiguous)
            
        for c in exclude_chars:
            chars = chars.replace(c, "")
            
        if not chars:
            return ""
            
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_passphrase(words=4, separator="-"):
        # Simple word list for passphrases
        word_list = [
            "apple", "banana", "cherry", "dragon", "eagle", "forest", "galaxy",
            "harbor", "island", "jungle", "kingdom", "lemon", "mountain", "nebula",
            "ocean", "phoenix", "quantum", "rainbow", "sunset", "thunder", "universe",
            "velvet", "whisper", "xenon", "yellow", "zenith", "aurora", "breeze",
            "crystal", "diamond", "ember", "flame", "glacier", "horizon", "ivory"
        ]
        return separator.join(secrets.choice(word_list) for _ in range(words))


class PasswordAnalyzer:
    """Password strength analysis."""
    
    @staticmethod
    def analyze(password):
        if not password:
            return {"score": 0, "strength": "None", "feedback": [], "crack_time": "instant"}
            
        if ZXCVBN_AVAILABLE:
            result = zxcvbn(password)
            score = result['score']
            crack_time = result['crack_times_display']['offline_slow_hashing_1e4_per_second']
            feedback = result['feedback']['suggestions']
            
            strength_map = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}
            return {
                "score": score,
                "strength": strength_map[score],
                "feedback": feedback,
                "crack_time": crack_time
            }
        else:
            # Basic analysis fallback
            score = 0
            feedback = []
            
            if len(password) >= 8: score += 1
            else: feedback.append("Use at least 8 characters")
            
            if len(password) >= 12: score += 1
            
            if any(c.isupper() for c in password): score += 0.5
            else: feedback.append("Add uppercase letters")
            
            if any(c.islower() for c in password): score += 0.5
            else: feedback.append("Add lowercase letters")
            
            if any(c.isdigit() for c in password): score += 0.5
            else: feedback.append("Add numbers")
            
            if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 0.5
            else: feedback.append("Add symbols")
            
            score = min(int(score), 4)
            strength_map = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}
            
            return {
                "score": score,
                "strength": strength_map[score],
                "feedback": feedback,
                "crack_time": "Unknown"
            }


class VaultDatabase:
    """Encrypted password storage."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.fernet = None
        self.conn = None
        
    def initialize(self, master_password):
        """Initialize database with master password."""
        if not CRYPTO_AVAILABLE:
            raise Exception("cryptography library not installed")
            
        # Derive key from master password
        salt = b'elsakr_password_vault_salt_2024'  # In production, use random salt stored separately
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.fernet = Fernet(key)
        
        # Connect to database
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        
    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT,
                password_encrypted TEXT NOT NULL,
                url TEXT,
                notes TEXT,
                category TEXT DEFAULT 'General',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Insert default categories
        default_cats = ['General', 'Work', 'Social', 'Finance', 'Shopping', 'Email']
        for cat in default_cats:
            try:
                cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
            except:
                pass
        self.conn.commit()
        
    def add_password(self, title, username, password, url="", notes="", category="General"):
        """Add a new password entry."""
        encrypted = self.fernet.encrypt(password.encode()).decode()
        now = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO passwords (title, username, password_encrypted, url, notes, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, username, encrypted, url, notes, category, now, now))
        self.conn.commit()
        return cursor.lastrowid
        
    def get_all_passwords(self):
        """Get all password entries (decrypted)."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM passwords ORDER BY title')
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            try:
                decrypted = self.fernet.decrypt(row[3].encode()).decode()
                result.append({
                    'id': row[0],
                    'title': row[1],
                    'username': row[2],
                    'password': decrypted,
                    'url': row[4],
                    'notes': row[5],
                    'category': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            except:
                pass
        return result
        
    def delete_password(self, id):
        """Delete a password entry."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM passwords WHERE id = ?', (id,))
        self.conn.commit()
        
    def get_categories(self):
        """Get all categories."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM categories ORDER BY name')
        return [row[0] for row in cursor.fetchall()]
        
    def close(self):
        if self.conn:
            self.conn.close()


class PasswordVault:
    """Main application class."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Elsakr Password Vault")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 700)
        self.root.configure(bg=Colors.BG_DARK)
        
        self.set_window_icon()
        self.load_logo()
        
        # State
        self.vault = None
        self.is_locked = True
        self.clipboard_timer = None
        
        # Show unlock screen first
        self.show_unlock_screen()
        
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
        
    def set_window_icon(self):
        try:
            icon_path = self.resource_path(os.path.join("assets", "fav.ico"))
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
            
    def load_logo(self):
        self.logo_photo = None
        try:
            logo_path = self.resource_path(os.path.join("assets", "Sakr-logo.png"))
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
                logo.thumbnail((50, 50), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo)
        except:
            pass
            
    def show_unlock_screen(self):
        """Show the master password unlock screen."""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Center frame
        center_frame = tk.Frame(self.root, bg=Colors.BG_DARK)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        if self.logo_photo:
            tk.Label(center_frame, image=self.logo_photo, bg=Colors.BG_DARK).pack(pady=(0, 20))
        
        # Title
        tk.Label(center_frame, text="🔐 Password Vault",
                font=("Segoe UI Bold", 28), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_DARK).pack(pady=(0, 10))
        
        tk.Label(center_frame, text="Enter your master password to unlock",
                font=("Segoe UI", 12), fg=Colors.TEXT_MUTED,
                bg=Colors.BG_DARK).pack(pady=(0, 30))
        
        # Password entry
        self.master_entry = tk.Entry(center_frame, font=("Segoe UI", 14),
                                     bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                                     insertbackground=Colors.TEXT_PRIMARY,
                                     relief='flat', show="•", width=30,
                                     highlightthickness=2,
                                     highlightbackground=Colors.BORDER,
                                     highlightcolor=Colors.PRIMARY)
        self.master_entry.pack(ipady=12, pady=(0, 20))
        self.master_entry.focus()
        self.master_entry.bind("<Return>", lambda e: self.unlock_vault())
        
        # Unlock button
        PremiumButton(center_frame, text="🔓 Unlock Vault",
                     command=self.unlock_vault, width=300, height=50).pack(pady=(0, 15))
        
        # Create new vault option
        tk.Label(center_frame, text="or", font=("Segoe UI", 10),
                fg=Colors.TEXT_MUTED, bg=Colors.BG_DARK).pack(pady=5)
        
        create_btn = tk.Label(center_frame, text="Create New Vault",
                             font=("Segoe UI", 11), fg=Colors.PRIMARY,
                             bg=Colors.BG_DARK, cursor="hand2")
        create_btn.pack()
        create_btn.bind("<Button-1>", lambda e: self.create_new_vault())
        
        # Warning if crypto not available
        if not CRYPTO_AVAILABLE:
            tk.Label(center_frame, text="⚠️ cryptography library not installed!\nPasswords won't be encrypted.",
                    font=("Segoe UI", 10), fg=Colors.WARNING,
                    bg=Colors.BG_DARK, justify="center").pack(pady=(20, 0))
            
    def unlock_vault(self):
        """Unlock the vault with master password."""
        password = self.master_entry.get()
        
        if not password:
            messagebox.showwarning("Error", "Please enter your master password")
            return
            
        try:
            db_path = os.path.join(os.path.dirname(__file__), "vault.db")
            self.vault = VaultDatabase(db_path)
            self.vault.initialize(password)
            self.is_locked = False
            self.show_main_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unlock vault:\n{str(e)}")
            
    def create_new_vault(self):
        """Create a new vault with a master password."""
        # Simple dialog for new password
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Vault")
        dialog.geometry("400x300")
        dialog.configure(bg=Colors.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Create Master Password",
                font=("Segoe UI Bold", 16), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_DARK).pack(pady=(30, 20))
        
        tk.Label(dialog, text="Password:",
                font=("Segoe UI", 10), fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_DARK).pack(anchor="w", padx=40)
        
        pass1 = tk.Entry(dialog, font=("Segoe UI", 12), show="•",
                        bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                        insertbackground=Colors.TEXT_PRIMARY, relief='flat')
        pass1.pack(fill="x", padx=40, ipady=8, pady=(5, 15))
        
        tk.Label(dialog, text="Confirm Password:",
                font=("Segoe UI", 10), fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_DARK).pack(anchor="w", padx=40)
        
        pass2 = tk.Entry(dialog, font=("Segoe UI", 12), show="•",
                        bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                        insertbackground=Colors.TEXT_PRIMARY, relief='flat')
        pass2.pack(fill="x", padx=40, ipady=8, pady=(5, 20))
        
        def create():
            if pass1.get() != pass2.get():
                messagebox.showerror("Error", "Passwords don't match!")
                return
            if len(pass1.get()) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters!")
                return
                
            dialog.destroy()
            self.master_entry.delete(0, tk.END)
            self.master_entry.insert(0, pass1.get())
            self.unlock_vault()
        
        PremiumButton(dialog, text="Create Vault", command=create,
                     width=150, height=40).pack()
        
    def show_main_ui(self):
        """Show the main vault UI."""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        main = tk.Frame(self.root, bg=Colors.BG_DARK)
        main.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Header
        self.create_header(main)
        
        # Notebook for tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=Colors.BG_DARK, borderwidth=0)
        style.configure('TNotebook.Tab', background=Colors.BG_CARD, 
                       foreground=Colors.TEXT_SECONDARY, padding=[20, 10],
                       font=('Segoe UI', 10))
        style.map('TNotebook.Tab', background=[('selected', Colors.BG_DARK)],
                 foreground=[('selected', Colors.TEXT_PRIMARY)])
        
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Tabs
        self.create_generator_tab()
        self.create_analyzer_tab()
        self.create_vault_tab()
        
    def create_header(self, parent):
        header = tk.Frame(parent, bg=Colors.BG_DARK)
        header.pack(fill=tk.X)
        
        title_frame = tk.Frame(header, bg=Colors.BG_DARK)
        title_frame.pack(side=tk.LEFT)
        
        if self.logo_photo:
            tk.Label(title_frame, image=self.logo_photo, bg=Colors.BG_DARK).pack(side=tk.LEFT, padx=(0, 15))
        
        title_text = tk.Frame(title_frame, bg=Colors.BG_DARK)
        title_text.pack(side=tk.LEFT)
        
        tk.Label(title_text, text="Password Vault", 
                font=("Segoe UI Bold", 22), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_DARK).pack(anchor=tk.W)
        tk.Label(title_text, text="Generate, Analyze & Store Passwords Securely",
                font=("Segoe UI", 10), fg=Colors.TEXT_MUTED,
                bg=Colors.BG_DARK).pack(anchor=tk.W)
        
        # Lock button
        lock_btn = tk.Label(header, text="🔒 Lock", font=("Segoe UI", 11),
                           fg=Colors.TEXT_SECONDARY, bg=Colors.BG_DARK, cursor="hand2")
        lock_btn.pack(side=tk.RIGHT)
        lock_btn.bind("<Button-1>", lambda e: self.lock_vault())
        
    def lock_vault(self):
        """Lock the vault."""
        if self.vault:
            self.vault.close()
            self.vault = None
        self.is_locked = True
        self.show_unlock_screen()
        
    def create_generator_tab(self):
        """Create password generator tab."""
        tab = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(tab, text="🔑 Generator")
        
        content = tk.Frame(tab, bg=Colors.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left side - Options
        left = tk.Frame(content, bg=Colors.BG_DARK, width=350)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left.pack_propagate(False)
        
        options_card = PremiumCard(left, padx=20, pady=20)
        options_card.pack(fill=tk.X)
        
        tk.Label(options_card, text="⚙️ Options",
                font=("Segoe UI Semibold", 13), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(0, 15))
        
        # Length slider
        tk.Label(options_card, text="Length",
                font=("Segoe UI", 10), fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W)
        
        length_frame = tk.Frame(options_card, bg=Colors.BG_CARD)
        length_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.length_var = tk.IntVar(value=16)
        self.length_slider = ttk.Scale(length_frame, from_=8, to=64,
                                       variable=self.length_var, orient="horizontal",
                                       command=self.update_generator_preview)
        self.length_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.length_label = tk.Label(length_frame, text="16",
                                    font=("Segoe UI Bold", 12), fg=Colors.PRIMARY,
                                    bg=Colors.BG_CARD, width=4)
        self.length_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Character options
        self.gen_uppercase = tk.BooleanVar(value=True)
        self.gen_lowercase = tk.BooleanVar(value=True)
        self.gen_digits = tk.BooleanVar(value=True)
        self.gen_symbols = tk.BooleanVar(value=True)
        self.gen_ambiguous = tk.BooleanVar(value=False)
        
        options = [
            ("Uppercase (A-Z)", self.gen_uppercase),
            ("Lowercase (a-z)", self.gen_lowercase),
            ("Digits (0-9)", self.gen_digits),
            ("Symbols (!@#$...)", self.gen_symbols),
            ("Exclude Ambiguous (0O1lI)", self.gen_ambiguous),
        ]
        
        for text, var in options:
            cb = tk.Checkbutton(options_card, text=text, variable=var,
                               font=("Segoe UI", 10), fg=Colors.TEXT_PRIMARY,
                               bg=Colors.BG_CARD, selectcolor=Colors.BG_INPUT,
                               activebackground=Colors.BG_CARD,
                               activeforeground=Colors.TEXT_PRIMARY,
                               command=self.update_generator_preview)
            cb.pack(anchor=tk.W, pady=2)
        
        # Passphrase option
        tk.Label(options_card, text="",
                bg=Colors.BG_CARD).pack(pady=5)
        
        PremiumButton(options_card, text="📝 Generate Passphrase",
                     command=self.generate_passphrase, width=280, height=40,
                     primary=False).pack()
        
        # Right side - Output
        right = tk.Frame(content, bg=Colors.BG_DARK)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        output_card = PremiumCard(right, padx=25, pady=25)
        output_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(output_card, text="🔐 Generated Password",
                font=("Segoe UI Semibold", 13), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(0, 20))
        
        # Password display
        self.gen_password_var = tk.StringVar()
        password_frame = tk.Frame(output_card, bg=Colors.BG_INPUT, 
                                  highlightbackground=Colors.BORDER, highlightthickness=1)
        password_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.gen_password_entry = tk.Entry(password_frame, textvariable=self.gen_password_var,
                                           font=("Consolas", 16), bg=Colors.BG_INPUT,
                                           fg=Colors.TEXT_PRIMARY, relief='flat',
                                           insertbackground=Colors.TEXT_PRIMARY)
        self.gen_password_entry.pack(fill=tk.X, padx=15, pady=12)
        
        # Buttons
        btn_frame = tk.Frame(output_card, bg=Colors.BG_CARD)
        btn_frame.pack(fill=tk.X, pady=(0, 20))
        
        PremiumButton(btn_frame, text="🔄 Generate",
                     command=self.generate_password, width=150, height=45).pack(side=tk.LEFT, padx=(0, 10))
        
        PremiumButton(btn_frame, text="📋 Copy",
                     command=self.copy_generated, width=120, height=45,
                     primary=False).pack(side=tk.LEFT, padx=(0, 10))
        
        PremiumButton(btn_frame, text="💾 Save to Vault",
                     command=self.save_generated_to_vault, width=150, height=45,
                     color=Colors.SUCCESS).pack(side=tk.LEFT)
        
        # Strength meter
        tk.Label(output_card, text="Strength",
                font=("Segoe UI", 10), fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W)
        
        self.gen_strength_bar = tk.Canvas(output_card, height=8, 
                                          bg=Colors.BG_INPUT, highlightthickness=0)
        self.gen_strength_bar.pack(fill=tk.X, pady=(5, 10))
        
        self.gen_strength_label = tk.Label(output_card, text="",
                                           font=("Segoe UI", 11), fg=Colors.TEXT_MUTED,
                                           bg=Colors.BG_CARD)
        self.gen_strength_label.pack(anchor=tk.W)
        
        # Generate initial password
        self.generate_password()
        
    def update_generator_preview(self, *args):
        self.length_label.config(text=str(self.length_var.get()))
        
    def generate_password(self):
        password = PasswordGenerator.generate(
            length=self.length_var.get(),
            uppercase=self.gen_uppercase.get(),
            lowercase=self.gen_lowercase.get(),
            digits=self.gen_digits.get(),
            symbols=self.gen_symbols.get(),
            exclude_ambiguous=self.gen_ambiguous.get()
        )
        self.gen_password_var.set(password)
        self.update_gen_strength(password)
        
    def generate_passphrase(self):
        passphrase = PasswordGenerator.generate_passphrase(words=4)
        self.gen_password_var.set(passphrase)
        self.update_gen_strength(passphrase)
        
    def update_gen_strength(self, password):
        result = PasswordAnalyzer.analyze(password)
        score = result['score']
        
        # Update bar
        self.gen_strength_bar.delete("all")
        width = self.gen_strength_bar.winfo_width()
        if width < 10:
            width = 400
        fill_width = width * ((score + 1) / 5)
        
        colors = [Colors.STRENGTH_WEAK, Colors.STRENGTH_WEAK, Colors.STRENGTH_FAIR,
                  Colors.STRENGTH_GOOD, Colors.STRENGTH_STRONG]
        color = colors[score]
        
        self.gen_strength_bar.create_rectangle(0, 0, fill_width, 8, fill=color, outline="")
        self.gen_strength_label.config(text=f"{result['strength']} • Crack time: {result['crack_time']}",
                                       fg=color)
        
    def copy_generated(self):
        password = self.gen_password_var.get()
        if password and CLIPBOARD_AVAILABLE:
            pyperclip.copy(password)
            self.gen_strength_label.config(text="✓ Copied! (Auto-clears in 30s)")
            
            # Clear clipboard after 30 seconds
            if self.clipboard_timer:
                self.root.after_cancel(self.clipboard_timer)
            self.clipboard_timer = self.root.after(30000, self.clear_clipboard)
            
    def clear_clipboard(self):
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy("")
            
    def save_generated_to_vault(self):
        password = self.gen_password_var.get()
        if not password:
            return
        self.show_save_dialog(password)
        
    def create_analyzer_tab(self):
        """Create password analyzer tab."""
        tab = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(tab, text="📊 Analyzer")
        
        content = tk.Frame(tab, bg=Colors.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        card = PremiumCard(content, padx=30, pady=30)
        card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="🔍 Password Strength Analyzer",
                font=("Segoe UI Semibold", 16), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(card, text="Enter a password to analyze:",
                font=("Segoe UI", 11), fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W)
        
        # Password entry
        self.analyze_var = tk.StringVar()
        self.analyze_var.trace_add("write", self.on_analyze_change)
        
        entry_frame = tk.Frame(card, bg=Colors.BG_INPUT,
                              highlightbackground=Colors.BORDER, highlightthickness=1)
        entry_frame.pack(fill=tk.X, pady=(10, 20))
        
        self.analyze_entry = tk.Entry(entry_frame, textvariable=self.analyze_var,
                                      font=("Consolas", 16), bg=Colors.BG_INPUT,
                                      fg=Colors.TEXT_PRIMARY, relief='flat',
                                      insertbackground=Colors.TEXT_PRIMARY)
        self.analyze_entry.pack(fill=tk.X, padx=15, pady=12)
        
        # Show/hide password
        self.show_password_var = tk.BooleanVar(value=True)
        show_cb = tk.Checkbutton(card, text="Show password", variable=self.show_password_var,
                                 font=("Segoe UI", 10), fg=Colors.TEXT_SECONDARY,
                                 bg=Colors.BG_CARD, selectcolor=Colors.BG_INPUT,
                                 command=self.toggle_analyze_visibility)
        show_cb.pack(anchor=tk.W)
        
        # Results section
        results_frame = tk.Frame(card, bg=Colors.BG_CARD)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Strength bar
        tk.Label(results_frame, text="Strength",
                font=("Segoe UI Semibold", 12), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W)
        
        self.analyze_bar = tk.Canvas(results_frame, height=12, 
                                     bg=Colors.BG_INPUT, highlightthickness=0)
        self.analyze_bar.pack(fill=tk.X, pady=(8, 5))
        
        self.analyze_strength_label = tk.Label(results_frame, text="—",
                                               font=("Segoe UI Bold", 14),
                                               fg=Colors.TEXT_MUTED, bg=Colors.BG_CARD)
        self.analyze_strength_label.pack(anchor=tk.W)
        
        self.analyze_time_label = tk.Label(results_frame, text="",
                                           font=("Segoe UI", 11),
                                           fg=Colors.TEXT_SECONDARY, bg=Colors.BG_CARD)
        self.analyze_time_label.pack(anchor=tk.W, pady=(5, 20))
        
        # Feedback
        tk.Label(results_frame, text="Suggestions",
                font=("Segoe UI Semibold", 12), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_CARD).pack(anchor=tk.W)
        
        self.analyze_feedback = tk.Label(results_frame, text="Enter a password to analyze",
                                         font=("Segoe UI", 11), fg=Colors.TEXT_MUTED,
                                         bg=Colors.BG_CARD, justify=tk.LEFT, wraplength=500)
        self.analyze_feedback.pack(anchor=tk.W, pady=(5, 0))
        
    def on_analyze_change(self, *args):
        password = self.analyze_var.get()
        result = PasswordAnalyzer.analyze(password)
        
        score = result['score']
        
        # Update bar
        self.analyze_bar.delete("all")
        width = self.analyze_bar.winfo_width()
        if width < 10:
            width = 500
        fill_width = width * ((score + 1) / 5)
        
        colors = [Colors.STRENGTH_WEAK, Colors.STRENGTH_WEAK, Colors.STRENGTH_FAIR,
                  Colors.STRENGTH_GOOD, Colors.STRENGTH_STRONG]
        color = colors[score] if password else Colors.TEXT_MUTED
        
        self.analyze_bar.create_rectangle(0, 0, fill_width, 12, fill=color, outline="")
        self.analyze_strength_label.config(text=result['strength'], fg=color)
        self.analyze_time_label.config(text=f"Crack time: {result['crack_time']}")
        
        if result['feedback']:
            self.analyze_feedback.config(text="• " + "\n• ".join(result['feedback']))
        else:
            self.analyze_feedback.config(text="No suggestions - password looks good!" if password else "Enter a password to analyze")
            
    def toggle_analyze_visibility(self):
        if self.show_password_var.get():
            self.analyze_entry.config(show="")
        else:
            self.analyze_entry.config(show="•")
        
    def create_vault_tab(self):
        """Create password vault tab."""
        tab = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.notebook.add(tab, text="🔒 My Vault")
        
        content = tk.Frame(tab, bg=Colors.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(content, bg=Colors.BG_DARK)
        header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header, text="💼 Saved Passwords",
                font=("Segoe UI Semibold", 14), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_DARK).pack(side=tk.LEFT)
        
        PremiumButton(header, text="➕ Add New",
                     command=lambda: self.show_save_dialog(),
                     width=120, height=35).pack(side=tk.RIGHT)
        
        # Password list
        list_card = PremiumCard(content, padx=0, pady=0)
        list_card.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        style = ttk.Style()
        style.configure("Vault.Treeview", background=Colors.BG_CARD,
                       foreground=Colors.TEXT_PRIMARY, fieldbackground=Colors.BG_CARD,
                       font=('Segoe UI', 10))
        style.configure("Vault.Treeview.Heading", background=Colors.BG_INPUT,
                       foreground=Colors.TEXT_SECONDARY, font=('Segoe UI Semibold', 10))
        
        columns = ("Title", "Username", "Category", "Created")
        self.vault_tree = ttk.Treeview(list_card, columns=columns, show="headings",
                                       style="Vault.Treeview")
        
        self.vault_tree.heading("Title", text="Title")
        self.vault_tree.heading("Username", text="Username")
        self.vault_tree.heading("Category", text="Category")
        self.vault_tree.heading("Created", text="Created")
        
        self.vault_tree.column("Title", width=200)
        self.vault_tree.column("Username", width=200)
        self.vault_tree.column("Category", width=100)
        self.vault_tree.column("Created", width=150)
        
        scrollbar = ttk.Scrollbar(list_card, orient="vertical", command=self.vault_tree.yview)
        self.vault_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vault_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.vault_tree.bind("<Double-1>", self.on_vault_double_click)
        
        # Load passwords
        self.refresh_vault_list()
        
    def refresh_vault_list(self):
        """Refresh the vault password list."""
        for item in self.vault_tree.get_children():
            self.vault_tree.delete(item)
            
        if self.vault:
            passwords = self.vault.get_all_passwords()
            for p in passwords:
                created = p['created_at'][:10] if p['created_at'] else ""
                self.vault_tree.insert("", "end", iid=p['id'],
                                       values=(p['title'], p['username'], 
                                              p['category'], created))
                                              
    def on_vault_double_click(self, event):
        """Handle double-click on vault item."""
        selection = self.vault_tree.selection()
        if selection:
            item_id = selection[0]
            passwords = self.vault.get_all_passwords()
            for p in passwords:
                if str(p['id']) == str(item_id):
                    self.show_password_details(p)
                    break
                    
    def show_password_details(self, password_data):
        """Show password details dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Details")
        dialog.geometry("450x400")
        dialog.configure(bg=Colors.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=password_data['title'],
                font=("Segoe UI Bold", 18), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_DARK).pack(pady=(25, 20))
        
        info_frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        info_frame.pack(fill=tk.X, padx=30)
        
        fields = [
            ("Username", password_data['username']),
            ("Password", password_data['password']),
            ("URL", password_data['url']),
            ("Category", password_data['category']),
        ]
        
        for label, value in fields:
            row = tk.Frame(info_frame, bg=Colors.BG_DARK)
            row.pack(fill=tk.X, pady=5)
            
            tk.Label(row, text=label + ":", font=("Segoe UI", 10),
                    fg=Colors.TEXT_MUTED, bg=Colors.BG_DARK, width=12,
                    anchor="w").pack(side=tk.LEFT)
            
            if label == "Password":
                tk.Label(row, text="•" * len(value) if value else "",
                        font=("Segoe UI", 11), fg=Colors.TEXT_PRIMARY,
                        bg=Colors.BG_DARK).pack(side=tk.LEFT)
            else:
                tk.Label(row, text=value or "—", font=("Segoe UI", 11),
                        fg=Colors.TEXT_PRIMARY, bg=Colors.BG_DARK).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        btn_frame.pack(pady=30)
        
        def copy_password():
            if CLIPBOARD_AVAILABLE:
                pyperclip.copy(password_data['password'])
                messagebox.showinfo("Copied", "Password copied to clipboard!")
                
        def delete_password():
            if messagebox.askyesno("Delete", f"Delete '{password_data['title']}'?"):
                self.vault.delete_password(password_data['id'])
                self.refresh_vault_list()
                dialog.destroy()
        
        PremiumButton(btn_frame, text="📋 Copy Password",
                     command=copy_password, width=150, height=40).pack(side=tk.LEFT, padx=5)
        
        PremiumButton(btn_frame, text="🗑️ Delete",
                     command=delete_password, width=100, height=40,
                     color=Colors.ERROR).pack(side=tk.LEFT, padx=5)
        
    def show_save_dialog(self, password=""):
        """Show dialog to save a new password."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Password")
        dialog.geometry("450x450")
        dialog.configure(bg=Colors.BG_DARK)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="💾 Save Password",
                font=("Segoe UI Bold", 18), fg=Colors.TEXT_PRIMARY,
                bg=Colors.BG_DARK).pack(pady=(25, 20))
        
        form = tk.Frame(dialog, bg=Colors.BG_DARK)
        form.pack(fill=tk.X, padx=30)
        
        # Title
        tk.Label(form, text="Title *", font=("Segoe UI", 10),
                fg=Colors.TEXT_SECONDARY, bg=Colors.BG_DARK).pack(anchor="w")
        title_entry = tk.Entry(form, font=("Segoe UI", 11), bg=Colors.BG_INPUT,
                              fg=Colors.TEXT_PRIMARY, relief='flat',
                              insertbackground=Colors.TEXT_PRIMARY)
        title_entry.pack(fill=tk.X, ipady=6, pady=(3, 10))
        
        # Username
        tk.Label(form, text="Username", font=("Segoe UI", 10),
                fg=Colors.TEXT_SECONDARY, bg=Colors.BG_DARK).pack(anchor="w")
        username_entry = tk.Entry(form, font=("Segoe UI", 11), bg=Colors.BG_INPUT,
                                 fg=Colors.TEXT_PRIMARY, relief='flat',
                                 insertbackground=Colors.TEXT_PRIMARY)
        username_entry.pack(fill=tk.X, ipady=6, pady=(3, 10))
        
        # Password
        tk.Label(form, text="Password *", font=("Segoe UI", 10),
                fg=Colors.TEXT_SECONDARY, bg=Colors.BG_DARK).pack(anchor="w")
        password_entry = tk.Entry(form, font=("Segoe UI", 11), bg=Colors.BG_INPUT,
                                 fg=Colors.TEXT_PRIMARY, relief='flat',
                                 insertbackground=Colors.TEXT_PRIMARY)
        password_entry.pack(fill=tk.X, ipady=6, pady=(3, 10))
        password_entry.insert(0, password)
        
        # URL
        tk.Label(form, text="URL", font=("Segoe UI", 10),
                fg=Colors.TEXT_SECONDARY, bg=Colors.BG_DARK).pack(anchor="w")
        url_entry = tk.Entry(form, font=("Segoe UI", 11), bg=Colors.BG_INPUT,
                            fg=Colors.TEXT_PRIMARY, relief='flat',
                            insertbackground=Colors.TEXT_PRIMARY)
        url_entry.pack(fill=tk.X, ipady=6, pady=(3, 10))
        
        # Category
        tk.Label(form, text="Category", font=("Segoe UI", 10),
                fg=Colors.TEXT_SECONDARY, bg=Colors.BG_DARK).pack(anchor="w")
        
        categories = self.vault.get_categories() if self.vault else ['General']
        category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(form, textvariable=category_var, values=categories,
                                      font=("Segoe UI", 11))
        category_combo.pack(fill=tk.X, ipady=3, pady=(3, 20))
        
        def save():
            title = title_entry.get().strip()
            pwd = password_entry.get()
            
            if not title or not pwd:
                messagebox.showwarning("Error", "Title and Password are required!")
                return
                
            self.vault.add_password(
                title=title,
                username=username_entry.get().strip(),
                password=pwd,
                url=url_entry.get().strip(),
                category=category_var.get()
            )
            self.refresh_vault_list()
            dialog.destroy()
            messagebox.showinfo("Saved", f"Password '{title}' saved successfully!")
        
        PremiumButton(form, text="💾 Save", command=save,
                     width=150, height=45).pack()


def main():
    root = tk.Tk()
    app = PasswordVault(root)
    root.mainloop()


if __name__ == "__main__":
    main()
