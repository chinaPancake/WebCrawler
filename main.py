import json

import grequests
import requests
from lxml.html import fromstring
import httplib2
from httplib2 import RedirectLimit
import typer
import csv
from bs4 import BeautifulSoup, SoupStrainer
import urllib.parse


# we have to crawl: link, title, number of internal links, number of times url was referenced by other pages
# crawl --page <URL> --format <csv/json> --output <path_to_file>

# done link
# done title
# counting internal and external links is done

class ToCrawl:
    def __init__(self, url: str):
        # input url
        self.url = url

        # get request form URL
        self.response = grequests.get(self.url)

        # all arrays and sets
        self.all_titles = []
        visited_sites = set()
        links_to_visit = []
        # links dict to save json/csv file
        links = {

        }


        # append and add to array and set
        links_to_visit.append(self.url)
        visited_sites.add(self.url)

        # asynchronous request
        rs = (grequests.get(link) for link in links_to_visit)
        # get array with all requests
        rs_to_process = grequests.map(rs)

        # while loop, work as long as request to process are bigger > 0
        while len(rs_to_process) > 0:
            content = rs_to_process[0]
            # pop (delete) (0) from rs_to_process array
            rs_to_process.pop(0)
            # change url value to links_to_visit and pop it
            url = links_to_visit.pop(0)

            # if url not in links then we want to add blank tuple
            if url not in links:
                links[url] = ("",0,0,0)

            # if content is None we want to skip it and go to next content value
            if content is None:
                continue

            # try loop
            try:
                # set link_data as list
                link_data = list(links[url])
                # get title from content page
                for title in BeautifulSoup(content.text, 'html.parser', parseOnlyThese=SoupStrainer('title')):
                    # append title into all_tittles
                    self.all_titles.append(title.text)
                    # add page title into link_data list
                    link_data[0] = title.text
                # start extract_links function
                internals, externals = self.extract_links(response=content.text)
                # get through every internal link
                for inter in internals:
                    # if internal link is not in links then add blank tuple
                    if inter not in links:
                        links[url] = ("", 0, 0, 1)
                        # set inter_link_data into list, increment reference and set links as a tuple of inter_link_data
                    else:
                        inter_link_data = list(links[inter])
                        inter_link_data[-1] += 1
                        links[inter] = tuple(inter_link_data)

                # not visited internal pages (content)
                internals_not_visited = []

                # another loop where we go through every internal link
                for inter in internals:
                    if inter not in visited_sites:
                        internals_not_visited.append(inter)
                        visited_sites.add(inter)

                # asynchronous request
                rs = (grequests.get(link) for link in internals_not_visited)
                rs_to_process = rs_to_process + (grequests.map(rs))
                links_to_visit = links_to_visit+internals_not_visited

                link_data[1] = len(internals)
                link_data[2] = len(externals)
                print(link_data)

            except (RedirectLimit, httplib2.ServerNotFoundError, UnicodeError, httplib2.RelativeURIError, TypeError):
                print('redirection limit on', content)

        print(links)

    def is_external_link(self, link: str) -> bool:
        return link.startswith('https') or link.startswith('http')

    def save_to_file(self):
        pass


    def extract_links(self, response: str):
        # get all links at once
        all_links = []
        for link in BeautifulSoup(response, 'html.parser', parseOnlyThese=SoupStrainer('a')):
            if link.has_attr('href'):
                all_links.append(link['href'])

        external_links = []
        internal_links = []
        for link in all_links:
            if self.is_external_link(link=link):
                external_links.append(link)
            else:
                internal_links.append(urllib.parse.urljoin(self.url, link))

        return internal_links, external_links

if __name__ == "__main__":
    typer.run(ToCrawl)