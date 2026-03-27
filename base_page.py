from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class BasePage:
    def __init__(self, driver):
        self.driver = driver
  
        self.wait = WebDriverWait(self.driver, 15)

    def find_element(self, locator):
        """Eleman görünene kadar bekler ve döndürür."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click_element(self, locator):
        """Eleman tıklanabilir olunca tıklar."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def send_keys_to_element(self, locator, text):
        """Kutuyu bulur, temizler ve yazıyı yazar."""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)