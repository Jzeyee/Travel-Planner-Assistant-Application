import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
import re
import subprocess

class Profile:
    def __init__(self, parent_frame, profile_btn, use_custom_menu=False):
        self.parent = parent_frame
        self.profile_btn = profile_btn
        self.profile_data_file = "user_profile.json"
        self.use_custom_menu = use_custom_menu  # Add this parameter
        
        self.COLORS = {
            'primary': '#1e3d59',
            'secondary': '#3498db',
            'accent': '#27ae60',
            'danger': '#e74c3c',
            'light': '#f8f9fa',
            'dark': '#2c3e50',
            'gray': '#95a5a6',
            'white': '#ffffff'
        }
        self.load_profile_data()
        
        # Only create widgets when not using custom menu
        if not use_custom_menu:
            self.create_profile_widgets()
    
    def load_profile_data(self):
        if os.path.exists(self.profile_data_file):
            try:
                with open(self.profile_data_file, 'r', encoding='utf-8') as f:
                    self.profile_data = json.load(f)
            except:
                self.profile_data = self.get_default_profile()
        else:
            self.profile_data = self.get_default_profile()
    
    def save_profile_data(self):
        try:
            with open(self.profile_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.profile_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    def get_default_profile(self):
        # Try to get user information from user_session.json
        session_file = 'user_session.json'
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    return {
                        "personal_info": {
                            "full_name": session_data.get('user_name', 'Guest User'),
                            "email": session_data.get('email', 'guest@example.com'),
                            "phone": "",
                            "address": "",
                            "nationality": "",
                            "date_of_birth": ""
                        }
                    }
            except:
                pass
        
        return {
            "personal_info": {
                "full_name": "Guest User",
                "email": "guest@example.com",
                "phone": "",
                "address": "",
                "nationality": "",
                "date_of_birth": ""
            }
        }
    
    def create_profile_widgets(self):
        """Only set button command when not using custom menu"""
        if not self.use_custom_menu:
            self.profile_btn.config(command=self.show_profile_menu)
    
    def show_profile_menu(self):
        """Only show menu when not using custom menu"""
        if self.use_custom_menu:
            return  # Do not show built-in menu
        
        menu = tk.Menu(self.parent, tearoff=0)
        menu.configure(
            bg=self.COLORS['white'],
            fg=self.COLORS['dark'],
            activebackground=self.COLORS['secondary'],
            activeforeground=self.COLORS['white'],
            font=('Arial', 10),
            borderwidth=0
        )
        
        menu_items = [
            ("👤 View Profile", self.view_profile),
            ("", None),
            ("ℹ️ About", self.show_about),
            ("🚪 Logout", self.logout)
        ]
        
        for label, command in menu_items:
            if label == "":
                menu.add_separator()
            elif command:
                menu.add_command(label=label, command=command)
        
        try:
            menu.tk_popup(
                self.profile_btn.winfo_rootx(),
                self.profile_btn.winfo_rooty() + self.profile_btn.winfo_height()
            )
            menu.grab_set()
        finally:
            menu.grab_release()

    def view_profile(self):
        profile_window = tk.Toplevel(self.parent)
        profile_window.title("My Profile")
        profile_window.geometry("650x500")
        profile_window.configure(bg=self.COLORS['light'])
        profile_window.transient(self.parent)
        profile_window.grab_set()
        
        self.center_window(profile_window, 650, 500)
        
        main_frame = tk.Frame(profile_window, bg=self.COLORS['white'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(
            main_frame,
            text="👤 Profile", 
            font=('Arial', 18, 'bold'), 
            bg=self.COLORS['white'], 
            fg=self.COLORS['primary']
        ).pack(pady=(0, 20))
        
        canvas = tk.Canvas(main_frame, bg=self.COLORS['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        personal_frame = self.create_section_frame(scrollable_frame, "Personal Information")
        
        self.name_var = tk.StringVar(value=self.profile_data["personal_info"]["full_name"])
        self.create_label_entry(personal_frame, "Full Name:", self.name_var, 0)
        
        self.email_var = tk.StringVar(value=self.profile_data["personal_info"]["email"])
        self.create_label_entry(personal_frame, "Email:", self.email_var, 1)
        
        self.phone_var = tk.StringVar(value=self.profile_data["personal_info"]["phone"])
        self.create_label_entry(personal_frame, "Phone:", self.phone_var, 2)
        
        self.address_var = tk.StringVar(value=self.profile_data["personal_info"]["address"])
        self.create_label_entry(personal_frame, "Address:", self.address_var, 3)
        
        self.nationality_var = tk.StringVar(value=self.profile_data["personal_info"]["nationality"])
        nationalities = ["Select", "USA", "Canada", "UK", "Australia", "China", "Japan", 
                        "Korea", "Singapore", "Malaysia", "Other"]
        self.create_label_combobox(personal_frame, "Nationality:", self.nationality_var, nationalities, 4)
        
        self.dob_var = tk.StringVar(value=self.profile_data["personal_info"]["date_of_birth"])
        self.create_label_entry(personal_frame, "Date of Birth (YYYY-MM-DD):", self.dob_var, 5)
        
        button_frame = tk.Frame(scrollable_frame, bg=self.COLORS['white'])
        button_frame.pack(fill='x', pady=(20, 10))
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save Profile", 
            command=lambda: self.save_profile(profile_window),
            bg=self.COLORS['accent'],
            fg=self.COLORS['white'],
            font=('Arial', 12, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        save_btn.pack(side='left', padx=(0, 10))
        
        close_btn = tk.Button(
            button_frame,
            text="Close", 
            command=profile_window.destroy,
            bg=self.COLORS['gray'],
            fg=self.COLORS['white'],
            font=('Arial', 12),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        close_btn.pack(side='left')
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_section_frame(self, parent, title):
        frame = tk.LabelFrame(
            parent,
            text=f"  {title}  ", 
            font=('Arial', 13, 'bold'),
            bg=self.COLORS['white'],
            fg=self.COLORS['primary'],
            padx=15,
            pady=15,
            relief='solid',
            bd=1
        )
        frame.pack(fill='x', pady=(0, 15))
        return frame

    def create_label_entry(self, parent, label_text, variable, row):
        tk.Label(
            parent,
            text=label_text,
            font=('Arial', 11), 
            bg=self.COLORS['white'],
            fg=self.COLORS['dark'],
            anchor='w'
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Arial', 11),
            bg=self.COLORS['light'],
            relief='solid',
            bd=1
        )
        entry.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        parent.grid_columnconfigure(1, weight=1)
        return entry

    def create_label_combobox(self, parent, label_text, variable, options, row):
        tk.Label(
            parent,
            text=label_text,
            font=('Arial', 11), 
            bg=self.COLORS['white'],
            fg=self.COLORS['dark'],
            anchor='w'
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        combobox = ttk.Combobox(
            parent,
            textvariable=variable,
            values=options,
            state='readonly',
            font=('Arial', 11)
        )
        combobox.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        parent.grid_columnconfigure(1, weight=1)
        return combobox
    
    def center_window(self, window, width, height):
        window.update_idletasks()
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def save_profile(self, profile_window):
        try:
            email = self.email_var.get()
            if email and not self.validate_email(email):
                messagebox.showwarning("Validation", "Please enter a valid email address.")
                return
            
            dob = self.dob_var.get()
            if dob:
                try:
                    datetime.strptime(dob, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Validation", "Please enter date in YYYY-MM-DD format.")
                    return
            
            self.profile_data["personal_info"]["full_name"] = self.name_var.get()
            self.profile_data["personal_info"]["email"] = email
            self.profile_data["personal_info"]["phone"] = self.phone_var.get()
            self.profile_data["personal_info"]["address"] = self.address_var.get()
            self.profile_data["personal_info"]["nationality"] = self.nationality_var.get()
            self.profile_data["personal_info"]["date_of_birth"] = dob
            
            if self.save_profile_data():
                messagebox.showinfo("Success", "Profile saved successfully!")
                profile_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to save profile.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile: {str(e)}")
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def show_about(self):
        about_text = """
Traney Hotel Booking System
        
Version 2.0
© 2024 Traney Travel
        
Features:
• User Profile Management
        
Contact: support@traneytravel.com
Phone: +1 (800) 123-4567
        
Thank you for choosing Traney!
        """
        messagebox.showinfo("About", about_text)
    
    def logout(self):
        try:
            if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
                return
            
            # If custom menu exists, hide it first
            if hasattr(self.parent, 'hide_profile_menu'):
                try:
                    self.parent.hide_profile_menu()
                except:
                    pass
            
            # Destroy main window
            try:
                self.parent.destroy()
            except:
                pass
            
            # Start main.py
            try:
                subprocess.Popen(["python", "main.py"])
            except Exception as e:
                print(f"Error starting main.py: {e}")
                messagebox.showinfo("Logout", "You have been logged out.\n\nPlease run main.py manually.")
                
        except Exception as e:
            messagebox.showinfo("Logout", "Logout completed.")