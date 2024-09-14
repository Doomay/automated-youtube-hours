from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
import random
import threading

class YouTubeViewBot:
    def __init__(self, video_url, view_count, min_watch_time, max_watch_time, proxy_file='proxy.txt'):
        """
        Initialize the bot with video URL, number of views to generate, 
        a range for video watch time, and optional proxy file.
        
        :param video_url: URL of the YouTube video to be viewed
        :param view_count: Number of times the browser should be reopened
        :param min_watch_time: Minimum duration (in seconds) to watch the video
        :param max_watch_time: Maximum duration (in seconds) to watch the video
        :param proxy_file: Path to the file containing proxy IPs (default is 'proxy.txt')
        """
        self.video_url = video_url
        self.view_count = view_count
        self.min_watch_time = min_watch_time
        self.max_watch_time = max_watch_time
        self.proxy_list = self.load_proxies(proxy_file)

    def load_proxies(self, proxy_file):
        """
        Load proxy IPs from a file into a list.

        :param proxy_file: Path to the proxy file
        :return: List of proxies
        """
        try:
            with open(proxy_file, 'r') as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            print(f"Error: Proxy file {proxy_file} not found.")
            return []

    def get_random_proxy(self):
        """
        Select a random proxy from the proxy list.
        
        :return: A random proxy IP
        """
        return random.choice(self.proxy_list) if self.proxy_list else None
    
    def set_proxy(self, proxy_ip_port):
        """
        Configure a Selenium WebDriver to use a given proxy IP.

        :param proxy_ip_port: Proxy IP and port (e.g., '123.45.67.89:8080')
        :return: WebDriver instance with proxy settings
        """
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy_ip_port}')
        chrome_options.add_argument('--headless')  # Run in headless mode
        
        return webdriver.Chrome(options=chrome_options)

    def watch_video(self):
        """
        Open the browser with a randomly selected proxy, watch the video for 
        a random duration within the specified range, then close the browser. 
        Repeat this process for the specified number of views.
        """
        for i in range(self.view_count):
            proxy_ip_port = self.get_random_proxy()
            if not proxy_ip_port:
                print("No valid proxies found. Exiting...")
                break

            print(f"Attempting to use proxy: {proxy_ip_port}")

            success = False
            attempt = 0
            max_attempts = 5  # Number of attempts to get a working proxy

            while not success and attempt < max_attempts:
                attempt += 1
                driver = None
                try:
                    # Launch browser with proxy settings
                    driver = self.set_proxy(proxy_ip_port)

                    # Open the video URL
                    driver.get(self.video_url)
                    
                    # Watch the video for a random duration within the specified range
                    watch_time = random.randint(self.min_watch_time, self.max_watch_time)
                    print(f"Watching video for {watch_time} seconds...")
                    sleep(watch_time)
                    
                    success = True  # Mark as successful if no exception occurred
                except:
                    print(f"Connection failed with proxy {proxy_ip_port}")
                    if driver:
                        driver.quit()
                    proxy_ip_port = self.get_random_proxy()  # Get a new proxy
                    print(f"Retrying with a new proxy: {proxy_ip_port}")
                    sleep(5)  # Wait before retrying

                finally:
                    if driver and not success:
                        driver.quit()

            if not success:
                print(f"Failed to connect after {max_attempts} attempts. Moving to next view.")
                continue

            print(f"Completed view {i + 1}/{self.view_count}")
            sleep(10)


def run_bot_instances(video_url, total_views, min_watch_time, max_watch_time, instances, proxy_file='proxy.txt'):
    """
    Run multiple instances of the YouTubeViewBot to achieve the desired total views.

    :param video_url: URL of the YouTube video to be viewed
    :param total_views: Total number of views to generate
    :param min_watch_time: Minimum duration (in seconds) to watch the video
    :param max_watch_time: Maximum duration (in seconds) to watch the video
    :param instances: Number of bot instances to run
    :param proxy_file: Path to the file containing proxy IPs (default is 'proxy.txt')
    """
    views_per_instance = total_views // instances
    threads = []

    for _ in range(instances):
        bot = YouTubeViewBot(video_url, views_per_instance, min_watch_time, max_watch_time, proxy_file)
        thread = threading.Thread(target=bot.watch_video)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    # Get input from user
    video_url = input("Enter YouTube video URL:\n")
    total_views = int(input("Total number of views to generate:\n"))
    min_watch_time = int(input("Enter minimum watch time (in seconds):\n"))
    max_watch_time = int(input("Enter maximum watch time (in seconds):\n"))
    instances = int(input("Number of bot instances to run:\n"))

    # Validate that min_watch_time is less than max_watch_time
    if min_watch_time > max_watch_time:
        print("Error: Minimum watch time cannot be greater than maximum watch time.")
    else:
        # Run the bot instances
        run_bot_instances(video_url, total_views, min_watch_time, max_watch_time, instances)
