import logging
import pathlib
from robocorp.tasks import task
from mainLt import Scrapper
from utils import Helpers


@task
def minimal_task():
    logging.info("Start of execution")
    header = [
        "date",
        "title",
        "description",
        "image_filename",
        "phrase_occurrence",
        "money_value_occurrence",
    ]
    url = "https://www.latimes.com/"
    input_vars = Helpers.get_input_vars()
    # in our robocloud we supply matching keys and the values
    search_phrase = input_vars.get("search_phrase", "")
    category_section = input_vars.get("category", "")
    number_of_news = input_vars.get("number_of_news", "")
    errors = []
    if not search_phrase:
        errors.append("Search phrase is empty")
    elif not category_section:
        errors.append("Search category is empty")

    if errors:
        raise AssertionError(",".join(errors))

    output_folder = Helpers.create_folder(
        pathlib.Path(__file__).parent.resolve(), "raidinglat"
    )

    browser = Scrapper()
    browser.open_browser(url)
    try:
        browser.search_lattimes(search_phrase)
        browser.set_news_category(category_section)
        browser.sort_news()
        results = browser.get_news_data(search_phrase, output_folder, number_of_news)
        Helpers.save_to_file(
            pathlib.Path(output_folder).joinpath("result.csv"), results, header
        )
        print("End of execution")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.close_browser()
