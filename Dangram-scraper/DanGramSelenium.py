from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.get("http://visl.sdu.dk/visl/da/parsing/automatic/parse.php")
#assert "Python" in driver.title
#element = driver.find_element_by_name("pika")
element = driver.find_element_by_name("theform")
element.send_keys("some text")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()