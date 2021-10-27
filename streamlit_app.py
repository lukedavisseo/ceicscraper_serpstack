import requests
from requests.exceptions import Timeout, SSLError, MissingSchema
import streamlit as st
import pandas as pd
import json
import tldextract
import time

access_key = st.text_input("Enter Serpstack key")

# SERP data to put into a DataFrame

serp = {
	'urls': [],
	'titles': [],
	'meta_desc': [],
	'competitor': []
}

# List of competitors

competitor_urls = ["tradingeconomics.com", "theglobaleconomy.com", "countryeconomy.com", "focus-economics.com", "worldbank.org", "knoema.com"]

# Area to enter data

st.title("CEIC Scraper")

multi_kw = st.text_area('Enter keywords, 1 per line').lower()
csv_toggle = st.radio('Create CSV', ['Yes', 'No'])

lines = multi_kw.split("\n")
keywords = [line for line in lines]

submit = st.button('Submit')

# Code to execute when submit button is pressed

if submit:

	msg = st.markdown('Processing, please wait...')

	for k in keywords:
		
		st.header(f'{k}')

		google_search_url = 'http://www.google.com/search?q=' + k.replace(' ', '+')

		st.write(google_search_url)

		params = {
			'access_key': access_key,
			'query': k,
			'gl': 'uk'
		}

		api_result = requests.get('http://api.serpstack.com/search', params, verify=False)

		for i in range(5):
			try:
				time.sleep(2)
				api_response = api_result.json()
				org = api_response.get("organic_results")

				for results in range(0,len(org)):
					link = (org[results]['url'])
					ext = tldextract.extract(link)
					if ext.registered_domain in competitor_urls:
						serp['urls'].append(link)
						serp['titles'].append(org[results]['title'])
						serp['meta_desc'].append(org[results]['snippet'])
						serp['competitor'].append("Competitor match found")
						st.write(f'Competitor match found: {ext.registered_domain}')
				if not serp['competitor']:
					st.write('No competitors found')
				break

			except (ValueError, Timeout, SSLError, MissingSchema) as e:
				st.error(f"{e} found! Retrying...")
				continue
			
		if serp['competitor'] and csv_toggle:
			df = {key:pd.Series(value, dtype='object') for key, value in serp.items()}
			serp_df = pd.DataFrame(df)
			serp_df_csv = serp_df.to_csv()
			st.download_button(label=f'Download SERP data for {k}', data=serp_df_csv, file_name=f'{k}_serp.csv', mime='text/csv')
		else:
			pass

	msg = st.markdown('Completed!')
