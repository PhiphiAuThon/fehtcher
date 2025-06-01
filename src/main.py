import fetcher
import save_file
import img_downloader
from tqdm import tqdm

HEROES_PAGE = "https://feheroes.fandom.com/wiki/List_of_Heroes"
RESPLENDENT_PAGE = "https://feheroes.fandom.com/wiki/Resplendent_Heroes"
REFINES_PAGE = "https://feheroes.fandom.com/wiki/Weapon_Refinery"
FOLDER_PATH = "database"
HEROES_TXT = "heroes.txt"
REFINE_TXT = "refined_heroes.txt"
RESP_TXT = "resplendent_heroes.txt"

def process_heroes(ctx):
    with tqdm(total=len(ctx['filtered_heroes']), desc="Fetching heroes") as pbar:
        for hero in ctx['filtered_heroes']:
            pbar.set_description(f"{hero.replace('_',' ')}")
            data = fetcher.get_hero_data(hero)
            save_file.save_hero_to_files(hero, data, FOLDER_PATH)
            icon_index = ctx['heroes'].index(hero)
            if icon_index >= 0:
                icon_link = ctx['icon_links'][icon_index]
                filename = icon_link.split('/')[-1].replace("_FC", "")
                img_downloader.download_image(icon_link, FOLDER_PATH + "/icons/" + filename)
            save_file.save_hero_id_to_done(hero, FOLDER_PATH, HEROES_TXT)
            pbar.update(1)
    for hero in ctx['filtered_heroes']:
        print(f"\t{hero.replace('_',' ')}")

def process_refined_heroes(ctx):
    with tqdm(total=len(ctx['filtered_refined_heroes']), desc="Processing refined heroes") as pbar:
        for hero in ctx['filtered_refined_heroes']:
            pbar.set_description(f"{hero.replace('_',' ')}")
            data = fetcher.get_hero_data(hero)
            save_file.save_hero_to_files(hero, data, FOLDER_PATH)
            save_file.save_hero_id_to_done(hero, FOLDER_PATH, REFINE_TXT)
            pbar.update(1)
    for hero in ctx['filtered_refined_heroes']:
        print(f"\t{hero.replace('_',' ')}")

if __name__ == "__main__":
    ctx = {}
    steps = {
        "Fetching All Heroes list...": lambda ctx:
            ctx.update({
                'heroes': fetcher.get_heroes_ids(HEROES_PAGE)
            }),
        "Fetching Icons links...": lambda ctx:
            ctx.update({
                'icon_links': img_downloader.get_heroes_icons_links(HEROES_PAGE)
            }),
        "Selecting Heroes to update...": lambda ctx:
            ctx.update({
                'filtered_heroes': save_file.get_heroes_to_update(ctx['heroes'], FOLDER_PATH, HEROES_TXT)
            }),
        "Processing Heroes...": lambda ctx:
            process_heroes(ctx),
        "Fetching Refines...": lambda ctx:
            ctx.update({
                'refines': fetcher.get_refines(REFINES_PAGE),
                'refined_heroes': list(fetcher.get_refines(REFINES_PAGE).keys())
            }),
        "Selecting Refined Heroes to update...": lambda ctx:
            ctx.update({
                'filtered_refined_heroes': save_file.get_heroes_to_update(ctx['refined_heroes'], FOLDER_PATH, REFINE_TXT)
            }),
        "Processing Refined Heroes...": lambda ctx: 
            process_refined_heroes(ctx),
        "Fetching Resplendent Heroes...": lambda ctx:
            ctx.update({
                'resplendent_heroes': fetcher.get_heroes_ids(RESPLENDENT_PAGE)
            }),
        "Updating Resplendent Heroes list...": lambda ctx: 
            [
                save_file.save_hero_id_to_done(hero, FOLDER_PATH, RESP_TXT)
                for hero in save_file.get_heroes_to_update(ctx['resplendent_heroes'], FOLDER_PATH, RESP_TXT)
            ]
    }

    for label, func in steps.items():
        print(label)
        func(ctx)

