import schedule
import time
import datetime
import re
import pandas as pd
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def my_crawler_job():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{current_time}] 啟動爬蟲任務...")

    # 【重大修正】必須把 driver 的設定與啟動放在函數「裡面」
    # 這樣每次排程執行時，才會開啟一個全新的無頭瀏覽器
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    url = 'https://ieknet.iek.org.tw/ieknews/default.aspx?actiontype=ieknews&indu_idno=1'
    
    try:
        print(f"正在前往: {url}")
        driver.get(url)
        time.sleep(8)  

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        data = []
        seen_links = set()
        articles = soup.find_all('a', href=re.compile(r'news_more\.aspx'))
        
        print(f"偵測到 {len(articles)} 筆新聞連結，過濾中...")

        for a in articles:
            title = a.get('title') or a.text.strip()
            href = a.get('href')
            
            if len(title) > 5 and href not in seen_links:
                full_link = urljoin('https://ieknet.iek.org.tw/', href)
                
                date_val = "未知日期"
                parent = a.find_parent('div') or a.find_parent('li')
                if parent:
                    date_tag = parent.find('li', title="新聞日期")
                    if date_tag:
                        date_val = date_tag.text.strip()
                
                data.append({
                    'title': title,
                    'link': full_link,
                    'date': date_val,
                    'photo_link': "無圖片" 
                })
                seen_links.add(href)
            
            if len(data) >= 7: break

        for news in data:
            print(f" 進入: {news['title'][:15]}...")
            driver.get(news['link'])
            time.sleep(4)
            art_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            img = art_soup.find('img', class_='img-fluid') or art_soup.find('div', id='NewsContent').find('img') if art_soup.find(id='NewsContent') else None
            if img:
                news['photo_link'] = urljoin('https://ieknet.iek.org.tw', img.get('src'))

        df = pd.DataFrame(data, columns=['date', 'title', 'link', 'photo_link'])
        
        print("\n" + "="*50)
        print(df[['date', 'title']])
        
        # 存檔 (會自動透過 Docker Volume 寫入到本機資料夾)
        df.to_csv("IEKNEWS.csv", index=False, encoding="utf-8-sig")
        
        if not df.empty:
            print("\n[第一篇標題]:", df.iloc[0]['title'])
            print("[第一篇日期]:", df.iloc[0]['date'])

    except Exception as e:
        print(f" 發生錯誤: {e}")

    finally:
        # 用完瀏覽器後關閉
        driver.quit()
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 任務結束，釋放記憶體。")


# ================= 排程器設定區 =================

# 設定每 1 分鐘執行一次 (方便現在馬上測試看結果)
#schedule.every(1).minutes.do(my_crawler_job)

schedule.every().day.at("08:00").do(my_crawler_job)

print("爬蟲排程器已成功啟動！(設定為每日 08:00 執行)")

# 啟動無窮迴圈
while True:
    schedule.run_pending()
    time.sleep(1)