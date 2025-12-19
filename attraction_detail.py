import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import io
from datetime import datetime, timedelta
import os
import time
import webbrowser
import random
import gc

class CalendarPopup:
    def __init__(self, parent, callback, initial_date=None):
        self.parent = parent
        self.callback = callback
        self.selected_date = initial_date or datetime.now()
        
        # Create popup window
        self.popup = tk.Toplevel(parent)
        self.popup.title("Select Date")
        self.popup.geometry("400x350")
        self.popup.configure(bg="white")
        self.popup.resizable(False, False)
        
        # Make popup modal
        self.popup.transient(parent)
        self.popup.grab_set()
        
        # Center the popup
        self.popup.geometry("+%d+%d" % (
            parent.winfo_rootx() + parent.winfo_width() // 2 - 200,
            parent.winfo_rooty() + parent.winfo_height() // 2 - 175
        ))
        
        # Color scheme
        self.colors = {
            "primary": "#1e3d59",
            "secondary": "#ff6e40",
            "light": "#f8fafc",
            "dark": "#1e3d59",
            "border": "#e2e8f0",
        }
        
        # Current date for calendar display
        self.current_date = datetime.now()
        
        # Create calendar UI
        self.create_calendar_ui()
        
        # Bind escape key to close
        self.popup.bind("<Escape>", lambda e: self.popup.destroy())
    
    def create_calendar_ui(self):
        """Create calendar UI"""
        # Header frame
        header_frame = tk.Frame(self.popup, bg="white", padx=20, pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Select Visit Date", 
                font=("Segoe UI", 16, "bold"),
                bg="white", fg=self.colors["primary"]).pack()
        
        # Navigation frame
        nav_frame = tk.Frame(self.popup, bg="white", padx=20)
        nav_frame.pack(fill="x", pady=(0, 10))
        
        # Month and year label
        self.month_year_label = tk.Label(nav_frame, 
                                        font=("Segoe UI", 14, "bold"),
                                        bg="white", fg=self.colors["primary"])
        self.month_year_label.pack(side="left", expand=True)
        
        # Navigation buttons
        prev_btn = tk.Button(nav_frame, text="←", font=("Segoe UI", 12),
                            bg=self.colors["light"], fg=self.colors["primary"],
                            relief="solid", width=3, cursor="hand2",
                            command=self.prev_month)
        prev_btn.pack(side="left", padx=(0, 5))
        self.add_hover_effect(prev_btn, "#e2e8f0", self.colors["light"])
        
        today_btn = tk.Button(nav_frame, text="Today", font=("Segoe UI", 12),
                             bg=self.colors["primary"], fg="white",
                             relief="solid", cursor="hand2",
                             command=self.go_to_today)
        today_btn.pack(side="left", padx=5)
        self.add_hover_effect(today_btn, "#2a4d6e", self.colors["primary"])
        
        next_btn = tk.Button(nav_frame, text="→", font=("Segoe UI", 12),
                            bg=self.colors["light"], fg=self.colors["primary"],
                            relief="solid", width=3, cursor="hand2",
                            command=self.next_month)
        next_btn.pack(side="left", padx=(5, 0))
        self.add_hover_effect(next_btn, "#e2e8f0", self.colors["light"])
        
        # Calendar grid frame
        self.calendar_frame = tk.Frame(self.popup, bg="white", padx=20, pady=10)
        self.calendar_frame.pack(fill="both", expand=True)
        
        # Update and generate calendar
        self.update_month_year_label()
        self.generate_calendar()
        
        # Selected date display
        selected_frame = tk.Frame(self.popup, bg="white", padx=20, pady=10)
        selected_frame.pack(fill="x")
        
        tk.Label(selected_frame, text="Selected:",
                font=("Segoe UI", 12),
                bg="white", fg=self.colors["primary"]).pack(side="left")
        
        self.selected_date_label = tk.Label(selected_frame, 
                                           text=self.selected_date.strftime("%B %d, %Y"),
                                           font=("Segoe UI", 12, "bold"),
                                           bg="white", fg=self.colors["secondary"])
        self.selected_date_label.pack(side="left", padx=(10, 0))
        
        # Action buttons
        action_frame = tk.Frame(self.popup, bg="white", padx=20, pady=10)
        action_frame.pack(fill="x")
        
        cancel_btn = tk.Button(action_frame, text="Cancel",
                              font=("Segoe UI", 12),
                              bg=self.colors["light"], fg=self.colors["primary"],
                              relief="solid", cursor="hand2",
                              command=self.popup.destroy,
                              width=10)
        cancel_btn.pack(side="left", padx=(0, 10))
        self.add_hover_effect(cancel_btn, "#e2e8f0", self.colors["light"])
        
        select_btn = tk.Button(action_frame, text="Select",
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors["primary"], fg="white",
                              relief="solid", cursor="hand2",
                              command=self.select_date,
                              width=10)
        select_btn.pack(side="right")
        self.add_hover_effect(select_btn, "#2a4d6e", self.colors["primary"])
    
    def generate_calendar(self):
        """Generate calendar days"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Create day headers
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            day_label = tk.Label(self.calendar_frame, text=day,
                                font=("Segoe UI", 10, "bold"),
                                bg="white", fg=self.colors["primary"],
                                width=5, height=1)
            day_label.grid(row=0, column=i, padx=2, pady=2)
        
        # Get first day of month and number of days
        year = self.current_date.year
        month = self.current_date.month
        first_day = datetime(year, month, 1)
        
        # Get day of week (0=Monday, 6=Sunday)
        first_day_weekday = first_day.weekday()  # 0=Monday
        # Convert to 0=Sunday format
        first_day_weekday = (first_day_weekday + 1) % 7
        
        # Get number of days in month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        days_in_month = (next_month - first_day).days
        
        # Generate day buttons
        day_num = 1
        for week in range(6):  # Max 6 weeks in a month
            for day in range(7):  # 7 days a week
                if (week == 0 and day < first_day_weekday) or day_num > days_in_month:
                    # Empty cell
                    tk.Label(self.calendar_frame, text="",
                            bg="white", width=5, height=2).grid(row=week+1, column=day, padx=2, pady=2)
                else:
                    # Create day button
                    day_date = datetime(year, month, day_num)
                    is_today = day_date.date() == datetime.now().date()
                    is_selected = day_date.date() == self.selected_date.date()
                    is_past = day_date.date() < datetime.now().date()
                    
                    # Determine button style
                    if is_selected:
                        bg_color = self.colors["secondary"]
                        fg_color = "white"
                        relief = "solid"
                    elif is_today:
                        bg_color = self.colors["light"]
                        fg_color = self.colors["primary"]
                        relief = "solid"
                    elif is_past:
                        bg_color = "#f8fafc"
                        fg_color = "#cbd5e1"
                        relief = "flat"
                    else:
                        bg_color = "white"
                        fg_color = self.colors["dark"]
                        relief = "solid"
                    
                    # Create day button
                    day_btn = tk.Button(self.calendar_frame, text=str(day_num),
                                      font=("Segoe UI", 10),
                                      bg=bg_color, fg=fg_color,
                                      relief=relief, borderwidth=1,
                                      width=4, height=1, cursor="hand2",
                                      command=lambda d=day_date: self.set_selected_date(d))
                    day_btn.grid(row=week+1, column=day, padx=2, pady=2)
                    
                    # Add hover effect for future dates only
                    if not is_past:
                        day_btn.bind("<Enter>", 
                                   lambda e, btn=day_btn: btn.config(bg="#e2e8f0") if btn.cget("state") != "disabled" else None)
                        day_btn.bind("<Leave>", 
                                   lambda e, btn=day_btn, bg=bg_color: btn.config(bg=bg) if btn.cget("state") != "disabled" else None)
                    
                    # Disable past dates
                    if is_past:
                        day_btn.config(state="disabled")
                    
                    day_num += 1
    
    def set_selected_date(self, date):
        """Set selected date"""
        self.selected_date = date
        self.selected_date_label.config(text=date.strftime("%B %d, %Y"))
        self.generate_calendar()  # Refresh to update selection
    
    def select_date(self):
        """Select the date and close popup"""
        self.callback(self.selected_date)
        self.popup.destroy()
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_date.month == 1:
            self.current_date = datetime(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month - 1, 1)
        
        self.update_month_year_label()
        self.generate_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_date.month == 12:
            self.current_date = datetime(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month + 1, 1)
        
        self.update_month_year_label()
        self.generate_calendar()
    
    def go_to_today(self):
        """Go to today's date"""
        self.current_date = datetime.now()
        self.set_selected_date(self.current_date)
        self.update_month_year_label()
        self.generate_calendar()
    
    def update_month_year_label(self):
        """Update month and year label"""
        month_year = self.current_date.strftime("%B %Y")
        self.month_year_label.config(text=month_year)
    
    def add_hover_effect(self, widget, hover_color, normal_color):
        """Add hover effect to widget"""
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color) if widget.cget("state") != "disabled" else None)
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color) if widget.cget("state") != "disabled" else None)

class AttractionDetailApp:
    def __init__(self, root, attraction, email):
        self.root = root
        self.attraction = attraction
        self.email = email
        
        # Set full screen by default
        self.root.title(f"Traney - {attraction['name']}")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f8ff")
        
        # Color scheme
        self.colors = {
            "primary": "#1e3d59",
            "secondary": "#ff6e40",
            "accent": "#ff8c66",
            "light": "#f8fafc",
            "dark": "#1e3d59",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "card_bg": "#ffffff",
            "sidebar_bg": "#ffffff",
            "nav_bg": "#1e3d59",
            "nav_active": "#ff6e40",
            "text_light": "#64748b",
            "border": "#e2e8f0",
            "footer_bg": "#1e3d59",
            "footer_text": "#b0c4de",
        }
        
        # Ensure attraction has all required fields
        self.ensure_attraction_fields()
        
        # Image cache
        self.image_cache = {}
        
        # Selected date
        self.selected_date = datetime.now()
        
        # Create UI
        self.setup_ui()
        
        # Bind Escape key to toggle fullscreen
        self.root.bind("<Escape>", self.toggle_fullscreen)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def ensure_attraction_fields(self):
        """Ensure the attraction has all required fields"""
        default_fields = {
            "best_time": "9:00 AM - 5:00 PM",
            "phone": "Not specified",
            "website": "Not available",
            "opening_hours": "9:00 AM - 5:00 PM",
            "address": "Address not available",
            "accessibility": "Generally accessible",
            "highlights": ["Scenic views", "Cultural significance", "Photo opportunities"],
            "facilities": ["Parking", "Restrooms", "Guided tours"],
            "color": "#6c5b7b"
        }
        
        for field, default_value in default_fields.items():
            if field not in self.attraction:
                self.attraction[field] = default_value
        
        # Ensure tags exist
        if "tags" not in self.attraction or not self.attraction["tags"]:
            self.attraction["tags"] = [self.attraction.get("category", "Attraction")]
    
    def setup_ui(self):
        """Setup the UI components"""
        # Create header
        self.create_header()
        
        # Create main container with scrollbar
        self.create_main_scrollable_container()
        
        # Create detail content
        self.create_detail_content()
        
        # Create footer
        self.create_footer()
    
    def create_header(self):
        """Create header with back button and navigation"""
        self.header = tk.Frame(self.root, bg=self.colors["nav_bg"], height=70)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        header_container = tk.Frame(self.header, bg=self.colors["nav_bg"])
        header_container.pack(fill="both", expand=True, padx=30)
        
        # Back button
        back_btn = tk.Button(header_container, text="← Back to Attractions",
                           font=("Segoe UI", 12, "bold"),
                           bg=self.colors["nav_bg"], fg="white",
                           relief="flat", cursor="hand2",
                           command=self.go_back)
        back_btn.pack(side="left")
        self.add_hover_effect(back_btn, "#2a4d6e", self.colors["nav_bg"])
        
        # Title centered
        title_label = tk.Label(header_container, 
                             text=self.attraction["name"][:40] + ("..." if len(self.attraction["name"]) > 40 else ""),
                             font=("Segoe UI", 16, "bold"),
                             bg=self.colors["nav_bg"], fg="white")
        title_label.pack(side="left", padx=20, expand=True)
        
        # Full screen toggle
        fs_btn = tk.Button(header_container, text="⛶", font=("Segoe UI", 18),
                         bg=self.colors["nav_bg"], fg="white",
                         relief="flat", cursor="hand2",
                         command=self.toggle_fullscreen)
        fs_btn.pack(side="right", padx=(10, 0))
        self.add_hover_effect(fs_btn, "#2a4d6e", self.colors["nav_bg"])
    
    def create_main_scrollable_container(self):
        """Create main container with scrollbar"""
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True, side="top")
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(self.main_container, bg=self.colors["light"], 
                               highlightthickness=0)
        
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", 
                                 command=self.canvas.yview)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        self.content_frame = tk.Frame(self.canvas, bg=self.colors["light"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, 
                                                       anchor="nw")
        
        # Bind events for scrolling
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def create_detail_content(self):
        """Create detailed attraction content"""
        # Main content container
        main_content = tk.Frame(self.content_frame, bg=self.colors["light"])
        main_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Hero image
        self.create_hero_image(main_content)
        
        # Details section
        self.create_details_section(main_content)
        
        # Booking section
        self.create_booking_section(main_content)
    
    def create_hero_image(self, parent):
        """Create hero image section"""
        hero_frame = tk.Frame(parent, bg="white", height=400)
        hero_frame.pack(fill="x", pady=(0, 20))
        hero_frame.pack_propagate(False)
        
        # Load and display image
        try:
            photo = self.load_image(self.attraction["image_file"], size=(1200, 400))
            image_label = tk.Label(hero_frame, image=photo, bg="white")
            image_label.image = photo  # Keep reference to prevent garbage collection
            image_label.pack(fill="both", expand=True)
        except Exception as e:
            # Fallback if image fails to load
            fallback_frame = tk.Frame(hero_frame, bg=self.attraction.get("color", "#6c5b7b"))
            fallback_frame.pack(fill="both", expand=True)
            tk.Label(fallback_frame, text="🏛️", font=("Arial", 64),
                    bg=self.attraction.get("color", "#6c5b7b"), fg="white").pack(expand=True)
        
        # Overlay with attraction name
        overlay = tk.Frame(hero_frame, bg="#333333", height=80)
        overlay.place(relx=0, rely=1, y=-80, relwidth=1)
        
        # Add price badge
        price_text = "FREE" if self.attraction["price"] == 0 else f"RM {self.attraction['price']}"
        price_bg = self.colors["success"] if self.attraction["price"] == 0 else self.colors["secondary"]
        price_label = tk.Label(overlay, text=price_text, 
                              font=("Segoe UI", 14, "bold"),
                              bg=price_bg, fg="white",
                              padx=15, pady=5)
        price_label.place(relx=0.05, rely=0.5, anchor="w")
        
        tk.Label(overlay, text=self.attraction["name"], 
                font=("Segoe UI", 20, "bold"),
                bg="#333333", fg="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # Add country flag for international attractions
        if self.attraction.get("id", 0) >= 9:
            location = self.attraction.get("location", "")
            if location:
                parts = location.split(", ")
                if parts:
                    country = parts[-1]
                    flag_text = self.get_country_flag(country)
                    tk.Label(overlay, text=flag_text, font=("Segoe UI", 20),
                            bg="#333333", fg="white").place(relx=0.95, rely=0.5, anchor="e")
    
    def get_country_flag(self, country):
        """Get emoji flag for country"""
        flag_map = {
            "France": "🇫🇷",
            "China": "🇨🇳",
            "USA": "🇺🇸",
            "India": "🇮🇳",
            "Australia": "🇦🇺",
            "Italy": "🇮🇹",
            "Japan": "🇯🇵",
            "Malaysia": "🇲🇾"
        }
        return flag_map.get(country, "🌐")
    
    def create_details_section(self, parent):
        """Create details section"""
        details_container = tk.Frame(parent, bg="white")
        details_container.pack(fill="x", pady=(0, 20))
        
        # Content with padding
        content = tk.Frame(details_container, bg="white", padx=30, pady=30)
        content.pack(fill="both", expand=True)
        
        # Location and rating row
        info_row = tk.Frame(content, bg="white")
        info_row.pack(fill="x", pady=(0, 20))
        
        # Location
        location_frame = tk.Frame(info_row, bg="white")
        location_frame.pack(side="left")
        tk.Label(location_frame, text="📍", font=("Segoe UI", 16),
                bg="white").pack(side="left")
        tk.Label(location_frame, text=self.attraction.get("location", "Location not specified"), 
                font=("Segoe UI", 14),
                bg="white", fg=self.colors["text_light"]).pack(side="left", padx=(5, 0))
        
        # Rating
        rating_frame = tk.Frame(info_row, bg="white")
        rating_frame.pack(side="right")
        
        # Stars
        stars_frame = tk.Frame(rating_frame, bg="white")
        stars_frame.pack(side="left")
        
        rating = self.attraction.get("rating", 0)
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        
        for i in range(5):
            if i < full_stars:
                star = "★"
                color = "#ff6e40"
            elif i == full_stars and half_star:
                star = "⯨"
                color = "#ff6e40"
            else:
                star = "☆"
                color = "#e2e8f0"
            
            tk.Label(stars_frame, text=star, font=("Segoe UI", 16),
                    bg="white", fg=color).pack(side="left")
        
        reviews = self.attraction.get("reviews", 0)
        tk.Label(rating_frame, text=f" {rating:.1f} ({reviews:,} reviews)",
                font=("Segoe UI", 14),
                bg="white", fg=self.colors["dark"]).pack(side="left", padx=(10, 0))
        
        # Description
        tk.Label(content, text="Description", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        desc_frame = tk.Frame(content, bg="white")
        desc_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(desc_frame, text=self.attraction.get("description", "No description available"), 
                font=("Segoe UI", 14),
                bg="white", fg=self.colors["dark"],
                wraplength=1100, justify="left").pack(anchor="w")
        
        # Highlights
        tk.Label(content, text="Highlights", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        for highlight in self.attraction["highlights"]:
            highlight_frame = tk.Frame(content, bg="white")
            highlight_frame.pack(fill="x", pady=5)
            
            tk.Label(highlight_frame, text="✓", 
                    font=("Segoe UI", 14),
                    bg="white", fg=self.colors["success"]).pack(side="left", padx=(0, 10))
            tk.Label(highlight_frame, text=highlight, 
                    font=("Segoe UI", 14),
                    bg="white", fg=self.colors["dark"]).pack(side="left")
        
        # Details grid
        details_grid = tk.Frame(content, bg=self.colors["light"], padx=20, pady=20)
        details_grid.pack(fill="x", pady=20)
        
        details = [
            ("⏰ Duration", self.attraction["duration"]),
            ("🎯 Best Time", self.attraction["best_time"]),
            ("🕒 Opening Hours", self.attraction["opening_hours"]),
            ("📞 Contact", self.attraction["phone"]),
            ("🌐 Website", self.attraction["website"]),
            ("🏠 Address", self.attraction["address"])
        ]
        
        row, col = 0, 0
        for label, value in details:
            detail_card = tk.Frame(details_grid, bg="white", padx=20, pady=15,
                                  relief="flat", highlightbackground=self.colors["border"],
                                  highlightthickness=1)
            detail_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            tk.Label(detail_card, text=label, 
                    font=("Segoe UI", 12, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w")
            
            # Make website clickable
            if label == "🌐 Website" and value != "Not available" and not value.startswith("www."):
                website_label = tk.Label(detail_card, text=value, 
                                        font=("Segoe UI", 12),
                                        bg="white", fg="#1e40af",
                                        cursor="hand2")
                website_label.pack(anchor="w", pady=5)
                website_label.bind("<Button-1>", lambda e, url=value: self.open_website(url))
            else:
                tk.Label(detail_card, text=value, 
                        font=("Segoe UI", 12),
                        bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=5)
            
            col += 1
            if col == 3:
                col = 0
                row += 1
        
        for i in range(3):
            details_grid.grid_columnconfigure(i, weight=1)
        
        # Facilities
        tk.Label(content, text="Facilities", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        facilities_frame = tk.Frame(content, bg="white")
        facilities_frame.pack(fill="x", pady=(0, 20))
        
        facilities_list = self.attraction["facilities"]
        if not facilities_list:
            facilities_list = ["Parking", "Restrooms", "Guided tours", "Souvenir shop"]
        
        for facility in facilities_list:
            facility_label = tk.Label(facilities_frame, text=f"✓ {facility}", 
                                     font=("Segoe UI", 12),
                                     bg=self.colors["light"], fg=self.colors["primary"],
                                     padx=15, pady=8)
            facility_label.pack(side="left", padx=5, pady=5)
        
        # Tags
        tk.Label(content, text="Tags", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        tags_frame = tk.Frame(content, bg="white")
        tags_frame.pack(fill="x", pady=(0, 20))
        
        for tag in self.attraction["tags"]:
            tag_label = tk.Label(tags_frame, text=tag, 
                                font=("Segoe UI", 11),
                                bg=self.colors["primary"], fg="white",
                                padx=12, pady=5)
            tag_label.pack(side="left", padx=5, pady=5)
    
    def create_booking_section(self, parent):
        """Create booking section with calendar popup"""
        booking_container = tk.Frame(parent, bg="white", padx=30, pady=30)
        booking_container.pack(fill="x", pady=(0, 20))
        
        tk.Label(booking_container, text="Book Your Visit", 
                font=("Segoe UI", 24, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 20))
        
        # Create a container for the left side (date) and right side (ticket & price)
        booking_grid = tk.Frame(booking_container, bg="white")
        booking_grid.pack(fill="x")
        
        # Left column - Date selection (40% width)
        left_column = tk.Frame(booking_grid, bg="white")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Right column - Tickets and price (60% width)
        right_column = tk.Frame(booking_grid, bg="white")
        right_column.pack(side="right", fill="both", expand=True)
        
        # ========= LEFT COLUMN: Date Selection =========
        date_card = tk.Frame(left_column, bg=self.colors["light"], 
                            relief="solid", borderwidth=1,
                            highlightbackground=self.colors["border"])
        date_card.pack(fill="both", expand=True, pady=5)
        
        # Date selection header
        date_header = tk.Label(date_card, text="📅 Visit Date", 
                              font=("Segoe UI", 14, "bold"),
                              bg=self.colors["light"], fg=self.colors["primary"])
        date_header.pack(anchor="w", padx=15, pady=15)
        
        # Selected date display with calendar icon
        date_field_frame = tk.Frame(date_card, bg="white",
                                   relief="solid", borderwidth=1,
                                   highlightbackground=self.colors["border"])
        date_field_frame.pack(fill="x", padx=15, pady=10)
        
        # Date display (clickable)
        self.date_var = tk.StringVar(value=self.selected_date.strftime("%Y-%m-%d"))
        
        self.date_display = tk.Label(date_field_frame, 
                                    textvariable=self.date_var,
                                    font=("Segoe UI", 12),
                                    bg="white", fg=self.colors["dark"],
                                    padx=12, pady=10)
        self.date_display.pack(side="left", fill="x", expand=True)
        
        # Calendar icon button (smaller)
        calendar_btn = tk.Button(date_field_frame, text="📅", 
                                font=("Segoe UI", 12),
                                bg="white", fg=self.colors["primary"],
                                relief="flat", cursor="hand2",
                                command=self.open_calendar_popup)
        calendar_btn.pack(side="right", padx=5, pady=5)
        self.add_hover_effect(calendar_btn, "#e2e8f0", "white")
        
        # Make the whole date field clickable
        date_field_frame.bind("<Button-1>", lambda e: self.open_calendar_popup())
        self.date_display.bind("<Button-1>", lambda e: self.open_calendar_popup())
        
        # Date format hint
        tk.Label(date_card, text="Click to select date",
                font=("Segoe UI", 10),
                bg=self.colors["light"], fg=self.colors["text_light"],
                padx=15, pady=10).pack(anchor="w")
        
        # ========= RIGHT COLUMN: Tickets & Price =========
        # Ticket quantity card
        ticket_card = tk.Frame(right_column, bg=self.colors["light"], 
                              relief="solid", borderwidth=1,
                              highlightbackground=self.colors["border"])
        ticket_card.pack(fill="x", pady=5)
        
        ticket_header = tk.Label(ticket_card, text="👥 Number of Tickets", 
                                font=("Segoe UI", 14, "bold"),
                                bg=self.colors["light"], fg=self.colors["primary"])
        ticket_header.pack(anchor="w", padx=15, pady=15)
        
        counter_frame = tk.Frame(ticket_card, bg=self.colors["light"], padx=15, pady=10)
        counter_frame.pack(fill="x")
        
        self.ticket_var = tk.IntVar(value=1)
        
        # Decrease button (smaller)
        dec_btn = tk.Button(counter_frame, text="−", font=("Segoe UI", 14),
                           bg="white", fg=self.colors["primary"],
                           relief="solid", width=2, cursor="hand2",
                           command=lambda: self.ticket_var.set(max(1, self.ticket_var.get() - 1)))
        dec_btn.pack(side="left")
        self.add_hover_effect(dec_btn, "#e2e8f0", "white")
        
        # Ticket count display (smaller)
        tk.Label(counter_frame, textvariable=self.ticket_var,
                font=("Segoe UI", 16, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"],
                width=6).pack(side="left", padx=10)
        
        # Increase button (smaller)
        inc_btn = tk.Button(counter_frame, text="+", font=("Segoe UI", 14),
                           bg="white", fg=self.colors["primary"],
                           relief="solid", width=2, cursor="hand2",
                           command=lambda: self.ticket_var.set(self.ticket_var.get() + 1))
        inc_btn.pack(side="left")
        self.add_hover_effect(inc_btn, "#e2e8f0", "white")
        
        # Price card
        price_card = tk.Frame(right_column, bg=self.colors["light"], 
                             relief="solid", borderwidth=1,
                             highlightbackground=self.colors["border"])
        price_card.pack(fill="x", pady=10)
        
        # Price header
        price_header = tk.Label(price_card, text="💰 Price Summary", 
                               font=("Segoe UI", 14, "bold"),
                               bg=self.colors["light"], fg=self.colors["primary"])
        price_header.pack(anchor="w", padx=15, pady=15)
        
        # Price details frame
        price_details = tk.Frame(price_card, bg=self.colors["light"], padx=15, pady=10)
        price_details.pack(fill="x")
        
        # Unit price
        unit_price_frame = tk.Frame(price_details, bg=self.colors["light"])
        unit_price_frame.pack(fill="x", pady=5)
        
        tk.Label(unit_price_frame, text="Unit Price:",
                font=("Segoe UI", 12),
                bg=self.colors["light"], fg=self.colors["text_light"]).pack(side="left")
        
        unit_price_text = "FREE" if self.attraction["price"] == 0 else f"RM {self.attraction['price']}"
        self.unit_price_label = tk.Label(unit_price_frame, text=unit_price_text,
                                        font=("Segoe UI", 12, "bold"),
                                        bg=self.colors["light"], fg=self.colors["primary"])
        self.unit_price_label.pack(side="right")
        
        # Total price
        total_price_frame = tk.Frame(price_details, bg=self.colors["light"])
        total_price_frame.pack(fill="x", pady=5)
        
        tk.Label(total_price_frame, text="Total Amount:",
                font=("Segoe UI", 14),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(side="left")
        
        self.price_label = tk.Label(total_price_frame,
                                   text=f"RM {self.attraction['price']}" if self.attraction["price"] > 0 else "FREE",
                                   font=("Segoe UI", 20, "bold"),
                                   bg=self.colors["light"],
                                   fg=self.colors["secondary"])
        self.price_label.pack(side="right")
        
        # Update price when tickets change
        def update_price(*args):
            total_price = self.attraction["price"] * self.ticket_var.get()
            if self.attraction["price"] > 0:
                self.price_label.config(text=f"RM {total_price}")
            else:
                self.price_label.config(text="FREE")
        
        self.ticket_var.trace("w", update_price)
        
        # ========= ACTION BUTTONS =========
        action_frame = tk.Frame(booking_container, bg="white")
        action_frame.pack(fill="x", pady=20)
        
        # Back button
        back_btn = tk.Button(action_frame, text="← Back to Attractions",
                           font=("Segoe UI", 12),
                           bg=self.colors["light"], fg=self.colors["primary"],
                           relief="solid", cursor="hand2",
                           command=self.go_back,
                           padx=30, pady=10)
        back_btn.pack(side="left", padx=(0, 20))
        self.add_hover_effect(back_btn, "#e2e8f0", self.colors["light"])
        
        # Book Now button
        book_btn = tk.Button(action_frame, text="📅 Book Now",
                           font=("Segoe UI", 14, "bold"),
                           bg=self.colors["primary"], fg="white",
                           relief="solid", cursor="hand2",
                           command=self.open_booking_detail,
                           padx=40, pady=10)
        book_btn.pack(side="right")
        self.add_hover_effect(book_btn, "#2a4d6e", self.colors["primary"])
    
    def open_calendar_popup(self):
        """Open calendar popup"""
        try:
            # Get current selected date
            current_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except:
            current_date = datetime.now()
        
        # Create calendar popup
        calendar_popup = CalendarPopup(self.root, self.on_date_selected, current_date)
    
    def on_date_selected(self, selected_date):
        """Callback when date is selected from calendar popup"""
        self.selected_date = selected_date
        self.date_var.set(selected_date.strftime("%Y-%m-%d"))
    
    def create_footer(self):
        """Create simple footer"""
        footer = tk.Frame(self.root, bg=self.colors["footer_bg"], height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        footer_container = tk.Frame(footer, bg=self.colors["footer_bg"])
        footer_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Copyright only
        tk.Label(footer_container, text="© 2024 Traney Travel Services", 
                font=("Segoe UI", 10),
                bg=self.colors["footer_bg"], fg=self.colors["footer_text"]).pack()
    
    def load_image(self, url: str, size: tuple = (300, 200)) -> ImageTk.PhotoImage:
        """Load image from local file"""
        cache_key = f"{url}_{size[0]}_{size[1]}"
        if cache_key in self.image_cache:
            self.image_cache[cache_key]["last_used"] = time.time()
            return self.image_cache[cache_key]["image"]
        
        try:
            # Try as local file
            if os.path.exists(url):
                image = Image.open(url)
            else:
                raise FileNotFoundError(f"File not found: {url}")
            
            image = image.convert('RGB')
            image = image.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_cache[cache_key] = {"image": photo, "last_used": time.time()}
            return photo
            
        except Exception:
            # Create placeholder image
            placeholder = Image.new('RGB', size, (245, 247, 250))
            draw = ImageDraw.Draw(placeholder)
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(229, 231, 235), width=1)
            draw.text((size[0]//2, size[1]//2), "Image\nNot Found", 
                     fill=(156, 163, 175), anchor="mm", align="center")
            photo = ImageTk.PhotoImage(placeholder)
            
            self.image_cache[cache_key] = {"image": photo, "last_used": time.time()}
            return photo
    
    def open_booking_detail(self):
        """Open booking detail page with booking information"""
        try:
            # Validate date
            selected_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
            if selected_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                messagebox.showerror("Invalid Date", "Please select a future date for your visit.")
                return
            
            # Calculate total price
            unit_price = self.attraction["price"]
            ticket_count = self.ticket_var.get()
            total_price = unit_price * ticket_count
            
            # Confirm booking
            confirmation = messagebox.askyesno(
                "Confirm Booking", 
                f"Book {ticket_count} ticket(s) for {self.attraction['name']} "
                f"on {self.date_var.get()}?\n\n"
                f"Unit Price: {'FREE' if unit_price == 0 else f'RM {unit_price}'}\n"
                f"Total: {'FREE' if total_price == 0 else f'RM {total_price}'}"
            )
            
            if not confirmation:
                return
            
            # Generate unique booking ID
            booking_id = f"BK{random.randint(100000, 999999)}"
            
            # Prepare booking data
            booking_details = {
                "booking_id": booking_id,
                "booking_type": "attraction",
                "status": "pending",
                "attraction_name": self.attraction["name"],
                "attraction_location": self.attraction["location"],
                "attraction_id": self.attraction["id"],
                "date": self.date_var.get(),
                "time_slot": "Any time",
                "tickets": ticket_count,
                "ticket_price": str(unit_price),
                "total_price": str(total_price),
                "image_file": self.attraction.get("image_file", ""),
                "category": self.attraction.get("category", ""),
                "duration": self.attraction.get("duration", ""),
                "opening_hours": self.attraction.get("opening_hours", ""),
                "rating": self.attraction.get("rating", 0),
                "reviews": self.attraction.get("reviews", 0),
                "user_email": self.email,
                "customer_name": "Guest",  # Default value
                "phone": "",  # Will be filled in booking form
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Store the current root reference
            current_root = self.root
            
            # Clean up image cache to prevent memory issues
            self.image_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            # Destroy current window
            current_root.destroy()
            
            # Import and create booking detail window
            try:
                import booking_detail
                booking_root = tk.Tk()
                booking_root.title("Booking Confirmation - Traney")
                booking_root.geometry("900x700")
                booking_root.configure(bg="#f8fafc")
                
                # Create booking detail app
                booking_detail.BookingDetailApp(booking_root, booking_details, self.email)
                booking_root.mainloop()
            except ImportError as ie:
                messagebox.showerror("Error", f"Booking module not found: {ie}")
                # Try to go back to attractions page
                self.safe_go_back()
            
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            # Clean up and try to go back
            self.safe_go_back()
    
    def go_back(self):
        """Go back to attractions page - main method"""
        self.safe_go_back()
    
    def safe_go_back(self):
        """Safe method to go back to attractions page"""
        try:
            # Clean up all image references
            self.image_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            # Destroy the current window
            self.root.quit()
            self.root.destroy()
            
            # Start fresh attractions window
            import attraction
            import tkinter as tk
            
            root = tk.Tk()
            root.attributes('-fullscreen', True)
            
            # Force another garbage collection
            gc.collect()
            
            app = attraction.AttractionApp(root, self.email)
            root.mainloop()
            
        except Exception as e:
            print(f"Error in go_back: {e}")
            # Last resort: just close everything
            try:
                self.root.destroy()
            except:
                pass
    
    def on_close(self):
        """Handle window closing"""
        self.safe_go_back()
    
    def open_website(self, url):
        """Open attraction website in browser"""
        if url and url != "Not available":
            if not url.startswith('http'):
                url = 'https://' + url
            webbrowser.open(url)
    
    def add_hover_effect(self, widget, hover_color, normal_color):
        """Add hover effect to widget"""
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color) if widget.cget("state") != "disabled" else None)
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color) if widget.cget("state") != "disabled" else None)
    
    def on_frame_configure(self, event=None):
        """Reset the scroll region"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Reset the canvas window width"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def toggle_fullscreen(self, event=None):
        """Toggle full screen mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        return "break"