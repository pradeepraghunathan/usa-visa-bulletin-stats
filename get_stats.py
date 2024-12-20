import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_visa_bulletin_data(fiscal_year: int, month: str, suffix: str) -> Optional[BeautifulSoup]:
	"""
	Fetches and parses the Visa Bulletin data for a given fiscal year and month.

	Args:
		fiscal_year (int): The fiscal year for which to fetch the data.
		month (str): The month for which to fetch the data.
		suffix (str): The suffix for the URL (e.g., '2025').

	Returns:
		Optional[BeautifulSoup]: Parsed HTML content of the target table or None if no valid table is found.
	"""
	url = f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{fiscal_year}/visa-bulletin-for-{month}-{suffix}.html"
	response = requests.get(url)
	soup = BeautifulSoup(response.content, 'html.parser')
	tables = soup.find_all('table')

	# Filter tables that have more than 2 rows
	valid_tables = [table for table in tables if len(table.find_all('tr')) > 2]

	if not valid_tables:
		logging.warning(f"No tables with more than 2 rows found for {month} {suffix}.")
		return None

	target_table = valid_tables[2]
	rows = target_table.find_all("tr")
	headers = [cell.text for cell in rows[0].find_all("td")]

	desired_columns = ['INDIA']
	desired_indexes = [headers.index(col) for col in desired_columns]
	
	data = []

	month_dict = { "january": "Jan",
					"february": "Feb",
					"march": "Mar",
					"april": "Apr",
					"may": "May",
					"june": "Jun",
					"july": "Jul",
					"august": "Aug",
					"september": "Sep",
					"october": "Oct",
					"november": "Nov",
					"december": "Dec",
					   
			   }

	data.append('01'+month_dict.get(month)+str(suffix)[2:4])

	i = 0
	for row in rows:
		i = i+1
		cols = row.find_all('td')
		selected_data = [cols[i].text for i in desired_indexes]
		if i in [2,3,4]:  # only process rows with content
			data.append(selected_data[0].replace(u'\xa0', u' '))

	target_table = valid_tables[3]

	# Find the specific table with employment-based data (simplified, real parsing might vary)
	#table = soup.find('table')  # You would refine this to find the correct table
	rows = target_table.find_all('tr')
	
	#data = []
	i = 0
	for row in rows:
		#print(row)
		i = i+1
		cols = row.find_all('td')
		selected_data = [cols[i].text for i in desired_indexes]
		if i in [2,3,4]:  # only process rows with content
			data.append(selected_data[0].replace(u'\xa0', u' '))

	new_data = []
	i = 0
	for row in data:
		i=i+1
		if i != 1:
			month = row
			month = month[2:5]
			row = row[0:2] + month.capitalize() + row[5:7]
		new_data.append(row)

	return new_data

def extract_india_data(data: BeautifulSoup) -> Dict[str, List[str]]:
	"""
	Extracts India-specific data from the given table.

	Args:
		data (BeautifulSoup): The table from which to extract data.

	Returns:
		Dict[str, List[str]]: Extracted data for India.
	"""
	# Implementation for extracting India-specific data
	india_data = { 'Visa Bulletin Release Month': [], 'EB1 Final Action Date': [], 'EB2 Final Action Date': [], 'EB3 Final Action Date': [], 'EB1 Filing Date': [], 'EB2 Filing Date': [], 'EB3 Filing Date': [] }
	i = 0
	visa_bulletin_release_month = ""
	for row in data:
		i=i+1
		if i == 1:
			visa_bulletin_release_month = row#datetime.strptime(row, "%d%b%y")
			india_data['Visa Bulletin Release Month'].append(visa_bulletin_release_month)
		elif i == 2:
			if row == "C":
				india_data['EB1 Final Action Date'].append(visa_bulletin_release_month)
			else:
				india_data['EB1 Final Action Date'].append(row)
		elif i == 3:
			if row == "C":
				india_data['EB2 Final Action Date'].append(visa_bulletin_release_month)
			else:
				india_data['EB2 Final Action Date'].append(row)
		elif i == 4:
			if row == "C":
				india_data['EB3 Final Action Date'].append(visa_bulletin_release_month)
			else:
				india_data['EB3 Final Action Date'].append(row)	
		elif i == 5:
			if row == "C":
				india_data['EB1 Filing Date'].append(visa_bulletin_release_month)
			else:
				india_data['EB1 Filing Date'].append(row)
		elif i == 6:
			if row == "C":
				india_data['EB2 Filing Date'].append(visa_bulletin_release_month)
			else:
				india_data['EB2 Filing Date'].append(row)
		elif i == 7:
			if row == "C":
				india_data['EB3 Filing Date'].append(visa_bulletin_release_month)
			else:
				india_data['EB3 Filing Date'].append(row)


	return india_data


def process_visa_bulletin_data(fiscal_years: List[int], months: List[str]) -> pd.DataFrame:
	"""
	Processes visa bulletin data for the given fiscal years and months.

	Args:
		fiscal_years (List[int]): List of fiscal years to process.
		months (List[str]): List of months to process.

	Returns:
		pd.DataFrame: DataFrame containing the processed visa bulletin data.
	"""
	visa_bulletin_data = []

	for fiscal_year in fiscal_years:
		for month in months:
			try:
				suffix = fiscal_year - 1 if month in ['october', 'november', 'december'] else fiscal_year
				data = get_visa_bulletin_data(fiscal_year, month, suffix)
				if data:
					india_data = extract_india_data(data)
					visa_bulletin_data.append(india_data)
			except Exception as e:
				logging.error(f"Error parsing data for {fiscal_year}-{month}: {e}")

	return pd.DataFrame(visa_bulletin_data)

def plot_visa_bulletin_data(df: pd.DataFrame) -> None:
	"""
	Plots the visa bulletin data.

	Args:
		df (pd.DataFrame): DataFrame containing the visa bulletin data.
	"""
	plt.figure(figsize=(10, 6))

	# Convert list columns to string or another suitable format
	df['Visa Bulletin Release Month'] = df['Visa Bulletin Release Month'].apply(lambda x: x[0])
	df['EB1 Final Action Date'] = df['EB1 Final Action Date'].apply(lambda x: x[0])
	df['EB2 Final Action Date'] = df['EB2 Final Action Date'].apply(lambda x: x[0])
	df['EB3 Final Action Date'] = df['EB3 Final Action Date'].apply(lambda x: x[0])

	# Plotting
	plt.plot(df['Visa Bulletin Release Month'], df['EB1 Final Action Date'], label='EB1 Final Action Date')
	plt.plot(df['Visa Bulletin Release Month'], df['EB2 Final Action Date'], label='EB2 Final Action Date')
	plt.plot(df['Visa Bulletin Release Month'], df['EB3 Final Action Date'], label='EB3 Final Action Date')

	plt.xlabel('Visa Bulletin Release Month')
	plt.ylabel('Final Action Date')
	plt.title('Visa Bulletin Trends')
	plt.legend()
	plt.show()

if __name__ == "__main__":
	fiscal_years = [2020, 2021, 2022, 2023, 2024, 2025]
	months = ['october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september']

	df = process_visa_bulletin_data(fiscal_years, months)
	logging.info(df)

	df.to_csv("output.csv", index=False)
	plot_visa_bulletin_data(df)