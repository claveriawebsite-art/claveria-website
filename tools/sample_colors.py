from PIL import Image
im = Image.open('/home/user/google_drive/website logo.png').convert('RGB')
print('logo size', im.size, 'corners:', im.getpixel((5, 5)), im.getpixel((1994, 5)), im.getpixel((5, 1994)), im.getpixel((1000, 10)))
h = Image.open('/home/user/google_drive/website homepage.jpg')
print('hero size', h.size)
