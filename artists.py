import pylast, json, requests, glob
from lastfmcache import LastfmCache
from PIL import Image
import os

path_to_git = "/home/kasket/git/KevinFroissart/"

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

with open(path_to_git + "config.json", "r+") as f:
    config = json.load(f)

network = pylast.LastFMNetwork(api_key=config['apikey'], api_secret=config['secret'], username=config['username'], password_hash=pylast.md5(config['password']))
cache = LastfmCache(config['apikey'], config['secret'])
cache.enable_file_cache()


try:
    artists = network.get_authenticated_user().get_top_artists(limit=6, period=pylast.PERIOD_7DAYS)
    top_artist = network.get_authenticated_user().get_top_artists(limit=6, period="12month")
except Exception as e:
    print(e)

artist_dict = {}
top_artist_dict = {}

for a in top_artist:
    artist = cache.get_artist(a.item.name)
    top_artist_dict.update({ a.item.name : artist.cover_image })

for a in artists:
    artist = cache.get_artist(a.item.name)
    artist_dict.update({ a.item.name : artist.cover_image })

for k, v in artist_dict.items():
    if not v:
        v = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
    res = requests.get(v).content
    with open(path_to_git + "artist_images/" + v.split('/')[-1], "wb") as f:
        f.write(res)
    artist_dict[k] = "artist_images/" + v.split('/')[-1]
    
for k, v in top_artist_dict.items():
    if not v:
        v = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
    res = requests.get(v).content
    with open(path_to_git + "artist_images/" + v.split('/')[-1], "wb") as f:
        f.write(res)
    top_artist_dict[k] = "artist_images/" + v.split('/')[-1]

new_height, new_width = (250, 250)
for a in glob.glob("artist_images\\*.jpg"):
    im = Image.open(a)
    im_thumb = crop_max_square(im).resize((500, 500), Image.LANCZOS)
    im_thumb.save(a)

url_temp = "https://raw.githubusercontent.com/KevinFroissart/KevinFroissart/master/"

template = """\
## Who I've been listening to this week
"""

for image in artist_dict.values():
    template = template + "| <img src=" + url_temp + image.replace('\\', '/') + "> "
template = template + " |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
for artist in artist_dict.keys():
    template = template + "| " + "<b>" + artist + "</b> "
template = template + " |\n"

template = template + "\n\n" + """\
## My top artists this year
"""

for image in top_artist_dict.values():
    template = template + "| <img src=" + url_temp + image.replace('\\', '/') + "> "
template = template + " |\n| :---: | :---: | :---: | :---: | :---: | :---: |\n"
for artist in top_artist_dict.keys():
    template = template + "| " + "<b>" + artist + "</b> "
template = template + " |\n"

readme = open(path_to_git + "READMECOPY.md", "r").read()
with open(path_to_git + "README.md", "w") as f:
    f.write(readme.format(template=template))

os.system("git -C " + path_to_git + " add . && git -C " + path_to_git + " commit -m \"Update Artists\" && git -C " + path_to_git + " push")
