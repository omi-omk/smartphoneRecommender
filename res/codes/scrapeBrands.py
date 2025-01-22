from bs4 import BeautifulSoup
import requests
import csv



source = requests.get('https://gadgets.ndtv.com/mobiles/all-brands').text
soup = BeautifulSoup(source,'lxml')

csv_file = open('brand_mobile.csv', 'w',newline='')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['brands', 'links'])


#num = 0
for brand in soup.find_all('a',class_='rvw-title'):
    brands = brand['title']
    link = brand['href']
    csv_writer.writerow([brands, link])
    
    #num = num + 1
#print(num)
