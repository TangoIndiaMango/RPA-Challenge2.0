import shutil
import requests
import csv
from RPA.Robocorp.WorkItems import WorkItems
import pathlib
import os


class Helpers:

    @staticmethod
    def download_image(image_src, image_filename, folder_to_save):
        """sumary_line

        Keyword arguments:
        image_src -- src of an image
        image_filename -- name of an image
        folder_to_save -- folder to save image
        Return: path_to_saved_image
        """
        path_to_saved_image = os.path.join(folder_to_save, image_filename)
        try:
            # Ensure folder exists
            pathlib.Path(folder_to_save).mkdir(parents=True, exist_ok=True)

            with open(path_to_saved_image, "wb") as handle:
                response = requests.get(image_src, stream=True)

                # Check if response status is OK
                if not response.ok:
                    print(f"Failed to download image: {response.status_code}")
                    return

                # Write image content to file
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
            print(f"Image saved to: {path_to_saved_image}")
        except Exception as e:
            print("Error saving image:", e)

    @staticmethod
    def save_to_file(path_to_csv, data, headers):
        """sumary_line

        Keyword arguments:
        path_to_csv -- path to csv file
        data -- data to save to csv file
        headers -- headers of csv file
        Return: a writer to write data to csv file
        """
        with open(path_to_csv, "w", encoding="UTF8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for item in data:
                writer.writerow(item)

    @staticmethod
    def get_image_name(src):
        """sumary_line

        Keyword arguments:
        src -- src of an image
        Return: image name
        """

        split_item = None
        if ".jpg" in src:
            split_item = ".jpg"
        elif ".png" in src:
            split_item = ".png"
        else:
            return None
        if split_item is not None:
            return src.split(split_item)[0].split("/")[-1] + split_item

    @staticmethod
    def check_contains_money(title, description):
        """sumary_line

        Keyword arguments:
        title -- title of an item
        description -- description of an item
        Return: boolean value
        """

        money_keywords = ["dollar", "USD", "$"]
        title_lower = title.lower()
        description_lower = description.lower()
        for keyword in money_keywords:
            if keyword in title_lower or keyword in description_lower:
                return True
        return False

    @staticmethod
    def get_input_vars():
        """sumary_line

        Keyword arguments:
        Return: input variables for the robocorp cloud instance
        """
        items = WorkItems()
        items.get_input_work_item()
        variables = items.get_work_item_variables()
        return variables

    @staticmethod
    def create_folder(parent_folder, folder_name):
        """sumary_line

        Keyword arguments:
        parent_folder -- parent folder
        folder_name -- name of a folder
        Return: path to a folder
        """
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    @staticmethod
    def count_occurrence(title, description, search_phrase):
        """sumary_line

        Keyword arguments:
        title -- title of an item
        description -- description of an item
        search_phrase -- search phrase
        Return: number of occurrences
        """
        title_occurrences = title.lower().count(search_phrase.lower())
        description_occurrences = description.lower().count(search_phrase.lower())
        return title_occurrences + description_occurrences
