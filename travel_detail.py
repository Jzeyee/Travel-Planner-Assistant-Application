import tkinter as tk
from tkinter import ttk
import datetime
import random
from PIL import Image, ImageTk
import os


class TravelDetail:
    def __init__(self, root, itinerary_data, user_data, email="user@example.com"):
        self.root = root
        self.email = email
        self.itinerary_data = itinerary_data
        self.user_data = user_data
        self.root.attributes('-fullscreen', True)
        
        # Color scheme matching travel_plan.py
        self.COLORS = {
            'primary': '#1e3d59',
            'secondary': '#ff6e40',
            'accent': '#ff8c66',
            'light': '#f8fafc',
            'dark': '#1e3d59',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'card_bg': '#ffffff',
            'sidebar_bg': '#ffffff',
            'nav_bg': '#1e3d59',
            'nav_active': '#ff6e40',
            'hover_nav': '#2a4d6e',
            'text_light': '#64748b',
            'border': '#e2e8f0',
            'footer_bg': '#1e3d59',
            'footer_text': '#b0c4de',
        }

        self.day_activities = {}
        self.image_cache = {}
        self.placeholder_images = {}
        
        # Load data
        self.hotel_data = self.load_hotel_data()
        self.attractions_data = self.load_attractions_data()
        self.restaurants_data = self.load_restaurants_data()
        self.car_rental_data = self.load_car_rental_data()
        
        # Pre-load placeholder images
        self.preload_placeholders()
        
        # Generate activities
        self.generate_all_day_activities()
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components for travel details"""
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Show details immediately
        self.show_details_page()
    
    def create_header(self):
        """Create header with back button"""
        header = tk.Frame(self.root, bg=self.COLORS["nav_bg"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        left_frame = tk.Frame(header, bg=self.COLORS["nav_bg"])
        left_frame.pack(side="left", padx=30)
        
        back_btn = tk.Button(left_frame, text="← Back", 
                           font=("Segoe UI", 12), bg=self.COLORS["nav_bg"], 
                           fg="white", relief="flat", cursor="hand2",
                           command=self.root.destroy)
        back_btn.pack(side="left", padx=(0, 20))
        self.add_hover_effect(back_btn, self.COLORS["hover_nav"], self.COLORS["nav_bg"])
        
        logo_frame = tk.Frame(left_frame, bg=self.COLORS["nav_bg"])
        logo_frame.pack(side="left")
        
        tk.Label(logo_frame, text="✈️", font=("Arial", 28),
                bg=self.COLORS["nav_bg"], fg="white").pack(side="left")
        
        logo_text = tk.Frame(logo_frame, bg=self.COLORS["nav_bg"])
        logo_text.pack(side="left", padx=8)
        tk.Label(logo_text, text="Traney", font=("Segoe UI", 22, "bold"),
                bg=self.COLORS["nav_bg"], fg="white").pack()
        
        title_frame = tk.Frame(header, bg=self.COLORS["nav_bg"])
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(title_frame, text="Travel Plan Details", 
                font=("Segoe UI", 18, "bold"),
                bg=self.COLORS["nav_bg"], fg="white").pack()
        
        tk.Label(title_frame, text=self.itinerary_data['destination'], 
                font=("Segoe UI", 14),
                bg=self.COLORS["nav_bg"], fg=self.COLORS["footer_text"]).pack()
    
    def create_main_content(self):
        """Create main content area with paned window"""
        self.main_container = tk.Frame(self.root, bg=self.COLORS["light"])
        self.main_container.pack(fill="both", expand=True)
        
        # Create a paned window for sidebar and main content
        self.paned_window = ttk.PanedWindow(self.main_container, orient="horizontal")
        self.paned_window.pack(fill="both", expand=True)
        
        # Left panel (sidebar) - WIDER width (increased from 350 to 450)
        self.sidebar_container = tk.Frame(self.paned_window, bg=self.COLORS["light"], width=450)
        self.paned_window.add(self.sidebar_container, weight=0)
        
        # Right panel (main content) - scrollable
        self.content_container = tk.Frame(self.paned_window, bg=self.COLORS["light"])
        self.paned_window.add(self.content_container, weight=1)
        
        # Create scrollable canvas for main content
        self.canvas = tk.Canvas(self.content_container, bg=self.COLORS["light"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.content_frame = tk.Frame(self.canvas, bg=self.COLORS["light"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel to main canvas
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def create_footer(self):
        """Create footer"""
        footer = tk.Frame(self.root, bg=self.COLORS["footer_bg"], height=40)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        tk.Label(footer, text="© 2024 Traney Travel Services",
                font=("Segoe UI", 10),
                bg=self.COLORS["footer_bg"], fg=self.COLORS["footer_text"]).pack(expand=True)
    
    def on_frame_configure(self, event=None):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event=None):
        """Update canvas window width when canvas size changes"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def on_mousewheel(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")
    
    def preload_placeholders(self):
        """Pre-load placeholder images for categories"""
        categories = {
            'attraction': ('🏛️', '#4f46e5'),
            'hotel': ('🏨', '#059669'),
            'car': ('🚗', '#dc2626'),
            'food': ('🍽️', '#d97706'),
            'landscape': ('🏞️', '#0891b2'),
            'city': ('🏙️', '#7c3aed'),
        }
        
        for category, (emoji, color) in categories.items():
            img = Image.new('RGB', (300, 200), color)
            self.placeholder_images[category] = img
    
    def load_local_image(self, filename, size=(300, 200), placeholder_category='attraction'):
        """Load image from local file with caching and error handling"""
        if not filename:
            return self.create_placeholder_image(placeholder_category, size)
        
        # Check cache
        if filename in self.image_cache:
            return self.image_cache[filename]
        
        # Define possible image paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "data", "images", filename),
            os.path.join(base_dir, "images", filename),
            os.path.join(base_dir, filename),
        ]
        
        for img_path in possible_paths:
            try:
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[filename] = photo
                    return photo
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")
                continue
        
        # If no image found, create placeholder
        placeholder = self.create_placeholder_image(placeholder_category, size)
        self.image_cache[filename] = placeholder
        return placeholder
    
    def create_placeholder_image(self, category, size=(300, 200)):
        """Create a colored placeholder image with emoji"""
        colors = {
            'attraction': ('🏛️', '#4f46e5'),
            'hotel': ('🏨', '#059669'),
            'car': ('🚗', '#dc2626'),
            'food': ('🍽️', '#d97706'),
            'landscape': ('🏞️', '#0891b2'),
            'city': ('🏙️', '#7c3aed'),
            'default': ('🖼️', '#1e3d59'),
        }
        
        emoji, color = colors.get(category, colors['default'])
        
        # Create image with color background
        img = Image.new('RGB', size, color)
        
        # We can't add text to PIL image easily, so we'll return a basic colored image
        return ImageTk.PhotoImage(img)
    
    def create_text_placeholder(self, text, size=(300, 200)):
        """Create a text-based placeholder image"""
        img = Image.new('RGB', size, '#1e3d59')
        return ImageTk.PhotoImage(img)
    
    def show_details_page(self):
        """Show the travel details page with sidebar and main content"""
        self.create_travel_details_sidebar()
        self.create_scrollable_itinerary_section()
    
    def create_travel_details_sidebar(self):
        """Create travel details sidebar on left - WIDER version"""
        # Make sidebar scrollable within its own fixed height
        sidebar_canvas = tk.Canvas(self.sidebar_container, bg=self.COLORS['card_bg'], highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(self.sidebar_container, orient="vertical", command=sidebar_canvas.yview)
        
        sidebar_scrollable_frame = tk.Frame(sidebar_canvas, bg=self.COLORS['card_bg'])
        
        sidebar_scrollable_frame.bind(
            "<Configure>",
            lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        )
        
        sidebar_canvas.create_window((0, 0), window=sidebar_scrollable_frame, anchor="nw")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to sidebar canvas
        sidebar_canvas.bind("<Enter>", lambda e: self.bind_sidebar_mousewheel(sidebar_canvas))
        sidebar_canvas.bind("<Leave>", lambda e: self.unbind_mousewheel())
        
        card_content = tk.Frame(sidebar_scrollable_frame, bg=self.COLORS['card_bg'])
        card_content.pack(fill='x', expand=True, padx=35, pady=35)  # Increased padding for wider sidebar
        
        tk.Label(card_content, text="📋 Trip Details", 
                font=("Segoe UI", 22, 'bold'), bg=self.COLORS['card_bg'], 
                fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 30))  # Increased font size and spacing
        
        details = [
            ("📍 Destination", self.itinerary_data['destination']),
            ("📅 Trip Dates", f"{self.itinerary_data['start_date']} to {self.itinerary_data['end_date']}"),
            ("⏳ Duration", f"{self.itinerary_data['days']} days"),
            ("👥 Travelers", f"{self.itinerary_data['travelers']} person(s)"),
            ("💰 Budget Level", self.itinerary_data['budget']),
            ("🚗 Transportation", self.itinerary_data['transportation']),
            ("🎯 Travel Styles", ", ".join(self.itinerary_data['travel_styles']) if self.itinerary_data['travel_styles'] else "Not specified"),
            ("📋 Plan ID", self.itinerary_data['plan_id']),
        ]
        
        for icon_label, value in details:
            detail_frame = tk.Frame(card_content, bg=self.COLORS['card_bg'])
            detail_frame.pack(fill='x', pady=(0, 20))  # Increased spacing
            
            tk.Label(detail_frame, text=icon_label, 
                    font=("Segoe UI", 13, 'bold'), bg=self.COLORS['card_bg'],  # Increased font size
                    fg=self.COLORS['text_light']).pack(anchor='w', pady=(0, 8))
            
            tk.Label(detail_frame, text=value if value else "Not specified", 
                    font=("Segoe UI", 15), bg=self.COLORS['card_bg'],  # Increased font size
                    fg=self.COLORS['primary'], wraplength=380, justify='left').pack(anchor='w')  # Increased wrap length
        
        tk.Frame(card_content, bg=self.COLORS['border'], height=1).pack(fill='x', pady=30)
        
        tk.Label(card_content, text="💰 Estimated Cost", 
                font=("Segoe UI", 20, 'bold'), bg=self.COLORS['card_bg'],  # Increased font size
                fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 20))
        
        cost_items = [
            ("🏨 Accommodation", self.calculate_accommodation_cost()),
            ("🍽️ Food & Dining", self.calculate_food_cost()),
            ("🎟️ Activities", self.calculate_activities_cost()),
            ("🚗 Transportation", self.calculate_transportation_cost()),
        ]
        
        total_cost = 0
        for item, cost in cost_items:
            item_frame = tk.Frame(card_content, bg=self.COLORS['card_bg'])
            item_frame.pack(fill='x', pady=(0, 12))  # Increased spacing
            
            tk.Label(item_frame, text=item, 
                    font=("Segoe UI", 13), bg=self.COLORS['card_bg'],  # Increased font size
                    fg=self.COLORS['text_light']).pack(side='left')
            
            tk.Label(item_frame, text=cost, 
                    font=("Segoe UI", 13, 'bold'), bg=self.COLORS['card_bg'],  # Increased font size
                    fg=self.COLORS['primary']).pack(side='right')
            
            try:
                if "RM" in cost:
                    total_cost += float(cost.replace("RM", "").replace(",", "").strip())
                elif "¥" in cost:
                    total_cost += float(cost.replace("¥", "").replace(",", "").strip())
                elif "S$" in cost:
                    total_cost += float(cost.replace("S$", "").replace(",", "").strip()) * 3.5
                elif "NT$" in cost:
                    total_cost += float(cost.replace("NT$", "").replace(",", "").strip()) * 0.15
                elif "HK$" in cost:
                    total_cost += float(cost.replace("HK$", "").replace(",", "").strip()) * 0.6
                elif "฿" in cost:
                    total_cost += float(cost.replace("฿", "").replace(",", "").strip()) * 0.13
            except:
                pass
        
        total_frame = tk.Frame(card_content, bg=self.COLORS['primary'], height=2)
        total_frame.pack(fill='x', pady=20)
        total_frame.pack_propagate(False)
        
        tk.Label(total_frame, text="TOTAL ESTIMATED COST", 
                font=("Segoe UI", 15, 'bold'), bg=self.COLORS['primary'],  # Increased font size
                fg="white").pack(side='left', padx=15, pady=10)  # Increased padding
        
        total_text = f"RM {total_cost:,.2f}" if "Malaysia" in self.itinerary_data['destination'] else f"¥ {total_cost:,.0f}"
        tk.Label(total_frame, text=total_text, 
                font=("Segoe UI", 18, 'bold'), bg=self.COLORS['primary'],  # Increased font size
                fg="white").pack(side='right', padx=15, pady=10)  # Increased padding
        
        tk.Frame(card_content, bg=self.COLORS['border'], height=1).pack(fill='x', pady=30)
        
        if self.itinerary_data['transportation'] in ["Rental Car", "Mix of All"]:
            tk.Label(card_content, text="🚗 Car Rental Recommendation", 
                    font=("Segoe UI", 20, 'bold'), bg=self.COLORS['card_bg'],  # Increased font size
                    fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 20))
            
            destination = self.itinerary_data['destination']
            if destination in self.car_rental_data:
                cars = self.car_rental_data[destination][:1]
                for car in cars:
                    car_frame = tk.Frame(card_content, bg=self.COLORS['light'], padx=20, pady=20)  # Increased padding
                    car_frame.pack(fill='x', pady=(0, 15))
                    
                    tk.Label(car_frame, text=car['name'], 
                            font=("Segoe UI", 16, 'bold'), bg=self.COLORS['light'],  # Increased font size
                            fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 8))
                    
                    tk.Label(car_frame, text=f"{car['type']} • {car['price_per_day']}/day", 
                            font=("Segoe UI", 14), bg=self.COLORS['light'],  # Increased font size
                            fg=self.COLORS['text_light']).pack(anchor='w', pady=(0, 12))
                    
                    for feature in car['features'][:3]:  # Show 3 features instead of 2
                        tk.Label(car_frame, text=f"✓ {feature}", 
                                font=("Segoe UI", 11), bg=self.COLORS['light'],  # Increased font size
                                fg=self.COLORS['success']).pack(anchor='w')
        
        # Separator instead of action buttons
        tk.Frame(card_content, bg=self.COLORS['border'], height=1).pack(fill='x', pady=30)
    
    def create_scrollable_itinerary_section(self):
        """Create scrollable itinerary section in main content"""
        tk.Label(self.content_frame, text="✅ Your Travel Plan is Ready!", 
                font=("Segoe UI", 28, 'bold'), bg=self.COLORS['light'], 
                fg=self.COLORS['primary']).pack(pady=(20, 5))
        
        tk.Label(self.content_frame, 
                font=("Segoe UI", 24, 'bold'), bg=self.COLORS['light'], 
                fg=self.COLORS['primary']).pack(anchor='w', pady=(20, 10), padx=20)
        
        # Show top attractions with images
        self.show_top_attractions()
        
        for day in range(1, self.itinerary_data['days'] + 1):
            day_card = self.create_day_itinerary_card(day)
            day_card.pack(fill='x', pady=(0, 25), padx=20)
        
        self.create_itinerary_summary()
        
        tk.Frame(self.content_frame, bg=self.COLORS['light'], height=20).pack()
    
    def show_top_attractions(self):
        """Show top attractions with images"""
        section_frame = tk.Frame(self.content_frame, bg=self.COLORS['light'])
        section_frame.pack(fill='x', pady=(0, 30))
        
        header_frame = tk.Frame(section_frame, bg=self.COLORS['light'])
        header_frame.pack(fill='x', pady=(0, 20), padx=20)
        
        tk.Label(header_frame, text="🏛️ Top Attractions", 
                font=("Segoe UI", 22, 'bold'), bg=self.COLORS['light'], 
                fg=self.COLORS['primary']).pack(side='left')
        
        destination = self.itinerary_data['destination']
        if destination in self.attractions_data:
            attractions = self.attractions_data[destination]
            
            attractions_container = tk.Frame(section_frame, bg=self.COLORS['light'])
            attractions_container.pack(fill='x', padx=20)
            
            # Display first 3 attractions
            for attraction in attractions[:3]:
                att_frame = tk.Frame(attractions_container, bg=self.COLORS['light'])
                att_frame.pack(side='left', fill='both', expand=True, padx=10)
                self.create_enhanced_attraction_card(att_frame, attraction)
    
    def create_enhanced_attraction_card(self, parent, attraction):
        """Create enhanced attraction card with image"""
        card_frame = tk.Frame(parent, bg=self.COLORS['card_bg'], 
                            relief='flat', bd=1, 
                            highlightbackground=self.COLORS['border'],
                            highlightthickness=1)
        card_frame.pack(fill='both', expand=True)
        
        # Image section with loading
        image_frame = tk.Frame(card_frame, bg=self.COLORS['light'], height=180)
        image_frame.pack(fill='x')
        image_frame.pack_propagate(False)
        
        # Try to load image 
        try:
            if attraction.get('image_file'):
                photo = self.load_local_image(attraction['image_file'], (320, 180), 'attraction')
                img_label = tk.Label(image_frame, image=photo, bg=self.COLORS['light'])
                img_label.pack(fill='both', expand=True)
                img_label.image = photo
                
                # Add overlay with attraction name
                overlay_frame = tk.Frame(image_frame, bg='black')
                overlay_frame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)
                
                tk.Label(overlay_frame, text=attraction['name'], 
                        font=("Segoe UI", 14, 'bold'), bg='black',
                        fg='white', padx=10, pady=5).pack(side='left')
                
                # Rating badge
                rating_frame = tk.Frame(overlay_frame, bg=self.COLORS['warning'])
                rating_frame.pack(side='right', padx=10, pady=5)
                tk.Label(rating_frame, text=f"⭐ {attraction['rating']}", 
                        font=("Segoe UI", 11, 'bold'), bg=self.COLORS['warning'],
                        fg='white', padx=8, pady=2).pack()
            else:
                # Fallback to placeholder
                placeholder_frame = tk.Frame(image_frame, bg=self.COLORS['primary'])
                placeholder_frame.pack(fill='both', expand=True)
                
                tk.Label(placeholder_frame, text="🏛️", 
                        font=("Segoe UI", 48), bg=self.COLORS['primary'],
                        fg="white").pack(pady=10)
                tk.Label(placeholder_frame, text=attraction['name'], 
                        font=("Segoe UI", 14, 'bold'), bg=self.COLORS['primary'],
                        fg="white", wraplength=300).pack()
        except Exception as e:
            print(f"Error displaying image: {e}")
            placeholder_frame = tk.Frame(image_frame, bg=self.COLORS['primary'])
            placeholder_frame.pack(fill='both', expand=True)
            
            tk.Label(placeholder_frame, text="🏛️", 
                    font=("Segoe UI", 48), bg=self.COLORS['primary'],
                    fg="white").pack(pady=10)
            tk.Label(placeholder_frame, text=attraction['name'], 
                    font=("Segoe UI", 14, 'bold'), bg=self.COLORS['primary'],
                    fg="white", wraplength=300).pack()
        
        content_frame = tk.Frame(card_frame, bg=self.COLORS['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Description
        tk.Label(content_frame, text=attraction['description'], 
                font=("Segoe UI", 11), bg=self.COLORS['card_bg'], 
                fg=self.COLORS['text_light'], wraplength=280, justify='left').pack(anchor='w', pady=(0, 10))
        
        # Details row
        details_frame = tk.Frame(content_frame, bg=self.COLORS['card_bg'])
        details_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(details_frame, text=f"🕐 {attraction['duration']}", 
                font=("Segoe UI", 10), bg=self.COLORS['card_bg'], 
                fg=self.COLORS['text_light']).pack(side='left')
        
        tk.Label(details_frame, text=f"💰 {attraction['price']}", 
                font=("Segoe UI", 10, 'bold'), bg=self.COLORS['card_bg'], 
                fg=self.COLORS['success']).pack(side='right')
        
        # Features
        if attraction.get('features'):
            features_frame = tk.Frame(content_frame, bg=self.COLORS['light'], padx=10, pady=8)
            features_frame.pack(fill='x', pady=(5, 0))
            
            features_text = " • ".join(attraction['features'][:2])
            tk.Label(features_frame, text=features_text, 
                    font=("Segoe UI", 9), bg=self.COLORS['light'], 
                    fg=self.COLORS['dark'], wraplength=280).pack()
    
    def create_day_itinerary_card(self, day):
        """Create a detailed card for a day's itinerary"""
        card_frame = tk.Frame(self.content_frame, bg=self.COLORS['card_bg'], 
                            relief='flat', bd=0)
        
        content_frame = tk.Frame(card_frame, bg=self.COLORS['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=25)
        
        header_frame = tk.Frame(content_frame, bg=self.COLORS['primary'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        day_label = tk.Label(header_frame, text=f"Day {day}", 
                           font=("Segoe UI", 22, 'bold'), 
                           bg=self.COLORS['primary'], 
                           fg="white", padx=20, pady=15)
        day_label.pack(side='left')
        
        if self.itinerary_data.get('start_date'):
            try:
                start_date = datetime.datetime.strptime(self.itinerary_data['start_date'], "%m/%d/%y")
                current_date = start_date + datetime.timedelta(days=day-1)
                date_label = tk.Label(header_frame, 
                                    text=current_date.strftime("%A, %B %d, %Y"),
                                    font=("Segoe UI", 14), 
                                    bg=self.COLORS['primary'], 
                                    fg="#b0c4de", padx=20)
                date_label.pack(side='right')
            except:
                pass
        
        themes = ["Arrival & First Impressions", "Cultural Immersion", "Nature Exploration", 
                 "Food Discovery", "Historical Journey", "Local Experiences", "Relaxation Day"]
        theme = themes[(day-1) % len(themes)]
        
        theme_frame = tk.Frame(content_frame, bg=self.COLORS['card_bg'])
        theme_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(theme_frame, text=f"🌟 {theme}", 
                font=("Segoe UI", 18, 'bold'), 
                bg=self.COLORS['card_bg'], 
                fg=self.COLORS['secondary']).pack(anchor='w')
        
        summaries = [
            "Get settled and explore the local area. Perfect for recovering from travel.",
            "Dive deep into the local culture with museums, temples, and traditional activities.",
            "Explore natural wonders, parks, and outdoor adventures.",
            "A culinary journey through local cuisine and food markets.",
            "Step back in time with historical sites and monuments.",
            "Experience local life like a resident with authentic activities.",
            "Take it easy with relaxing activities and spa treatments."
        ]
        summary = summaries[(day-1) % len(summaries)]
        
        summary_frame = tk.Frame(content_frame, bg=self.COLORS['light'], padx=15, pady=10)
        summary_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(summary_frame, text=summary, 
                font=("Segoe UI", 12), 
                bg=self.COLORS['light'], 
                fg=self.COLORS['dark'], wraplength=600, justify='left').pack()
        
        # Show recommended attraction for this day with image
        destination = self.itinerary_data['destination']
        if destination in self.attractions_data:
            attractions = self.attractions_data[destination]
            if attractions:
                attraction = attractions[day % len(attractions)]
                self.create_day_attraction_section(content_frame, attraction, day)
        
        # Car rental recommendation section (only for certain days)
        if day == 1 and self.itinerary_data['transportation'] in ["Rental Car", "Mix of All"]:
            self.create_car_recommendation_section(content_frame, destination)
        
        if day in self.day_activities:
            for activity in self.day_activities[day]:
                activity_frame = tk.Frame(content_frame, bg=self.COLORS['card_bg'])
                activity_frame.pack(fill='x', pady=12)
                
                time_bg = tk.Frame(activity_frame, bg=self.COLORS['primary'], width=200)
                time_bg.pack(side='left', fill='y', padx=(0, 15))
                time_bg.pack_propagate(False)
                
                time_label = tk.Label(time_bg, text=activity['time'], 
                                    font=("Segoe UI", 11, 'bold'), 
                                    bg=self.COLORS['primary'], 
                                    fg="white", padx=15, pady=8)
                time_label.pack(fill='both', expand=True)
                
                desc_frame = tk.Frame(activity_frame, bg=self.COLORS['card_bg'])
                desc_frame.pack(side='left', fill='both', expand=True)
                
                tk.Label(desc_frame, text=activity['activity'], 
                        font=("Segoe UI", 13, 'bold'), 
                        bg=self.COLORS['card_bg'], 
                        fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 5))
                
                descriptions = [
                    "Explore local markets and try street food",
                    "Visit famous landmarks and take photos",
                    "Relax at a local cafe and people-watch",
                    "Join a guided tour to learn more",
                    "Shop for souvenirs and local crafts",
                ]
                desc = descriptions[(self.day_activities[day].index(activity) + day) % len(descriptions)]
                
                tk.Label(desc_frame, text=f"💡 {desc}", 
                        font=("Segoe UI", 11), 
                        bg=self.COLORS['card_bg'], 
                        fg=self.COLORS['text_light']).pack(anchor='w')
                
                duration_frame = tk.Frame(desc_frame, bg=self.COLORS['card_bg'])
                duration_frame.pack(fill='x', pady=(5, 0))
                
                tk.Label(duration_frame, text="⏱️ 2-3 hours", 
                        font=("Segoe UI", 10), 
                        bg=self.COLORS['card_bg'], 
                        fg=self.COLORS['success']).pack(side='left', padx=(0, 15))
                
                tk.Label(duration_frame, text="💰 RM 50-100 / ¥ 1000-2000", 
                        font=("Segoe UI", 10), 
                        bg=self.COLORS['card_bg'], 
                        fg=self.COLORS['warning']).pack(side='left')
        
        tips_frame = tk.Frame(content_frame, bg=self.COLORS['light'])
        tips_frame.pack(fill='x', pady=(20, 0))
        
        tk.Label(tips_frame, text="💡 Tips for Today:", 
                font=("Segoe UI", 12, 'bold'), 
                bg=self.COLORS['light'], 
                fg=self.COLORS['primary']).pack(anchor='w', pady=(10, 5))
        
        tips = [
            "Wear comfortable shoes for walking",
            "Bring a water bottle to stay hydrated",
            "Have local currency for small purchases",
            "Keep hotel address handy",
        ]
        
        for i in range(min(3, len(tips))):
            tip = tips[(day-1+i) % len(tips)]
            tip_label = tk.Label(tips_frame, text=f"• {tip}", 
                               font=("Segoe UI", 10), 
                               bg=self.COLORS['light'], 
                               fg=self.COLORS['dark'], wraplength=600, justify='left')
            tip_label.pack(anchor='w', pady=2)
        
        return card_frame
    
    def create_day_attraction_section(self, parent, attraction, day):
        """Create attraction recommendation section for a day with image"""
        section_frame = tk.Frame(parent, bg=self.COLORS['light'], padx=15, pady=15)
        section_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(section_frame, text="🏛️ Recommended Attraction", 
                font=("Segoe UI", 14, 'bold'), bg=self.COLORS['light'], 
                fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 10))
        
        att_content = tk.Frame(section_frame, bg=self.COLORS['light'])
        att_content.pack(fill='x')
        
        # Create two-column layout: image on left, details on right
        main_frame = tk.Frame(att_content, bg=self.COLORS['light'])
        main_frame.pack(fill='x')
        
        # Image column
        image_col = tk.Frame(main_frame, bg=self.COLORS['light'], width=200)
        image_col.pack(side='left', fill='y', padx=(0, 15))
        image_col.pack_propagate(False)
        
        # Load and display image
        image_display = tk.Frame(image_col, bg=self.COLORS['light'], height=120)
        image_display.pack(fill='both', expand=True)
        image_display.pack_propagate(False)
        
        try:
            if attraction.get('image_file'):
                photo = self.load_local_image(attraction['image_file'], (200, 120), 'attraction')
                img_label = tk.Label(image_display, image=photo, bg=self.COLORS['light'])
                img_label.pack(fill='both', expand=True)
                img_label.image = photo
            else:
                placeholder = tk.Frame(image_display, bg=self.COLORS['primary'])
                placeholder.pack(fill='both', expand=True)
                
                tk.Label(placeholder, text="🏛️", 
                        font=("Segoe UI", 36), bg=self.COLORS['primary'],
                        fg="white").pack(pady=10)
        except Exception as e:
            print(f"Error loading attraction image: {e}")
            placeholder = tk.Frame(image_display, bg=self.COLORS['primary'])
            placeholder.pack(fill='both', expand=True)
            
            tk.Label(placeholder, text="🏛️", 
                    font=("Segoe UI", 36), bg=self.COLORS['primary'],
                    fg="white").pack(pady=10)
        
        # Details column
        details_col = tk.Frame(main_frame, bg=self.COLORS['light'])
        details_col.pack(side='left', fill='both', expand=True)
        
        tk.Label(details_col, text=attraction['name'], 
                font=("Segoe UI", 16, 'bold'), bg=self.COLORS['light'], 
                fg=self.COLORS['secondary']).pack(anchor='w', pady=(0, 5))
        
        tk.Label(details_col, text=attraction['description'], 
                font=("Segoe UI", 11), bg=self.COLORS['light'], 
                fg=self.COLORS['dark'], wraplength=350, justify='left').pack(anchor='w', pady=(0, 10))
        
        details_frame = tk.Frame(details_col, bg=self.COLORS['light'])
        details_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(details_frame, text=f"⭐ Rating: {attraction['rating']}/5", 
                font=("Segoe UI", 10), bg=self.COLORS['light'], 
                fg=self.COLORS['warning']).pack(side='left', padx=(0, 15))
        
        tk.Label(details_frame, text=f"💰 Price: {attraction['price']}", 
                font=("Segoe UI", 10), bg=self.COLORS['light'], 
                fg=self.COLORS['success']).pack(side='left', padx=(0, 15))
        
        tk.Label(details_frame, text=f"🕐 Duration: {attraction['duration']}", 
                font=("Segoe UI", 10), bg=self.COLORS['light'], 
                fg=self.COLORS['text_light']).pack(side='left')
        
        # Features
        if attraction.get('features'):
            features_frame = tk.Frame(details_col, bg=self.COLORS['light'])
            features_frame.pack(fill='x', pady=(5, 0))
            
            tk.Label(features_frame, text="Features:", 
                    font=("Segoe UI", 10, 'bold'), bg=self.COLORS['light'], 
                    fg=self.COLORS['primary']).pack(anchor='w')
            
            for feature in attraction['features'][:3]:
                tk.Label(features_frame, text=f"• {feature}", 
                        font=("Segoe UI", 10), bg=self.COLORS['light'], 
                        fg=self.COLORS['dark']).pack(anchor='w')
    
    def create_car_recommendation_section(self, parent, destination):
        """Create car recommendation section with images"""
        if destination not in self.car_rental_data:
            return
            
        section_frame = tk.Frame(parent, bg=self.COLORS['light'], padx=15, pady=15)
        section_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(section_frame, text="🚗 Car Rental Recommendation", 
                font=("Segoe UI", 14, 'bold'), bg=self.COLORS['light'], 
                fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 10))
        
        cars = self.car_rental_data[destination][:2]
        
        for car in cars:
            car_card = tk.Frame(section_frame, bg=self.COLORS['card_bg'], 
                              relief='flat', bd=1,
                              highlightbackground=self.COLORS['border'],
                              highlightthickness=1)
            car_card.pack(fill='x', pady=(0, 10))
            
            car_content = tk.Frame(car_card, bg=self.COLORS['card_bg'])
            car_content.pack(fill='both', expand=True, padx=15, pady=15)
            
            # Two-column layout for car
            car_layout = tk.Frame(car_content, bg=self.COLORS['card_bg'])
            car_layout.pack(fill='x')
            
            # Image column
            image_col = tk.Frame(car_layout, bg=self.COLORS['card_bg'], width=120)
            image_col.pack(side='left', fill='y', padx=(0, 15))
            image_col.pack_propagate(False)
            
            # Load car image
            try:
                if car.get('image_file'):
                    photo = self.load_local_image(car['image_file'], (120, 80), 'car')
                    img_label = tk.Label(image_col, image=photo, bg=self.COLORS['card_bg'])
                    img_label.pack(fill='both', expand=True)
                    img_label.image = photo
                else:
                    placeholder = tk.Frame(image_col, bg=self.COLORS['primary'])
                    placeholder.pack(fill='both', expand=True)
                    
                    tk.Label(placeholder, text="🚗", 
                            font=("Segoe UI", 36), bg=self.COLORS['primary'],
                            fg="white").pack(pady=10)
            except Exception as e:
                print(f"Error loading car image: {e}")
                placeholder = tk.Frame(image_col, bg=self.COLORS['primary'])
                placeholder.pack(fill='both', expand=True)
                
                tk.Label(placeholder, text="🚗", 
                        font=("Segoe UI", 36), bg=self.COLORS['primary'],
                        fg="white").pack(pady=10)
            
            # Details column
            details_col = tk.Frame(car_layout, bg=self.COLORS['card_bg'])
            details_col.pack(side='left', fill='both', expand=True)
            
            # Car header
            header_frame = tk.Frame(details_col, bg=self.COLORS['card_bg'])
            header_frame.pack(fill='x', pady=(0, 5))
            
            tk.Label(header_frame, text=car['name'], 
                    font=("Segoe UI", 16, 'bold'), bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['primary']).pack(side='left')
            
            tk.Label(header_frame, text=f"💰 {car['price_per_day']}/day", 
                    font=("Segoe UI", 14, 'bold'), bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['secondary']).pack(side='right')
            
            # Car details
            details_frame = tk.Frame(details_col, bg=self.COLORS['card_bg'])
            details_frame.pack(fill='x', pady=(0, 5))
            
            tk.Label(details_frame, text=f"Type: {car['type']}", 
                    font=("Segoe UI", 11), bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['text_light']).pack(side='left', padx=(0, 15))
            
            tk.Label(details_frame, text=f"Rating: ⭐ {car['rating']}/5", 
                    font=("Segoe UI", 11), bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['warning']).pack(side='left', padx=(0, 15))
            
            # Features
            features_frame = tk.Frame(details_col, bg=self.COLORS['card_bg'])
            features_frame.pack(fill='x', pady=(5, 0))
            
            features_text = " • ".join(car['features'][:3])
            tk.Label(features_frame, text=features_text, 
                    font=("Segoe UI", 10), bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['success']).pack(anchor='w')
            
            # Suitable for
            suitable_frame = tk.Frame(details_col, bg=self.COLORS['light'])
            suitable_frame.pack(fill='x', pady=(10, 0))
            
            tk.Label(suitable_frame, text=f"Perfect for: {', '.join(car['suitable_for'][:2])}", 
                    font=("Segoe UI", 10), bg=self.COLORS['light'], 
                    fg=self.COLORS['dark'], padx=10, pady=5).pack()
            
            # Space instead of book button
            tk.Frame(details_col, bg=self.COLORS['card_bg'], height=10).pack()
    
    def create_itinerary_summary(self):
        """Create a summary section at the end of the itinerary"""
        summary_frame = tk.Frame(self.content_frame, bg=self.COLORS['card_bg'])
        summary_frame.pack(fill='x', pady=(20, 0), padx=20)
        
        content_frame = tk.Frame(summary_frame, bg=self.COLORS['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=25)
        
        tk.Label(content_frame, text="📊 Trip Summary", 
                font=("Segoe UI", 22, 'bold'), 
                bg=self.COLORS['card_bg'], 
                fg=self.COLORS['primary']).pack(anchor='w', pady=(0, 20))
        
        stats_frame = tk.Frame(content_frame, bg=self.COLORS['card_bg'])
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats = [
            ("Total Days", f"{self.itinerary_data['days']} days"),
            ("Activities Planned", f"{self.itinerary_data['days'] * 4} activities"),
            ("Recommended Attractions", f"{min(4, len(self.attractions_data.get(self.itinerary_data['destination'], [])))} spots"),
            ("Car Rental Options", f"{len(self.car_rental_data.get(self.itinerary_data['destination'], []))} vehicles"),
        ]
        
        for i in range(0, len(stats), 2):
            row_frame = tk.Frame(stats_frame, bg=self.COLORS['card_bg'])
            row_frame.pack(fill='x', pady=10)
            
            for j in range(2):
                if i + j < len(stats):
                    stat_frame = tk.Frame(row_frame, bg=self.COLORS['light'], padx=15, pady=10)
                    stat_frame.pack(side='left', fill='both', expand=True, padx=(0, 20 if j == 0 else 0))
                    
                    tk.Label(stat_frame, text=stats[i + j][0], 
                            font=("Segoe UI", 12), 
                            bg=self.COLORS['light'], 
                            fg=self.COLORS['text_light']).pack(anchor='w', pady=(0, 5))
                    
                    tk.Label(stat_frame, text=stats[i + j][1], 
                            font=("Segoe UI", 16, 'bold'), 
                            bg=self.COLORS['light'], 
                            fg=self.COLORS['primary']).pack(anchor='w')
        
        tk.Label(content_frame, text="🎯 Final Recommendations", 
                font=("Segoe UI", 18, 'bold'), 
                bg=self.COLORS['card_bg'], 
                fg=self.COLORS['secondary']).pack(anchor='w', pady=(20, 10))
        
        recommendations = [
            "Book popular attractions in advance to avoid queues",
            "Try local transportation for authentic experience",
            "Learn basic greetings in the local language",
            "Keep emergency numbers saved in your phone",
            "Share your itinerary with family or friends",
        ]
        
        for rec in recommendations:
            rec_frame = tk.Frame(content_frame, bg=self.COLORS['card_bg'])
            rec_frame.pack(fill='x', pady=5)
            
            tk.Label(rec_frame, text="✓", 
                    font=("Segoe UI", 12), 
                    bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['success']).pack(side='left', padx=(0, 10))
            
            tk.Label(rec_frame, text=rec, 
                    font=("Segoe UI", 11), 
                    bg=self.COLORS['card_bg'], 
                    fg=self.COLORS['dark'], wraplength=600, justify='left').pack(side='left')
    
    def generate_all_day_activities(self):
        """Generate activities for all days"""
        self.day_activities = {}
        destination = self.itinerary_data['destination']
        
        for day in range(1, self.itinerary_data['days'] + 1):
            activities = self.generate_day_activities(destination, day)
            self.day_activities[day] = activities
    
    def generate_day_activities(self, destination, day):
        """Generate activities for a specific day"""
        activities = []
        
        morning_options = [
            "Visit local market for breakfast and fresh produce",
            "Morning city tour with professional guide",
            "Historical site visit and cultural exploration",
            "Nature walk or hike in nearby parks",
            "Museum visit to learn about local history"
        ]
        
        afternoon_options = [
            "Local restaurant lunch with traditional cuisine",
            "Shopping district exploration and souvenir hunting",
            "Cultural performance or traditional show",
            "Guided tour of architectural landmarks",
            "Relaxation time at local cafes or parks"
        ]
        
        evening_options = [
            "Fine dining experience at highly-rated restaurant",
            "Night market visit for street food and local crafts",
            "City lights viewing from observation deck",
            "Cultural show or theater performance",
            "Local bar or cafe for nightlife experience"
        ]
        
        morning = random.choice(morning_options)
        afternoon = random.choice(afternoon_options)
        evening = random.choice(evening_options)
        
        activities.append({"time": "Morning ", "activity": morning})
        activities.append({"time": "Afternoon ", "activity": afternoon})
        activities.append({"time": "Evening ", "activity": evening})
        
        return activities
    
    def bind_sidebar_mousewheel(self, canvas):
        """Bind mousewheel to sidebar canvas"""
        canvas.bind_all("<MouseWheel>", lambda e: self.on_canvas_mousewheel(e, canvas))
    
    def unbind_mousewheel(self):
        """Unbind mousewheel from all"""
        self.canvas.unbind_all("<MouseWheel>")
    
    def on_canvas_mousewheel(self, event, canvas):
        """Handle mouse wheel scrolling for specific canvas"""
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        else:
            canvas.yview_scroll(1, "units")
    
    def add_hover_effect(self, widget, hover_color, normal_color):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color) if widget.cget("state") != "disabled" else None)
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color) if widget.cget("state") != "disabled" else None)
    
    # Data loading methods
    def load_hotel_data(self):
        return {
            "Kuala Lumpur, Malaysia": [
                {"name": "Riveria City Kuala Lumpur Sentral by Archos", "price": "RM 93", "rating": 4.0, "type": "3-star", "features": ["City views", "Swimming pool", "Modern design"], "location": "KL Sentral"},
                {"name": "Kingston Hotel 10 - Bukit Jalil", "price": "RM 82", "rating": 3.8, "type": "Budget", "features": ["Budget friendly", "Clean rooms", "Free WiFi"], "location": "Bukit Jalil"},
            ],
            "Tokyo, Japan": [
                {"name": "Sakura Garden Inn - Shinjuku", "price": "¥ 7,000", "rating": 4.2, "type": "3-star", "features": ["Traditional garden", "Near Shinjuku Station", "Cultural experience"], "location": "Shinjuku"},
                {"name": "The Gate Hotel Asakusa", "price": "¥ 8,500", "rating": 4.3, "type": "4-star", "features": ["Rooftop bar", "Temple views", "Modern design"], "location": "Asakusa"},
            ],
            "Bangkok, Thailand": [
                {"name": "Bangkok Marriott Hotel The Surawongse", "price": "฿ 3,200", "rating": 4.5, "type": "5-star", "features": ["Infinity pool", "Rooftop bar", "City views"], "location": "Silom"},
                {"name": "Maduzi Hotel", "price": "฿ 4,500", "rating": 4.7, "type": "Luxury", "features": ["Art deco design", "Personal butler", "Central location"], "location": "Sukhumvit"},
            ],
            "Singapore, Singapore": [
                {"name": "Marina Bay Sands", "price": "S$ 500", "rating": 4.8, "type": "5-star", "features": ["Infinity pool", "SkyPark", "Casino"], "location": "Marina Bay"},
                {"name": "Hotel 81", "price": "S$ 80", "rating": 3.5, "type": "Budget", "features": ["Clean rooms", "Central location", "Basic amenities"], "location": "Geylang"},
            ],
            "Hong Kong, China": [
                {"name": "The Ritz-Carlton Hong Kong", "price": "HK$ 3,500", "rating": 4.9, "type": "5-star", "features": ["Highest hotel", "Ozone bar", "Spa"], "location": "Kowloon"},
                {"name": "Butterfly on Wellington", "price": "HK$ 900", "rating": 4.1, "type": "4-star", "features": ["Central location", "Modern design", "Good value"], "location": "Central"},
            ],
            "Taipei, Taiwan": [
                {"name": "W Taipei", "price": "NT$ 6,500", "rating": 4.6, "type": "5-star", "features": ["Trendy design", "WOOBAR", "City views"], "location": "Xinyi"},
                {"name": "CityInn Hotel", "price": "NT$ 1,800", "rating": 4.2, "type": "Budget", "features": ["Free snacks", "Modern rooms", "Good location"], "location": "Ximending"},
            ],
            "Shanghai, China": [
                {"name": "The Peninsula Shanghai", "price": "¥ 2,500", "rating": 4.8, "type": "5-star", "features": ["Bund views", "Luxury spa", "Heritage building"], "location": "The Bund"},
                {"name": "Jinjiang Inn", "price": "¥ 300", "rating": 3.8, "type": "Budget", "features": ["Clean rooms", "Multiple locations", "Basic amenities"], "location": "Citywide"},
            ],
            "Beijing, China": [
                {"name": "The Opposite House", "price": "¥ 1,800", "rating": 4.7, "type": "5-star", "features": ["Contemporary art", "Design hotel", "Sanlitun area"], "location": "Chaoyang"},
                {"name": "Holiday Inn Express", "price": "¥ 450", "rating": 4.0, "type": "Budget", "features": ["Free breakfast", "Modern rooms", "Good location"], "location": "Dongcheng"},
            ],
            "Penang, Malaysia": [
                {"name": "Eastern & Oriental Hotel", "price": "RM 380", "rating": 4.6, "type": "5-star", "features": ["Heritage hotel", "Seafront", "Colonial charm"], "location": "Georgetown"},
                {"name": "Areca Hotel Penang", "price": "RM 120", "rating": 4.3, "type": "Boutique", "features": ["Peranakan style", "Heritage area", "Cozy ambiance"], "location": "Georgetown"},
            ],
        }
    
    def load_attractions_data(self):
        """Load attractions data with local image files"""
        return {
            "Kuala Lumpur, Malaysia": [
                {
                    "name": "Petronas Twin Towers",
                    "price": "RM 85", 
                    "rating": 4.8, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Sky bridge", "Observation deck", "Shopping mall"],
                    "image_file": "PTT.jpg",
                    "description": "Iconic twin skyscrapers offering breathtaking city views from the observation deck."
                },
                {
                    "name": "Batu Caves",
                    "price": "RM 25", 
                    "rating": 4.5, 
                    "duration": "2 hours", 
                    "best_time": "Early morning",
                    "features": ["Hindu temples", "Cave exploration", "Monkey watching"],
                    "image_file": "BC.jpg",
                    "description": "Limestone caves featuring Hindu temples and colorful staircase."
                },
                {
                    "name": "KL Tower",
                    "price": "RM 52", 
                    "rating": 4.6, 
                    "duration": "1-2 hours", 
                    "best_time": "Evening",
                    "features": ["Panoramic views", "Revolving restaurant", "Sky deck"],
                    "image_file": "KLT.jpg",
                    "description": "Communication tower offering 360-degree views of Kuala Lumpur."
                },
                {
                    "name": "Merdeka Square",
                    "price": "Free", 
                    "rating": 4.4, 
                    "duration": "1 hour", 
                    "best_time": "Morning/Evening",
                    "features": ["Historical site", "Open space", "Photo opportunities"],
                    "image_file": "MSquare.jpg",
                    "description": "Historical square where Malaysia declared independence in 1957."
                }
            ],
            "Tokyo, Japan": [
                {
                    "name": "Tokyo Skytree",
                    "price": "¥ 2,060", 
                    "rating": 4.7, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Tallest tower", "Observation decks", "Shopping"],
                    "image_file": "TS.jpg",
                    "description": "World's tallest tower offering stunning views of Tokyo."
                },
                {
                    "name": "Senso-ji Temple",
                    "price": "Free", 
                    "rating": 4.8, 
                    "duration": "1-2 hours", 
                    "best_time": "Early morning",
                    "features": ["Ancient temple", "Shopping street", "Cultural experience"],
                    "image_file": "ST.jpg",
                    "description": "Tokyo's oldest temple with vibrant Nakamise shopping street."
                },
                {
                    "name": "Shibuya Crossing",
                    "price": "Free", 
                    "rating": 4.6, 
                    "duration": "30 mins", 
                    "best_time": "Evening",
                    "features": ["Busiest crossing", "Iconic view", "Shopping nearby"],
                    "image_file": "SC.jpg",
                    "description": "World's busiest pedestrian crossing, famous for its organized chaos."
                },
                {
                    "name": "Meiji Shrine",
                    "price": "Free", 
                    "rating": 4.7, 
                    "duration": "1-2 hours", 
                    "best_time": "Morning",
                    "features": ["Shinto shrine", "Forest trail", "Cultural site"],
                    "image_file": "MS.jpg",
                    "description": "Dedicated to Emperor Meiji, surrounded by peaceful forest."
                }
            ],
            "Bangkok, Thailand": [
                {
                    "name": "Grand Palace",
                    "price": "฿ 500", 
                    "rating": 4.8, 
                    "duration": "3-4 hours", 
                    "best_time": "Morning",
                    "features": ["Emerald Buddha", "Royal residence", "Thai architecture"],
                    "image_file": "GP.jpg",
                    "description": "Former royal residence with stunning Thai architecture."
                },
                {
                    "name": "Wat Arun",
                    "price": "฿ 100", 
                    "rating": 4.7, 
                    "duration": "1-2 hours", 
                    "best_time": "Sunset",
                    "features": ["Riverside temple", "Colorful porcelain", "Great views"],
                    "image_file": "WA.jpg",
                    "description": "Riverside temple known as 'Temple of Dawn' with beautiful spires."
                },
                {
                    "name": "Chatuchak Market",
                    "price": "Free", 
                    "rating": 4.5, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Weekend market", "Shopping", "Street food"],
                    "image_file": "CM.jpg",
                    "description": "World's largest weekend market with 15,000 stalls."
                },
                {
                    "name": "Wat Pho",
                    "price": "฿ 200", 
                    "rating": 4.6, 
                    "duration": "1-2 hours", 
                    "best_time": "Morning",
                    "features": ["Reclining Buddha", "Thai massage school", "Temple complex"],
                    "image_file": "WP.jpg",
                    "description": "Home to the magnificent 46-meter long Reclining Buddha."
                }
            ],
            "Singapore, Singapore": [
                {
                    "name": "Gardens by the Bay",
                    "price": "S$ 28", 
                    "rating": 4.8, 
                    "duration": "3-4 hours", 
                    "best_time": "Evening",
                    "features": ["Supertrees", "Cloud Forest", "Flower Dome"],
                    "image_file": "GBTB.jpg",
                    "description": "Futuristic nature park with iconic Supertrees and biodomes."
                },
                {
                    "name": "Marina Bay Sands",
                    "price": "S$ 23", 
                    "rating": 4.7, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["Infinity pool", "Observation deck", "Shopping"],
                    "image_file": "MBS.jpg",
                    "description": "Iconic integrated resort with the world's largest infinity pool."
                },
                {
                    "name": "Sentosa Island",
                    "price": "S$ 4", 
                    "rating": 4.6, 
                    "duration": "Full day", 
                    "best_time": "All day",
                    "features": ["Beaches", "Universal Studios", "Resorts World"],
                    "image_file": "SI.jpg",
                    "description": "Island resort with beaches, theme parks, and entertainment."
                },
                {
                    "name": "Singapore Zoo",
                    "price": "S$ 48", 
                    "rating": 4.7, 
                    "duration": "4-5 hours", 
                    "best_time": "Morning",
                    "features": ["Rainforest zoo", "Animal shows", "Open enclosures"],
                    "image_file": "SZ.jpg",
                    "description": "World-renowned rainforest zoo with open enclosures."
                }
            ],
            "Hong Kong, China": [
                {
                    "name": "Victoria Peak",
                    "price": "HK$ 52", 
                    "rating": 4.8, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["Peak Tram", "Sky Terrace", "City views"],
                    "image_file": "VP.jpg",
                    "description": "Highest point on Hong Kong Island with spectacular harbor views."
                },
                {
                    "name": "Star Ferry",
                    "price": "HK$ 5", 
                    "rating": 4.7, 
                    "duration": "30 mins", 
                    "best_time": "Evening",
                    "features": ["Harbor cruise", "Iconic ferry", "Affordable"],
                    "image_file": "SF.jpg",
                    "description": "Iconic ferry offering stunning views of Hong Kong's skyline."
                },
                {
                    "name": "Tian Tan Buddha",
                    "price": "Free", 
                    "rating": 4.6, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Giant Buddha", "Cable car", "Monastery"],
                    "image_file": "TTB.jpg",
                    "description": "34-meter tall bronze Buddha statue on Lantau Island."
                },
                {
                    "name": "Temple Street Night Market",
                    "price": "Free", 
                    "rating": 4.4, 
                    "duration": "1-2 hours", 
                    "best_time": "Evening",
                    "features": ["Street market", "Local food", "Bargain shopping"],
                    "image_file": "TSNM.jpg",
                    "description": "Vibrant night market famous for street food and shopping."
                }
            ],
            "Taipei, Taiwan": [
                {
                    "name": "Taipei 101",
                    "price": "NT$ 600", 
                    "rating": 4.8, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["Observation deck", "Damper ball", "Shopping mall"],
                    "image_file": "T101.jpg",
                    "description": "Iconic skyscraper that was once the world's tallest building."
                },
                {
                    "name": "Shilin Night Market",
                    "price": "Free", 
                    "rating": 4.7, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["Street food", "Shopping", "Local culture"],
                    "image_file": "SNM.jpg",
                    "description": "Largest and most famous night market in Taipei."
                },
                {
                    "name": "National Palace Museum",
                    "price": "NT$ 350", 
                    "rating": 4.7, 
                    "duration": "3-4 hours", 
                    "best_time": "Morning",
                    "features": ["Chinese artifacts", "Jade collection", "Historical"],
                    "image_file": "NPM.jpg",
                    "description": "Home to one of the largest collections of Chinese artifacts."
                },
                {
                    "name": "Elephant Mountain",
                    "price": "Free", 
                    "rating": 4.6, 
                    "duration": "1-2 hours", 
                    "best_time": "Sunset",
                    "features": ["Hiking trail", "City views", "Photo spot"],
                    "image_file": "EM.jpg",
                    "description": "Popular hiking spot offering stunning views of Taipei 101."
                }
            ],
            "Shanghai, China": [
                {
                    "name": "The Bund",
                    "price": "Free", 
                    "rating": 4.8, 
                    "duration": "1-2 hours", 
                    "best_time": "Evening",
                    "features": ["Colonial architecture", "River views", "Historical"],
                    "image_file": "TB.jpg",
                    "description": "Famous waterfront area with colonial-era buildings."
                },
                {
                    "name": "Shanghai Tower",
                    "price": "¥ 180", 
                    "rating": 4.7, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["World's 2nd tallest", "Observation deck", "Fast elevator"],
                    "image_file": "STower.jpg",
                    "description": "China's tallest building with breathtaking panoramic views."
                },
                {
                    "name": "Yu Garden",
                    "price": "¥ 40", 
                    "rating": 4.6, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Classical garden", "Tea house", "Traditional architecture"],
                    "image_file": "YG.jpg",
                    "description": "Beautiful classical Chinese garden from the Ming Dynasty."
                },
                {
                    "name": "Nanjing Road",
                    "price": "Free", 
                    "rating": 4.5, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["Shopping street", "Pedestrian mall", "Historical"],
                    "image_file": "NR.jpg",
                    "description": "One of the world's busiest shopping streets with modern malls."
                }
            ],
            "Beijing, China": [
                {
                    "name": "Great Wall of China",
                    "price": "¥ 45", 
                    "rating": 4.9, 
                    "duration": "Full day", 
                    "best_time": "Morning",
                    "features": ["UNESCO site", "Hiking", "Historical"],
                    "image_file": "GWOC.jpg",
                    "description": "Ancient fortification stretching over 13,000 miles across China."
                },
                {
                    "name": "Forbidden City",
                    "price": "¥ 60", 
                    "rating": 4.8, 
                    "duration": "3-4 hours", 
                    "best_time": "Morning",
                    "features": ["Imperial palace", "UNESCO site", "Historical"],
                    "image_file": "FC.jpg",
                    "description": "Former Chinese imperial palace from Ming to Qing Dynasties."
                },
                {
                    "name": "Temple of Heaven",
                    "price": "¥ 15", 
                    "rating": 4.7, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Imperial temple", "UNESCO site", "Park"],
                    "image_file": "TOH.jpg",
                    "description": "Imperial complex where emperors prayed for good harvests."
                },
                {
                    "name": "Summer Palace",
                    "price": "¥ 30", 
                    "rating": 4.7, 
                    "duration": "3-4 hours", 
                    "best_time": "Morning",
                    "features": ["Imperial garden", "Kunming Lake", "Long Corridor"],
                    "image_file": "SP.jpg",
                    "description": "Vast ensemble of lakes, gardens and palaces from Qing Dynasty."
                }
            ],
            "Penang, Malaysia": [
                {
                    "name": "George Town Street Art",
                    "price": "Free", 
                    "rating": 4.8, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Murals", "Historical buildings", "Walking tour"],
                    "image_file": "GTSA.jpg",
                    "description": "UNESCO World Heritage Site famous for street art and murals."
                },
                {
                    "name": "Kek Lok Si Temple",
                    "price": "RM 2", 
                    "rating": 4.7, 
                    "duration": "2-3 hours", 
                    "best_time": "Morning",
                    "features": ["Buddhist temple", "Giant statue", "Pagoda"],
                    "image_file": "KLST.jpg",
                    "description": "Largest Buddhist temple in Malaysia with beautiful architecture."
                },
                {
                    "name": "Penang Hill",
                    "price": "RM 30", 
                    "rating": 4.6, 
                    "duration": "3-4 hours", 
                    "best_time": "Morning",
                    "features": ["Funicular railway", "Cool weather", "Viewpoints"],
                    "image_file": "PH.jpg",
                    "description": "Hill station with panoramic views of Penang and mainland."
                },
                {
                    "name": "Batu Ferringhi Beach",
                    "price": "Free", 
                    "rating": 4.5, 
                    "duration": "2-3 hours", 
                    "best_time": "Evening",
                    "features": ["Beach", "Water sports", "Night market"],
                    "image_file": "BFB.jpg",
                    "description": "Popular beach with water sports, resorts, and night market."
                }
            ],
        }
    
    def load_restaurants_data(self):
        return {
            "Kuala Lumpur, Malaysia": [
                {"name": "Jalan Alor Food Street", "type": "Street Food", "price_range": "RM 10-30", "rating": 4.5, "features": ["Local cuisine", "Night market", "Variety"]},
                {"name": "Nasi Kandar Pelita", "type": "Local", "price_range": "RM 15-25", "rating": 4.3, "features": ["Malay-Indian", "24 hours", "Popular"]},
            ],
            "Tokyo, Japan": [
                {"name": "Tsukiji Outer Market", "type": "Market", "price_range": "¥ 1,000-3,000", "rating": 4.7, "features": ["Seafood", "Fresh sushi", "Market atmosphere"]},
                {"name": "Ichiran Ramen", "type": "Ramen", "price_range": "¥ 890", "rating": 4.5, "features": ["Tonkotsu ramen", "Individual booths", "24 hours"]},
            ],
            "Bangkok, Thailand": [
                {"name": "Jay Fai", "type": "Street Food", "price_range": "฿ 500-1,000", "rating": 4.8, "features": ["Michelin star", "Crab omelette", "Long queues"]},
                {"name": "Thip Samai Pad Thai", "type": "Local", "price_range": "฿ 100-200", "rating": 4.6, "features": ["Famous pad thai", "Open late", "Popular"]},
            ],
            "Singapore, Singapore": [
                {"name": "Lau Pa Sat", "type": "Hawker Centre", "price_range": "S$ 5-15", "rating": 4.5, "features": ["Satay street", "Local food", "Historic"]},
                {"name": "Newton Food Centre", "type": "Hawker Centre", "price_range": "S$ 10-20", "rating": 4.4, "features": ["Seafood", "Local dishes", "Night market"]},
            ],
            "Hong Kong, China": [
                {"name": "Tim Ho Wan", "type": "Dim Sum", "price_range": "HK$ 50-100", "rating": 4.6, "features": ["Michelin star", "Affordable", "Pork buns"]},
                {"name": "Lan Fong Yuen", "type": "Cha Chaan Teng", "price_range": "HK$ 40-80", "rating": 4.4, "features": ["Hong Kong milk tea", "Local breakfast", "Historic"]},
            ],
            "Taipei, Taiwan": [
                {"name": "Din Tai Fung", "type": "Dim Sum", "price_range": "NT$ 200-400", "rating": 4.7, "features": ["Xiao long bao", "Michelin star", "International"]},
                {"name": "Raohe Night Market", "type": "Night Market", "price_range": "NT$ 50-150", "rating": 4.6, "features": ["Street food", "Local snacks", "Vibrant"]},
            ],
            "Shanghai, China": [
                {"name": "Jia Jia Tang Bao", "type": "Soup Dumplings", "price_range": "¥ 30-60", "rating": 4.5, "features": ["Xiao long bao", "Authentic", "Local favorite"]},
                {"name": "Yang's Fry Dumplings", "type": "Dumplings", "price_range": "¥ 20-40", "rating": 4.4, "features": ["Sheng jian bao", "Crispy", "Popular"]},
            ],
            "Beijing, China": [
                {"name": "Quanjude Roast Duck", "type": "Peking Duck", "price_range": "¥ 200-400", "rating": 4.6, "features": ["Traditional", "Historic", "Signature dish"]},
                {"name": "Huguosi Snacks", "type": "Street Food", "price_range": "¥ 20-50", "rating": 4.5, "features": ["Local snacks", "Traditional", "Variety"]},
            ],
            "Penang, Malaysia": [
                {"name": "Gurney Drive Hawker Centre", "type": "Hawker Centre", "price_range": "RM 10-30", "rating": 4.6, "features": ["Seafood", "Local dishes", "Seaside"]},
                {"name": "New Lane Hawker Centre", "type": "Hawker Centre", "price_range": "RM 5-20", "rating": 4.5, "features": ["Street food", "Local favorites", "Night market"]},
            ],
        }
    
    def load_car_rental_data(self):
        """Load car rental data with local images"""
        return {
            "Kuala Lumpur, Malaysia": [
                {
                    "name": "Toyota Vios",
                    "type": "Sedan",
                    "price_per_day": "RM 120",
                    "features": ["Air Conditioning", "Automatic", "5 Seats", "Bluetooth"],
                    "image_file": "TVios.jpg",
                    "rating": 4.3,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["City driving", "Family trips", "Business"]
                },
                {
                    "name": "Honda HR-V",
                    "type": "SUV",
                    "price_per_day": "RM 180",
                    "features": ["GPS", "Automatic", "5 Seats", "Reverse Camera"],
                    "image_file": "HRV.jpg",
                    "rating": 4.5,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Family trips", "Road trips", "Extra space"]
                },
            ],
            "Tokyo, Japan": [
                {
                    "name": "Toyota Prius",
                    "type": "Hybrid",
                    "price_per_day": "¥ 6,000",
                    "features": ["Hybrid", "Fuel Efficient", "Automatic", "GPS"],
                    "image_file": "TPrius.jpg",
                    "rating": 4.4,
                    "transmission": "Automatic",
                    "fuel": "Hybrid",
                    "suitable_for": ["City driving", "Eco-friendly", "Long distance"]
                },
                {
                    "name": "Nissan X-Trail",
                    "type": "SUV",
                    "price_per_day": "¥ 8,500",
                    "features": ["4WD", "Automatic", "7 Seats", "Winter Tires"],
                    "image_file": "Nissan_XTrail.jpg",
                    "rating": 4.5,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Mountain trips", "Family", "All weather"]
                },
            ],
            "Bangkok, Thailand": [
                {
                    "name": "Toyota Yaris",
                    "type": "Hatchback",
                    "price_per_day": "฿ 1,200",
                    "features": ["Fuel Efficient", "Automatic", "5 Seats", "City Car"],
                    "image_file": "Toyota_Yaris.jpg",
                    "rating": 4.3,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["City driving", "Budget", "Small groups"]
                },
                {
                    "name": "Honda CR-V",
                    "type": "SUV",
                    "price_per_day": "฿ 2,000",
                    "features": ["Spacious", "Automatic", "5 Seats", "Comfort"],
                    "image_file": "Honda_CRV.jpg",
                    "rating": 4.5,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Family trips", "Road trips", "Comfort"]
                },
            ],
            "Singapore, Singapore": [
                {
                    "name": "Mercedes-Benz A-Class",
                    "type": "Luxury Sedan",
                    "price_per_day": "S$ 150",
                    "features": ["Premium", "Automatic", "5 Seats", "Tech Features"],
                    "image_file": "Mercedes_A_Class.jpg",
                    "rating": 4.6,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Business", "Luxury", "Comfort"]
                },
                {
                    "name": "Hyundai i10",
                    "type": "Compact",
                    "price_per_day": "S$ 80",
                    "features": ["Compact", "Easy Parking", "Fuel Efficient", "Basic"],
                    "image_file": "Hyundai_i10.jpg",
                    "rating": 4.2,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["City driving", "Budget", "Solo/Couple"]
                },
            ],
            "Hong Kong, China": [
                {
                    "name": "BMW 3 Series",
                    "type": "Luxury Sedan",
                    "price_per_day": "HK$ 1,200",
                    "features": ["Premium", "Automatic", "5 Seats", "Luxury Features"],
                    "image_file": "BMW_3_Series.jpg",
                    "rating": 4.7,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Business", "Luxury", "Comfort"]
                },
                {
                    "name": "Toyota Corolla",
                    "type": "Sedan",
                    "price_per_day": "HK$ 600",
                    "features": ["Reliable", "Automatic", "5 Seats", "Comfort"],
                    "image_file": "Toyota_Corolla.jpg",
                    "rating": 4.4,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["City driving", "Family", "Business"]
                },
            ],
            "Taipei, Taiwan": [
                {
                    "name": "Toyota Camry",
                    "type": "Sedan",
                    "price_per_day": "NT$ 2,500",
                    "features": ["Comfort", "Automatic", "5 Seats", "Spacious"],
                    "image_file": "Toyota_Camry.jpg",
                    "rating": 4.5,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Family trips", "Comfort", "Long distance"]
                },
                {
                    "name": "Mazda CX-5",
                    "type": "SUV",
                    "price_per_day": "NT$ 3,000",
                    "features": ["Stylish", "Automatic", "5 Seats", "Premium"],
                    "image_file": "Mazda_CX5.jpg",
                    "rating": 4.6,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Family", "Style", "Comfort"]
                },
            ],
            "Shanghai, China": [
                {
                    "name": "Volkswagen Lavida",
                    "type": "Sedan",
                    "price_per_day": "¥ 400",
                    "features": ["Popular", "Automatic", "5 Seats", "Comfort"],
                    "image_file": "Volkswagen_Lavida.jpg",
                    "rating": 4.3,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["City driving", "Family", "Business"]
                },
                {
                    "name": "Buick GL8",
                    "type": "MPV",
                    "price_per_day": "¥ 600",
                    "features": ["Spacious", "Automatic", "7 Seats", "Comfort"],
                    "image_file": "Buick_GL8.jpg",
                    "rating": 4.5,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Large groups", "Family", "Business"]
                },
            ],
            "Beijing, China": [
                {
                    "name": "Audi A6L",
                    "type": "Luxury Sedan",
                    "price_per_day": "¥ 800",
                    "features": ["Premium", "Automatic", "5 Seats", "Luxury"],
                    "image_file": "Audi_A6L.jpg",
                    "rating": 4.7,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Business", "Luxury", "Comfort"]
                },
                {
                    "name": "Haval H6",
                    "type": "SUV",
                    "price_per_day": "¥ 450",
                    "features": ["Chinese brand", "Automatic", "5 Seats", "Value"],
                    "image_file": "Haval_H6.jpg",
                    "rating": 4.4,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["Family", "Value", "Comfort"]
                },
            ],
            "Penang, Malaysia": [
                {
                    "name": "Perodua Myvi",
                    "type": "Hatchback",
                    "price_per_day": "RM 80",
                    "features": ["Fuel Efficient", "Easy Parking", "5 Seats", "Basic"],
                    "image_file": "Perodua_Myvi.jpg",
                    "rating": 4.2,
                    "transmission": "Automatic",
                    "fuel": "Petrol",
                    "suitable_for": ["City driving", "Budget travel", "Solo/Couple"]
                },
                {
                    "name": "Toyota Hilux",
                    "type": "Pickup Truck",
                    "price_per_day": "RM 200",
                    "features": ["Rugged", "Automatic", "5 Seats", "Durable"],
                    "image_file": "Toyota_Hilux.jpg",
                    "rating": 4.5,
                    "transmission": "Automatic",
                    "fuel": "Diesel",
                    "suitable_for": ["Adventure", "Rural areas", "Durability"]
                },
            ],
        }
    
    # Cost calculation methods
    def calculate_accommodation_cost(self):
        days = self.itinerary_data['days']
        budget = self.itinerary_data['budget']
        travelers = self.itinerary_data['travelers']
        destination = self.itinerary_data['destination']
        
        if "Malaysia" in destination:
            if "Low" in budget:
                base = 60
            elif "Medium" in budget:
                base = 120
            elif "High" in budget:
                base = 250
            else:  # Luxury
                base = 400
            cost = base * days * travelers
            return f"RM {cost:,.0f}"
        elif "Japan" in destination:
            if "Low" in budget:
                base = 3000
            elif "Medium" in budget:
                base = 7000
            elif "High" in budget:
                base = 15000
            else:  # Luxury
                base = 25000
            cost = base * days * travelers
            return f"¥ {cost:,.0f}"
        elif "Thailand" in destination:
            if "Low" in budget:
                base = 800
            elif "Medium" in budget:
                base = 2000
            elif "High" in budget:
                base = 4000
            else:  # Luxury
                base = 8000
            cost = base * days * travelers
            return f"฿ {cost:,.0f}"
        elif "Singapore" in destination:
            if "Low" in budget:
                base = 100
            elif "Medium" in budget:
                base = 250
            elif "High" in budget:
                base = 500
            else:  # Luxury
                base = 1000
            cost = base * days * travelers
            return f"S$ {cost:,.0f}"
        elif "Hong Kong" in destination:
            if "Low" in budget:
                base = 500
            elif "Medium" in budget:
                base = 1200
            elif "High" in budget:
                base = 2500
            else:  # Luxury
                base = 5000
            cost = base * days * travelers
            return f"HK$ {cost:,.0f}"
        elif "Taiwan" in destination:
            if "Low" in budget:
                base = 1200
            elif "Medium" in budget:
                base = 2500
            elif "High" in budget:
                base = 5000
            else:  # Luxury
                base = 10000
            cost = base * days * travelers
            return f"NT$ {cost:,.0f}"
        else:  # China (Shanghai/Beijing)
            if "Low" in budget:
                base = 200
            elif "Medium" in budget:
                base = 500
            elif "High" in budget:
                base = 1000
            else:  # Luxury
                base = 2000
            cost = base * days * travelers
            return f"¥ {cost:,.0f}"
        return "N/A"
    
    def calculate_food_cost(self):
        days = self.itinerary_data['days']
        budget = self.itinerary_data['budget']
        travelers = self.itinerary_data['travelers']
        destination = self.itinerary_data['destination']
        
        if "Malaysia" in destination:
            if "Low" in budget:
                daily = 40
            elif "Medium" in budget:
                daily = 80
            elif "High" in budget:
                daily = 150
            else:  # Luxury
                daily = 250
            cost = daily * days * travelers
            return f"RM {cost:,.0f}"
        elif "Japan" in destination:
            if "Low" in budget:
                daily = 2000
            elif "Medium" in budget:
                daily = 4000
            elif "High" in budget:
                daily = 8000
            else:  # Luxury
                daily = 15000
            cost = daily * days * travelers
            return f"¥ {cost:,.0f}"
        elif "Thailand" in destination:
            if "Low" in budget:
                daily = 300
            elif "Medium" in budget:
                daily = 600
            elif "High" in budget:
                daily = 1200
            else:  # Luxury
                daily = 2500
            cost = daily * days * travelers
            return f"฿ {cost:,.0f}"
        elif "Singapore" in destination:
            if "Low" in budget:
                daily = 30
            elif "Medium" in budget:
                daily = 60
            elif "High" in budget:
                daily = 120
            else:  # Luxury
                daily = 250
            cost = daily * days * travelers
            return f"S$ {cost:,.0f}"
        elif "Hong Kong" in destination:
            if "Low" in budget:
                daily = 150
            elif "Medium" in budget:
                daily = 300
            elif "High" in budget:
                daily = 600
            else:  # Luxury
                daily = 1200
            cost = daily * days * travelers
            return f"HK$ {cost:,.0f}"
        elif "Taiwan" in destination:
            if "Low" in budget:
                daily = 300
            elif "Medium" in budget:
                daily = 600
            elif "High" in budget:
                daily = 1200
            else:  # Luxury
                daily = 2500
            cost = daily * days * travelers
            return f"NT$ {cost:,.0f}"
        else:  # China (Shanghai/Beijing)
            if "Low" in budget:
                daily = 100
            elif "Medium" in budget:
                daily = 200
            elif "High" in budget:
                daily = 400
            else:  # Luxury
                daily = 800
            cost = daily * days * travelers
            return f"¥ {cost:,.0f}"
        return "N/A"
    
    def calculate_activities_cost(self):
        days = self.itinerary_data['days']
        budget = self.itinerary_data['budget']
        travelers = self.itinerary_data['travelers']
        destination = self.itinerary_data['destination']
        
        if "Malaysia" in destination:
            if "Low" in budget:
                daily = 30
            elif "Medium" in budget:
                daily = 60
            elif "High" in budget:
                daily = 120
            else:  # Luxury
                daily = 200
            cost = daily * days * travelers
            return f"RM {cost:,.0f}"
        elif "Japan" in destination:
            if "Low" in budget:
                daily = 1500
            elif "Medium" in budget:
                daily = 3000
            elif "High" in budget:
                daily = 6000
            else:  # Luxury
                daily = 10000
            cost = daily * days * travelers
            return f"¥ {cost:,.0f}"
        elif "Thailand" in destination:
            if "Low" in budget:
                daily = 500
            elif "Medium" in budget:
                daily = 1000
            elif "High" in budget:
                daily = 2000
            else:  # Luxury
                daily = 4000
            cost = daily * days * travelers
            return f"฿ {cost:,.0f}"
        elif "Singapore" in destination:
            if "Low" in budget:
                daily = 40
            elif "Medium" in budget:
                daily = 80
            elif "High" in budget:
                daily = 150
            else:  # Luxury
                daily = 300
            cost = daily * days * travelers
            return f"S$ {cost:,.0f}"
        elif "Hong Kong" in destination:
            if "Low" in budget:
                daily = 100
            elif "Medium" in budget:
                daily = 200
            elif "High" in budget:
                daily = 400
            else:  # Luxury
                daily = 800
            cost = daily * days * travelers
            return f"HK$ {cost:,.0f}"
        elif "Taiwan" in destination:
            if "Low" in budget:
                daily = 400
            elif "Medium" in budget:
                daily = 800
            elif "High" in budget:
                daily = 1600
            else:  # Luxury
                daily = 3000
            cost = daily * days * travelers
            return f"NT$ {cost:,.0f}"
        else:  # China (Shanghai/Beijing)
            if "Low" in budget:
                daily = 150
            elif "Medium" in budget:
                daily = 300
            elif "High" in budget:
                daily = 600
            else:  # Luxury
                daily = 1200
            cost = daily * days * travelers
            return f"¥ {cost:,.0f}"
        return "N/A"
    
    def calculate_transportation_cost(self):
        days = self.itinerary_data['days']
        budget = self.itinerary_data['budget']
        travelers = self.itinerary_data['travelers']
        destination = self.itinerary_data['destination']
        
        if "Malaysia" in destination:
            if "Low" in budget:
                daily = 20
            elif "Medium" in budget:
                daily = 40
            elif "High" in budget:
                daily = 80
            else:  # Luxury
                daily = 150
            cost = daily * days * travelers
            return f"RM {cost:,.0f}"
        elif "Japan" in destination:
            if "Low" in budget:
                daily = 1000
            elif "Medium" in budget:
                daily = 2000
            elif "High" in budget:
                daily = 4000
            else:  # Luxury
                daily = 8000
            cost = daily * days * travelers
            return f"¥ {cost:,.0f}"
        elif "Thailand" in destination:
            if "Low" in budget:
                daily = 200
            elif "Medium" in budget:
                daily = 400
            elif "High" in budget:
                daily = 800
            else:  # Luxury
                daily = 1500
            cost = daily * days * travelers
            return f"฿ {cost:,.0f}"
        elif "Singapore" in destination:
            if "Low" in budget:
                daily = 15
            elif "Medium" in budget:
                daily = 30
            elif "High" in budget:
                daily = 60
            else:  # Luxury
                daily = 120
            cost = daily * days * travelers
            return f"S$ {cost:,.0f}"
        elif "Hong Kong" in destination:
            if "Low" in budget:
                daily = 50
            elif "Medium" in budget:
                daily = 100
            elif "High" in budget:
                daily = 200
            else:  # Luxury
                daily = 400
            cost = daily * days * travelers
            return f"HK$ {cost:,.0f}"
        elif "Taiwan" in destination:
            if "Low" in budget:
                daily = 200
            elif "Medium" in budget:
                daily = 400
            elif "High" in budget:
                daily = 800
            else:  # Luxury
                daily = 1500
            cost = daily * days * travelers
            return f"NT$ {cost:,.0f}"
        else:  # China (Shanghai/Beijing)
            if "Low" in budget:
                daily = 50
            elif "Medium" in budget:
                daily = 100
            elif "High" in budget:
                daily = 200
            else:  # Luxury
                daily = 400
            cost = daily * days * travelers
            return f"¥ {cost:,.0f}"
        return "N/A"