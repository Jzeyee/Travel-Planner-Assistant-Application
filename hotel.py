import tkinter as tk
from tkinter import ttk, messagebox
import os, datetime, json, re
from PIL import Image, ImageTk, ImageDraw
import subprocess
import hashlib
from datetime import datetime

# Add Profile import
from profile import Profile

class Hotel:
    def __init__(self, root, email):
        self.root = root
        self.email = email  # User email for profile
        self.root.title("Traney Hotel")
        self.root.geometry("1200x700")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f8ff')
        
        # Try to load username
        self.user_name = "Guest User"
        session_file = 'user_session.json'
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    self.user_name = session_data.get('user_name', 'Guest User')
            except:
                pass
        
        # Profile menu state
        self.is_menu_open = False
        self.profile_menu = None
        
        # Add: Create custom fonts
        self.create_custom_fonts()
        
        # Keyboard shortcuts for fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # Current state variables
        self.current_page = "main"
        self.selected_room_price = None
        self.current_hotel_data = None
        self.image_cache = {}
        
        # Navigation history for back button functionality
        self.navigation_stack = ["main"]
        
        # UI color scheme - Use consistent color scheme with home.py
        self.colors = {
            "primary": "#1e3d59", "secondary": "#ff6e40", "accent": "#ff8c66",
            "light": "#f0f8ff", "dark": "#1e3d59", "success": "#4CAF50",
            "warning": "#ff6e40", "card_bg": "#ffffff", "header_bg": "#1e3d59",
            "sidebar_bg": "#ffffff", "highlight": "#ff8c66", "nav_bg": "#1e3d59",
            "nav_active": "#ff8c66", "nav_inactive": "#b0c4de", "text_light": "#b0c4de",
            "border": "#e0e0e0", "footer_bg": "#1e3d59"
        }
        
        # Load hotel data from JSON files
        self.city_hotels = self.load_hotels_from_json()
        self.hotels = self.load_all_hotels_from_json()
        self.filtered_hotels = self.hotels.copy()
        
        # Filter variables
        self.category_var = tk.StringVar(value="All")
        self.star_var = tk.StringVar(value="All")
        self.price_var = tk.IntVar(value=1000)
        self.rating_var = tk.DoubleVar(value=7.0)
        self.sort_var = tk.StringVar(value="Rating (High to Low)")
        
        # Booking form variables
        self.room_checkin_var = tk.StringVar()
        self.room_checkout_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.payment_var = tk.StringVar(value="credit_card")

        # Initialize the main page
        self.init_main_page()
        self.bind_mousewheel_to_all()
    
    def create_custom_fonts(self):
        """Create custom fonts - new method"""
        import tkinter.font as tkFont
        # Create fonts with strikethrough
        self.strike_font = tkFont.Font(family="Arial", size=14, overstrike=True)
        self.normal_font = tkFont.Font(family="Arial", size=14)
        self.bold_font = tkFont.Font(family="Arial", size=20, weight="bold")
        self.price_font = tkFont.Font(family="Arial", size=20, weight="bold")
        self.title_font = tkFont.Font(family="Arial", size=24, weight="bold")
        self.subtitle_font = tkFont.Font(family="Arial", size=16, weight="bold")
        self.menu_font = tkFont.Font(family="Arial", size=11)
        self.menu_bold_font = tkFont.Font(family="Arial", size=11, weight="bold")
    
    def init_main_page(self):
        """Initialize and show the main hotel browsing page"""
        self.current_page = "main"
        
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Build the UI
        self.create_header()
        
        # Add: Initialize Profile system before creating main content
        self.profile_system = Profile(self.root, self.profile_btn, use_custom_menu=True)
        
        self.create_main_content()
        self.show_hotels_page_optimized()
    
    def create_header(self):
        """Create top navigation bar - consistent with home.py"""
        header = tk.Frame(self.root, bg='#1e3d59', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)  # Maintain fixed height
        
        # Logo section (click to return to homepage)
        logo_frame = tk.Frame(header, bg='#1e3d59')
        logo_frame.pack(side='left', padx=30)
        logo_frame.bind("<Button-1>", lambda e: self.navigate_to_page("home.py"))
        
        tk.Label(logo_frame, text="🏨", font=("Arial", 28), bg='#1e3d59', fg="white").pack(side='left')
        
        logo_text = tk.Frame(logo_frame, bg='#1e3d59')
        logo_text.pack(side='left', padx=8)
        tk.Label(logo_text, text="Traney", font=("Arial", 22, "bold"), bg='#1e3d59', fg="white").pack()
        
        # Navigation menu
        nav_frame = tk.Frame(header, bg='#1e3d59')
        nav_frame.pack(side='left', padx=30)
        
        # Navigation items: (icon, text, script file)
        nav_items = [
            ("🏠", "Home", "home.py"),
            ("🏨", "Hotel", "Hotel.py"),
            ("✈️", "Flight", "flight.py"),
            ("🏛️", "Attractions", "attraction.py"),
            ("🚗", "Car Rental", "car_rental.py"),
            ("🗺️", "Travel Plan", "travel_plan.py"),
            ("🎒", "Packing List", "packing.py")
        ]
        
        self.nav_buttons = {}  # Store button references
        
        for icon, text, script in nav_items:
            btn_frame = tk.Frame(nav_frame, bg='#1e3d59')
            btn_frame.pack(side='left', padx=2)
            
            is_current = text == "Hotel"  # Current page is Hotel
            
            btn = tk.Button(btn_frame, text=f"{icon} {text}", 
                          font=("Arial", 11, "bold" if is_current else "normal"),
                          bg='#1e3d59',
                          fg='#ff8c66' if is_current else '#b0c4de',
                          relief="flat", cursor="hand2",
                          padx=12, pady=8,
                          command=lambda s=script: self.navigate_to_page(s))
            btn.pack()
            
            self.nav_buttons[text] = btn_frame
            
            # Add underline for current active page
            if is_current:
                underline = tk.Frame(btn_frame, bg='#ff8c66', height=3)
                underline.pack(fill='x', pady=(2, 0))
            
            # Hover effects for navigation buttons
            btn.bind("<Enter>", lambda e, b=btn, t=text: 
                    b.config(bg='#2a4d6e') if t != "Hotel" else None)
            btn.bind("<Leave>", lambda e, b=btn, t=text: 
                    b.config(bg='#1e3d59') if t != "Hotel" else None)
        
        # Right section: search, profile, fullscreen
        right_frame = tk.Frame(header, bg='#1e3d59')
        right_frame.pack(side='right', padx=3)

        # Search bar
        search_frame = tk.Frame(right_frame, bg="white", height=42)
        search_frame.pack(side='left')
        search_frame.pack_propagate(False)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), bg="white",
                                    relief="flat", width=25)
        self.search_entry.pack(side='left', fill='both', expand=True, padx=(12, 0))
        self.search_entry.insert(0, "Search hotels...")
        self.search_entry.config(fg="gray")  # Gray placeholder text
        
        # Placeholder text handling
        def clear_placeholder(e):
            if self.search_entry.get() == "Search hotels...":
                self.search_entry.delete(0, 'end')
                self.search_entry.config(fg="black")
        
        def add_placeholder(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search hotels...")
                self.search_entry.config(fg="gray")
        
        self.search_entry.bind("<FocusIn>", clear_placeholder)
        self.search_entry.bind("<FocusOut>", add_placeholder)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_hotels())

        # Profile button
        profile_frame = tk.Frame(right_frame, bg='#1e3d59')
        profile_frame.pack(side='left')

        self.profile_btn = tk.Button(
            profile_frame, 
            text="👤", 
            font=("Segoe UI", 22), 
            bg='#1e3d59',
            fg="white", 
            relief="flat", 
            cursor="hand2", 
            padx=15, 
            pady=5,
            highlightthickness=0,
            bd=0,
            takefocus=0,
            activebackground='#2a4d6e',
            activeforeground='white',
            command=self.toggle_profile_menu
        )
        self.profile_btn.pack()
        
        # Fullscreen toggle button
        fullscreen_btn = tk.Button(right_frame, text="⛶", font=("Arial", 18), 
                                 bg='#1e3d59', fg="white",
                                 relief="flat", cursor="hand2",
                                 borderwidth=0, highlightthickness=0,
                                 command=self.toggle_fullscreen)
        fullscreen_btn.pack(side='left', padx=(10, 0))
    
    def toggle_profile_menu(self):
        """Toggle dropdown menu show/hide"""
        if self.is_menu_open:
            self.hide_profile_menu()
        else:
            self.show_profile_menu()

    def show_profile_menu(self):
        """Show dropdown menu - modified to be consistent with flight.py"""
        if self.is_menu_open:
            return
            
        self.is_menu_open = True
        
        # Create menu window
        self.profile_menu = tk.Toplevel(self.root)
        self.profile_menu.title("")
        self.profile_menu.overrideredirect(True)  # Remove window border
        self.profile_menu.configure(bg='white')
        
        # Add shadow effect
        self.profile_menu.attributes('-topmost', True)
        
        # Calculate menu position
        button_x = self.profile_btn.winfo_rootx()
        button_y = self.profile_btn.winfo_rooty()
        button_height = self.profile_btn.winfo_height()
        
        menu_width = 250
        menu_height = 350  # Reduced height because one menu item was removed
        
        x = button_x - menu_width + self.profile_btn.winfo_width()
        y = button_y + button_height
        
        self.profile_menu.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
        
        # Create menu content
        self.create_menu_content()
        
        # Bind click outside to close menu
        self.profile_menu.bind("<FocusOut>", lambda e: self.hide_profile_menu())
        self.root.bind("<Button-1>", lambda e: self.check_click_outside(e))

    def create_menu_content(self):
        """Create menu content connected to profile.py - consistent with flight.py"""
        # Main container
        main_container = tk.Frame(self.profile_menu, bg='white', 
                                highlightbackground='#e0e0e0', highlightthickness=1)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Top user info area
        user_info_frame = tk.Frame(main_container, bg='#f8f9fa')
        user_info_frame.pack(fill='x', padx=0, pady=0)
        
        # Avatar and username
        avatar_frame = tk.Frame(user_info_frame, bg='#f8f9fa')
        avatar_frame.pack(fill='x', padx=20, pady=15)
        
        # Avatar
        avatar_label = tk.Label(avatar_frame, text="👤", 
                            font=('Arial', 20), bg='#f8f9fa', fg='#ff8c66')
        avatar_label.pack(side='left', padx=(0, 12))
        
        # User info
        info_frame = tk.Frame(avatar_frame, bg='#f8f9fa')
        info_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(info_frame, text=self.user_name, 
                font=('Arial', 12, 'bold'), bg='#f8f9fa', fg='#333333').pack(anchor='w')
        tk.Label(info_frame, text=self.email, 
                font=('Arial', 10), bg='#f8f9fa', fg='#666666').pack(anchor='w', pady=(2, 0))
        
        # Separator
        separator1 = tk.Frame(main_container, bg='#f0f0f0', height=1)
        separator1.pack(fill='x', pady=(0, 5))
        
        # Menu options area - removed "My Bookings"
        menu_options_frame = tk.Frame(main_container, bg='white')
        menu_options_frame.pack(fill='both', expand=True, padx=0, pady=10)
        
        # Menu options - removed "My Bookings", only three items remain
        menu_items = [
            ("📝 My Profile", self.profile_system.view_profile),
            ("ℹ️ About", self.profile_system.show_about),
            ("🚪 Logout", self.profile_system.logout)
        ]
        
        for i, (text, command_func) in enumerate(menu_items):
            item_frame = tk.Frame(menu_options_frame, bg='white')
            item_frame.pack(fill='x', padx=20, pady=5)
            
            # Create menu item - use lambda to ensure correct parameter passing
            item_btn = tk.Button(item_frame, text=f"   {text}", 
                            font=self.menu_font,
                            bg='white', fg='#333333',
                            relief='flat', cursor='hand2',
                            anchor='w',
                            padx=0, pady=8,
                            command=lambda cmd=command_func: self.execute_profile_command(cmd))
            
            item_btn.pack(fill='x')
            
            # Hover effects
            item_btn.bind("<Enter>", lambda e, b=item_btn: b.config(bg='#f5f5f5', fg='#ff8c66'))
            item_btn.bind("<Leave>", lambda e, b=item_btn: b.config(bg='white', fg='#333333'))
        
        # Logout session info
        session_frame = tk.Frame(main_container, bg='#f8f9fa')
        session_frame.pack(fill='x', padx=0, pady=(5, 0))
        
        session_content = tk.Frame(session_frame, bg='#f8f9fa')
        session_content.pack(fill='x', padx=20, pady=10)
        
        # Current session info
        session_time = datetime.now().strftime("%H:%M")
        session_date = datetime.now().strftime("%Y-%m-%d")
        
        tk.Label(session_content, text=f"Logged in: {session_time}", 
                font=('Arial', 9), bg='#f8f9fa', fg='#666666').pack(anchor='w')
        tk.Label(session_content, text=f"Date: {session_date}", 
                font=('Arial', 9), bg='#f8f9fa', fg='#666666').pack(anchor='w', pady=(2, 0))

    def execute_profile_command(self, command_func):
        """Execute profile command and close menu"""
        self.hide_profile_menu()
        command_func()

    def hide_profile_menu(self):
        """Hide dropdown menu"""
        if self.profile_menu:
            self.profile_menu.destroy()
            self.profile_menu = None
        self.is_menu_open = False

    def check_click_outside(self, event):
        """Check if clicked outside the menu"""
        if self.is_menu_open and self.profile_menu:
            # Check if click position is inside the menu window
            menu_x = self.profile_menu.winfo_rootx()
            menu_y = self.profile_menu.winfo_rooty()
            menu_width = self.profile_menu.winfo_width()
            menu_height = self.profile_menu.winfo_height()
            
            click_x = event.x_root
            click_y = event.y_root
            
            # Check if clicked the menu button
            button_x = self.profile_btn.winfo_rootx()
            button_y = self.profile_btn.winfo_rooty()
            button_width = self.profile_btn.winfo_width()
            button_height = self.profile_btn.winfo_height()
            
            button_clicked = (button_x <= click_x <= button_x + button_width and 
                            button_y <= click_y <= button_y + button_height)
            
            # Check if clicked inside the menu
            menu_clicked = (menu_x <= click_x <= menu_x + menu_width and 
                          menu_y <= click_y <= menu_y + menu_height)
            
            if not menu_clicked and not button_clicked:
                self.hide_profile_menu()
    
    def create_main_content(self):
        """Create main content area container"""
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True)
    
    def load_all_hotels_from_json(self):
        """Load all hotels from JSON file"""
        possible_paths = [
            "hotels.json", "./hotels.json",
            os.path.join(os.path.dirname(__file__), "hotels.json"),
            "data/hotels.json"
        ]
        
        for json_file in possible_paths:
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    all_hotels = []
                    for city, hotels in data.get("cities", {}).items():
                        for hotel in hotels:
                            converted_hotel = self.convert_city_hotel_format(hotel)
                            converted_hotel['city'] = city
                            all_hotels.append(converted_hotel)
                    
                    return all_hotels
                except:
                    continue
        
        # If no JSON file found, use the embedded data
        try:
            all_hotels = []
            for city, hotels in HOTEL_DATA.get("cities", {}).items():
                for hotel in hotels:
                    converted_hotel = self.convert_city_hotel_format(hotel)
                    converted_hotel['city'] = city
                    all_hotels.append(converted_hotel)
            return all_hotels
        except:
            return []
    
    def load_hotels_from_json(self):
        """Load city-based hotels from JSON file"""
        possible_paths = [
            "hotels.json", "./hotels.json",
            os.path.join(os.path.dirname(__file__), "hotels.json"),
            "data/hotels.json"
        ]
        
        for json_file in possible_paths:
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return data.get("cities", {})
                except:
                    continue
        
        return HOTEL_DATA.get("cities", {})
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.fullscreen_state = not self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', self.fullscreen_state)
        return "break"
    
    def get_hotel_image(self, hotel_data):
        """Get hotel image from cache or load from file"""
        if not hasattr(self, 'image_cache'):
            self.image_cache = {}
        
        hotel_name = hotel_data.get('name', '')
        cache_key = hotel_name
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        filename = hotel_data.get('_image_file', 'hotel.jpg')
        image_path = os.path.join("images", filename)
        
        if not os.path.exists(image_path):
            generic_files = ["hotel.jpg", "hot1.jpg", "hot2.jpg", "hot3.jpg"]
            for file in generic_files:
                alt_path = os.path.join("images", file)
                if os.path.exists(alt_path):
                    image_path = alt_path
                    filename = file
                    break
        
        try:
            img = Image.open(image_path)
            img = img.resize((300, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = photo
            return photo
        except:
            return self.create_placeholder_image()
    
    def create_placeholder_image(self):
        """Create a placeholder image when hotel image is not available"""
        img = Image.new('RGB', (300, 200), color='#3498db')
        draw = ImageDraw.Draw(img)
        draw.text((120, 80), "🏨", fill='white')
        draw.text((100, 150), "Hotel", fill='white')
        return ImageTk.PhotoImage(img)
    
    def show_hotels_page_optimized(self):
        """Show the main hotels browsing page with filters"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        if not self.navigation_stack or self.navigation_stack[-1] != "main":
            self.navigation_stack = ["main"]
        
        # Main content layout
        main_content = tk.Frame(self.main_container, bg=self.colors["light"])
        main_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left sidebar for filters
        left_frame = tk.Frame(main_content, bg=self.colors["light"], width=280)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Right content area for hotel listings
        right_frame = tk.Frame(main_content, bg=self.colors["light"])
        right_frame.pack(side="left", fill="both", expand=True)
        
        # Build the page components
        self.create_sidebar_optimized(left_frame)
        self.create_main_content_optimized(right_frame)
        self.create_footer(self.main_container)
        self.bind_mousewheel_to_all()
    
    def create_sidebar_optimized(self, parent):
        """Create the filter sidebar"""
        sidebar = tk.Frame(parent, bg=self.colors["sidebar_bg"], width=260,
                          relief="flat", highlightbackground=self.colors["border"],
                          highlightthickness=1)
        sidebar.pack(fill="both", expand=True)
        
        # Filter header
        filter_header = tk.Frame(sidebar, bg=self.colors["primary"], height=40)
        filter_header.pack(fill="x", pady=(0, 10))
        filter_header.pack_propagate(False)
        
        tk.Label(filter_header, text="🔍 FILTERS", font=("Arial", 12, "bold"),
                bg=self.colors["primary"], fg="white").pack(expand=True)
        
        # Filter content area
        filter_content = tk.Frame(sidebar, bg=self.colors["sidebar_bg"])
        filter_content.pack(fill="both", expand=True, padx=12, pady=8)
        
        # Category filter
        tk.Label(filter_content, text="Category", font=("Arial", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 6))
        
        categories_frame = tk.Frame(filter_content, bg=self.colors["sidebar_bg"])
        categories_frame.pack(fill="x", pady=(0, 12))
        
        categories = [("🌍 All", "All"), ("🏨 City Hotel", "City Hotel"),
                     ("🏖️ Resort", "Resort"), ("💎 Luxury", "Luxury Hotel"),
                     ("💰 Budget", "Budget Hotel")]
        
        for icon, category in categories:
            btn = tk.Radiobutton(categories_frame, text=icon, variable=self.category_var,
                                value=category, font=("Arial", 10),
                                bg=self.colors["sidebar_bg"], fg=self.colors["dark"],
                                selectcolor=self.colors["light"],
                                activebackground=self.colors["sidebar_bg"],
                                command=self.filter_hotels)
            btn.pack(anchor="w", pady=1)
        
        # Star rating filter
        tk.Label(filter_content, text="Star Rating", font=("Arial", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(8, 6))
        
        star_frame = tk.Frame(filter_content, bg=self.colors["sidebar_bg"])
        star_frame.pack(fill="x", pady=(0, 12))
        
        stars = [("⭐ All", "All"), ("⭐⭐⭐⭐⭐ 5 Stars", "5"),
                ("⭐⭐⭐⭐ 4 Stars", "4"), ("⭐⭐⭐ 3 Stars", "3")]
        
        for icon, star in stars:
            btn = tk.Radiobutton(star_frame, text=icon, variable=self.star_var,
                                value=star, font=("Arial", 10), bg=self.colors["sidebar_bg"],
                                fg=self.colors["dark"], selectcolor=self.colors["light"],
                                activebackground=self.colors["sidebar_bg"],
                                command=self.filter_hotels)
            btn.pack(anchor="w", pady=1)
        
        # Price range filter
        tk.Label(filter_content, text="Price Range (RM)", font=("Arial", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(8, 6))
        
        price_frame = tk.Frame(filter_content, bg=self.colors["sidebar_bg"])
        price_frame.pack(fill="x", pady=(0, 12))
        
        self.price_label = tk.Label(price_frame, text=f"Max: RM {self.price_var.get()}",
                                   font=("Arial", 10), bg=self.colors["sidebar_bg"],
                                   fg=self.colors["secondary"])
        self.price_label.pack(anchor="w")
        
        price_scale = tk.Scale(price_frame, from_=0, to=1000, variable=self.price_var,
                              orient="horizontal", length=180, showvalue=False,
                              bg=self.colors["sidebar_bg"], fg=self.colors["dark"],
                              troughcolor=self.colors["light"], sliderrelief="flat",
                              sliderlength=15, highlightthickness=0,
                              command=self.on_price_change)
        price_scale.pack(fill="x", pady=4)
        
        # Minimum rating filter
        tk.Label(filter_content, text="Minimum Rating", font=("Arial", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(8, 6))
        
        rating_frame = tk.Frame(filter_content, bg=self.colors["sidebar_bg"])
        rating_frame.pack(fill="x", pady=(0, 15))
        
        rating_text = tk.Label(rating_frame, text=f"{self.rating_var.get()}/10",
                              font=("Arial", 10), bg=self.colors["sidebar_bg"],
                              fg=self.colors["secondary"])
        rating_text.pack()
        
        rating_scale = tk.Scale(rating_frame, from_=0, to=10, variable=self.rating_var,
                               orient="horizontal", length=180, showvalue=False,
                               bg=self.colors["sidebar_bg"], fg=self.colors["dark"],
                               troughcolor=self.colors["light"], sliderrelief="flat",
                               sliderlength=15, highlightthickness=0, resolution=0.5,
                               command=lambda v: self.on_rating_change(v, rating_text))
        rating_scale.pack(fill="x", pady=4)
        
        # Reset filters button
        tk.Button(filter_content, text="🔄 Reset Filters", font=("Arial", 11),
                 bg=self.colors["primary"], fg="white", relief="flat",
                 cursor="hand2", command=self.reset_filters,
                 height=1, pady=5).pack(fill="x", pady=(15, 5))
    
    def create_main_content_optimized(self, parent):
        """Create the main content area with hotel listings"""
        header = tk.Frame(parent, bg=self.colors["light"])
        header.pack(fill="x", pady=(0, 10))
        
        tk.Label(header, text="🏨 Find Your Perfect Stay", 
                font=("Arial", 20, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(side="left")
        
        # Sort dropdown
        sort_frame = tk.Frame(header, bg=self.colors["light"])
        sort_frame.pack(side="right")
        
        tk.Label(sort_frame, text="Sort:", font=("Arial", 10),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(side="left", padx=(0, 5))
        
        sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var,
                                 values=["Rating (High to Low)", "Price (Low to High)",
                                        "Price (High to Low)", "Name (A-Z)", "Stars (High to Low)"],
                                 state="readonly", font=("Arial", 10), width=18)
        sort_combo.pack(side="left")
        sort_combo.bind("<<ComboboxSelected>>", self.sort_hotels)
        
        # Results count
        results_frame = tk.Frame(parent, bg=self.colors["light"])
        results_frame.pack(fill="x", pady=(0, 10))
        
        self.results_label = tk.Label(results_frame, text=f"{len(self.filtered_hotels)} Hotels Found",
                                     font=("Arial", 12), bg=self.colors["light"], fg=self.colors["primary"])
        self.results_label.pack(side="left")
        
        # Tabbed interface
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.configure("TNotebook", background=self.colors["light"])
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[10, 5])
        
        all_hotels_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(all_hotels_frame, text="🏨 All Hotels")
        
        city_hotels_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(city_hotels_frame, text="🌆 City Hotels")
        
        self.create_hotels_grid_optimized(all_hotels_frame)
        self.create_city_hotels_section_optimized(city_hotels_frame)
    
    def create_hotels_grid_optimized(self, parent):
        """Create scrollable grid of hotel cards"""
        canvas_frame = tk.Frame(parent, bg=self.colors["light"])
        canvas_frame.pack(fill="both", expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(canvas_frame, bg=self.colors["light"], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["light"])
        
        # Configure scrolling
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.grid_frame = scrollable_frame
        self.display_hotels_grid_optimized()
        self.canvas = canvas
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 2))
        scrollbar.pack(side="right", fill="y")
        
        # Mousewheel scrolling
        canvas.bind("<MouseWheel>", self._on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
    
    def display_hotels_grid_optimized(self):
        """Display hotel cards in grid layout"""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Show message if no hotels found
        if not self.filtered_hotels:
            no_results = tk.Frame(self.grid_frame, bg=self.colors["light"])
            no_results.pack(expand=True, pady=50)
            
            tk.Label(no_results, text="🔍", font=("Arial", 48), bg=self.colors["light"], fg=self.colors["accent"]).pack()
            tk.Label(no_results, text="No hotels found", font=("Arial", 16, "bold"), bg=self.colors["light"], fg=self.colors["primary"]).pack(pady=10)
            tk.Label(no_results, text="Try adjusting your filters",font=("Arial", 12), bg=self.colors["light"], fg=self.colors["text_light"]).pack()
            return
        
        # Display hotels in 3-column grid
        row, col = 0, 0
        for hotel in self.filtered_hotels:
            card = self.create_hotel_card_optimized(self.grid_frame, hotel)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1
        
        # Configure grid columns to be equal width
        for i in range(3):
            self.grid_frame.grid_columnconfigure(i, weight=1, uniform="col")
    
    def create_hotel_card_optimized(self, parent, hotel_data):
        """Create a single hotel card with image, info, and booking button"""
        card = tk.Frame(parent, bg="white", relief="flat",
                       highlightbackground=self.colors["border"], highlightthickness=1,
                       width=280, height=350)
        
        # Hotel image
        photo = self.get_hotel_image(hotel_data)
        if photo:
            image_label = tk.Label(card, image=photo, bg="white")
            image_label.image = photo
            image_label.pack(fill="x")
        else:
            # Placeholder if image not found
            image_frame = tk.Frame(card, bg='#3498db', height=150)
            image_frame.pack(fill="x")
            image_frame.pack_propagate(False)
            tk.Label(image_frame, text="🏨", font=("Arial", 48),
                    bg='#3498db', fg="white").pack(expand=True)
        
        # Hotel information
        content = tk.Frame(card, bg="white", padx=12, pady=12)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text=hotel_data['name'], font=("Arial", 12, "bold"),
                bg="white", fg=self.colors["dark"], wraplength=240).pack(anchor="w")
        tk.Label(content, text=f"📍 {hotel_data['location']}", font=("Arial", 10),
                bg="white", fg=self.colors["text_light"]).pack(anchor="w", pady=(2, 8))
        
        # Rating and stars
        info_frame = tk.Frame(content, bg="white")
        info_frame.pack(fill="x", pady=(0, 8))
        tk.Label(info_frame, text=hotel_data['stars'], font=("Arial", 11),
                bg="white", fg="#f39c12").pack(side="left")
        tk.Label(info_frame, text=f"⭐ {hotel_data['rating']}/10", font=("Arial", 10, "bold"),
                bg="white", fg=self.colors["dark"]).pack(side="right")
        
        # Price
        price_frame = tk.Frame(content, bg="white")
        price_frame.pack(fill="x", pady=8)
        tk.Label(price_frame, text=f"RM {hotel_data['price']}", font=("Arial", 14, "bold"),
                bg="white", fg=self.colors["secondary"]).pack(side="left")
        
        # Booking button
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", pady=(8, 10))
        tk.Button(btn_frame, text="View Details", font=("Arial", 10, "bold"),
                 bg=self.colors["secondary"], fg="white", relief="flat",
                 cursor="hand2",
                 command=lambda h=hotel_data: self.show_booking_page(h)).pack(side="left", fill="x", expand=True)    
        
        return card
    
    def create_city_hotels_section_optimized(self, parent):
        """Create city hotels selection section"""
        container = tk.Frame(parent, bg=self.colors["light"])
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not self.city_hotels:
            tk.Label(container, text="No city hotels available", font=("Arial", 14),
                    bg=self.colors["light"], fg=self.colors["text_light"]).pack(expand=True)
            return
        
        cities_frame = tk.Frame(container, bg=self.colors["light"])
        cities_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(cities_frame, text="Select City:", font=("Arial", 12, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # City selection buttons
        buttons_frame = tk.Frame(cities_frame, bg=self.colors["light"])
        buttons_frame.pack(fill="x")
        
        cities = list(self.city_hotels.keys())
        row, col = 0, 0
        for i, city in enumerate(cities):
            city_btn = tk.Button(buttons_frame, text=city, font=("Arial", 11),
                               bg=self.colors["primary"], fg="white", relief="flat",
                               cursor="hand2", padx=15, pady=8,
                               command=lambda c=city: self.show_city_hotels(c))
            city_btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            buttons_frame.grid_columnconfigure(col, weight=1)
            col += 1
            if col == 3:
                col = 0
                row += 1
    
    def navigate_to_page(self, script_file):
        """Navigate to other travel modules"""
        if script_file == "Hotel.py":
            return
        
        try:
            # Save user session
            session_data = {
                'email': self.email,
                'user_name': self.user_name
            }
            with open('user_session.json', 'w') as f:
                json.dump(session_data, f)
            
            # Launch other modules as separate processes
            if script_file == "home.py":
                self.root.destroy()
                subprocess.Popen(["python", script_file])
            elif script_file == "attraction.py":
                self.root.destroy()
                import attraction
                root = tk.Tk()
                attraction.AttractionApp(root, self.email)
                root.mainloop()
            else:
                self.root.destroy()
                subprocess.Popen(["python", script_file])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open {script_file}: {e}")

    def logout(self):
        """Logout confirmation and window close"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
    
    def on_price_change(self, value):
        """Update price label when slider changes"""
        self.price_label.config(text=f"Max: RM {int(float(value))}")
        self.filter_hotels()
    
    def on_rating_change(self, value, label):
        """Update rating label when slider changes"""
        label.config(text=f"{float(value):.1f}/10")
        self.filter_hotels()
    
    def filter_hotels(self, *args):
        """Filter hotels based on current filter settings"""
        category = self.category_var.get()
        star_rating = self.star_var.get()
        max_price = self.price_var.get()
        min_rating = self.rating_var.get()
        
        # Apply filters
        self.filtered_hotels = [
            hotel for hotel in self.hotels
            if (category == "All" or hotel.get("category", "") == category) and
            (star_rating == "All" or (hotel.get("stars", "").count("★") >= int(star_rating) if star_rating.isdigit() else True)) and
            hotel["price"] <= max_price and
            hotel["rating"] >= min_rating
        ]
        
        # Apply sorting and update display
        self.sort_hotels()
        self.display_hotels_grid_optimized()
        self.results_label.config(text=f"{len(self.filtered_hotels)} Hotels Found")
    
    def sort_hotels(self, *args):
        """Sort hotels based on selected sort option"""
        sort_by = self.sort_var.get()
        
        if sort_by == "Rating (High to Low)":
            self.filtered_hotels.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "Price (Low to High)":
            self.filtered_hotels.sort(key=lambda x: x["price"])
        elif sort_by == "Price (High to Low)":
            self.filtered_hotels.sort(key=lambda x: x["price"], reverse=True)
        elif sort_by == "Name (A-Z)":
            self.filtered_hotels.sort(key=lambda x: x["name"])
        elif sort_by == "Stars (High to Low)":
            self.filtered_hotels.sort(key=lambda x: x["stars"].count("★"), reverse=True)
        
        self.display_hotels_grid_optimized()
    
    def reset_filters(self):
        """Reset all filters to default values"""
        self.category_var.set("All")
        self.star_var.set("All")
        self.price_var.set(1000)
        self.rating_var.set(7.0)
        self.price_label.config(text=f"Max: RM {self.price_var.get()}")
        self.filter_hotels()
    
    def convert_city_hotel_format(self, city_hotel):
        """Convert city hotel format from JSON to standard format"""
        try:
            price_str = city_hotel.get('discount_price', 'RM 0')
            price_num = float(price_str.replace('RM ', '').replace(',', '').strip())
            if price_num.is_integer():
                 price_num = int(price_num)
        except:
            price_num = 0
        
        try:
            rating_num = float(city_hotel.get('rating', 0))
        except:
            rating_num = 0
        
        # Generate unique hotel ID from name hash
        hotel_id = int(hashlib.sha256(city_hotel.get('name', '').encode()).hexdigest(), 16) % 10000
        
        return {
            'id': hotel_id,
            'name': city_hotel.get('name', ''),
            'stars': city_hotel.get('stars', ''),
            'rating': rating_num,
            'reviews': city_hotel.get('reviews', ''),
            'location': city_hotel.get('location', ''),
            'room_type': city_hotel.get('room_type', ''),
            'price': price_num,
            'original_price': price_num * 1.2,
            'discount_price': price_num,
            'total_price': price_num * 1.1,
            'category': 'City Hotel',
            'tags': ['City', 'Urban', 'Modern'],
            'description': city_hotel.get('feature_review', ''),
            'duration': 'Flexible stay',
            'best_time': 'Any time',
            'highlights': city_hotel.get('booking_details', {}).get('highlights', []),
            'amenities': city_hotel.get('booking_details', {}).get('amenities', []),
            'opening_hours': 'Check-in: 2:00 PM, Check-out: 12:00 PM',
            'facilities': ['Restaurant', 'WiFi', 'Gym', 'Pool'],
            'accessibility': 'Fully accessible',
            '_image_file': city_hotel.get('_image_file', 'hotel.jpg'),
            'booking_details': city_hotel.get('booking_details', {})
        }
    
    def show_city_hotels(self, city):
        """Show hotels for a specific city"""
        if city in self.city_hotels:
            hotels = self.city_hotels[city]
            self.show_search_results(city, hotels)
        else:
            messagebox.showinfo("Info", f"No hotels found for {city}")
    
    def show_search_results(self, city_name, hotels):
        """Show search results for a city"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        self.navigation_stack.append(f"city_{city_name}")
        
        # Create scrollable results page
        canvas = tk.Canvas(self.main_container, bg=self.colors["light"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["light"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Page header
        header_frame = tk.Frame(scrollable_frame, bg=self.colors["light"], padx=15, pady=15)
        header_frame.pack(fill="x")
        
        tk.Button(header_frame, text="← Back", font=("Arial", 11),
                 bg=self.colors["primary"], fg=self.colors["text_light"],
                 relief="flat", cursor="hand2",
                 command=self.show_hotels_page_optimized).pack(anchor="w", pady=(0, 10))
        
        tk.Label(header_frame, text=f"🏙️ Hotels in {city_name}", font=("Arial", 20, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 5))
        tk.Label(header_frame, text=f"Found {len(hotels)} hotels", font=("Arial", 12),
                bg=self.colors["light"], fg=self.colors["text_light"]).pack(anchor="w")
        
        # Hotels grid
        hotels_frame = tk.Frame(scrollable_frame, bg=self.colors["light"], padx=15, pady=15)
        hotels_frame.pack(fill="both", expand=True)
        
        if hotels:
            row, col = 0, 0
            for hotel in hotels:
                converted_hotel = self.convert_city_hotel_format(hotel)
                card = self.create_hotel_card_optimized(hotels_frame, converted_hotel)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                hotels_frame.grid_columnconfigure(col, weight=1)
                col += 1
                if col == 3:
                    col = 0
                    row += 1
        else:
            tk.Label(hotels_frame, text="No hotels found", font=("Arial", 14),
                    bg=self.colors["light"], fg=self.colors["text_light"]).pack(expand=True, pady=50)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 2))
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind("<MouseWheel>", self._on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.create_footer(self.main_container)
        self.bind_mousewheel_to_all()
    
    def show_detail_page(self, hotel_data):
        """Show detailed hotel information page"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.navigation_stack.append(f"detail_{hotel_data.get('id', hash(hotel_data['name']))}")
        self.create_detail_content(hotel_data)
        self.bind_mousewheel_to_all()
    
    def create_detail_content(self, hotel_data):
        """Create detailed hotel information view"""
        canvas = tk.Canvas(self.main_container, bg=self.colors["light"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["light"])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.detail_canvas = canvas
        
        # Hotel image
        photo = self.get_hotel_image(hotel_data)
        if photo:
            image_label = tk.Label(scrollable_frame, image=photo, bg="white")
            image_label.image = photo
            image_label.pack(fill="x")
        
        # Hotel details
        content = tk.Frame(scrollable_frame, bg="white", padx=25, pady=20)
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Hotel name and location
        title_frame = tk.Frame(content, bg="white")
        title_frame.pack(fill="x", pady=(0, 15))
        tk.Label(title_frame, text=hotel_data['name'], font=("Arial", 22, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w")
        tk.Label(title_frame, text=f"📍 {hotel_data['location']}", font=("Arial", 14),
                bg="white", fg=self.colors["text_light"]).pack(anchor="w", pady=(5, 10))
        
        # Rating and price
        info_frame = tk.Frame(content, bg="white")
        info_frame.pack(fill="x", pady=(0, 20))
        
        rating_frame = tk.Frame(info_frame, bg="white")
        rating_frame.pack(side="left")
        tk.Label(rating_frame, text=hotel_data['stars'], font=("Arial", 16),
                bg="white", fg="#f39c12").pack(side="left")
        tk.Label(rating_frame, text=f"⭐ {hotel_data['rating']}/10 ({hotel_data.get('reviews', '')})",
                font=("Arial", 12), bg="white", fg=self.colors["dark"]).pack(side="left", padx=5)
        
        price_frame = tk.Frame(info_frame, bg="white")
        price_frame.pack(side="right")
        tk.Label(price_frame, text=f"RM {hotel_data['price']}", font=("Arial", 20, "bold"),
                bg="white", fg=self.colors["secondary"]).pack(side="left")
        
        # Description
        tk.Label(content, text="Description", font=("Arial", 16, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(10, 10))
        
        desc_frame = tk.Frame(content, bg="white")
        desc_frame.pack(fill="x", pady=(0, 15))
        tk.Label(desc_frame, text=hotel_data['description'], font=("Arial", 12),
                bg="white", fg=self.colors["dark"], wraplength=700, justify="left").pack(anchor="w")
        
        # Highlights (if available)
        if hotel_data.get("highlights"):
            tk.Label(content, text="Highlights", font=("Arial", 16, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(10, 10))

            for highlight in hotel_data.get("highlights", []):
                highlight_frame = tk.Frame(content, bg="white")
                highlight_frame.pack(fill="x", pady=2)

                tk.Label(highlight_frame, text="✓", font=("Arial", 12),
                        bg="white", fg=self.colors["success"]).pack(side="left", padx=(0, 10))
                tk.Label(highlight_frame, text=highlight, font=("Arial", 12),
                        bg="white", fg=self.colors["dark"]).pack(side="left")
        
        # Action buttons
        action_frame = tk.Frame(content, bg="white")
        action_frame.pack(fill="x", pady=(20, 0))
        tk.Button(action_frame, text="← Back to Hotels", font=("Arial", 12),
                 bg=self.colors["light"], fg=self.colors["primary"],
                 relief="flat", cursor="hand2",
                 command=self.show_hotels_page_optimized,
                 padx=20, pady=8).pack(side="left", padx=(0, 20))
        
        tk.Button(action_frame, text="📅 Book Now", font=("Arial", 12, "bold"),
                 bg=self.colors["secondary"], fg="white", relief="flat",
                 cursor="hand2",
                 command=lambda h=hotel_data: self.show_booking_page(h),
                 padx=30, pady=8).pack(side="right")
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 2))
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind("<MouseWheel>", self._on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.create_footer(self.main_container)
    
    def show_booking_page(self, hotel_data):
        """Start booking process for selected hotel"""
        self.current_hotel_data = hotel_data
        
        self.show_room_selection_page(hotel_data)
        self.bind_mousewheel_to_all()
    
    def show_room_selection_page(self, hotel_data):
        """Show room selection page for booking"""
        self.current_page = "room_selection"
        self.current_hotel_data = hotel_data
        
        # Clear current window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.navigation_stack.append(f"booking_{hotel_data.get('id', hash(hotel_data['name']))}")
        
        try:
            from hotel_detail import RoomSelection
            self.room_selection_page = RoomSelection(
                master=self.root,
                hotel_data=hotel_data,
                colors=self.colors,
                profile_system=self.profile_system,
                go_back_callback=self.restore_main_page,  
                open_booking_detail_callback=self.open_booking_detail_window
            )
            self.create_footer(self.root)
            self.bind_mousewheel_to_all()
        except ImportError as e:
            messagebox.showerror("Error", f"Cannot load room selection module: {e}")
            self.restore_main_page()
    
    def restore_main_page(self):
        """Return to main hotel browsing page"""
        self.init_main_page()

    def open_booking_detail_window(self, booking_data):
        """Open booking confirmation window"""
        try:
            booking_window = tk.Toplevel(self.root)
            booking_window.title("Booking Confirmation")
            booking_window.geometry("900x700")
            
            # Get user email from profile or use default
            user_email = booking_data.get("user_email", "")
            if not user_email and hasattr(self, 'profile_system'):
                try:
                    profile_data = self.profile_system.profile_data
                    user_email = profile_data.get("personal_info", {}).get("email", "")
                except:
                    user_email = self.email
            
            from booking_detail import BookingDetailApp
            BookingDetailApp(booking_window, booking_data, email=user_email, booking_type="hotel")
            booking_window.protocol("WM_DELETE_WINDOW", lambda: self.on_booking_window_close(booking_window))
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open booking details: {str(e)}")

    def on_booking_window_close(self, window):
        """Handle booking window closure"""
        window.destroy()

    def save_booking_to_file(self, booking_data):
        """Save booking to JSON file"""
        try:
            bookings_file = "bookings.json"
            
            if os.path.exists(bookings_file):
                with open(bookings_file, 'r', encoding='utf-8') as f:
                    bookings = json.load(f)
            else:
                bookings = []
            
            bookings.append({
                "id": booking_data["booking_id"],
                "hotel_name": booking_data["hotel_name"],
                "room_type": booking_data["room_type"],
                "check_in": booking_data["check_in"],
                "check_out": booking_data["check_out"],
                "guests": int(re.search(r'\d+', booking_data["guests"]).group()) if re.search(r'\d+', booking_data["guests"]) else 2,
                "status": "Confirmed",
                "price": float(re.search(r'\d+', booking_data["total_price"]).group()) if re.search(r'\d+', booking_data["total_price"]) else 0,
                "booking_date": datetime.now().strftime("%Y-%m-%d"),
                "email": booking_data["user_email"],
                "user_name": booking_data["user_name"],
                "user_phone": booking_data["user_phone"]
            })
            
            with open(bookings_file, 'w', encoding='utf-8') as f:
                json.dump(bookings, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def create_footer(self, parent):
        """Create footer with copyright information"""
        footer = tk.Frame(parent, bg=self.colors["footer_bg"], height=40)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        tk.Label(footer, text="© 2024 Traney Travel Services. All rights reserved.",
                font=("Arial", 9), bg=self.colors["footer_bg"], fg="white").pack(side="left", padx=15)
    
    def bind_mousewheel_to_all(self):
        """Enable mousewheel scrolling for all scrollable areas"""
        self.root.unbind_all("<MouseWheel>")
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self._bind_wheel_to_canvases(self.root)
    
    def _bind_wheel_to_canvases(self, widget):
        """Recursively bind mousewheel to canvas widgets"""
        if isinstance(widget, tk.Canvas):
            widget.bind("<MouseWheel>", self._on_mousewheel)
        try:
            for child in widget.winfo_children():
                self._bind_wheel_to_canvases(child)
        except:
            pass
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        # Find the canvas under mouse cursor
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if isinstance(widget, tk.Canvas):
                widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return "break"
            widget = widget.master
        
        # Fallback to main canvas if no specific canvas found
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        
        # Fallback to detail canvas
        if hasattr(self, 'detail_canvas') and self.detail_canvas.winfo_exists():
            self.detail_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        
        return "break"

# Hotel data, containing 18 hotels
HOTEL_DATA = {
    "cities": {
        "Bangkok": [
            {
                "name": "NASA BANGKOK",
                "stars": "★★★★",
                "rating": "7.8",
                "feature_review": "Convenient location, Easy to get around",
                "location": "Near Ramkhamhaeng Metro Station - Ratchadaphisek",
                "room_type": "Standard Double Or Twin Room",
                "original_price": "RM 79",
                "discount_price": "RM 74",
                "total_price": "Total (incl. taxes & fees): RM 88",
                "_image_file": "hotel1.jpg",
                "booking_details": {}
            },
            {
                "name": "Grand Palace Hotel Bangkok",
                "stars": "★★★★★",
                "rating": "8.5",
                "feature_review": "Luxury stay with panoramic city views",
                "location": "Sukhumvit Road, Bangkok",
                "room_type": "Deluxe King Room",
                "original_price": "RM 250",
                "discount_price": "RM 220",
                "total_price": "Total (incl. taxes & fees): RM 245",
                "_image_file": "hotel2.jpg",
                "booking_details": {}
            },
            {
                "name": "Siam Heritage Boutique Hotel",
                "stars": "★★★",
                "rating": "7.2",
                "feature_review": "Traditional Thai style with modern amenities",
                "location": "Riverside, Bangkok",
                "room_type": "Superior Room",
                "original_price": "RM 120",
                "discount_price": "RM 105",
                "total_price": "Total (incl. taxes & fees): RM 118",
                "_image_file": "hotel3.jpg",
                "booking_details": {}
            }
        ],
        "Kuala Lumpur": [
            {
                "name": "Riveria City Kuala Lumpur",
                "stars": "★★★★",
                "rating": "8.6",
                "feature_review": "Great swimming pool",
                "location": "Near Petaling street Market - KL sentral",
                "room_type": "Studio",
                "original_price": "RM 190",
                "discount_price": "RM 93",
                "total_price": "Total (incl. taxes & fees): RM 100",
                "_image_file": "hotel4.jpg",
                "booking_details": {}
            },
            {
                "name": "The Majestic Hotel KL",
                "stars": "★★★★★",
                "rating": "9.0",
                "feature_review": "Colonial-style luxury",
                "location": "KLCC, Kuala Lumpur",
                "room_type": "Executive Suite",
                "original_price": "RM 450",
                "discount_price": "RM 380",
                "total_price": "Total (incl. taxes & fees): RM 420",
                "_image_file": "hotel5.jpg",
                "booking_details": {}
            }
        ],
        "Singapore": [
            {
                "name": "Marina Bay Sands",
                "stars": "★★★★★",
                "rating": "9.2",
                "feature_review": "Iconic infinity pool",
                "location": "Marina Bay, Singapore",
                "room_type": "Deluxe Room",
                "original_price": "RM 800",
                "discount_price": "RM 700",
                "total_price": "Total (incl. taxes & fees): RM 770",
                "_image_file": "hotel6.jpg",
                "booking_details": {}
            },
            {
                "name": "Hotel 81 Singapore",
                "stars": "★★★",
                "rating": "6.8",
                "feature_review": "Budget-friendly",
                "location": "Geylang, Singapore",
                "room_type": "Standard Room",
                "original_price": "RM 150",
                "discount_price": "RM 120",
                "total_price": "Total (incl. taxes & fees): RM 135",
                "_image_file": "hotel7.jpg",
                "booking_details": {}
            }
        ],
        "Tokyo": [
            {
                "name": "Park Hotel Tokyo",
                "stars": "★★★★",
                "rating": "8.5",
                "feature_review": "Art-themed rooms",
                "location": "Shiodome, Tokyo",
                "room_type": "Artist Room",
                "original_price": "RM 850",
                "discount_price": "RM 750",
                "total_price": "Total (incl. taxes & fees): RM 825",
                "_image_file": "hotel8.jpg",
                "booking_details": {}
            },
            {
                "name": "APA Hotel Tokyo",
                "stars": "★★★",
                "rating": "7.0",
                "feature_review": "Compact business hotel",
                "location": "Shinjuku, Tokyo",
                "room_type": "Business Single",
                "original_price": "RM 300",
                "discount_price": "RM 250",
                "total_price": "Total (incl. taxes & fees): RM 275",
                "_image_file": "hotel9.jpg",
                "booking_details": {}
            }
        ],
        "Bali": [
            {
                "name": "AYANA Resort Bali",
                "stars": "★★★★★",
                "rating": "9.3",
                "feature_review": "Cliff-top resort",
                "location": "Jimbaran, Bali",
                "room_type": "Ocean View Suite",
                "original_price": "RM 1200",
                "discount_price": "RM 1000",
                "total_price": "Total (incl. taxes & fees): RM 1100",
                "_image_file": "hotel10.jpg",
                "booking_details": {}
            }
        ],
        "Hong Kong": [
            {
                "name": "The Peninsula Hong Kong",
                "stars": "★★★★★",
                "rating": "9.1",
                "feature_review": "Heritage hotel",
                "location": "Tsim Sha Tsui",
                "room_type": "Deluxe Harbor View",
                "original_price": "RM 1800",
                "discount_price": "RM 1600",
                "total_price": "Total (incl. taxes & fees): RM 1760",
                "_image_file": "hotel11.jpg",
                "booking_details": {}
            }
        ],
        "Seoul": [
            {
                "name": "Lotte Hotel Seoul",
                "stars": "★★★★★",
                "rating": "8.9",
                "feature_review": "Premium location",
                "location": "Jung-gu, Seoul",
                "room_type": "Executive Room",
                "original_price": "RM 950",
                "discount_price": "RM 820",
                "total_price": "Total (incl. taxes & fees): RM 902",
                "_image_file": "hotel12.jpg",
                "booking_details": {}
            }
        ],
        "Taipei": [
            {
                "name": "W Taipei",
                "stars": "★★★★★",
                "rating": "8.8",
                "feature_review": "Trendy hotel",
                "location": "Xinyi District",
                "room_type": "Wonderful Room",
                "original_price": "RM 850",
                "discount_price": "RM 750",
                "total_price": "Total (incl. taxes & fees): RM 825",
                "_image_file": "hotel13.jpg",
                "booking_details": {}
            }
        ],
        "Phuket": [
            {
                "name": "Dusit Thani Laguna",
                "stars": "★★★★★",
                "rating": "8.9",
                "feature_review": "Beachfront luxury",
                "location": "Laguna, Phuket",
                "room_type": "Deluxe Room",
                "original_price": "RM 700",
                "discount_price": "RM 600",
                "total_price": "Total (incl. taxes & fees): RM 650",
                "_image_file": "hotel14.jpg",
                "booking_details": {}
            }
        ],
        "Shanghai": [
            {
                "name": "JW Marriott Shanghai",
                "stars": "★★★★★",
                "rating": "8.7",
                "feature_review": "Bund view",
                "location": "Pudong, Shanghai",
                "room_type": "Executive Suite",
                "original_price": "RM 850",
                "discount_price": "RM 750",
                "total_price": "Total (incl. taxes & fees): RM 800",
                "_image_file": "hotel15.jpg",
                "booking_details": {}
            }
        ],
        "Osaka": [
            {
                "name": "Intercontinental Osaka",
                "stars": "★★★★★",
                "rating": "8.8",
                "feature_review": "City center",
                "location": "Umeda, Osaka",
                "room_type": "Deluxe Room",
                "original_price": "RM 750",
                "discount_price": "RM 680",
                "total_price": "Total (incl. taxes & fees): RM 720",
                "_image_file": "hotel16.jpg",
                "booking_details": {}
            }
        ],
        "Hanoi": [
            {
                "name": "Sofitel Legend Metropole",
                "stars": "★★★★★",
                "rating": "9.0",
                "feature_review": "Colonial charm",
                "location": "Hoan Kiem, Hanoi",
                "room_type": "Historic Room",
                "original_price": "RM 500",
                "discount_price": "RM 450",
                "total_price": "Total (incl. taxes & fees): RM 480",
                "_image_file": "hotel17.jpg",
                "booking_details": {}
            }
        ],
        "Ho Chi Minh": [
            {
                "name": "Park Hyatt Saigon",
                "stars": "★★★★★",
                "rating": "8.9",
                "feature_review": "French colonial style",
                "location": "District 1",
                "room_type": "Park King",
                "original_price": "RM 600",
                "discount_price": "RM 550",
                "total_price": "Total (incl. taxes & fees): RM 590",
                "_image_file": "hotel18.jpg",
                "booking_details": {}
            }
        ]
    }
}

if __name__ == "__main__":
    root = tk.Tk()
    Hotel(root, "user@example.com")
    root.mainloop()