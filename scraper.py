import multiprocessing
from helpers import scrape_product, scrape_search
import threading
import sys
import csv

###########################################################################################
# CONSTANTS
THREAD_COUNT = multiprocessing.cpu_count() * 2
PAGE_URL = "https://www.amazon.in/gp/bestsellers/hpc/1374621031/ref=zg_bs_nav_hp_3_1374620031"
LOCK = threading.Lock()
WRITE_CSV_HEADER = True
MAX_PRODUCTS = 100
###########################################################################################

def append_to_csv(data):
    with open('output.csv', 'a', encoding="utf-8") as f:
        global WRITE_CSV_HEADER
        w = csv.DictWriter(f, data.keys())
        if WRITE_CSV_HEADER:
            w.writeheader()
            WRITE_CSV_HEADER = False
        w.writerow(data)

def product_list_fetcher(product_list):
    for product_link in product_list:
        data = scrape_product("https://www.amazon.in" + product_link)
        if data and data['name']:
            LOCK.acquire()
            append_to_csv(data)
            print("Fetch Success for - " + product_link)
            LOCK.release()
        else:
            print(":( could not ftech product, try again")

# product_list_fetcher(["/Dabur-Hajmola-120-Tablet-Anardana/dp/B01CJUZPSU/ref=zg_bs_1374621031_1?_encoding=UTF8&psc=1&refRID=M90AT64K59JM96SYSPPD"])

# fetch page results
page_links = []
i = 1
while True:
    next_url = PAGE_URL + "&pg=" + str(i)
    page_data_links = scrape_search(next_url)
    if page_data_links:
        page_links += page_data_links
    else:
        break
    if len(page_links) >= MAX_PRODUCTS:
        page_links = page_links[:MAX_PRODUCTS]
        break
    i += 1

if not page_links:
    print("no links to crawl -- :( ")
    sys.exit()

###########################################################################################
# FETCH PRODUCT LINKS USING MULTIPLE THREADS
links_per_thread = len(page_links) // THREAD_COUNT
threads = []
curr_offset = 0
while curr_offset < len(page_links):
    links = page_links[curr_offset : curr_offset+links_per_thread]
    curr_offset += links_per_thread
    threads.append(threading.Thread(target=product_list_fetcher, args=(links,))) 

# start threads
for t in threads:
    t.start()

# join all
for t in threads:
    t.join()