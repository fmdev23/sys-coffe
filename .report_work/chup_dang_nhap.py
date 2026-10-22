import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from main import CoffeeApp
from PIL import ImageGrab

app = CoffeeApp()
app.attributes('-topmost', True)

def capture():
    app.update_idletasks()
    x, y = app.winfo_rootx(), app.winfo_rooty()
    ImageGrab.grab(bbox=(x, y, x + app.winfo_width(), y + app.winfo_height())).save(ROOT / 'sodo/dang_nhap.png')
    app.destroy()

app.after(2000, capture)
app.mainloop()
