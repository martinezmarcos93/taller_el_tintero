from PIL import Image
from pathlib import Path

logo_path = Path('assets/Logo_El_Tintero.png')
if not logo_path.exists():
    logo_path = Path('assets/Logo_El_Tintero.png')

if logo_path.exists():
    img = Image.open(logo_path).convert('RGBA')
    sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    imgs = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
    Path('assets').mkdir(exist_ok=True)
    imgs[0].save('assets/icono.ico', format='ICO', sizes=sizes, append_images=imgs[1:])
    print('[OK] assets/icono.ico generado.')
else:
    print('[WARN] Logo no encontrado. El exe no tendra icono personalizado.')
    img = Image.new('RGBA', (256,256), (28,34,58,255))
    img.save('assets/icono.ico', format='ICO')