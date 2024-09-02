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


def scrape_and_save_links(search_queries, output_file, play_sound):
    base_url = "https://www.jofogas.hu/magyarorszag?q={}"
    new_links = []

    for query in search_queries:
        url = base_url.format(query)
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.select('.list-items .list-item')
        for item in items:
            link = item.select_one('.item-title a')['href']
            if not link_exists(link, output_file):
                save_link(link, output_file)
                new_links.append(link)

    if new_links:
        notify_new_links(new_links, play_sound)
    else:
        print("No new links found.")


def link_exists(link, output_file):
    if not os.path.exists(output_file):
        return False
    with open(output_file, 'r') as file:
        return link in file.read()


def save_link(link, output_file):
    with open(output_file, 'a') as file:
        file.write(link + '\n')


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

    for link in links:
        text_area.insert(tk.END, link + '\n')

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


def start_scraping(timer_duration, play_sound):
    search_queries = read_search_queries('search_queries.txt')
    print("Scraping started...")
    while True:
        scrape_and_save_links(search_queries, 'output_links.txt', play_sound)
        countdown_timer(timer_duration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape jofogas.hu for new links.')
    parser.add_argument('--timer', type=int, default=180, help='Set the timer duration in seconds')
    parser.add_argument('--sound', type=str, choices=['yes', 'no'], default='no',
                        help='Enable or disable sound notification')
    args = parser.parse_args()

    play_sound = args.sound == 'yes'
    start_scraping(args.timer, play_sound)
