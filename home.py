import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import subprocess
from PIL import Image, ImageTk
import tkinter.font as tkFont
import sys
from profile import Profile

class HomeApp:
    def __init__(self, root, email=None, user_name=None):
        self.root = root
        
        # Get user information from parameters
        self.email = email
        self.user_name = user_name
        
        # Try to load from session if user info not provided
        if not email or not user_name:
            self.load_user_session()
        
        # Profile menu status
        self.is_menu_open = False
        
        # Create custom fonts
        self.create_custom_fonts()
        
        # Ensure images folder exists
        if not os.path.exists('images'):
            os.makedirs('images')
        
        self.root.title(f"Traney - Home")
        # Auto fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f8ff')
        
        try:
            self.root.iconbitmap('car_icon.ico')
        except:
            pass

        # Promotion data - using local images
        self.current_promo_index = 0
        self.indicators = []
        self.promotions = [
            {
                "title": "Summer Vacation Sale",
                "desc": "Up to 50% off on flights to Bali",
                "price": "FROM RM 599",
                "image": "promo1.jpg",
                "page": "flight.py"
            },
            {
                "title": "Luxury Hotel Discount",
                "desc": "5-star hotels at 3-star prices",
                "price": "FROM RM 299/NIGHT",
                "image": "promo2.jpg",
                "page": "hotel.py"
            },
            {
                "title": "Car Rental Special",
                "desc": "Free upgrade on luxury car rentals",
                "price": "FROM RM 199/DAY",
                "image": "promo3.jpg",
                "page": "car_rental.py"
            }
        ]
        
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_header()
        
        # Initialize Profile here - important!
        self.profile_system = Profile(self.root, self.profile_btn, use_custom_menu=True)
        
        self.create_main_content()
        
        # Add shortcut to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        
        # Bind F11 for fullscreen toggle
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())

    def load_user_session(self):
        """Load user information from session file"""
        session_file = 'user_session.json'
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    self.email = session_data.get('email', 'user@example.com')
                    self.user_name = session_data.get('user_name', 'Guest User')
            except:
                self.email = 'user@example.com'
                self.user_name = 'Guest User'
        else:
            self.email = 'user@example.com'
            self.user_name = 'Guest User'

    def create_custom_fonts(self):
        """Create custom fonts"""
        # Create strikethrough font
        self.strike_font = tkFont.Font(family="Arial", size=14, overstrike=True)
        self.normal_font = tkFont.Font(family="Arial", size=14)
        self.bold_font = tkFont.Font(family="Arial", size=20, weight="bold")
        self.price_font = tkFont.Font(family="Arial", size=20, weight="bold")
        self.title_font = tkFont.Font(family="Arial", size=24, weight="bold")
        self.subtitle_font = tkFont.Font(family="Arial", size=16, weight="bold")
        self.menu_font = tkFont.Font(family="Arial", size=11)
        self.menu_bold_font = tkFont.Font(family="Arial", size=11, weight="bold")

    def lighten_color(self, color, amount=20):
        """Color lightening function"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = min(255, r + amount)
            g = min(255, g + amount)
            b = min(255, b + amount)
            
            return f'#{r:02x}{g:02x}{b:02x}'
        return color

    def create_header(self):
        """Create top navigation bar - consistent with Hotel page"""
        header = tk.Frame(self.root, bg='#1e3d59', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)  # Maintain fixed height
        
        # Logo section (click to return home)
        logo_frame = tk.Frame(header, bg='#1e3d59')
        logo_frame.pack(side='left', padx=30)
        logo_frame.bind("<Button-1>", lambda e: self.navigate_to_page("home.py"))
        
        tk.Label(logo_frame, text="🏠", font=("Arial", 28), bg='#1e3d59', fg="white").pack(side='left')
        
        logo_text = tk.Frame(logo_frame, bg='#1e3d59')
        logo_text.pack(side='left', padx=8)
        tk.Label(logo_text, text="Traney", font=("Arial", 22, "bold"), bg='#1e3d59', fg="white").pack()
        
        # Navigation menu
        nav_frame = tk.Frame(header, bg='#1e3d59')
        nav_frame.pack(side='left', padx=30)
        
        # Navigation items: (icon, text, script file)
        nav_items = [
            ("🏠", "Home", "home.py"),
            ("🏨", "Hotel", "hotel.py"),
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
            
            is_current = text == "Home"  # Current page is Home
            
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
                    b.config(bg='#2a4d6e') if t != "Home" else None)
            btn.bind("<Leave>", lambda e, b=btn, t=text: 
                    b.config(bg='#1e3d59') if t != "Home" else None)
        
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
        self.search_entry.insert(0, "Search...")
        self.search_entry.config(fg="gray")  # Gray placeholder text
        
        # Placeholder text handling
        def clear_placeholder(e):
            if self.search_entry.get() == "Search...":
                self.search_entry.delete(0, 'end')
                self.search_entry.config(fg="black")
        
        def add_placeholder(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search...")
                self.search_entry.config(fg="gray")
        
        self.search_entry.bind("<FocusIn>", clear_placeholder)
        self.search_entry.bind("<FocusOut>", add_placeholder)
        
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
        """Show dropdown menu"""
        if self.is_menu_open:
            return
            
        self.is_menu_open = True
        
        # Create menu window
        self.profile_menu = tk.Toplevel(self.root)
        self.profile_menu.title("")
        self.profile_menu.overrideredirect(True)  # Remove window borders
        self.profile_menu.configure(bg='white')
        
        # Add shadow effect
        self.profile_menu.attributes('-topmost', True)
        
        # Calculate menu position
        button_x = self.profile_btn.winfo_rootx()
        button_y = self.profile_btn.winfo_rooty()
        button_height = self.profile_btn.winfo_height()
        
        menu_width = 250
        menu_height = 350  # Reduced height since one menu item removed
        
        x = button_x - menu_width + self.profile_btn.winfo_width()
        y = button_y + button_height
        
        self.profile_menu.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
        
        # Create menu content
        self.create_menu_content()
        
        # Bind click outside to close menu
        self.profile_menu.bind("<FocusOut>", lambda e: self.hide_profile_menu())
        self.root.bind("<Button-1>", lambda e: self.check_click_outside(e))

    def create_menu_content(self):
        """Create menu content connected to profile.py - REMOVED "My Bookings" """
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
        
        # Menu options area - REMOVED "My Bookings"
        menu_options_frame = tk.Frame(main_container, bg='white')
        menu_options_frame.pack(fill='both', expand=True, padx=0, pady=10)
        
        # Menu options - REMOVED "My Bookings", only three items remain
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
        
        # Current session information
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
        """Check if clicked outside menu"""
        if self.is_menu_open and self.profile_menu:
            # Check if click position is inside menu window
            menu_x = self.profile_menu.winfo_rootx()
            menu_y = self.profile_menu.winfo_rooty()
            menu_width = self.profile_menu.winfo_width()
            menu_height = self.profile_menu.winfo_height()
            
            click_x = event.x_root
            click_y = event.y_root
            
            # Check if clicked profile button
            button_x = self.profile_btn.winfo_rootx()
            button_y = self.profile_btn.winfo_rooty()
            button_width = self.profile_btn.winfo_width()
            button_height = self.profile_btn.winfo_height()
            
            button_clicked = (button_x <= click_x <= button_x + button_width and 
                            button_y <= click_y <= button_y + button_height)
            
            # Check if clicked inside menu
            menu_clicked = (menu_x <= click_x <= menu_x + menu_width and 
                          menu_y <= click_y <= menu_y + menu_height)
            
            if not menu_clicked and not button_clicked:
                self.hide_profile_menu()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def create_main_content(self):
        """Create main content area"""
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#f0f8ff')
        self.main_container.pack(fill='both', expand=True)

        # Create scrollable frame
        self.create_scrollable_frame()
        
        # Image promotion carousel
        self.create_image_promotion_carousel()
        
        # Module quick access
        self.create_modern_module_cards()
        
        # Recommendations section - 1 recommendation per module, 4 modules total
        self.create_single_recommendations()
        
        # Add footer
        self.create_footer()

    def create_scrollable_frame(self):
        """Create scrollable frame"""
        main_frame = tk.Frame(self.main_container, bg='#f0f8ff')
        main_frame.pack(fill='both', expand=True)
        
        # Create Canvas and scrollbar
        self.canvas = tk.Canvas(main_frame, bg='#f0f8ff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        
        # Configure Canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack Canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f8ff')
        
        # Add scrollable frame to Canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure scroll region
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_image_promotion_carousel(self):
        """Create image promotion carousel"""
        title_frame = tk.Frame(self.scrollable_frame, bg='#f0f8ff')
        title_frame.pack(fill='x', padx=40, pady=(20, 15))
        
        banner_main = tk.Frame(title_frame, bg='#f0f8ff', height=80)
        banner_main.pack(fill='x')
        banner_main.pack_propagate(False)
        
        left_decoration = tk.Frame(banner_main, bg='#ff8c66', width=20, height=80)
        left_decoration.pack(side='left', fill='y')
        
        banner_content = tk.Frame(banner_main, bg='#1e3d59', height=80)
        banner_content.pack(side='left', fill='both', expand=True)
        banner_content.pack_propagate(False)
        
        title_container = tk.Frame(banner_content, bg='#1e3d59')
        title_container.pack(expand=True)
        
        left_fire = tk.Label(title_container, text="🔥", font=('Arial', 28), bg='#1e3d59', fg='#ff8c66')
        left_fire.pack(side='left', padx=(0, 15))
        
        tk.Label(title_container, text="HOT DEALS", 
                font=('Arial', 36, 'bold'), bg='#1e3d59', fg='white').pack(side='left', padx=5)
        
        right_fire = tk.Label(title_container, text="🔥", font=('Arial', 28), bg='#1e3d59', fg='#ff8c66')
        right_fire.pack(side='left', padx=(15, 0))
        
        bottom_line = tk.Frame(title_frame, bg='#ff8c66', height=3)
        bottom_line.pack(fill='x', pady=(5, 0))
        
        self.promo_display_frame = tk.Frame(self.scrollable_frame, bg='#f0f8ff', height=600)
        self.promo_display_frame.pack(fill='x', padx=40, pady=(0, 20))
        self.promo_display_frame.pack_propagate(False)
        
        nav_frame = tk.Frame(self.scrollable_frame, bg='#f0f8ff')
        nav_frame.pack(fill='x', padx=40, pady=(0, 40))
        
        left_nav_btn = tk.Button(nav_frame, text="◀", 
                               font=('Arial', 16, 'bold'),
                               bg='#1e3d59', fg='white',
                               relief='flat', cursor='hand2',
                               width=3, height=1,
                               command=self.show_previous_promotion)
        left_nav_btn.pack(side='left', padx=(0, 20))
        
        indicator_frame = tk.Frame(nav_frame, bg='#f0f8ff')
        indicator_frame.pack(side='left', expand=True)
        
        self.indicators = []
        for i in range(len(self.promotions)):
            indicator = tk.Label(indicator_frame, text="●", 
                               font=('Arial', 20),
                               fg='#cccccc' if i != 0 else '#ff8c66',
                               bg='#f0f8ff',
                               cursor='hand2')
            indicator.pack(side='left', padx=5)
            indicator.bind("<Button-1>", lambda e, idx=i: self.show_promotion_by_index(idx))
            self.indicators.append(indicator)
        
        right_nav_btn = tk.Button(nav_frame, text="▶", 
                                font=('Arial', 16, 'bold'),
                                bg='#1e3d59', fg='white',
                                relief='flat', cursor='hand2',
                                width=3, height=1,
                                command=self.show_next_promotion)
        right_nav_btn.pack(side='right')
        
        def add_hover_effect(btn):
            btn.bind("<Enter>", lambda e: btn.config(bg='#ff8c66'))
            btn.bind("<Leave>", lambda e: btn.config(bg='#1e3d59'))
        
        add_hover_effect(left_nav_btn)
        add_hover_effect(right_nav_btn)
        
        self.show_current_promotion()

    def show_promotion_by_index(self, index):
        """Show promotion by index"""
        self.current_promo_index = index
        self.show_current_promotion()

    def show_current_promotion(self):
        """Show current promotion"""
        for widget in self.promo_display_frame.winfo_children():
            widget.destroy()
        
        promo = self.promotions[self.current_promo_index]
        
        # Use local image
        try:
            # Try to load local image
            img_path = promo["image"]
            
            if not os.path.exists(img_path):
                # Check images folder
                img_path = os.path.join("images", promo["image"])
                if not os.path.exists(img_path):
                    # Use default background if local image not found
                    raise FileNotFoundError(f"Image not found: {promo['image']}")
            
            img = Image.open(img_path)
            
            frame_width = 1200
            frame_height = 500
            
            img_width, img_height = img.size
            target_width = frame_width
            target_height = int(img_height * (target_width / img_width))
            
            if target_height > frame_height:
                target_height = frame_height
                target_width = int(img_width * (target_height / img_height))
            
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(self.promo_display_frame, image=photo, bg='#f0f8ff')
            img_label.image = photo
            img_label.pack(fill='both', expand=True)
            
            # Add click event
            img_label.bind("<Button-1>", lambda e, p=promo['page']: self.navigate_to_page(p))
            
        except Exception as e:
            print(f"Using default background: {e}")
            # Create default background
            default_frame = tk.Frame(self.promo_display_frame, bg='#1e3d59', height=500)
            default_frame.pack(fill='both', expand=True)
            default_frame.pack_propagate(False)
            
            content_frame = tk.Frame(default_frame, bg='#1e3d59')
            content_frame.pack(expand=True)
            
            # Add icon
            icon_label = tk.Label(content_frame, text="🔥", font=('Arial', 80),
                               bg='#1e3d59', fg='#ff8c66')
            icon_label.pack(pady=(0, 20))
            
            # Add text content
            tk.Label(content_frame, text=promo['title'], 
                    font=('Arial', 32, 'bold'), bg='#1e3d59', fg='white').pack(pady=(0, 15))
            
            tk.Label(content_frame, text=promo['desc'], 
                    font=('Arial', 18), bg='#1e3d59', fg='#ff8c66').pack(pady=(0, 20))
            
            tk.Label(content_frame, text=promo['price'], 
                    font=('Arial', 28, 'bold'), bg='#1e3d59', fg='#ff8c66').pack(pady=(0, 30))
            
            # Add click event
            default_frame.bind("<Button-1>", lambda e, p=promo['page']: self.navigate_to_page(p))
            content_frame.bind("<Button-1>", lambda e, p=promo['page']: self.navigate_to_page(p))
        
        if hasattr(self, 'indicators'):
            for i, indicator in enumerate(self.indicators):
                if i == self.current_promo_index:
                    indicator.config(fg='#ff8c66')
                else:
                    indicator.config(fg='#cccccc')

    def show_next_promotion(self):
        """Show next promotion"""
        self.current_promo_index = (self.current_promo_index + 1) % len(self.promotions)
        self.show_current_promotion()

    def show_previous_promotion(self):
        """Show previous promotion"""
        self.current_promo_index = (self.current_promo_index - 1) % len(self.promotions)
        self.show_current_promotion()

    def create_modern_module_cards(self):
        """Create modern module cards"""
        section_frame = tk.Frame(self.scrollable_frame, bg='#f0f8ff')
        section_frame.pack(fill='x', padx=40, pady=(0, 60))
        
        title_frame = tk.Frame(section_frame, bg='#f0f8ff')
        title_frame.pack(fill='x', pady=(0, 40))
        
        tk.Label(title_frame, text="OUR SERVICES", 
                font=('Arial', 32, 'bold'), bg='#f0f8ff', fg='#1e3d59').pack(anchor='center')
        
        tk.Label(title_frame, text="Everything you need for a perfect journey", 
                font=('Arial', 16), bg='#f0f8ff', fg='#666666').pack(anchor='center', pady=(10, 0))
        
        modules_container = tk.Frame(section_frame, bg='#f0f8ff')
        modules_container.pack(fill='x')
        
        modules = [
            {
                "name": "Flight ",
                "desc": "Search and book flights worldwide with best prices",
                "module": "flight.py",
                "color": "#3498db",
                "icon": "    ✈️",
                "image": "flight_recommend.jpg"
            },
            {
                "name": "Hotel ", 
                "desc": "Find and book hotels, resorts, and apartments",
                "module": "hotel.py",
                "color": "#e74c3c",
                "icon": "🏨",
                "image": "hotel_recommend.jpg"
            },
            {
                "name": "Car Rental",
                "desc": "Rent cars, SUVs, and luxury vehicles for your trip",
                "module": "car_rental.py",
                "color": "#2ecc71",
                "icon": "🚗",
                "image": "car_recommend.jpg"
            },
            {
                "name": "Attractions",
                "desc": "Discover amazing places and book tours",
                "module": "attraction.py",
                "color": "#9b59b6",
                "icon": "    🏛️",
                "image": "attraction_recommend.jpg"
            },
            {
                "name": "Travel Plan",
                "desc": "Plan your perfect itinerary with our tools",
                "module": "travel_plan.py",
                "color": "#f39c12",
                "icon": "    🗺️",
            },
            {
                "name": "Packing List",
                "desc": "Create and manage packing lists for any trip",
                "module": "packing.py",
                "color": "#1abc9c",
                "icon": "🎒",
                "image": "packing_bg.jpg"
            }
        ]
        
        for row in range(2):
            row_frame = tk.Frame(modules_container, bg='#f0f8ff')
            row_frame.pack(fill='x', pady=(0, 25))
            
            for col in range(3):
                module_index = row * 3 + col
                if module_index < len(modules):
                    module = modules[module_index]
                    self.create_premium_module_card(row_frame, module, col)

    def create_premium_module_card(self, parent, module_data, column):
        """Create premium module card"""
        card_frame = tk.Frame(parent, bg='white', relief='groove', bd=2, 
                             width=400, height=220, cursor='hand2')
        
        if column == 0:
            card_frame.pack(side='left', fill='both', expand=True)
        elif column == 1:
            card_frame.pack(side='left', fill='both', expand=True, padx=30)
        else:
            card_frame.pack(side='left', fill='both', expand=True)
        
        card_frame.pack_propagate(False)
        
        card_frame.bind("<Button-1>", lambda e, m=module_data['module']: self.navigate_to_page(m))
        
        color_bar = tk.Frame(card_frame, bg=module_data['color'], height=5)
        color_bar.pack(fill='x')
        
        main_content = tk.Frame(card_frame, bg='white')
        main_content.pack(fill='both', expand=True, padx=25, pady=25)
        
        left_frame = tk.Frame(main_content, bg='white')
        left_frame.pack(side='left', fill='y')
        
        icon_frame = tk.Frame(left_frame, bg='#f8f9fa', width=60, height=60)
        icon_frame.pack(pady=(0, 15))
        icon_frame.pack_propagate(False)
        
        tk.Label(icon_frame, text=module_data['icon'], 
                font=('Arial', 28), bg='#f8f9fa', fg=module_data['color']).pack(expand=True)
        
        right_frame = tk.Frame(main_content, bg='white')
        right_frame.pack(side='left', fill='both', expand=True, padx=(20, 0))
        
        tk.Label(right_frame, text=module_data['name'], 
                font=('Arial', 18, 'bold'), bg='white', fg='#1e3d59').pack(anchor='w', pady=(0, 10))
        
        tk.Label(right_frame, text=module_data['desc'], 
                font=('Arial', 12), bg='white', fg='#666666',
                wraplength=220, justify='left').pack(anchor='w', pady=(0, 20))
        
        access_btn = tk.Button(right_frame, text="Explore →",
                            font=('Arial', 12, 'bold'), bg=module_data['color'], fg='white',
                            relief='flat', cursor='hand2',
                            padx=20, pady=8,
                            command=lambda m=module_data['module']: self.navigate_to_page(m))
        access_btn.pack(anchor='w')
        
        def on_enter(e):
            card_frame.config(bg='#f8f9fa')
            access_btn.config(bg=self.lighten_color(module_data['color'], 20))
            
        def on_leave(e):
            card_frame.config(bg='white')
            access_btn.config(bg=module_data['color'])
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        access_btn.bind("<Enter>", on_enter)
        access_btn.bind("<Leave>", on_leave)

    def create_single_recommendations(self):
        """Create single recommendation section - 1 recommendation per module, 4 total"""
        title_frame = tk.Frame(self.scrollable_frame, bg='#f0f8ff')
        title_frame.pack(fill='x', padx=40, pady=(20, 30))
        
        tk.Label(title_frame, text="🌟 TOP RECOMMENDATIONS", 
                font=('Arial', 32, 'bold'), bg='#f0f8ff', fg='#1e3d59').pack(anchor='center')
        
        tk.Label(title_frame, text="Our top picks from each category", 
                font=('Arial', 16), bg='#f0f8ff', fg='#666666').pack(anchor='center', pady=(10, 0))
        
        # Recommendations content frame
        self.recommendations_content = tk.Frame(self.scrollable_frame, bg='#f0f8ff')
        self.recommendations_content.pack(fill='x', padx=40, pady=(0, 40))
        
        # Create recommendations for all 4 modules
        self.create_all_recommendations()

    def create_all_recommendations(self):
        """Create recommendations for all 4 modules"""
        for widget in self.recommendations_content.winfo_children():
            widget.destroy()
        
        # Hotel recommendation (1)
        hotels = [
            {
                "id": "HTL001",
                "name": "Shanghai Sky Hotel",
                "location": "Shanghai, China",
                "address": "No. 123 Nanjing Road, Shanghai",
                "price": 499,
                "discount_price": 449,
                "currency": "RM",
                "unit": "/night",
                "rating": 4.8,
                "reviews": 1284,
                "image_file": "hotel_recommend.jpg",  # Use local file
                "tag": "City View",
                "features": ["Bund View", "Infinity Pool", "Spa", "Free WiFi", "Breakfast Included"],
                "description": "Luxury hotel with stunning views of The Bund. Perfect for business and leisure travelers.",
                "check_in": "14:00",
                "check_out": "12:00",
                "room_types": ["Deluxe King", "Executive Suite", "Presidential Suite"],
                "amenities": ["Swimming Pool", "Spa", "Fitness Center", "Restaurant", "Bar"],
                "category": "hotel"
            }
        ]
        
        # Flight recommendation (1)
        flights = [
            {
                "id": "FLT001",
                "name": "Kuala Lumpur → Seoul",
                "location": "Kuala Lumpur to Seoul",
                "airline": "Korean Air",
                "flight_no": "KE672",
                "departure": "KUL 08:00",
                "arrival": "ICN 15:45",
                "price": 1899,
                "discount_price": 1799,
                "currency": "RM",
                "unit": "/person",
                "rating": 4.8,
                "duration": "6h 45m",
                "type": "Direct",
                "image_file": "flight_recommend.jpg",  # Use local file
                "features": ["Business Class", "Korean Meal", "Entertainment System", "30kg Baggage", "Priority Boarding"],
                "description": "Direct flight from Kuala Lumpur to Seoul with award-winning Korean Air service.",
                "aircraft": "Boeing 777-300ER",
                "amenities": ["In-flight Entertainment", "Meal Service", "Complimentary Drinks", "WiFi", "USB Ports"],
                "category": "flight"
            }
        ]
        
        # Car rental recommendation (1)
        cars = [
            {
                "id": "CAR001",
                "name": "Toyota Camry",
                "location": "Kuala Lumpur, Malaysia",
                "type": "Sedan",
                "brand": "Toyota",
                "model_year": 2023,
                "price": 159,
                "discount_price": 139,
                "currency": "RM",
                "unit": "/day",
                "rating": 4.7,
                "transmission": "Automatic",
                "seats": 5,
                "image_file": "car_recommend.jpg",  # Use local file
                "tag": "Economical",
                "features": ["Fuel Efficient", "GPS Navigation", "Bluetooth", "Air Conditioning", "USB Ports"],
                "description": "Reliable and fuel-efficient sedan perfect for city driving and road trips.",
                "fuel_type": "Petrol",
                "mileage": "Unlimited",
                "insurance": "Comprehensive",
                "pickup_locations": ["KUL Airport", "Downtown KL", "KL Sentral"],
                "category": "car"
            }
        ]
        
        # Attraction recommendation (1)
        attractions = [
            {
                "id": "ATT001",
                "name": "Tokyo Disneyland",
                "location": "Tokyo, Japan",
                "address": "1-1 Maihama, Urayasu, Chiba 279-0031",
                "price": 299,
                "discount_price": 269,
                "currency": "RM",
                "unit": "/adult",
                "rating": 4.9,
                "duration": "Full Day",
                "image_file": "attraction_recommend.jpg",  # Use local file
                "tag": "Theme Park",
                "features": ["All-day Ticket", "Fast Pass Available", "Character Meet", "Parade", "Fireworks"],
                "description": "The magical kingdom where dreams come true. Experience Disney magic in Tokyo!",
                "operating_hours": "08:00 - 22:00",
                "best_time": "Weekdays morning",
                "includes": ["Park Admission", "Map", "Show Schedule"],
                "category": "attraction"
            }
        ]
        
        # Combine all recommendations
        all_recommendations = hotels + flights + cars + attractions
        
        # Create cards container
        cards_frame = tk.Frame(self.recommendations_content, bg='#f0f8ff')
        cards_frame.pack(fill='both', expand=True)
        
        # Create card for each recommendation
        for i, item in enumerate(all_recommendations):
            card = self.create_recommendation_card(cards_frame, item, i)
            if i < len(all_recommendations) - 1:
                card.pack(side='left', fill='both', expand=True, padx=(0, 20))
            else:
                card.pack(side='left', fill='both', expand=True)

    def create_recommendation_card(self, parent, item_data, index):
        """Create recommendation card"""
        card_width = 280
        card_height = 450
        
        # Main card frame
        card = tk.Frame(parent, bg='white', relief='flat',
                       highlightbackground='#e0e0e0', highlightthickness=1,
                       width=card_width, height=card_height, cursor='hand2')
        card.pack_propagate(False)
        
        # Bind click event - now calls external detail page
        card.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        
        # Image area
        img_frame = tk.Frame(card, bg='#f5f5f5', height=180)
        img_frame.pack(fill='x')
        img_frame.pack_propagate(False)
        
        # Load local image
        image_file = item_data.get("image_file", "")
        if image_file:
            photo = self.load_local_image(image_file, size=(card_width, 180))
            if photo:
                image_label = tk.Label(img_frame, image=photo, bg='#f5f5f5')
                image_label.image = photo
                image_label.pack(fill='both', expand=True)
                image_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
            else:
                # Create default image
                self.create_default_image(img_frame, item_data, index)
        else:
            # Create default image if no image file specified
            self.create_default_image(img_frame, item_data, index)
        
        # Content area
        content_frame = tk.Frame(card, bg='white')
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Name
        name_label = tk.Label(content_frame, text=item_data['name'], 
                font=('Arial', 14, 'bold'), bg='white', fg='#1e3d59',
                wraplength=card_width-30, justify='left')
        name_label.pack(anchor='w', pady=(0, 5))
        name_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        
        # Location - ensure item_data has location field
        location_text = f"📍 {item_data.get('location', 'Not specified')}"
        location_label = tk.Label(content_frame, text=location_text, 
                font=('Arial', 11), bg='white', fg='#666666')
        location_label.pack(anchor='w', pady=(0, 8))
        location_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        
        # Tag
        if 'tag' in item_data:
            tag_label = tk.Label(content_frame, text=item_data['tag'], 
                               font=('Arial', 9, 'bold'),
                               bg='#e8f4f8', fg='#3498db',
                               padx=6, pady=2)
            tag_label.pack(anchor='w', pady=(0, 8))
            tag_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        
        # Description
        description = item_data['description'][:60] + "..." if len(item_data['description']) > 60 else item_data['description']
        desc_label = tk.Label(content_frame, text=description, 
                font=('Arial', 10), bg='white', fg='#555555',
                wraplength=card_width-30, justify='left')
        desc_label.pack(anchor='w', pady=(0, 15))
        desc_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        
        # Bottom area
        bottom_frame = tk.Frame(content_frame, bg='white')
        bottom_frame.pack(fill='x', side='bottom')
        
        # Price
        price_frame = tk.Frame(bottom_frame, bg='white')
        price_frame.pack(side='left', fill='y')
        
        # Create fonts
        strike_font = tkFont.Font(family="Arial", size=10, overstrike=True)
        price_font = tkFont.Font(family="Arial", size=14, weight="bold")
        
        if item_data.get('discount_price'):
            # Original price
            original_price = tk.Label(price_frame, 
                    text=f"{item_data['currency']} {item_data['price']}{item_data['unit']}", 
                    font=strike_font, bg='white', fg='#999999')
            original_price.pack(anchor='w')
            original_price.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
            
            # Discount price
            discount_price = tk.Label(price_frame, 
                    text=f"{item_data['currency']} {item_data['discount_price']}{item_data['unit']}", 
                    font=price_font, bg='white', fg='#ff8c66')
            discount_price.pack(anchor='w', pady=(2, 0))
            discount_price.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        else:
            # Normal price
            price_label = tk.Label(price_frame, 
                    text=f"{item_data['currency']} {item_data['price']}{item_data['unit']}", 
                    font=price_font, bg='white', fg='#ff8c66')
            price_label.pack(anchor='w')
            price_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))
        
        # View details button - now opens external detail page
        view_btn = tk.Button(bottom_frame, text="View →",
                           font=('Arial', 10, 'bold'),
                           bg='#1e3d59', fg='white',
                           relief='flat', cursor='hand2',
                           padx=12, pady=4,
                           command=lambda data=item_data: self.open_detail_page(data))
        view_btn.pack(side='right')
        
        # Hover effects
        def on_enter(e):
            card.config(bg='#f8f9fa')
            view_btn.config(bg='#ff8c66')
            
        def on_leave(e):
            card.config(bg='white')
            view_btn.config(bg='#1e3d59')
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        view_btn.bind("<Enter>", on_enter)
        view_btn.bind("<Leave>", on_leave)
        
        return card

    def create_default_image(self, parent, item_data, index):
        """Create default image"""
        colors = ['#1e3d59', '#ff8c66', '#2ecc71', '#9b59b6']
        color_index = index % len(colors)
        placeholder = tk.Frame(parent, bg=colors[color_index])
        placeholder.pack(fill='both', expand=True)
        
        # Select icon based on category
        if item_data['category'] == 'hotel':
            icon = "🏨"
        elif item_data['category'] == 'flight':
            icon = "✈️"
        elif item_data['category'] == 'car':
            icon = "🚗"
        elif item_data['category'] == 'attraction':
            icon = "🏛️"
        else:
            icon = "⭐"
            
        placeholder_label = tk.Label(placeholder, text=icon, font=('Arial', 40),
                bg=colors[color_index], fg='white')
        placeholder_label.pack(expand=True)
        placeholder_label.bind("<Button-1>", lambda e, data=item_data: self.open_detail_page(data))

    def load_local_image(self, filename, size=(300, 200)):
        """Load image from local file"""
        try:
            # First check current directory
            img_path = filename
            if not os.path.exists(img_path):
                # Check images folder
                img_path = os.path.join("images", filename)
                if not os.path.exists(img_path):
                    # Return None if still not found
                    return None
            
            img = Image.open(img_path)
            
            # Convert to RGB mode
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            return photo
            
        except Exception as e:
            print(f"Error loading local image {filename}: {e}")
            return None

    def open_detail_page(self, item_data):
        """Open external detail page"""
        # Save data to temp file
        if not os.path.exists('temp'):
            os.makedirs('temp')
        
        temp_file = os.path.join('temp', 'current_item.json')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(item_data, f, indent=2, ensure_ascii=False)
        
        # Call external detail page
        try:
            # Close current window and open detail page
            self.root.destroy()
            subprocess.Popen(["python", "detail_page.py", temp_file])
        except Exception as e:
            print(f"Error opening detail page: {e}")
            # Show error message if cannot open detail page
            messagebox.showerror("Error", f"Cannot open detail page: {str(e)}\n\nMake sure detail_page.py is in the same directory.")

    def create_footer(self):
        """Create footer"""
        footer_frame = tk.Frame(self.scrollable_frame, bg='#1e3d59')
        footer_frame.pack(fill='x', pady=(50, 0))
        
        footer_content = tk.Frame(footer_frame, bg='#1e3d59')
        footer_content.pack(fill='both', expand=True, padx=50, pady=30)
        
        about_frame = tk.Frame(footer_content, bg='#1e3d59')
        about_frame.pack(side='left', fill='y', padx=(0, 50))
        
        tk.Label(about_frame, text="About Us", font=('Arial', 18, 'bold'),
                fg='white', bg='#1e3d59').pack(anchor='w', pady=(0, 15))
        tk.Label(about_frame, text="Traney provides comprehensive travel services including flights, hotels, car rentals, and attractions worldwide.",
                font=('Arial', 12), fg='#ff8c66', bg='#1e3d59', wraplength=300, justify='left').pack(anchor='w')
        
        contact_frame = tk.Frame(footer_content, bg='#1e3d59')
        contact_frame.pack(side='left', fill='y', padx=(0, 50))
        
        tk.Label(contact_frame, text="Contact Us", font=('Arial', 18, 'bold'),
                fg='white', bg='#1e3d59').pack(anchor='w', pady=(0, 15))
        
        contacts = [
            ("📞", "+60 3-1234 5678"),
            ("📧", "support@traney.com"),
            ("📍", "Kuala Lumpur, Malaysia")
        ]
        
        for icon, text in contacts:
            contact_item = tk.Frame(contact_frame, bg='#1e3d59')
            contact_item.pack(anchor='w', pady=5)
            tk.Label(contact_item, text=icon, font=('Arial', 12),
                    fg='#ff8c66', bg='#1e3d59').pack(side='left')
            tk.Label(contact_item, text=text, font=('Arial', 12),
                    fg='white', bg='#1e3d59').pack(side='left', padx=(8, 0))
        
        social_frame = tk.Frame(footer_content, bg='#1e3d59')
        social_frame.pack(side='left', fill='y')
        
        tk.Label(social_frame, text="Follow Us", font=('Arial', 18, 'bold'),
                fg='white', bg='#1e3d59').pack(anchor='w', pady=(0, 15))
        
        social_icons = ["📘", "🐦", "📷", "▶️"]
        social_frame_icons = tk.Frame(social_frame, bg='#1e3d59')
        social_frame_icons.pack(anchor='w')
        
        for icon in social_icons:
            btn = tk.Button(social_frame_icons, text=icon, font=('Arial', 16),
                     bg='#1e3d59', fg='white', relief='flat',
                     cursor='hand2')
            btn.pack(side='left', padx=(0, 12))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#2c3e50'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#1e3d59'))
        
        copyright_frame = tk.Frame(footer_frame, bg='#1e3d59')
        copyright_frame.pack(fill='x', padx=50, pady=(0, 20))
        
        tk.Label(copyright_frame, text="© 2024 Traney Travel. All rights reserved.",
                font=('Arial', 11), fg='#cccccc', bg='#1e3d59').pack()

    def navigate_to_page(self, script_file):
        """Navigate to other page"""
        if script_file == "home.py":
            return
        
        if os.path.exists(script_file):
            try:
                # Save current user info to session
                session_data = {
                    'email': self.email,
                    'user_name': self.user_name
                }
                with open('user_session.json', 'w') as f:
                    json.dump(session_data, f)
                
                self.root.destroy()
                subprocess.Popen(["python", script_file])
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open {script_file}: {str(e)}")
        else:
            messagebox.showinfo("Coming Soon", f"The {script_file.split('.')[0]} module is under development!")

def main():
    """Main function for standalone run"""
    root = tk.Tk()
    
    # Get user info from command line arguments
    if len(sys.argv) > 2:
        email = sys.argv[1]
        user_name = sys.argv[2]
        app = HomeApp(root, email=email, user_name=user_name)
    else:
        app = HomeApp(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()