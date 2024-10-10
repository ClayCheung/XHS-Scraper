import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

parser = argparse.ArgumentParser(description='小红书搜索脚本')
parser.add_argument('-q', '--query', type=str, help='搜索内容', required=True)
args = parser.parse_args()


# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("user-data-dir=./User_Data")  # 设置用户数据目录

# 初始化 WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # 打开小红书
    driver.get("https://www.xiaohongshu.com/explore")
    print("已打开小红书主页")
    
    # 等待用户扫码登录
    print("请扫码登录...")

    # 检测页面刷新
    while not driver.find_elements(By.XPATH, '//input[@placeholder="搜索小红书"]'):
        print("等待页面刷新...")
        time.sleep(1)
    print("页面已刷新，开始搜索")

    # 找到搜索框并输入搜索内容
    search_box = driver.find_element(By.XPATH, '//input[@placeholder="搜索小红书"]')
    print("找到搜索框")
    search_content = args.query  # 使用命令行参数传递的搜索内容
    search_box.send_keys(search_content)
    print(f"输入搜索内容: {search_content}")
    search_box.send_keys(Keys.RETURN)
    print("已提交搜索")

    # 等待搜索结果加载
    time.sleep(5)
    print("搜索结果加载完成")

    # 获取前 3 条笔记
    notes = driver.find_elements(By.XPATH, '//section[@class="note-item"]')[:1]
    print(f"找到 {len(notes)} 条笔记")
    for note in notes:
        # 点击打开笔记详情
        note.click()
        time.sleep(2)  # 等待详情页加载

        # 获取笔记详情
        title = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="title"]').text
        author = note.find_element(By.XPATH, '//div[@class="author-container"]//span[@class="username"]').text
        content = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="desc"]').text
        like_count = driver.find_element(By.CSS_SELECTOR, '#noteContainer > div.interaction-container > div.interactions.engage-bar > div > div > div.input-box > div.interact-container > div > div.left > span.like-wrapper.like-active > span.count').text
        
        print("标题:", title)
        print("作者:", author)
        print("内容:", content)
        print("点赞数量:", like_count)

        # 展开所有回复
        try:
            while True:
                # 找到并点击“展开”按钮
                load_more_buttons = driver.find_elements(By.XPATH, '//div[contains(text(), "展开")]')
                if not load_more_buttons:
                    break
                for button in load_more_buttons:
                    button.click()
                    time.sleep(1)  # 等待加载更多回复
        except Exception as e:
            print("没有更多回复需要展开或找不到展开按钮:", e)

        # 获取所有评论
        comments = driver.find_elements(By.XPATH, '//div[@class="comments-container"]//div[@class="list-container"]')

        for comment in comments:
            try:
                # 获取评论内容
                comment_text = comment.find_element(By.XPATH, './/span[@class="note-text"]').text
                print('评论:', comment_text)

                # 获取评论的回复
                replies = comment.find_elements(By.XPATH, './/div[@class="reply-container"]//span[@class="note-text"]')
                for reply in replies:
                    reply_text = reply.text
                    print('回复:', reply_text)
            except Exception as e:
                print('无法获取评论或回复:', e)
        # comments_total = driver.find_elements(By.XPATH, '//div[@class="comments-container"]//div[@class="total"]')
        # comments_list = driver.find_elements(By.XPATH, '//div[@class="comments-container"]//div[@class="list-container"]')
        # comment_texts = [comment.text for comment in comments]

   
        # print("评论:", comment_texts)
        print("-" * 20)

        driver.back()  # 返回搜索结果页
        time.sleep(2)  # 等待页面加载

finally:
    # 关闭浏览器
    print("关闭浏览器")
    time.sleep(100)
    # driver.quit()
