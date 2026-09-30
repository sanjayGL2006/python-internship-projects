import tkinter as tk
from tkinter import messagebox


class VisualCozyRoomGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Cozy Room & Ambiance Designer")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#2C2C2C")

        # Game State
        self.bg_color = "#D7CCC8"  # Initial Warm Beige Wall
        self.floor_color = "#5D4037"  # Initial Dark Wood Floor
        self.window_view_text = "☀️ Sunny Day"
        self.window_bg = "#81D4FA"
        self.selected_furniture = None

        self.setup_ui()

    def setup_ui(self):
        # Left Panel: Design Controls
        control_panel = tk.Frame(self.root, bg="#3E2723", width=250, height=650)
        control_panel.pack(side=tk.LEFT, fill=tk.Y)
        control_panel.pack_propagate(False)

        # Title
        tk.Label(control_panel, text="🛠️ DESIGN STUDIO", font=("Arial", 14, "bold"), fg="white", bg="#3E2723").pack(
            pady=15)

        # Section: Wall Paint
        tk.Label(control_panel, text="🧱 Wall Paint:", font=("Arial", 10, "bold"), fg="#D7CCC8", bg="#3E2723").pack(
            anchor="w", padx=15, pady=5)
        walls = [("Warm Beige", "#D7CCC8"), ("Sage Green", "#C8E6C9"), ("Charcoal Dark", "#37474F"),
                 ("Soft Pink", "#F8BBD0")]
        for name, color in walls:
            tk.Button(control_panel, text=name, bg=color, fg="black" if color != "#37474F" else "white",
                      command=lambda c=color: self.change_walls(c), width=20, height=1).pack(pady=2)

        # Section: Flooring
        tk.Label(control_panel, text="🪵 Flooring:", font=("Arial", 10, "bold"), fg="#D7CCC8", bg="#3E2723").pack(
            anchor="w", padx=15, pady=10)
        floors = [("Oak Hardwood", "#5D4037"), ("Light Pine", "#D7A15C"), ("Plush Carpet", "#ECEFF1"),
                  ("Marble Tile", "#B0BEC5")]
        for name, color in floors:
            tk.Button(control_panel, text=name, bg=color, fg="black" if color not in ["#5D4037"] else "white",
                      command=lambda c=color: self.change_flooring(c), width=20, height=1).pack(pady=2)

        # Section: Ambiance & Windows
        tk.Label(control_panel, text="💡 Ambiance / View:", font=("Arial", 10, "bold"), fg="#D7CCC8", bg="#3E2723").pack(
            anchor="w", padx=15, pady=10)
        views = [("Sunny Morning", "#81D4FA", "☀️ Sunny Day"), ("Rainy Evening", "#37474F", "🌧️ Heavy Rain"),
                 ("Cyberpunk Night", "#4A148C", "🌆 Neon Night")]
        for name, bg, text in views:
            tk.Button(control_panel, text=name, bg="#4E342E", fg="white",
                      command=lambda b=bg, t=text: self.change_ambiance(b, t), width=20, height=1).pack(pady=2)

        # Instructions Label at bottom of control panel
        tk.Label(control_panel, text="👉 Drag items in the room\n to place them!", font=("Arial", 9, "italic"),
                 fg="#FFCC80", bg="#3E2723", justify=tk.CENTER).pack(side=tk.BOTTOM, pady=20)

        # Right Panel: Dynamic Canvas (The actual room)
        self.canvas = tk.Canvas(self.root, width=650, height=650, bg="#2C2C2C", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.draw_room()
        self.spawn_furniture_dock()

    def draw_room(self):
        self.canvas.delete("room_structure")

        # Draw Walls
        self.canvas.create_rectangle(40, 40, 610, 430, fill=self.bg_color, outline="#795548", width=4,
                                     tags="room_structure")

        # Draw Floor (Perspective effect)
        self.canvas.create_polygon(40, 430, 610, 430, 650, 530, 0, 530, fill=self.floor_color, outline="#3E2723",
                                   width=2, tags="room_structure")

        # Draw Architectural Window
        self.canvas.create_rectangle(240, 80, 410, 220, fill=self.window_bg, outline="#FFFFFF", width=6,
                                     tags="room_structure")
        # Window Panes
        self.canvas.create_line(325, 80, 325, 220, fill="#FFFFFF", width=3, tags="room_structure")
        self.canvas.create_line(240, 150, 410, 150, fill="#FFFFFF", width=3, tags="room_structure")
        # Window Text Ambiance
        self.canvas.create_text(325, 130, text=self.window_view_text, font=("Arial", 12, "bold"), fill="white",
                                tags="room_structure")

    def change_walls(self, color):
        self.bg_color = color
        self.draw_room()

    def change_flooring(self, color):
        self.floor_color = color
        self.draw_room()

    def change_ambiance(self, bg_color, view_text):
        self.window_bg = bg_color
        self.window_view_text = view_text
        self.draw_room()

    def spawn_furniture_dock(self):
        # Decorative Furniture Catalog Dock at the absolute bottom floor area
        tk.Label(self.root, text="Furniture Catalog (Click to place inside room):", font=("Arial", 9, "bold"),
                 fg="white", bg="#2C2C2C").place(x=270, y=545)

        items = [
            ("🛋️ Cozy Sofa", "#D32F2F"),
            ("🪴 Monstera Plant", "#388E3C"),
            ("📻 Record Player", "#F57C00"),
            ("🪑 Cushion Chair", "#1976D2"),
            ("🐈 Sleeping Cat", "#FFA000"),
            ("🪵 Coffee Table", "#8D6E63")
        ]

        x_offset = 270
        for emoji_text, color in items:
            btn = tk.Button(self.root, text=emoji_text, bg=color, fg="white", font=("Arial", 9, "bold"))
            btn.bind("<Button-1>", lambda event, t=emoji_text, c=color: self.add_furniture_to_room(t, c))
            btn.place(x=x_offset, y=575)
            x_offset += 100

    def add_furniture_to_room(self, text, color):
        # Spawn item in the middle of the room canvas
        x, y = 325, 330

        # Visual representation of furniture item container box + text label
        frame_id = self.canvas.create_rectangle(x - 45, y - 20, x + 45, y + 20, fill=color, outline="white", width=2,
                                                tags="furniture")
        text_id = self.canvas.create_text(x, y, text=text, fill="white", font=("Arial", 10, "bold"), tags="furniture")

        # Bind drag and drop functionality directly onto the spawned tokens
        for visual_element in (frame_id, text_id):
            self.canvas.tag_bind(visual_element, "<Button-1>",
                                 lambda event, f=frame_id, t=text_id: self.start_drag(event, f, t))
            self.canvas.tag_bind(visual_element, "<B1-Motion>", self.drag)

    def start_drag(self, event, frame_id, text_id):
        self.drag_data = {"x": event.x, "y": event.y, "frame": frame_id, "text": text_id}

    def drag(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Move both the backing box and text at the same time
        self.canvas.move(self.drag_data["frame"], delta_x, delta_y)
        self.canvas.move(self.drag_data["text"], delta_x, delta_y)

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y


if __name__ == "__main__":
    root = tk.Tk()
    game = VisualCozyRoomGame(root)
    root.mainloop()
