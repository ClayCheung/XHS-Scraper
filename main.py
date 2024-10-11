import argparse
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置命令行参数
parser = argparse.ArgumentParser(description='小红书搜索脚本')
parser.add_argument('-q', '--query', type=str, help='搜索内容', required=True)
parser.add_argument('-n', '--number', type=int, help='获取笔记的数量', default=3)
parser.add_argument('-c', '--comments', type=int, help='查看的评论数量', default=20)
parser.add_argument('-r', '--replies', type=int, help='查看的回复数量', default=50)
parser.add_argument('--json', action='store_true', help='输出JSON格式')
args = parser.parse_args()

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("user-data-dir=./User_Data")  # 设置用户数据目录

# 初始化 WebDriver
driver = webdriver.Chrome(options=chrome_options)
long_wait = WebDriverWait(driver, 60)  # 设置长等待最长等待时间为60秒
wait = WebDriverWait(driver, 10)  # 设置短等待最长等待时间为10秒

try:
    # 打开小红书
    driver.get("https://www.xiaohongshu.com/explore")
    if not args.json:
        print("已打开小红书主页")
    
    # 等待用户扫码登录
    if not args.json:
        print("请扫码登录...")

    # 检测页面刷新
    search_box = long_wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="搜索小红书"]')))
    if not args.json:
        print("页面已刷新，开始搜索")

    # 找到搜索框并输入搜索内容
    search_content = args.query  # 使用命令行参数传递的搜索内容
    search_box.send_keys(search_content)
    if not args.json:
        print(f"输入搜索内容: {search_content}")
    search_box.send_keys(Keys.RETURN)
    if not args.json:
        print("已提交搜索")

    # 等待搜索结果加载
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//section[@class="note-item"]')))
    if not args.json:
        print("搜索结果加载完成")

    # 存储笔记信息的列表
    notes_data = []

    # 获取指定数量的笔记
    notes = driver.find_elements(By.XPATH, '//section[@class="note-item"]')[:args.number]
    if not args.json:
        print(f"找到 {len(notes)} 条笔记")
        print("-" * 20)
    
    for note in notes:
        from selenium.common.exceptions import NoSuchElementException
        # 获取前一条笔记的唯一标识符（内容的前10个字）
        try:
            last_title = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="desc"]').text[:10]
        except NoSuchElementException:
            last_title = ""

        # 点击打开笔记详情
        note.click()
        # 等待新的笔记加载完成，通过等待标题的变化
        wait.until(lambda driver: note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="desc"]').text[:10] != last_title)
        
        # 获取笔记详情
        try:
            title = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="title"]').text
            author = note.find_element(By.XPATH, '//div[@class="author-container"]//span[@class="username"]').text
            content = note.find_element(By.XPATH, '//div[@class="note-content"]//div[@class="desc"]').text
            like_count = driver.find_element(By.CSS_SELECTOR, '#noteContainer > div.interaction-container > div.interactions.engage-bar > div > div > div.input-box > div.interact-container > div > div.left > span.like-wrapper.like-active > span.count').text
        except NoSuchElementException:
            # 如果出现异常，退出当前循环
            continue

        # 实时打印笔记信息
        if not args.json:
            print("标题:", title)
            print("作者:", author)
            print("内容:", content)
            print("点赞数量:", like_count)

        # 存储当前笔记的信息
        note_info = {
            "title": title,
            "author": author,
            "content": content,
            "like_count": like_count,
            "comments": []
        }

        # 展开指定数量的评论
        try:
            expanded_comments = 0
            while expanded_comments < args.comments:
                load_more_buttons = driver.find_elements(By.XPATH, '//div[contains(text(), "展开")]')
                if not load_more_buttons:
                    break
                for button in load_more_buttons:
                    if expanded_comments >= args.comments:
                        break
                    button.click()
                    expanded_comments += 1
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="parent-comment"]')))
        except Exception as e:
            if not args.json:
                print("没有更多回复需要展开或找不到展开按钮:", e)

        # 获取指定数量的父评论
        parent_comments = driver.find_elements(By.XPATH, '//div[@class="parent-comment"]')[:args.comments]

        for parent_comment in parent_comments:
            try:
                # 获取父评论内容
                comment_text = parent_comment.find_element(By.XPATH, './/div[@class="comment-item"]//span[@class="note-text"]').text
                if not args.json:
                    print('评论:', comment_text)

                comment_info = {
                    "comment": comment_text,
                    "replies": []
                }

                # 获取该评论的指定数量的回复
                replies = parent_comment.find_elements(By.XPATH, './/div[@class="reply-container"]//span[@class="note-text"]')[:args.replies]
                for reply in replies:
                    reply_text = reply.text
                    if not args.json:
                        print('回复:', reply_text)
                    comment_info["replies"].append(reply_text)

                note_info["comments"].append(comment_info)
            except Exception as e:
                if not args.json:
                    print('无法获取评论或回复:', e)

        # 将当前笔记的信息添加到列表中
        notes_data.append(note_info)
        if not args.json:
            print("-" * 20)

        driver.back()  # 返回搜索结果页
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//section[@class="note-item"]')))

finally:
    # 根据参数决定是否输出JSON格式
    if args.json:
        print(json.dumps(notes_data, ensure_ascii=False, indent=4))
    else:
        print("-" * 20)
        print("关闭浏览器")

    # 关闭浏览器
    driver.quit()