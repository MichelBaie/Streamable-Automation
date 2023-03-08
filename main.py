from selenium import webdriver
import time
import json
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from drop_files import drop_files
WebElement.drop_files = drop_files

# Get filename to upload
if len(sys.argv) > 1:
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Le fichier fourni n'existe pas.")
        sys.exit()
else:
    print("Veuillez fournir un nom de fichier en argument.")
    sys.exit()

# Import Login of Streamable Account
with open('login.json') as f:
    data = json.load(f)
    username = data['username']
    password = data['password']



# Start Firefox
options = Options()
options.add_argument("--width=800")
options.add_argument("--height=600")
options.add_argument('-headless')
options.headless = True
driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox()

def login():
    try:
        driver.get("https://streamable.com/login")
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        driver.find_element("xpath", "/html/body/div[1]/div/div[1]/div/form/div[1]/input").send_keys(username)
        driver.find_element("xpath", "/html/body/div[1]/div/div[1]/div/form/div[2]/input").send_keys(password)
        time.sleep(1)
        driver.find_element("xpath", "/html/body/div[1]/div/div[1]/div/form/button").click()
        time.sleep(2)
    except:
        print("Une erreur est survenue lors du login.")
        driver.quit()
        sys.exit(1)
    print("Connecté à Streamable.")

def upload(filename):
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        before_upload_url = driver.find_element(By.ID, "video-url-input").get_attribute("value")
        driver.find_element("xpath", "/html/body/div[1]/div/div/div[1]/nav/a[1]").drop_files(file_path)
        time.sleep(3)
        driver.refresh()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "action-button")))
        after_upload_url = driver.find_element(By.ID, "video-url-input").get_attribute("value")
        if before_upload_url != after_upload_url:
            return after_upload_url
        else:
            return "Une erreur est survenue lors de la vérification de l'upload de la vidéo."
    except Exception as e:
        print("Une erreur est survenue lors de l'envoi de votre vidéo.")
        driver.quit()
        sys.exit(1)

def check_file_properties(filename):
    try:
        filesize_mb = os.path.getsize(filename) / (1024 * 1024)
        if filesize_mb > 250:
            print("Le fichier est trop volumineux.")
            sys.exit(1)
        duration = float(os.popen(f'ffprobe -i {filename} -show_entries format=duration -v quiet -of csv="p=0"').read().strip())
        if duration > 600:
            print("Le fichier est trop long.")
            sys.exit(1)
        if not os.popen(f'ffprobe -v error -select_streams v:0 -show_entries stream=codec_type -of default=nokey=1:noprint_wrappers=1 "{filename}"').read().strip() == 'video':
            print("Le fichier donné n'est pas une vidéo.")
    except Exception as e:
        print("Une erreur est survenue lors de la vérification du fichier.")
        driver.quit()
        sys.exit(1)
    print("Le fichier est valide.")

# Login on streamable.com
login()
# Check if file is compatible before upload
check_file_properties(filename)
# Upload video
print("Lien de la vidéo : ",upload(filename))
driver.quit()