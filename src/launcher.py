#!/usr/bin/env python3
"""
FEH Data Fetcher - Test Launcher
This script starts the bootstrap process and then displays hero data CSV from a random hero.
"""

import os
from tqdm import tqdm
from bootstrap import bootstrap_database
from fetcher import fetch_hero_data, get_heroes_to_update
from save_hero import save_hero_to_files , save_manuals


FOLDER_NAME = "database"


def main():
    """Main function that starts the bootstrap process and shows random hero data"""
    print("Starting FEH Data Fetcher Test Launcher...")
    print("=" * 50)
    
    try:
        # Start the bootstrap process
        data = bootstrap_database()
        
        print("\n" + "=" * 50)
        print("Bootstrap completed successfully!")

        heroes_to_update = get_heroes_to_update(data['heroes'], FOLDER_NAME, "heroes.txt")
        refines_to_update = get_heroes_to_update(data['refines'], FOLDER_NAME, "refines.txt")
        resplendents_to_update = get_heroes_to_update(data['resplendents'], FOLDER_NAME, "resplendents.txt")


        for category, update in zip(list(data.keys())[:-1], [heroes_to_update, refines_to_update, resplendents_to_update]):
            if update:
                print(f"\nSaving {category} heroes...")
                # Create progress bar for this category
                with tqdm(total=len(update), desc=f"Downloading {category}", unit="hero") as pbar:
                    for hero_id in update:
                        try:
                            pbar.set_postfix_str(f"{hero_id}")
                            hero_data = data[category][hero_id]
                            hero_page_data = fetch_hero_data(data[category][hero_id])
                            save_hero_to_files(hero_data, hero_page_data, FOLDER_NAME)
                            pbar.update(1)
                        except Exception as e:
                            pbar.set_postfix_str(f"Error: {hero_id} - {str(e)[:30]}")
                            pbar.update(1)
                            print(f"\nError processing {hero_id}: {e}")
        
        print("\nSaving manuals...")
        if os.path.exists(os.path.join(FOLDER_NAME, "manuals.csv")):
            os.remove(os.path.join(FOLDER_NAME, "manuals.csv"))
        save_manuals(data['manuals'], FOLDER_NAME)
        print("All downloads completed successfully! ✨")

    except Exception as e:
        print(f"\nError during bootstrap: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
