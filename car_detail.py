import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import io
from datetime import datetime, timedelta
import os
import random

class CarDetailApp:
    def __init__(self, root, vehicle, email):
        self.root = root
        self.vehicle = vehicle
        self.email = email
        
        # Set full screen by default
        self.root.title(f"Traney - {vehicle['name']}")
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
            "calendar_bg": "#ffffff",
            "calendar_header": "#1e3d59",
            "calendar_selected": "#ff6e40",
            "electric": "#48bb78",
            "premium": "#d69e2e",
        }
        
        # Image cache
        self.image_cache = {}
        
        # Ensure vehicle has all required fields
        self.ensure_vehicle_fields()
        
        # Create UI
        self.setup_ui()
        
        # Bind Escape key to toggle fullscreen
        self.root.bind("<Escape>", self.toggle_fullscreen)
    
    def ensure_vehicle_fields(self):
        """Ensure the vehicle has all required fields"""
        default_fields = {
            "transmission": "Automatic",
            "fuel_type": "Petrol",
            "seats": "4",
            "luggage": "2 Large Bags",
            "features": ["Air Conditioning", "Bluetooth", "GPS Navigation"],
            "pickup_locations": ["Main Airport", "City Center", "Downtown", "Train Station", "Hotel Zone"],
            "included": ["Unlimited Mileage", "Insurance", "24/7 Roadside Assistance"],
            "requirements": ["Valid Driver's License", "Credit Card", "Minimum Age: 21"],
            "color": "#4f46e5",
            "category": "Vehicle",
            "engine": "N/A",
            "is_electric": False,
            "discount": 0,
            "daily_rate": 0,
            "rating": 4.0,
            "reviews": 0,
            "available": 1,
            "range_km": "N/A",
            "charge_time": "N/A",
            "original_rate": 0,
            "original_price": 0
        }
        
        for field, default_value in default_fields.items():
            if field not in self.vehicle:
                self.vehicle[field] = default_value
        
        # Ensure price and daily_rate exist
        if "price" not in self.vehicle and "daily_rate" in self.vehicle:
            self.vehicle["price"] = self.vehicle["daily_rate"]
        elif "daily_rate" not in self.vehicle and "price" in self.vehicle:
            self.vehicle["daily_rate"] = self.vehicle["price"]
        elif "price" not in self.vehicle and "daily_rate" not in self.vehicle:
            self.vehicle["price"] = 100
            self.vehicle["daily_rate"] = 100
        
        # Ensure original price for discount
        if self.vehicle["discount"] > 0:
            self.vehicle["original_price"] = int(self.vehicle["price"] / (1 - self.vehicle["discount"]/100))
            self.vehicle["original_rate"] = int(self.vehicle["daily_rate"] / (1 - self.vehicle["discount"]/100))
        else:
            self.vehicle["original_price"] = self.vehicle["price"]
            self.vehicle["original_rate"] = self.vehicle["daily_rate"]
        
        # Ensure tags exist
        if "tags" not in self.vehicle or not self.vehicle["tags"]:
            self.vehicle["tags"] = [self.vehicle.get("type", "Vehicle")]
    
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
        back_btn = tk.Button(header_container, text="← Back to Car Rentals",
                           font=("Segoe UI", 12, "bold"),
                           bg=self.colors["nav_bg"], fg="white",
                           relief="flat", cursor="hand2",
                           command=self.go_back)
        back_btn.pack(side="left")
        self.add_hover_effect(back_btn, "#2a4d6e", self.colors["nav_bg"])
        
        # Title centered
        title_label = tk.Label(header_container, 
                             text=self.vehicle["name"][:40] + ("..." if len(self.vehicle["name"]) > 40 else ""),
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
        """Create detailed vehicle content"""
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
            photo = self.get_vehicle_image(self.vehicle, (1200, 400))
            image_label = tk.Label(hero_frame, image=photo, bg="white")
            image_label.image = photo
            image_label.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Error loading image: {e}")
            # Fallback if image fails to load
            fallback_frame = tk.Frame(hero_frame, bg=self.vehicle.get("color", "#3498db"))
            fallback_frame.pack(fill="both", expand=True)
            tk.Label(fallback_frame, text="🚗", font=("Arial", 64),
                    bg=self.vehicle.get("color", "#3498db"), fg="white").pack(expand=True)
        
        # Overlay with vehicle name
        overlay = tk.Frame(hero_frame, bg="#333333", height=80)
        overlay.place(relx=0, rely=1, y=-80, relwidth=1)
        
        # Add price badge
        price_text = f"RM {self.vehicle['price']}/day"
        price_label = tk.Label(overlay, text=price_text, 
                              font=("Segoe UI", 14, "bold"),
                              bg=self.colors["secondary"], fg="white",
                              padx=15, pady=5)
        price_label.place(relx=0.05, rely=0.5, anchor="w")
        
        tk.Label(overlay, text=self.vehicle["name"], 
                font=("Segoe UI", 20, "bold"),
                bg="#333333", fg="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # Add type badge
        type_badge = tk.Label(overlay, text=self.vehicle.get("category", "Vehicle"), 
                             font=("Segoe UI", 12, "bold"),
                             bg=self.colors["primary"], fg="white",
                             padx=10, pady=3)
        type_badge.place(relx=0.95, rely=0.5, anchor="e")
    
    def get_vehicle_image(self, car_data, size):
        """Get vehicle image from local files"""
        car_name = car_data.get('name', '')
        cache_key = f"{car_name}_{size[0]}_{size[1]}"
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        filename = car_data.get('image_file', 'car.jpg')
        image_path = os.path.join("images/cars", filename)
        
        # Check if file exists in cars folder
        if not os.path.exists(image_path):
            # Try to find generic car images
            generic_files = ["car.jpg", "car1.jpg", "car2.jpg", "car3.jpg", "car4.jpg"]
            for file in generic_files:
                alt_path = os.path.join("images/cars", file)
                if os.path.exists(alt_path):
                    image_path = alt_path
                    break
            else:
                # If still not found, try images folder directly
                for file in generic_files:
                    alt_path = os.path.join("images", file)
                    if os.path.exists(alt_path):
                        image_path = alt_path
                        break
        
        try:
            # Load from local file
            img = Image.open(image_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = photo
            return photo
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return self.create_vehicle_placeholder_image(size)
    
    def create_vehicle_placeholder_image(self, size):
        """Create a placeholder image for vehicles when image is not available"""
        img = Image.new('RGB', size, color='#3498db')
        draw = ImageDraw.Draw(img)
        
        # Draw car icon (simplified for larger size)
        car_width = min(size[0] // 3, 200)
        car_height = min(size[1] // 2, 150)
        car_x = (size[0] - car_width) // 2
        car_y = (size[1] - car_height) // 2
        
        # Draw car body
        draw.rectangle([car_x, car_y, car_x + car_width, car_y + car_height], 
                      fill='white', outline='white', width=2)
        
        # Draw wheels
        wheel_size = car_height // 5
        draw.ellipse([car_x + 10, car_y + car_height - wheel_size - 10,
                     car_x + 10 + wheel_size, car_y + car_height - 10], 
                    fill='black')
        draw.ellipse([car_x + car_width - wheel_size - 10, car_y + car_height - wheel_size - 10,
                     car_x + car_width - 10, car_y + car_height - 10], 
                    fill='black')
        
        # Draw text
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            draw.text((size[0] // 2, size[1] - 30), "Vehicle Image", 
                     fill='white', anchor="mm", font=font)
        except:
            draw.text((size[0] // 2, size[1] - 30), "Vehicle Image", 
                     fill='white', anchor="mm")
        
        photo = ImageTk.PhotoImage(img)
        return photo
    
    def create_details_section(self, parent):
        """Create details section"""
        details_container = tk.Frame(parent, bg="white")
        details_container.pack(fill="x", pady=(0, 20))
        
        # Content with padding
        content = tk.Frame(details_container, bg="white", padx=30, pady=30)
        content.pack(fill="both", expand=True)
        
        # Specs row
        specs_row = tk.Frame(content, bg="white")
        specs_row.pack(fill="x", pady=(0, 20))
        
        specs = [
            ("⚙️ Transmission", self.vehicle["transmission"]),
            ("⛽ Fuel Type", self.vehicle["fuel_type"]),
            ("👥 Seats", str(self.vehicle["seats"])),
            ("🧳 Luggage", f"{self.vehicle['luggage']} bags" if isinstance(self.vehicle['luggage'], (int, float)) else self.vehicle['luggage'])
        ]
        
        for i, (icon, value) in enumerate(specs):
            spec_frame = tk.Frame(specs_row, bg="white")
            spec_frame.pack(side="left", padx=(0, 40))
            
            tk.Label(spec_frame, text=icon, font=("Segoe UI", 16),
                    bg="white").pack(side="left", padx=(0, 5))
            
            tk.Label(spec_frame, text=value, 
                    font=("Segoe UI", 14),
                    bg="white", fg=self.colors["dark"]).pack(side="left")
        
        # Description
        tk.Label(content, text="Vehicle Description", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        desc_frame = tk.Frame(content, bg="white")
        desc_frame.pack(fill="x", pady=(0, 20))
        
        description = self.vehicle.get("description", 
                                      f"A comfortable and reliable {self.vehicle['name']} ({self.vehicle.get('model', '')}) " 
                                      f"perfect for your travel needs. {self.vehicle.get('category', 'Vehicle')} category " 
                                      f"with {self.vehicle.get('engine', 'efficient engine')}.")
        
        tk.Label(desc_frame, text=description, 
                font=("Segoe UI", 14),
                bg="white", fg=self.colors["dark"],
                wraplength=1100, justify="left").pack(anchor="w")
        
        # Features
        tk.Label(content, text="Features", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        features_grid = tk.Frame(content, bg="white")
        features_grid.pack(fill="x", pady=(0, 20))
        
        features_list = self.vehicle["features"]
        if not features_list or not isinstance(features_list, list):
            features_list = ["Air Conditioning", "Power Steering", "ABS Brakes", "Airbags", 
                           "Bluetooth", "USB Ports", "Rear Camera", "Cruise Control"]
        
        for i, feature in enumerate(features_list[:8]):  # Show max 8 features
            feature_frame = tk.Frame(features_grid, bg="white")
            feature_frame.grid(row=i//4, column=i%4, sticky="w", padx=(0, 20), pady=5)
            
            tk.Label(feature_frame, text="✓", 
                    font=("Segoe UI", 14),
                    bg="white", fg=self.colors["success"]).pack(side="left", padx=(0, 10))
            tk.Label(feature_frame, text=feature, 
                    font=("Segoe UI", 14),
                    bg="white", fg=self.colors["dark"]).pack(side="left")
        
        # Details grid
        details_grid = tk.Frame(content, bg=self.colors["light"], padx=20, pady=20)
        details_grid.pack(fill="x", pady=20)
        
        details = [
            ("📍 Pickup Locations", ", ".join(self.vehicle["pickup_locations"][:3])),
            ("📋 Included", ", ".join(self.vehicle["included"][:3])),
            ("✅ Requirements", ", ".join(self.vehicle["requirements"][:3])),
            ("⏰ Minimum Rental", self.vehicle.get("min_rental", "1 day")),
            ("🛡️ Insurance", self.vehicle.get("insurance", "Comprehensive")),
            ("📞 Support", self.vehicle.get("support", "24/7 Available")),
            ("📊 Category", self.vehicle.get("category", "Vehicle")),
            ("🔧 Engine", self.vehicle.get("engine", "N/A")),
            ("🎨 Color", self.vehicle.get("color", "N/A"))
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
            
            tk.Label(detail_card, text=value, 
                    font=("Segoe UI", 12),
                    bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(5, 0))
            
            col += 1
            if col == 3:
                col = 0
                row += 1
        
        for i in range(3):
            details_grid.grid_columnconfigure(i, weight=1)
        
        # Tags
        tk.Label(content, text="Tags", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        tags_frame = tk.Frame(content, bg="white")
        tags_frame.pack(fill="x", pady=(0, 20))
        
        for tag in self.vehicle["tags"]:
            tag_label = tk.Label(tags_frame, text=tag, 
                                font=("Segoe UI", 11),
                                bg=self.colors["primary"], fg="white",
                                padx=12, pady=5)
            tag_label.pack(side="left", padx=5, pady=5)
    
    def create_booking_section(self, parent):
        """Create booking section with calendar and pickup location"""
        booking_container = tk.Frame(parent, bg="white", padx=30, pady=30)
        booking_container.pack(fill="x", pady=(0, 20))
        
        tk.Label(booking_container, text="Book Your Rental", 
                font=("Segoe UI", 24, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 20))
        
        # Booking form
        form_frame = tk.Frame(booking_container, bg="white")
        form_frame.pack(fill="x")
        
        # Date selection row
        date_frame = tk.Frame(form_frame, bg="white")
        date_frame.pack(fill="x", pady=(0, 20))
        
        # Pickup date with calendar popup
        pickup_frame = tk.Frame(date_frame, bg="white")
        pickup_frame.pack(side="left", padx=(0, 40))
        
        tk.Label(pickup_frame, text="📅 Pickup Date", 
                font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # Pickup date entry with calendar button
        pickup_entry_frame = tk.Frame(pickup_frame, bg="white")
        pickup_entry_frame.pack()
        
        # Default pickup date (tomorrow)
        default_pickup = datetime.now() + timedelta(days=1)
        self.pickup_date_var = tk.StringVar(value=default_pickup.strftime("%Y-%m-%d"))
        
        pickup_entry = tk.Entry(pickup_entry_frame, textvariable=self.pickup_date_var,
                              font=("Segoe UI", 12), width=12,
                              relief="solid", borderwidth=1, state="readonly",
                              cursor="hand2")
        pickup_entry.pack(side="left")
        pickup_entry.bind("<Button-1>", lambda e: self.show_calendar("pickup", pickup_entry))
        
        # Calendar button
        pickup_cal_btn = tk.Button(pickup_entry_frame, text="📅",
                                 font=("Segoe UI", 12),
                                 bg=self.colors["primary"], fg="white",
                                 relief="solid", cursor="hand2",
                                 command=lambda: self.show_calendar("pickup", pickup_entry))
        pickup_cal_btn.pack(side="left", padx=(5, 0))
        self.add_hover_effect(pickup_cal_btn, "#2a4d6e", self.colors["primary"])
        
        # Return date with calendar popup
        return_frame = tk.Frame(date_frame, bg="white")
        return_frame.pack(side="left")
        
        tk.Label(return_frame, text="📅 Return Date", 
                font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # Return date entry with calendar button
        return_entry_frame = tk.Frame(return_frame, bg="white")
        return_entry_frame.pack()
        
        # Default return date (3 days after pickup)
        default_return = default_pickup + timedelta(days=3)
        self.return_date_var = tk.StringVar(value=default_return.strftime("%Y-%m-%d"))
        
        return_entry = tk.Entry(return_entry_frame, textvariable=self.return_date_var,
                              font=("Segoe UI", 12), width=12,
                              relief="solid", borderwidth=1, state="readonly",
                              cursor="hand2")
        return_entry.pack(side="left")
        return_entry.bind("<Button-1>", lambda e: self.show_calendar("return", return_entry))
        
        # Calendar button
        return_cal_btn = tk.Button(return_entry_frame, text="📅",
                                 font=("Segoe UI", 12),
                                 bg=self.colors["primary"], fg="white",
                                 relief="solid", cursor="hand2",
                                 command=lambda: self.show_calendar("return", return_entry))
        return_cal_btn.pack(side="left", padx=(5, 0))
        self.add_hover_effect(return_cal_btn, "#2a4d6e", self.colors["primary"])
        
        # Calculate days button
        days_frame = tk.Frame(date_frame, bg="white")
        days_frame.pack(side="right")
        
        # Bind date changes to update days
        self.pickup_date_var.trace("w", lambda *args: self.update_days_and_price())
        self.return_date_var.trace("w", lambda *args: self.update_days_and_price())
        
        self.days_var = tk.IntVar(value=3)
        self.days_label = tk.Label(days_frame, text=f"⏱️ Rental Duration: {self.days_var.get()} days", 
                                  font=("Segoe UI", 14),
                                  bg="white", fg=self.colors["primary"])
        self.days_label.pack()
        
        # Pickup location selection
        location_frame = tk.Frame(form_frame, bg="white")
        location_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(location_frame, text="📍 Select Pickup Point", 
                font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # Different types of pickup points
        pickup_points = [
            {
                "name": "Airport Terminal 1",
                "type": "airport",
                "icon": "✈️",
                "details": "Main Arrivals Hall, Gate A",
                "hours": "24/7"
            },
            {
                "name": "City Center Hub",
                "type": "city",
                "icon": "🏙️",
                "details": "123 Main Street",
                "hours": "7 AM - 10 PM"
            },
            {
                "name": "Train Station Plaza",
                "type": "station",
                "icon": "🚉",
                "details": "Central Station, West Exit",
                "hours": "6 AM - 11 PM"
            },
            {
                "name": "Beachside Resort",
                "type": "resort",
                "icon": "🏖️",
                "details": "Palm Beach Resort Lobby",
                "hours": "8 AM - 9 PM"
            },
            {
                "name": "Shopping Mall",
                "type": "mall",
                "icon": "🏬",
                "details": "Grand Mall, Parking Level B2",
                "hours": "10 AM - 10 PM"
            },
            {
                "name": "Business District",
                "type": "business",
                "icon": "🏢",
                "details": "Financial Center, Tower 1",
                "hours": "8 AM - 8 PM"
            }
        ]
        
        # Create pickup points selection frame
        self.location_points_frame = tk.Frame(location_frame, bg="white")
        self.location_points_frame.pack(fill="x", pady=(10, 0))
        
        # Variable to track selected location
        self.selected_location_var = tk.StringVar(value="")
        
        # Create location cards
        self.location_cards = []
        for i, point in enumerate(pickup_points):
            card = self.create_location_card(point, i)
            self.location_cards.append(card)
        
        # Time selection for pickup
        time_frame = tk.Frame(form_frame, bg="white")
        time_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(time_frame, text="🕐 Pickup Time", 
                font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # Time selection dropdown
        self.time_var = tk.StringVar(value="10:00 AM")
        time_options = [
            "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM",
            "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM",
            "4:00 PM", "5:00 PM", "6:00 PM"
        ]
        
        time_dropdown = ttk.Combobox(
            time_frame,
            textvariable=self.time_var,
            values=time_options,
            font=("Segoe UI", 12),
            state="readonly",
            width=15
        )
        time_dropdown.pack(side="left")
        
        # Additional options (optional extras)
        extras_frame = tk.Frame(form_frame, bg="white")
        extras_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(extras_frame, text="➕ Additional Services", 
                font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        self.extras_vars = {}
        extras_options = [
            ("Full Insurance Coverage (+RM 30/day)", 30),
            ("GPS Navigation (+RM 15/day)", 15),
            ("Child Seat (+RM 10/day)", 10),
            ("Additional Driver (+RM 20/day)", 20),
            ("Emergency Kit (+RM 5/day)", 5),
            ("WiFi Hotspot (+RM 12/day)", 12)
        ]
        
        extras_grid = tk.Frame(extras_frame, bg="white")
        extras_grid.pack(fill="x")
        
        for i, (option, price) in enumerate(extras_options):
            var = tk.BooleanVar(value=False)
            self.extras_vars[option] = var
            
            row = i // 2
            col = i % 2
            
            check_frame = tk.Frame(extras_grid, bg="white")
            check_frame.grid(row=row, column=col, sticky="w", padx=(0, 40), pady=5)
            
            check = tk.Checkbutton(check_frame, text=option,
                                  variable=var, font=("Segoe UI", 11),
                                  bg="white", fg=self.colors["dark"],
                                  command=self.update_days_and_price)
            check.pack(side="left")
        
        # Price calculation
        price_frame = tk.Frame(form_frame, bg=self.colors["light"], padx=20, pady=20)
        price_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(price_frame, text="Total Rental Cost:",
                font=("Segoe UI", 16),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(side="left")
        
        self.price_label = tk.Label(price_frame,
                                   text=f"RM {self.vehicle['price'] * 3}",
                                   font=("Segoe UI", 24, "bold"),
                                   bg=self.colors["light"],
                                   fg=self.colors["secondary"])
        self.price_label.pack(side="right")
        
        # Price breakdown
        breakdown_frame = tk.Frame(form_frame, bg=self.colors["light"], padx=20, pady=10)
        breakdown_frame.pack(fill="x", pady=(0, 10))
        
        self.breakdown_label = tk.Label(breakdown_frame,
                                       text=f"Base rate: RM {self.vehicle['price']}/day × 3 days = RM {self.vehicle['price'] * 3}",
                                       font=("Segoe UI", 11),
                                       bg=self.colors["light"], fg=self.colors["text_light"])
        self.breakdown_label.pack(anchor="w")
        
        # Action buttons
        action_frame = tk.Frame(form_frame, bg="white")
        action_frame.pack(fill="x", pady=(20, 0))
        
        # Back button
        back_btn = tk.Button(action_frame, text="← Back to Car Rentals",
                           font=("Segoe UI", 12),
                           bg=self.colors["light"], fg=self.colors["primary"],
                           relief="solid", cursor="hand2",
                           command=self.go_back,
                           padx=30, pady=10)
        back_btn.pack(side="left", padx=(0, 20))
        self.add_hover_effect(back_btn, "#e2e8f0", self.colors["light"])
        
        # Book Now button
        book_btn = tk.Button(action_frame, text="🚗 Book Now",
                           font=("Segoe UI", 14, "bold"),
                           bg=self.colors["primary"], fg="white",
                           relief="solid", cursor="hand2",
                           command=self.open_booking_detail,
                           padx=40, pady=10)
        book_btn.pack(side="right")
        self.add_hover_effect(book_btn, "#2a4d6e", self.colors["primary"])
        
        # Initialize price calculation
        self.update_days_and_price()
    
    def create_location_card(self, point, index):
        """Create a selectable location card"""
        row = index // 3
        col = index % 3
        
        card_frame = tk.Frame(self.location_points_frame, bg="white",
                            relief="solid", borderwidth=1,
                            highlightbackground=self.colors["border"])
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Configure grid weights
        self.location_points_frame.grid_columnconfigure(col, weight=1)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg="white", padx=15, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        # Icon and name
        icon_label = tk.Label(content_frame, text=point["icon"], 
                            font=("Segoe UI", 24),
                            bg="white")
        icon_label.pack(anchor="w", pady=(0, 5))
        
        name_label = tk.Label(content_frame, text=point["name"],
                            font=("Segoe UI", 12, "bold"),
                            bg="white", fg=self.colors["primary"])
        name_label.pack(anchor="w", pady=(0, 3))
        
        # Details
        details_label = tk.Label(content_frame, text=point["details"],
                               font=("Segoe UI", 10),
                               bg="white", fg=self.colors["text_light"],
                               wraplength=180)
        details_label.pack(anchor="w", pady=(0, 3))
        
        # Hours
        hours_label = tk.Label(content_frame, text=f"🕐 {point['hours']}",
                              font=("Segoe UI", 10),
                              bg="white", fg=self.colors["text_light"])
        hours_label.pack(anchor="w")
        
        # Selection indicator
        selection_indicator = tk.Frame(card_frame, bg=self.colors["primary"], height=3)
        selection_indicator.pack(fill="x", side="bottom")
        selection_indicator.pack_forget()  # Hide by default
        
        # Store point data and UI elements
        card_data = {
            "frame": card_frame,
            "point": point,
            "indicator": selection_indicator,
            "name_label": name_label,
            "content_frame": content_frame
        }
        
        # Bind click event
        card_frame.bind("<Button-1>", lambda e, cd=card_data: self.select_location_card(cd))
        content_frame.bind("<Button-1>", lambda e, cd=card_data: self.select_location_card(cd))
        icon_label.bind("<Button-1>", lambda e, cd=card_data: self.select_location_card(cd))
        name_label.bind("<Button-1>", lambda e, cd=card_data: self.select_location_card(cd))
        details_label.bind("<Button-1>", lambda e, cd=card_data: self.select_location_card(cd))
        hours_label.bind("<Button-1>", lambda e, cd=card_data: self.select_location_card(cd))
        
        # Change cursor to hand
        for widget in [card_frame, content_frame, icon_label, name_label, details_label, hours_label]:
            widget.config(cursor="hand2")
        
        return card_data
    
    def select_location_card(self, card_data):
        """Handle location card selection"""
        # Reset all cards to unselected state
        for card in self.location_cards:
            card["indicator"].pack_forget()
            card["frame"].config(highlightbackground=self.colors["border"])
            card["content_frame"].config(bg="white")
            card["name_label"].config(fg=self.colors["primary"])
        
        # Set selected card
        card_data["indicator"].pack(fill="x", side="bottom")
        card_data["frame"].config(highlightbackground=self.colors["secondary"])
        card_data["content_frame"].config(bg=self.colors["light"])
        card_data["name_label"].config(fg=self.colors["secondary"])
        
        # Set selected location
        self.selected_location_var.set(f"{card_data['point']['name']} ({card_data['point']['details']})")
    
    def show_calendar(self, calendar_type, entry_widget):
        """Show calendar popup for date selection"""
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Select {calendar_type.capitalize()} Date")
        popup.configure(bg=self.colors["light"])
        popup.geometry("300x300")
        popup.transient(self.root)  # Set to be on top of the main window
        popup.grab_set()  # Make popup modal
        
        # Position popup near the entry widget
        entry_x = entry_widget.winfo_rootx()
        entry_y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        popup.geometry(f"+{entry_x}+{entry_y}")
        
        # Create calendar
        if calendar_type == "pickup":
            current_date = datetime.strptime(self.pickup_date_var.get(), "%Y-%m-%d")
        else:
            current_date = datetime.strptime(self.return_date_var.get(), "%Y-%m-%d")
        
        # Custom calendar widget
        cal_frame = tk.Frame(popup, bg="white", relief="solid", borderwidth=1)
        cal_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Month and year header
        header_frame = tk.Frame(cal_frame, bg=self.colors["calendar_header"])
        header_frame.pack(fill="x")
        
        # Month-Year label
        month_year = current_date.strftime("%B %Y")
        month_label = tk.Label(header_frame, text=month_year,
                             font=("Segoe UI", 12, "bold"),
                             bg=self.colors["calendar_header"], fg="white")
        month_label.pack(pady=5)
        
        # Days of week header
        days_frame = tk.Frame(cal_frame, bg="white")
        days_frame.pack(fill="x")
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            day_label = tk.Label(days_frame, text=day, width=4,
                               font=("Segoe UI", 10, "bold"),
                               bg="white", fg=self.colors["primary"])
            day_label.pack(side="left")
        
        # Days grid
        days_grid = tk.Frame(cal_frame, bg="white")
        days_grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Get first day of month and number of days
        year, month = current_date.year, current_date.month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month + 1, 1) - timedelta(days=1) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)
        
        # Start weekday (0=Monday, 6=Sunday)
        start_weekday = first_day.weekday()
        
        # Create day buttons
        day_buttons = []
        selected_day = current_date.day
        
        # Empty cells for days before the first day of month
        for i in range(start_weekday):
            empty_label = tk.Label(days_grid, text="", width=4, height=2)
            empty_label.grid(row=0, column=i)
        
        # Create day buttons
        row, col = 0, start_weekday
        for day in range(1, last_day.day + 1):
            day_btn = tk.Button(days_grid, text=str(day), width=4, height=2,
                              font=("Segoe UI", 10),
                              bg="white", fg="black",
                              relief="flat",
                              command=lambda d=day, c=calendar_type, p=popup: self.select_date(d, c, p))
            
            if day == selected_day:
                day_btn.config(bg=self.colors["calendar_selected"], fg="white")
            
            day_btn.grid(row=row, column=col, padx=1, pady=1)
            day_buttons.append(day_btn)
            
            # Add hover effect
            self.add_hover_effect(day_btn, self.colors["light"], "white")
            
            col += 1
            if col == 7:
                col = 0
                row += 1
        
        # Navigation buttons
        nav_frame = tk.Frame(popup, bg=self.colors["light"])
        nav_frame.pack(pady=(0, 10))
        
        # Previous month button
        prev_btn = tk.Button(nav_frame, text="← Prev",
                           font=("Segoe UI", 10),
                           bg=self.colors["primary"], fg="white",
                           command=lambda: self.change_month(popup, calendar_type, -1))
        prev_btn.pack(side="left", padx=5)
        self.add_hover_effect(prev_btn, "#2a4d6e", self.colors["primary"])
        
        # Today button
        today_btn = tk.Button(nav_frame, text="Today",
                            font=("Segoe UI", 10),
                            bg=self.colors["secondary"], fg="white",
                            command=lambda: self.select_today(calendar_type, popup))
        today_btn.pack(side="left", padx=5)
        self.add_hover_effect(today_btn, self.colors["accent"], self.colors["secondary"])
        
        # Next month button
        next_btn = tk.Button(nav_frame, text="Next →",
                           font=("Segoe UI", 10),
                           bg=self.colors["primary"], fg="white",
                           command=lambda: self.change_month(popup, calendar_type, 1))
        next_btn.pack(side="left", padx=5)
        self.add_hover_effect(next_btn, "#2a4d6e", self.colors["primary"])
        
        # Close button
        close_btn = tk.Button(popup, text="Close",
                            font=("Segoe UI", 10),
                            bg=self.colors["light"], fg=self.colors["primary"],
                            command=popup.destroy)
        close_btn.pack(pady=(0, 10))
        self.add_hover_effect(close_btn, "#e2e8f0", self.colors["light"])
    
    def select_date(self, day, calendar_type, popup):
        """Handle date selection from calendar"""
        # Get current date from the calendar variable
        if calendar_type == "pickup":
            current_date = datetime.strptime(self.pickup_date_var.get(), "%Y-%m-%d")
        else:
            current_date = datetime.strptime(self.return_date_var.get(), "%Y-%m-%d")
        
        # Create new date with selected day
        selected_date = datetime(current_date.year, current_date.month, day)
        
        # Update the appropriate variable
        if calendar_type == "pickup":
            self.pickup_date_var.set(selected_date.strftime("%Y-%m-%d"))
            # If return date is before new pickup date, adjust it
            return_date = datetime.strptime(self.return_date_var.get(), "%Y-%m-%d")
            if return_date < selected_date:
                new_return = selected_date + timedelta(days=1)
                self.return_date_var.set(new_return.strftime("%Y-%m-%d"))
        else:
            self.return_date_var.set(selected_date.strftime("%Y-%m-%d"))
        
        # Close the popup
        popup.destroy()
        
        # Update days and price
        self.update_days_and_price()
    
    def select_today(self, calendar_type, popup):
        """Select today's date"""
        today = datetime.now()
        
        if calendar_type == "pickup":
            self.pickup_date_var.set(today.strftime("%Y-%m-%d"))
        else:
            self.return_date_var.set(today.strftime("%Y-%m-%d"))
        
        popup.destroy()
        self.update_days_and_price()
    
    def change_month(self, popup, calendar_type, delta):
        """Change month in calendar"""
        # Close current popup and reopen with new month
        popup.destroy()
        
        # Get current date and adjust month
        if calendar_type == "pickup":
            current_date = datetime.strptime(self.pickup_date_var.get(), "%Y-%m-%d")
        else:
            current_date = datetime.strptime(self.return_date_var.get(), "%Y-%m-%d")
        
        # Calculate new month
        year = current_date.year
        month = current_date.month + delta
        
        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1
        
        # Create new date with same day (or last day of month if needed)
        try:
            new_date = datetime(year, month, current_date.day)
        except ValueError:
            # Day doesn't exist in new month (e.g., Feb 30), use last day
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            new_date = datetime(year, month, last_day)
        
        # Update the variable temporarily for calendar display
        if calendar_type == "pickup":
            self.pickup_date_var.set(new_date.strftime("%Y-%m-%d"))
        else:
            self.return_date_var.set(new_date.strftime("%Y-%m-%d"))
        
        # Get entry widget and show calendar again
        if calendar_type == "pickup":
            # Find the pickup entry widget (simplified - in real app you'd store reference)
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    continue
                # Search for the entry widget
                # This is simplified - in production you'd store the widget reference
                pass
        else:
            # Similar for return entry
            pass
        
        # For now, we'll just update the variable and refresh
        # In a full implementation, you'd want to show the calendar again
        self.update_days_and_price()
    
    def update_days_and_price(self, *args):
        """Update rental days and price calculation"""
        try:
            # Calculate days difference
            pickup_date = datetime.strptime(self.pickup_date_var.get(), "%Y-%m-%d")
            return_date = datetime.strptime(self.return_date_var.get(), "%Y-%m-%d")
            
            if return_date < pickup_date:
                self.days_var.set(1)
                self.days_label.config(text="⏱️ Rental Duration: 1 day (minimum)")
                self.price_label.config(text="RM Invalid")
                self.breakdown_label.config(text="Return date must be after pickup date")
                return
            
            days_diff = (return_date - pickup_date).days
            if days_diff == 0:
                days_diff = 1  # Minimum 1 day rental
            
            self.days_var.set(days_diff)
            self.days_label.config(text=f"⏱️ Rental Duration: {days_diff} day(s)")
            
            # Base price
            base_price = self.vehicle["price"] * days_diff
            
            # Calculate extras
            extras_price = 0
            extras_breakdown = []
            
            for option, var in self.extras_vars.items():
                if var.get():
                    # Extract price from option text
                    price_str = option.split("RM ")[1].split("/")[0]
                    price = int(price_str)
                    extras_price += price * days_diff
                    extras_breakdown.append(f"{option.split(' (+')[0]}: +RM {price * days_diff}")
            
            # Total price
            total_price = base_price + extras_price
            
            # Update display
            self.price_label.config(text=f"RM {total_price}")
            
            # Create breakdown text
            breakdown_text = f"Base rate: RM {self.vehicle['price']}/day × {days_diff} days = RM {base_price}"
            if extras_breakdown:
                breakdown_text += "\n" + "\n".join(extras_breakdown)
            
            self.breakdown_label.config(text=breakdown_text)
            
        except ValueError:
            # Invalid date format
            self.days_label.config(text="⏱️ Invalid date format")
            self.price_label.config(text="RM N/A")
        except Exception as e:
            print(f"Error updating price: {e}")
    
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
    
    def open_booking_detail(self):
        """Open booking detail page with booking information"""
        try:
            # Validate dates
            pickup_date = datetime.strptime(self.pickup_date_var.get(), "%Y-%m-%d")
            return_date = datetime.strptime(self.return_date_var.get(), "%Y-%m-%d")
            
            if pickup_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                messagebox.showerror("Invalid Date", "Pickup date must be in the future.")
                return
            
            if return_date <= pickup_date:
                messagebox.showerror("Invalid Date", "Return date must be after pickup date.")
                return
            
            # Get selected location
            selected_location = self.selected_location_var.get()
            if not selected_location or selected_location.strip() == "":
                messagebox.showerror("Invalid Location", "Please select a pickup point.")
                return
            
            # Get selected time
            selected_time = self.time_var.get()
            
            # Calculate rental days and total price
            days = self.days_var.get()
            daily_price = self.vehicle["price"]
            
            # Calculate extras
            extras_price = 0
            extras_list = []
            for option, var in self.extras_vars.items():
                if var.get():
                    price_str = option.split("RM ")[1].split("/")[0]
                    price = int(price_str)
                    extras_price += price * days
                    extras_list.append(option.split(" (+")[0])
            
            total_price = (daily_price * days) + extras_price
            
            # Confirm booking
            confirmation = messagebox.askyesno(
                "Confirm Rental", 
                f"Rent {self.vehicle['name']} for {days} day(s)?\n\n"
                f"Pickup: {self.pickup_date_var.get()} at {selected_time}\n"
                f"Location: {selected_location}\n"
                f"Return: {self.return_date_var.get()}\n"
                f"Daily Rate: RM {daily_price}\n"
                f"Extras: {'None' if not extras_list else ', '.join(extras_list)}\n"
                f"Total: RM {total_price}"
            )
            
            if not confirmation:
                return
            
            # Generate unique booking ID
            booking_id = f"CR{random.randint(100000, 999999)}"
            
            # Prepare booking data
            booking_details = {
                "booking_id": booking_id,
                "booking_type": "car_rental",
                "status": "pending",
                "vehicle_name": self.vehicle["name"],
                "vehicle_type": self.vehicle.get("category", "Vehicle"),
                "vehicle_id": self.vehicle["id"],
                "pickup_date": self.pickup_date_var.get(),
                "pickup_time": selected_time,
                "return_date": self.return_date_var.get(),
                "pickup_location": selected_location,
                "rental_days": days,
                "daily_price": str(daily_price),
                "extras": extras_list,
                "extras_price": str(extras_price),
                "total_price": str(total_price),
                "image_file": self.vehicle.get("image_file", ""),
                "transmission": self.vehicle.get("transmission", ""),
                "fuel_type": self.vehicle.get("fuel_type", ""),
                "seats": self.vehicle.get("seats", ""),
                "features": ", ".join(self.vehicle.get("features", [])),
                "user_email": self.email,
                "customer_name": "Guest",  # Default value
                "phone": "",  # Will be filled in booking form
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Close current window and open booking detail
            self.root.destroy()
            
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
            except ImportError:
                messagebox.showerror("Error", "Booking module not found!")
                self.go_back()
            
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use valid dates in YYYY-MM-DD format.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def go_back(self):
        """Go back to car_rental.py page"""
        self.root.destroy()
        try:
            # Import car_rental module
            import car_rental
            
            # Create new root window for car rental
            root = tk.Tk()
            root.title("Traney - Car Rentals")
            root.attributes('-fullscreen', True)
            
            # Initialize CarRentalApp
            app = car_rental.CarRentalApp(root, self.email)
            
            # Start the mainloop
            root.mainloop()
            
        except ImportError as e:
            # Handle import error
            print(f"Error importing car_rental: {e}")
            messagebox.showerror("Error", "Cannot load car rental module. Please check if car_rental.py exists.")
        except AttributeError as e:
            # Handle wrong class name
            print(f"Error initializing CarRentalApp: {e}")
            try:
                # Try alternative class names
                import car_rental
                root = tk.Tk()
                root.attributes('-fullscreen', True)
                
                # Try different class names
                if hasattr(car_rental, 'CarApp'):
                    app = car_rental.CarApp(root, self.email)
                elif hasattr(car_rental, 'CarRental'):
                    app = car_rental.CarRental(root, self.email)
                else:
                    # List available classes
                    classes = [attr for attr in dir(car_rental) if not attr.startswith('_')]
                    print(f"Available classes in car_rental: {classes}")
                    raise Exception(f"No suitable class found in car_rental.py")
                    
                root.mainloop()
            except Exception as e2:
                messagebox.showerror("Error", f"Cannot load car rental application: {str(e2)}")
        except Exception as e:
            # Generic error handling
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
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

# Run the application
if __name__ == "__main__":
    # This file is meant to be imported, not run directly
    print("This module is designed to be imported, not run directly.")
    print("Please run car_rental.py instead.")