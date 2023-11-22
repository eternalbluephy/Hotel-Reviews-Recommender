from typing import List
from collections import namedtuple
from time import sleep
from random import randint

from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from rich import print
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

CommentItem = namedtuple('CommentItem', ('comment', 'score'))
progress = Progress(
    TextColumn('[bold blue]{task.description}'),
    BarColumn(bar_width=None),
    '•',
    TimeElapsedColumn(),
    '•',
    TimeRemainingColumn()
)

def random_sleep(begin: float = 1, end: float = 2):
    sleep(randint(begin, end))

def get_url(id: int) -> str:
    return f'https://hotels.ctrip.com/hotels/{id}.html'

def get_hotel_name(soup: BeautifulSoup) -> str:
    return soup.find('span', class_='detail-crumb_hotel').text

def get_max_pages(soup: BeautifulSoup, total: int = 0) -> int:
    pages_li = soup.find_all('div', class_='m_num')
    max_pages = int(pages_li.pop().text)
    return max_pages if total <= 0 else min(total, max_pages)

def get_comments(soup: BeautifulSoup) -> List[CommentItem]:
    comments: List[CommentItem] = []
    comment_items = soup.find_all('div', class_='m-reviewCard-item')
    for comment_item in comment_items:
        score = float(comment_item.find('div', class_='m-score_single').strong.text)
        comment = comment_item.find('div', class_='comment').p.text
        comments.append(CommentItem(comment, score))
    return comments

HOTELS = (68488139, 1052477)

options = EdgeOptions()
# 隐藏正在受到自动软件的控制的提示
options.add_argument('disable-blink-features=AutomationControlled')
driver = Edge(options=options)
driver.get('https://hotels.ctrip.com/')
driver.maximize_window()
wait = WebDriverWait(driver, 100)
# 登录
button = driver.find_element(By.CLASS_NAME, 'tl_nfes_home_header_login_IUsnp')
button.click()
wait.until(EC.presence_of_all_elements_located((By.ID, 'ibu_hotel_container')))

# 任务开始
print(f'[bold cyan]任务开始，共 {len(HOTELS)} 个酒店')
for i, id in enumerate(HOTELS):
    url = get_url(id)
    driver.get(url)
    all = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'hotel-detail_info_review')))
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    pages = get_max_pages(soup, 5)
    print(f'[bold blue]--- 第 {i+1} 个酒店 共 {pages} 页 ---[/bold blue]')
    task = progress.add_task(get_hotel_name(soup), total=pages)
    progress.start()
    for _ in range(pages):
        next = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-pagination_item .forward')))
        soup = BeautifulSoup(driver.page_source)
        comments = get_comments(soup)
        with open('result.txt', 'a', encoding='utf-8') as f:
            f.write(str(comments))
        random_sleep()
        progress.update(task, advance=1)
        next.click()
    progress.stop()
    progress.remove_task(task)

print('[bold green]所有任务已结束[/bold green]')
driver.quit()