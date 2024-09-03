import requests
from bs4 import BeautifulSoup
import time
import os
import tkinter as tk
from tkinter import messagebox
import argparse
from playsound import playsound


def read_search_queries(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('')
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def scrape_and_save_links(search_queries, output_file, play_sound, max_price):
    base_url = "https://www.jofogas.hu/magyarorszag?q={}"
    new_links = []

    for query in search_queries:
        url = base_url.format(query)
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.select('.list-items .list-item')
        for item in items:
            link = item.select_one('.item-title a')['href']
            price_span = item.select_one('.price-value')
            price = None
            if price_span and 'content' in price_span.attrs:
                try:
                    price = int(price_span['content'])
                except ValueError:
                    pass

            if price is not None and (max_price is None or price <= max_price):
                if not link_exists(link, output_file):
                    save_link(link, output_file, price)
                    new_links.append((link, price))

    if new_links:
        notify_new_links(new_links, play_sound)
    else:
        print("No new links found.")


def link_exists(link, output_file):
    if not os.path.exists(output_file):
        return False
    with open(output_file, 'r') as file:
        return link in file.read()


def save_link(link, output_file, price):
    with open(output_file, 'a') as file:
        file.write(f"{link} ({price})\n")


def notify_new_links(links, play_sound):
    root = tk.Tk()
    root.title("New links found!")

    if play_sound:
        playsound('notification.wav')

    text_area = tk.Text(root, wrap='word', height=20, width=100)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(root, command=text_area.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area.config(yscrollcommand=scrollbar.set)

    for link, price in links:
        text_area.insert(tk.END, f"{link} ({price})\n")

    text_area.config(state=tk.DISABLED)

    root.mainloop()


def countdown_timer(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        timer = f'{mins:02d}:{secs:02d}'
        print(f'\rTime until next scrape: {timer}', end='', flush=True)
        time.sleep(1)
        seconds -= 1
    print()


def start_scraping(timer_duration, play_sound, max_price):
    search_queries = read_search_queries('search_queries.txt')
    print("Scraping started...")
    while True:
        scrape_and_save_links(search_queries, 'output_links.txt', play_sound, max_price)
        countdown_timer(timer_duration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape jofogas.hu for new links.')
    parser.add_argument('--timer', type=int, default=180, help='Set the timer duration in seconds')
    parser.add_argument('--sound', type=str, choices=['yes', 'no'], default='no',
                        help='Enable or disable sound notification')
    parser.add_argument('--max_price', type=int, help='Set the maximum price for the items')
    args = parser.parse_args()

    play_sound = args.sound == 'yes'
    start_scraping(args.timer, play_sound, args.max_price)
