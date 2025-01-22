from bs4 import BeautifulSoup
import requests
import csv
file = open("brand_mobile.csv")
csvreader = csv.reader(file)
header = next(csvreader)
#print(header)
rows = []
for row in csvreader:
    #print(row[1])
    rows.append(row[1])
#print(rows)
file.close()

csv_file = open('mobiles.csv', 'w',newline='')

csv_writer = csv.writer(csv_file)
csv_writer.writerow(['mobiles', 'links'])
for link in rows:
    source = requests.get(link).text
    soup = BeautifulSoup(source,'lxml')

    for mobile in soup.find_all('a',class_='rvw-title'):
        mobiles = mobile['title']
        mobile_link = mobile['href']
        csv_writer.writerow([mobiles, mobile_link])


