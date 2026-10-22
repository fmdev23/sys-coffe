"""Bảng màu, biểu tượng và kiểu chữ dùng chung cho toàn bộ giao diện."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk

COLORS = {
    "background": "#F5F3EE", "surface": "#FFFFFF", "ink": "#203D34",
    "muted": "#6A7771", "primary": "#235C47", "primary_hover": "#184332",
    "sidebar": "#193C32", "sidebar_active": "#30594A", "line": "#DFE5DE",
    "gold": "#A97739", "gold_light": "#F4EBDD", "green_light": "#EAF3EC",
    "danger": "#AD4138", "danger_light": "#FBEFEB", "disabled": "#AFBAB2",
}

def rounded_controls(root, style):
    """Thay lớp vẽ của ttk; giữ nguyên sự kiện, focus và trạng thái control."""
    assets = Path(__file__).resolve().parents[1] / "assets"
    images = {path.stem: tk.PhotoImage(master=root, file=path)
              for path in (assets / "controls").glob("*.png")}
    # Phần giữa ảnh đủ rộng để Tk không phải lặp hàng nghìn ô khi vẽ.
    images["clear"] = tk.PhotoImage(master=root, width=128, height=128)
    images["logo"] = tk.PhotoImage(master=root, file=assets / "coffee_logo.png")
    root.ui_images = images  # Tkinter cần giữ tham chiếu ảnh trong suốt vòng đời cửa sổ.
    root.logo_small = images["logo"].subsample(6)
    root.logo_large = images["logo"].subsample(2)
    root.iconphoto(True, images["logo"].subsample(8), images["logo"])
    style.element_create("Coffee.Button.focus", "image", images["clear"],
        ("disabled", images["clear"]), ("focus", images["focus"]), border=11, padding=0, width=32, height=32, sticky="nsew")
    for name, asset in [("TButton", "secondary"), ("Accent.TButton", "primary"),
                        ("Soft.TButton", "soft"), ("Danger.TButton", "danger"),
                        ("Nav.TButton", "nav"), ("NavActive.TButton", "nav_selected")]:
        element = "Coffee." + name + ".border"
        hover = images.get(asset + "_hover", images[asset])
        style.element_create(element, "image", images[asset], ("disabled", images["disabled"]),
            ("pressed", hover), ("active", hover), border=11, padding=0, width=32, height=32, sticky="nsew")
        style.layout(name, [(element, {"sticky": "nsew", "children": [
            ("Coffee.Button.focus", {"sticky": "nsew", "children": [
                ("Button.padding", {"sticky": "nsew", "children": [("Button.label", {"sticky": "nsew"})]})]})]})])
    for name in ("Nav.TButton", "NavActive.TButton"):
        style.configure(name, background=COLORS["sidebar"], foreground="#F2F5EF", anchor="w", padding=(15, 10))
        style.map(name, background=[("active", COLORS["sidebar"])], foreground=[("!disabled", "#F2F5EF")])
    style.element_create("Coffee.field", "image", images["field"], ("disabled", images["field_disabled"]),
        ("focus", images["field_focus"]), border=9, padding=1, width=32, height=32, sticky="nsew")
    style.layout("TEntry", [("Coffee.field", {"sticky": "nsew", "children": [
        ("Entry.padding", {"sticky": "nsew", "children": [("Entry.textarea", {"sticky": "nsew"})]})]})])
    style.element_create("Coffee.Combobox.downarrow", "image", images["arrow_down"], sticky="")
    style.layout("TCombobox", [("Coffee.field", {"sticky": "nsew", "children": [
        ("Coffee.Combobox.downarrow", {"side": "right", "sticky": "ns"}),
        ("Combobox.padding", {"sticky": "nsew", "children": [("Combobox.textarea", {"sticky": "nsew"})]})]})])
    for direction in ("up", "down"):
        style.element_create(f"Coffee.Spinbox.{direction}arrow", "image", images["arrow_" + direction], sticky="")
    style.layout("TSpinbox", [("Coffee.field", {"sticky": "nsew", "children": [
        ("null", {"side": "right", "children": [
            ("Coffee.Spinbox.uparrow", {"side": "top"}), ("Coffee.Spinbox.downarrow", {"side": "bottom"})]}),
        ("Spinbox.padding", {"sticky": "nsew", "children": [("Spinbox.textarea", {"sticky": "nsew"})]})]})])
    style.configure("TSpinbox", padding=(8, 4))
    style.element_create("Coffee.Checkbutton.indicator", "image", images["check_0_0"],
        ("disabled", "selected", images["check_1_1"]), ("disabled", images["check_0_1"]),
        ("selected", images["check_1_0"]), sticky="w")
    style.layout("TCheckbutton", [("Checkbutton.padding", {"sticky": "nsew", "children": [
        ("Coffee.Checkbutton.indicator", {"side": "left"}),
        ("Checkbutton.focus", {"side": "left", "children": [("Checkbutton.label", {"sticky": "nsew"})]})]})])
    for name, asset in [("Panel.TFrame", "panel"), ("SelectedPanel.TFrame", "field_focus")]:
        element = "Coffee." + name + ".border"
        style.element_create(element, "image", images[asset], border=13, padding=0, width=32, height=32, sticky="nsew")
        style.layout(name, [(element, {"sticky": "nsew"})])
        style.configure(name, background=COLORS["background"])


def configure_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(background=COLORS["background"])
    style.configure(".", font=("Segoe UI", 10), foreground=COLORS["ink"])
    style.configure("TFrame", background=COLORS["background"])
    style.configure("TLabel", background=COLORS["background"])
    style.configure("Card.TFrame", background=COLORS["surface"])
    style.configure("Card.TLabel", background=COLORS["surface"])
    style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"))
    style.configure("Heading.TLabel", font=("Segoe UI", 13, "bold"), background=COLORS["surface"])
    style.configure("Subtitle.TLabel", foreground=COLORS["muted"])
    style.configure("Muted.Card.TLabel", foreground=COLORS["muted"], background=COLORS["surface"])
    style.configure("Metric.TLabel", font=("Segoe UI", 23, "bold"), background=COLORS["surface"])
    style.configure("TButton", padding=(15, 10), background=COLORS["background"], bordercolor=COLORS["line"],
                    lightcolor=COLORS["surface"], darkcolor=COLORS["surface"], relief="flat")
    style.map("TButton", background=[("active", COLORS["background"])],
              foreground=[("disabled", "#86918B")])
    for name, normal, hover, foreground in [
        ("Accent", COLORS["primary"], COLORS["primary_hover"], "white"),
        ("Danger", COLORS["danger_light"], "#F3DCD6", COLORS["danger"]),
        ("Soft", COLORS["green_light"], "#D6E8DB", COLORS["primary"]),
    ]:
        style.configure(name + ".TButton", background=COLORS["background"], foreground=foreground,
                        bordercolor=normal, lightcolor=normal, darkcolor=normal)
        style.map(name + ".TButton", background=[("!disabled", COLORS["background"])],
                  foreground=[("disabled", "#89958D"), ("!disabled", foreground)])
    style.configure("Treeview", rowheight=42, background=COLORS["surface"],
                    fieldbackground=COLORS["surface"], borderwidth=0, foreground=COLORS["ink"])
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=(10, 12),
                    background="#EDF0E9", foreground=COLORS["muted"], relief="flat")
    style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "white")])
    style.configure("TEntry", padding=9, background=COLORS["background"], fieldbackground="white")
    style.configure("TCombobox", padding=8, background=COLORS["background"], fieldbackground="white")
    style.map("TCombobox", fieldbackground=[("readonly", "white"), ("disabled", "#EBEDE7")],
              foreground=[("disabled", COLORS["muted"])])
    style.configure("TCheckbutton", background=COLORS["surface"], padding=2)
    for orient in ("Vertical", "Horizontal"):
        style.configure(orient + ".TScrollbar", arrowsize=13, background="#D6DED5",
                        bordercolor=COLORS["background"], lightcolor="#D6DED5", darkcolor="#D6DED5",
                        troughcolor=COLORS["background"])
    rounded_controls(root, style)
    # Cùng control, đổi màu nền ở góc bo cho các vùng thẻ trắng.
    for name in ("TButton", "Accent.TButton", "Soft.TButton", "Danger.TButton", "TEntry", "TCombobox", "TSpinbox"):
        style.configure("Card." + name, background=COLORS["surface"])
        style.map("Card." + name, background=[("!disabled", COLORS["surface"]), ("disabled", COLORS["surface"])])
