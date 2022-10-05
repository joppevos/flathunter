"""Expose crawler for Immobiliare"""
import re

from flathunter.logging import logger
from flathunter.abstract_crawler import Crawler


class CrawlImmobiliare(Crawler):
    """Implementation of Crawler interface for Immobiliare"""

    URL_PATTERN = re.compile(r'https://www\.immobiliare\.it')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    # pylint: disable=too-many-locals
    def extract_data(self, soup):
        """Extracts all exposes from a provided Soup object"""
        entries = []

        results = soup.find(
            'ul', {"class": "in-realEstateResults"})

        items = results.find_all(lambda l: l.has_attr(
            'class') and "in-realEstateResults__item" in l['class']
            and "in-realEstateResults__carouselAgency" not in l["class"])

        for row in items:
            flat_id = row['id'].replace("link_ad_", "")
            title_row = row.find('a', {"class": "in-card__title"})
            title = title_row.text.strip()
            url = title_row['href']

            image_item = row.find_all('img')
            image = image_item[0]['src'] if image_item else ""

            # the items arrange like so:
            # 0: price
            # 1: number of rooms
            # 2: size of the apartment
            details_list = row.find(
                "ul", {"class": "in-realEstateListCard__features"})

            price_li = details_list.find(
                "li", {"class": "in-realEstateListCard__features--main"})

            price = re.match(
                r".*\s([0-9]+.*)$",
                # if there is a discount on the price, then there will be a <div>,
                # otherwise the text we are looking for is directly inside the <li>
                (price_li.find("div") if price_li.find(
                    "div") else price_li).text.strip()
            )[1]

            other_details = details_list.find_all(
                lambda l: l.has_attr('aria-label'))

            rooms = other_details[0].text.strip()
            size = other_details[1].text.strip()

            address_match = re.match(r"\w+\s(.*)$", title)
            address = address_match[1] if address_match else ""

            details = {
                'id': int(flat_id),
                'image': image,
                'url': url,
                'title': title,
                'price': price,
                'size': size,
                'rooms': rooms,
                'address': address,
                'crawler': self.get_name()
            }

            entries.append(details)

        logger.debug('Number of entries found: %d', len(entries))

        return entries
