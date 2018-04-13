
import csv
import requests
from bs4 import BeautifulSoup

# get page with list of dragonflies
url = 'https://www.odonatacentral.org/index.php/ChecklistAction.showChecklist/location_id/13999'
response = requests.get(url)
html = response.content

# format for readability & utility
soup = BeautifulSoup(html, "html.parser")

# get all rows of first table
table = soup.find_all("table")[0].find_all("tr")

# open output file
outFile = open("./dragonflies.csv", "wb")
# create writer to write CSV file
writer = csv.writer(outFile)
# write headers
writer.writerow(["Name","Order","Suborder","Superfamily","Family","Genus","Species"
				,"Identification","Size","Length","Abdomen","Hindwing","Similar Species"
				,"Habitat","Discussion","Distribution"])

# loop through all rows
for row in table:
	# skip row if it is wrong format or does not have field guide
	if row.find("td") is not None and row.find_all("td")[2].find("a") is not None:
		# process row if it has a field guide
		url = row.find_all("td")[2].find("a").get("href")
		response = requests.get(url)
		html = response.content
		
		# format for readability & utility
		soup = BeautifulSoup(html, "html.parser")

		# dictionary to hold dragonfly data
		data = {}

		# get dragonfly common name
		h1Array = soup.find("h1").contents
		# save common name into dictionary
		data["Name"] = h1Array[len(h1Array)-1].strip()

		# find beginning of taxonomy data
		taxonomyData = soup.find("span", style="padding-left: 40px; font-size: 16px;")

		# get taxonomy data while there is more to get
		while taxonomyData is not None:
			# if taxonomy header is found then enter into dictionary
			if taxonomyData.find("strong") is not None:
				# save taxonomy data as dictionary entries
				data[taxonomyData.find("strong").string.strip()] = \
							taxonomyData.find('span').string.strip()
			
			# get taxonomy data if it is not sibling of beginning of taxonomy data
			if taxonomyData.find_next_sibling() is not None:
				# get next piece of taxonomy data
				taxonomyData = taxonomyData.find_next_sibling()
			else: # at end of taxonomy data, break out of while loop
				break

		# get data on dragonfly
		for h2Data in soup.find_all("h2", class_="subsection"):
			# save data as dictionary entries
			data[h2Data.text.strip()] = h2Data.find_next_sibling().text.strip()

		# split size data into more descriptive parts
		sizeData = data["Size"].split(";")
		data["Length"] = sizeData[0].split(":")[1].strip()
		data["Abdomen"] = sizeData[1].split(":")[1].strip()
		data["Hindwing"] = sizeData[2].split(":")[1].strip()

		# create CSV of dragonfly data, if data does not exist then enter empty string
		data_list = [data.get("Name", ""),data.get("Order", ""),data.get("Suborder", ""),
					data.get("Superfamily", ""),data.get("Family", ""),data.get("Genus", ""),
					data.get("Species", ""),data.get("Identification", ""),data.get("Size", ""),
					data.get("Length", ""),data.get("Abdomen", ""),data.get("Hindwing", ""),
					data.get("Similar Species", ""),data.get("Habitat", ""),data.get("Discussion", ""),
					data.get("Distribution", "")]

		# write data to CSV file
		writer.writerow(data_list)