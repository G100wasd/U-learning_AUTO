from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time as t


print("██████╗ ██╗  ██╗██╗███╗   ██╗███████╗    ██╗      █████╗ ██████╗ ")
print("██╔══██╗██║  ██║██║████╗  ██║██╔════╝    ██║     ██╔══██╗██╔══██╗")
print("██████╔╝███████║██║██╔██╗ ██║█████╗      ██║     ███████║██████╔╝")
print("██╔══██╗██╔══██║██║██║╚██╗██║██╔══╝      ██║     ██╔══██║██╔══██╗")
print("██║  ██║██║  ██║██║██║ ╚████║███████╗    ███████╗██║  ██║██████╔╝")
print("╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═════╝ ")
print("                                                                 ")

def parse_cookies(cookie_str):
    """
    将cookie字符串解析为字典列表
    
    Args:
        cookie_str: cookie字符串，格式为"name1=value1; name2=value2; ..."
    
    Returns:
        cookies_list: 包含字典的列表，每个字典有"name"和"value"键
    """
    cookies_list = []
    
    # 按分号分割每个cookie对
    cookie_pairs = cookie_str.split('; ')
    
    for cookie_pair in cookie_pairs:
        # 按第一个等号分割，因为值中可能包含等号
        if '=' in cookie_pair:
            name, value = cookie_pair.split('=', 1)
            cookies_list.append({
                "name": name.strip(),
                "value": value.strip()
            })
    
    return cookies_list

cookies_list = parse_cookies(input("输入你的cookie"))

qt = Options()
qt.add_argument("--no-sandbox")
qt.add_experimental_option("excludeSwitches", ["enable-automation"])
qt.add_experimental_option("useAutomationExtension", False)
qt.add_experimental_option(name='detach', value=True)
driver = webdriver.Edge(service=Service('msedgedriver.exe'), options=qt)
actions = ActionChains(driver)



driver.get("https://lms.dgut.edu.cn/ulearning") 
t.sleep(1)

all_cookies = []
for cookie in cookies_list:
    cookie_dict = {
        'name': cookie['name'],
        'value': cookie['value'],
        'domain': 'lms.dgut.edu.cn'
    }
    all_cookies.append(cookie_dict)
for cookie in all_cookies:
    try:
        driver.add_cookie(cookie)
        print(f"✅ 已注入: {cookie['name']}")
    except Exception as e:
        print(f"❌ 注入失败 {cookie['name']}: {e}")
driver.refresh()
t.sleep(2)

driver.get("https://lms.dgut.edu.cn/ulearning/index.html#/course/textbook?courseId=153698")
t.sleep(2)
try:
    close_btn = driver.find_element(By.CLASS_NAME, 'modal-dialog-container').find_element(By.CLASS_NAME, 'button')
    t.sleep(1)
    close_btn.click()
except:
    pass


learn_btn_list = driver.find_elements(By.CLASS_NAME, 'button-red-hollow')
learn_rate_list = driver.find_elements(
    By.CSS_SELECTOR, 
    'span[data-bind="text: chapter.progress + \'%\'"]'
)
count = 0
for rate in learn_rate_list:
    if((int)(rate.text.strip('%'))<100):
            break
    count+=1



main_window = driver.current_window_handle
main_url = driver.current_url

learn_btn_list[count].click()
print(f"从专题{count+1}开始")

 # ====== 处理新窗口的undefined问题 ======
try:
            # 1. 等待新窗口出现
            t.sleep(3)
            
            # 2. 获取所有窗口句柄
            all_windows = driver.window_handles
            
            if len(all_windows) > 1:
                print(f"检测到新窗口，共{len(all_windows)}个窗口")
                
                # 3. 切换到新窗口（最后一个通常是新打开的）
                new_window = all_windows[-1]
                driver.switch_to.window(new_window)
                print(f"切换到新窗口: {driver.current_url}")
                
                # 4. 等待页面加载
                t.sleep(2)
                
                # 5. 检查是否有undefined错误
                page_source = driver.page_source
                console_errors = []
                
                # 获取控制台错误
                try:
                    logs = driver.get_log('browser')
                    for log in logs:
                        if '401' in log['message'] or 'error' in log['message'].lower():
                            console_errors.append(log['message'][:100])
                except:
                    pass
                
                # 6. 如果发现401错误或undefined，修复认证
                if "undefined" in page_source or console_errors or '401' in str(page_source):
                    print("检测到401/undefined问题，开始修复认证...")
                    
                    # 获取当前窗口的域名
                    current_url = driver.current_url
                    if '//' in current_url:
                        domain = current_url.split('//')[1].split('/')[0]
                        print(f"新窗口域名: {domain}")
                    else:
                        domain = 'lms.dgut.edu.cn'
                    
                    # 重新注入Cookie
                    driver.delete_all_cookies()
                    
                    # 构建新窗口的Cookie（使用正确的域名）
                    new_window_cookies = []
                    for cookie in all_cookies:
                        cookie_copy = cookie.copy()
                        cookie_copy['domain'] = domain
                        new_window_cookies.append(cookie_copy)
                    
                    # 添加Cookie到新窗口
                    for cookie in new_window_cookies:
                        try:
                            driver.add_cookie(cookie)
                        except:
                            pass
                    
                    # 执行JavaScript修复脚本
                    try:
                        # 设置localStorage认证信息
                        driver.execute_script("""
                            localStorage.setItem('token', 'D9C8E6D3D66FDEE7239B26544E5A74F6');
                            localStorage.setItem('AUTHORIZATION', 'D9C8E6D3D66FDEE7239B26544E5A74F6');
                            localStorage.setItem('userInfo', document.cookie.match(/USER_INFO=([^;]+)/)?.[1] || '');
                        """)
                        
                        # 重新加载失败的JS资源
                        driver.execute_script("""
                            // 重新加载可能失败的资源
                            var failedResources = ['User.js', 'Course.js'];
                            failedResources.forEach(function(resource) {
                                var scripts = document.querySelectorAll('script[src*="' + resource + '"]');
                                scripts.forEach(function(script) {
                                    var newScript = document.createElement('script');
                                    newScript.src = script.src + '?' + new Date().getTime();
                                    document.head.appendChild(newScript);
                                });
                            });
                        """)
                        
                        t.sleep(2)
                    except Exception as js_error:
                        print(f"JavaScript修复失败: {js_error}")
                    
                    # 再次刷新
                    driver.refresh()
                    t.sleep(3)
                    
                    print("认证修复完成")
                

                
                # 刷新主窗口，更新进度
                driver.refresh()
                t.sleep(3)
                
                # 重新获取进度列表（因为页面可能已更新）
                learn_rate_list = driver.find_elements(
                    By.CSS_SELECTOR, 
                    'span[data-bind="text: chapter.progress + \'%\'"]'
                )
                learn_btn_list = driver.find_elements(By.CLASS_NAME, 'button-red-hollow')
except Exception as e:
    print(f"处理新窗口时出错: {e}")
    # 尝试返回主窗口
    try:
        driver.switch_to.window(main_window)
    except:
        pass

# ====== 修复代码结束 ======

# ====== 跳过提示 =====
try:
    t.sleep(3)

    pass_btn = driver.find_elements(By.CLASS_NAME, 'close-btn')[1]
    print(pass_btn.text)
    actions.click(pass_btn).perform()
    t.sleep(1)
except:
    pass
# ===== 跳过提示结束 =====


print("███╗   ███╗██╗   ██╗███████╗██╗     ███████╗██╗   ██╗███████╗███████╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗")
print("████╗ ████║██║   ██║██╔════╝██║     ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║")
print("██╔████╔██║██║   ██║█████╗  ██║     ███████╗ ╚████╔╝ ███████╗█████╗      ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║")
print("██║╚██╔╝██║██║   ██║██╔══╝  ██║     ╚════██║  ╚██╔╝  ╚════██║██╔══╝      ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║")
print("██║ ╚═╝ ██║╚██████╔╝███████╗███████╗███████║   ██║   ███████║███████╗    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║")
print("╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚══════╝╚══════╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝")
print("                                                                                                                              ")

chapter_items = driver.find_elements(By.CLASS_NAME, 'chapter-item')
for i in range(count, len(chapter_items)):
    current_chapter = chapter_items[i]
    page_lists = current_chapter.find_elements(By.CLASS_NAME, 'page-list')
    current_name = current_chapter.find_element(By.CLASS_NAME, 'chapter-name').find_element(By.CLASS_NAME, 'text')
    print("=-=-=-=-=-=-=-==-=-=-=-=-=-=-=-=-=-=-=")
    print(f"当前专题名称:{current_name.text}")
    print(f"当前专题共有{len(page_lists)}部分")
    for page_list in page_lists:
        page_names = page_list.find_elements(By.CLASS_NAME, 'page-name')

        for page_name in page_names:
            print(">---------")

            print(f"> {page_name.find_element(By.CLASS_NAME, 'text').text[1:]}")
            actions.click(page_name).perform()
            t.sleep(2)
            actions.click(page_name).perform()

            try:
                video_player = driver.find_element(By.CLASS_NAME, 'video-container')
                print("> 当前部分为:  视频")
                t.sleep(1)
                video_control = video_player.find_element(By.CLASS_NAME, 'mejs__controls')
                video_time = video_control.find_element(By.CLASS_NAME, 'mejs__duration')
                video_sound_btn = video_control.find_element(By.CLASS_NAME, 'mejs__volume-button').find_element(By.XPATH, './button')
                video_play_btn = video_control.find_element(By.CLASS_NAME, 'mejs__playpause-button').find_element(By.XPATH, './button')
                
                video_sound_btn.click()
                time_min, time_sec = map(int, video_time.text.split(':'))
                pause_count = time_min+1

                print(f"> 视频长度: {video_time.text}")
                print("> 已静音")
                video_play_btn.click()
                print("> 开始播放")
                print(f"> 消耗时间{pause_count*60}s (时间会比视频时间长 为了避免某些神秘的bug)")
                for j in range(pause_count+1):
                    t.sleep(60)
                    actions.click(video_play_btn).perform()
                    print(f"> 防止挂机检测X{j+1}")
                    t.sleep(1)
                    actions.click(video_play_btn).perform()

                print("> 播放结束")
                
                t.sleep(1)
 
            except:
                try:
                    submit_btn = driver.find_element(By.CLASS_NAME, 'question-view').find_element(By.CLASS_NAME, 'btn-submit')
                    t.sleep(1)
                    print("> 当前部分为:  小测")
                    question_list = driver.find_elements(By.CLASS_NAME, 'question-element-node')

                    for q in question_list:
                        question_area = q.find_element(By.CLASS_NAME, 'question-body-wrapper')
                        try:
                            answer_check = question_area.find_elements(By.CLASS_NAME, 'choice-item')[0]
                            driver.execute_script("arguments[0].scrollIntoView();", answer_check)
                            actions.click(answer_check).perform()
                            
                        except:
                            choice_check = question_area.find_elements(By.CLASS_NAME, 'choice-btn')[0]
                            driver.execute_script("arguments[0].scrollIntoView();", choice_check)
                            actions.click(choice_check).perform()
                        t.sleep(1)

                    driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.CLASS_NAME, 'question-operation-area'))
                    t.sleep(3)
                    print("q")
                    driver.execute_script("arguments[0].click();", submit_btn)
                    t.sleep(1)
                    print("> 小测已完成")
                    print("> 当然是全选A和全选对 😋")
                    t.sleep(1)
                    

                except:
                    print("< ERROR:404 >")

            print(">---------")
            print()
            t.sleep(2)

    actions.click(current_chapter.find_element(By.CLASS_NAME, 'chapter-name')).perform()

    t.sleep(1)
    if(i+1<len(chapter_items)):
        actions.click(chapter_items[i+1].find_element(By.CLASS_NAME, 'chapter-name')).perform()
    print('1')
    t.sleep(1)