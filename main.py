from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime, timedelta
import zoneinfo
from time import sleep


def driver_set():
    options = webdriver.FirefoxOptions()
    options.binary_location = r'C:\Users\molok\AppData\Local\Mozilla Firefox\firefox.exe'
    options.headless = True
    options.add_argument('-profile')
    options.add_argument(
        r'C:\Users\molok\AppData\Roaming\Mozilla\Firefox\Profiles\vm8a9lko.selenium')

    driver = webdriver.Firefox(
        service=FirefoxService(
            executable_path=r'C:\Users\molok\GitHub\.bots\toad\geckodriver.exe'),
        options=options)
    return driver


def open_chat():
    driver = driver_set()
    driver.get('https://vk.com/im?peers=161238107_c29_274804402_343518317&sel=c62')

    return driver


def get_work_type():
    driver = driver_set()
    driver.get('https://vk.com/im?peers=52394615_c62_343518317&sel=274804402')

    me = driver.find_elements(
        By.XPATH, '//div[@data-peer="274804402"]')
    driver.quit()

    work = 'Работа грабитель'
    for mes in reversed(me):
        mes = mes.find_element(By.CLASS_NAME, 'im-mess--text').text
        if mes in ('грабитель', 'крупье'):
            work = 'Работа '+mes
            break
        elif mes == 'столовая':
            work = 'Поход в столовую'
            break
    return work


def get_info(driver):
    send_mes(driver, 'Жаба инфо')

    driver.implicitly_wait(1)
    while 1:
        toad = driver.find_elements(
            By.XPATH, '//div[@data-peer="-191097210"]')
        info = toad[-1].find_element(By.CLASS_NAME, 'im-mess--text').text

        if info.find('Сода и ЖАБУШКА-КВАКУШКА') != -1:
            break

    return info


def paste(driver, text):
    message = driver.find_element(
        By.CLASS_NAME, 'im-chat-input--text')
    message.clear()
    message.send_keys(text)


def send(driver):
    driver.implicitly_wait(0.5)
    send_button = driver.find_element(
        By.CLASS_NAME, 'im-send-btn_send')
    send_button.click()


def send_mes(driver, text):
    paste(driver, text)
    send(driver)


def set_task(text, hours):
    zone = zoneinfo.ZoneInfo('Europe/Moscow')
    driver = open_chat()
    send_mes(driver, text)
    driver.quit()

    if text.find('Работа') != -1:
        text = 'Работа кончится в'
    elif text == 'Покормить Жабу':
        text = 'Покормить Жабу в'
    else:
        text = 'Снова на работу в'

    time = datetime.now(tz=zone)
    change = timedelta(hours=hours)
    time = time + change
    print("{} {}".format(text, time.strftime("%H:%M")))
    return time


def feed(scheduler):
    time = set_task('Покормить Жабу', 12)

    scheduler.add_job(feed, 'date', run_date=time, args=[scheduler])


def send_work(scheduler):
    # work_type = get_work_type()
    time = set_task('Работа крупье', 2)

    scheduler.add_job(wait_work, 'date', run_date=time, args=[scheduler])


def wait_work(scheduler):
    time = set_task('Завершить работу', 6)

    scheduler.add_job(send_work, 'date', run_date=time, args=[scheduler])


def calculate_time(text, str, format):
    zone = zoneinfo.ZoneInfo('Europe/Moscow')
    current_time = datetime.now(tz=zone)

    time = datetime.strptime(str, format)
    time_change = timedelta(hours=time.hour, minutes=time.minute)
    time = current_time + time_change
    print("{} {}".format(text, time.strftime("%H:%M")))
    return time


def again():
    driver = open_chat()
    message = get_info(driver).split('\n')
    driver.quit()

    if message[0].find('можно отправить на работу') != -1:
        send_work(scheduler)
    elif message[0].find('Можно забрать жабу с работы') != -1:
        driver = open_chat()
        send_mes(driver, 'Завершить работу')
        driver.quit()
    elif message[0].find('Отправить на работу можно будет через') != -1:
        str_time = message[0].replace(
            ':Отправить на работу можно будет через ', '')
        time = calculate_time('Снова на работу в', str_time, '%Hч:%Mм')
        scheduler.add_job(send_work, 'date', run_date=time, args=[scheduler])
    else:
        str_time = message[0].replace(':Забрать жабу можно через ', '')
        time = calculate_time('Работа кончится в',
                              str_time, '%H часов %M минут')
        scheduler.add_job(wait_work, 'date', run_date=time, args=[scheduler])


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
scheduler = BackgroundScheduler()
scheduler.start()

###########################################################################
driver = open_chat()
message = get_info(driver).split('\n')
driver.quit()

if message[0].find('можно отправить на работу') != -1:
    send_work(scheduler)
elif message[0].find('Можно забрать жабу с работы') != -1:
    driver = open_chat()
    send_mes(driver, 'Завершить работу')
    driver.quit()
    again()
elif message[0].find('Отправить на работу можно будет через') != -1:
    str_time = message[0].replace(
        ':Отправить на работу можно будет через ', '')
    time = calculate_time('Снова на работу в', str_time, '%Hч:%Mм')
    scheduler.add_job(send_work, 'date', run_date=time, args=[scheduler])
else:
    str_time = message[0].replace(':Забрать жабу можно через ', '')
    time = calculate_time('Работа кончится в', str_time, '%H часов %M минут')
    scheduler.add_job(wait_work, 'date', run_date=time, args=[scheduler])

if message[1].find('Жабу можно покормить') != -1:
    feed(scheduler)
else:
    str_time = message[1].replace(':Можно покормить через ', '')
    time = calculate_time('Покормить Жабу в', str_time, '%Hч:%Mм')
    scheduler.add_job(feed, 'date', run_date=time, args=[scheduler])
###########################################################################

while True:
    sleep(60)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
