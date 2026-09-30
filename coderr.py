import tkinter as tk


class BarbieDreamhouseGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎀 Barbie Dreamhouse & Fashion Studio 🎀")
        self.root.geometry("950x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#FFF0F5")  # Lavender Blush background

        # Barbie Theme Color Palette
        self.barbie_pink = "#FF69B4"
        self.hot_pink = "#FF1493"
        self.pastel_pink = "#FFB6C1"
        self.glam_purple = "#DDA0DD"

        # Game State
        self.wall_color = self.pastel_pink
        self.floor_color = "#FFF5EE"  # White Sea Shell Floor
        self.window_view = "🌴 Malibu Beach"
        self.window_bg = "#87CEEB"
        self.drag_data = {"x": 0, "y": 0, "frame": None, "text": None}

        self.setup_ui()

    def setup_ui(self):
        # Left Panel: Design Controls
        control_panel = tk.Frame(self.root, bg=self.barbie_pink, width=260, height=700, bd=4, relief=tk.RIDGE)
        control_panel.pack(side=tk.LEFT, fill=tk.Y)
        control_panel.pack_propagate(False)

        # Title Logo
        tk.Label(control_panel, text="✨ BARBIE Studio ✨", font=("Courier", 16, "bold"), fg="white", bg=self.hot_pink,
                 bd=3, relief=tk.RAISED).pack(fill=tk.X, padx=10, pady=15)

        # Section: Room Theme
        tk.Label(control_panel, text="🛋️ Select Room Style:", font=("Arial", 11, "bold"), fg="white",
                 bg=self.barbie_pink).pack(anchor="w", padx=15, pady=5)
        themes = [
            ("Classic Pink Bedroom", "#FFC0CB", "#FFF0F5"),
            ("Glam Dance Salon", "#DA70D6", "#E6E6FA"),
            ("Modern Malibu Kitchen", "#E0FFFF", "#F5F5DC"),
            ("Glitter Royal Suite", "#FFD700", "#FFF8DC")
        ]
        for name, wall, floor in themes:
            tk.Button(control_panel, text=name, bg=wall, fg="black", font=("Arial", 9),
                      command=lambda w=wall, f=floor: self.change_theme(w, f), width=22, height=1,
                      activebackground=self.hot_pink).pack(pady=3)

        # Section: Balcony Views
        tk.Label(control_panel, text="🌅 Malibu Views:", font=("Arial", 11, "bold"), fg="white",
                 bg=self.barbie_pink).pack(anchor="w", padx=15, pady=10)
        views = [
            ("Malibu Sunny Beach", "#87CEEB", "🌴 Malibu Beach"),
            ("Pink Sunset Party", "#FF6B6B", "🌆 Pink Sunset"),
            ("Starry Runway Night", "#1A1A40", "✨ Runway Night")
        ]
        for name, bg_col, text in views:
            tk.Button(control_panel, text=name, bg="#F0F0F0", fg="black", font=("Arial", 9),
                      command=lambda b=bg_col, t=text: self.change_view(b, t), width=22, height=1).pack(pady=3)

        # Bottom Instructions
        tk.Label(control_panel,
                 text="💖 YOU CAN DO ANYTHING! 💖\nClick items below to add them.\nDrag and arrange your room!",
                 font=("Courier", 9, "bold"), fg="white", bg=self.hot_pink, justify=tk.CENTER, bd=2,
                 relief=tk.GROOVE).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

        # Right Panel: Dynamic Canvas Window
        self.canvas = tk.Canvas(self.root, width=690, height=550, bg="#FFF0F5", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.draw_dreamhouse()
        self.spawn_item_dock()

    def draw_dreamhouse(self):
        self.canvas.delete("structure")

        # Main Room Walls
        self.canvas.create_rectangle(30, 30, 660, 400, fill=self.wall_color, outline=self.hot_pink, width=5,
                                     tags="structure")

        # Floor (Perspective slant)
        self.canvas.create_polygon(30, 400, 660, 400, 690, 520, 0, 520, fill=self.floor_color, outline=self.hot_pink,
                                   width=3, tags="structure")

        # Luxury French Balcony Window
        self.canvas.create_rectangle(230, 60, 460, 240, fill=self.window_bg, outline="#FFFFFF", width=8,
                                     tags="structure")
        self.canvas.create_line(345, 60, 345, 240, fill="#FFFFFF", width=4, tags="structure")
        self.canvas.create_line(230, 150, 460, 150, fill="#FFFFFF", width=2, tags="structure")

        # Window Scene Text
        self.canvas.create_text(345, 110, text=self.window_view, font=("Courier", 13, "bold"), fill="white",
                                tags="structure")

    def change_theme(self, wall, floor):
        self.wall_color = wall
        self.floor_color = floor
        self.draw_dreamhouse()

    def change_view(self, bg_col, text):
        self.window_bg = bg_col
        self.window_view = text
        self.draw_dreamhouse()

    def spawn_item_dock(self):
        # Bottom Dock Container for Dolls, Clothes, and furniture items
        dock_frame = tk.Frame(self.root, bg="#FFE4E1", height=150, bd=2, relief=tk.SUNKEN)
        dock_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(dock_frame, text="👗 BARBIE DOCK (Click items to add into Dreamhouse):", font=("Arial", 10, "bold"),
                 fg=self.hot_pink, bg="#FFE4E1").pack(anchor="w", padx=15, pady=2)

        items_container = tk.Frame(dock_frame, bg="#FFE4E1")
        items_container.pack(pady=5)

        # Custom Barbie assets
        barbie_items = [
            ("👸 Barbie Doll", "#FF1493"),
            ("🤵 Ken Doll", "#00BFFF"),
            ("🚗 Pink Convertible", "#FF69B4"),
            ("👗 Sparkle Dress", "#DA70D6"),
            ("🛏️ Princess Bed", "#FFB6C1"),
            ("💄 Makeup Vanity", "#FFC0CB"),
            ("🐕 Pink Puppy", "#FFA07A")
        ]

        for emoji_text, color in barbie_items:
            btn = tk.Button(items_container, text=emoji_text, bg=color,
                            fg="white" if color not in ["#FFB6C1", "#FFC0CB", "#FFA07A"] else "black",
                            font=("Arial", 9, "bold"), relief=tk.RAISED, bd=2)
            btn.bind("<Button-1>", lambda event, t=emoji_text, c=color: self.add_item_to_room(t, c))
            btn.pack(side=tk.LEFT, padx=8, pady=5)

    def add_item_to_room(self, text, color):
        # Spawns structural item tokens in the center play space
        x, y = 345, 330

        # Build token container box and overlay label
        frame_id = self.canvas.create_rectangle(x - 55, y - 22, x + 55, y + 22, fill=color, outline="white", width=3,
                                                tags="props")
        text_id = self.canvas.create_text(x, y, text=text,
                                          fill="white" if color not in ["#FFB6C1", "#FFC0CB", "#FFA07A"] else "black",
                                          font=("Arial", 10, "bold"), tags="props")

        # Tie mouse button tracking events to make tokens smoothly draggable
        for element_part in (frame_id, text_id):
            self.canvas.tag_bind(element_part, "<Button-1>",
                                 lambda event, f=frame_id, t=text_id: self.start_drag(event, f, t))
            self.canvas.tag_bind(element_part, "<B1-Motion>", self.drag)

    def start_drag(self, event, frame_id, text_id):
        self.drag_data = {"x": event.x, "y": event.y, "frame": frame_id, "text": text_id}

    def drag(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Move structural frame and text layer elements simultaneously
        self.canvas.move(self.drag_data["frame"], delta_x, delta_y)
        self.canvas.move(self.drag_data["text"], delta_x, delta_y)

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y


if __name__ == "__main__":
    root = tk.Tk()
    game = BarbieDreamhouseGame(root)
    root.mainloop()
