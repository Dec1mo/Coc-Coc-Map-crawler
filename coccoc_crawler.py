# -*- coding: utf-8 -*-

import requests
import json
import time
import random as rd
import numpy as np
from collections import namedtuple
import logging

Area = namedtuple("Area", ['bot', 'top', 'left', 'right', 'name'])
areas = []
areas.append(Area(20.668394, 23.426274, 102.110642, 105.322665, 'area_1'))
areas.append(Area(20.668394, 23.426274, 105.322665, 108.062333, 'area_2'))
areas.append(Area(16.320860, 20.668394, 103.740271, 107.094002, 'area_3'))
areas.append(Area(11.664441, 16.320860, 105.804559, 109.488939, 'area_4'))
areas.append(Area(8.572525, 11.664441, 104.411107, 109.252761, 'area_5'))

EPSILON = 0.000001
URL = 'https://map.coccoc.com/map/search.json?borders={}%2C{}%2C{}%2C{}'
LOG_FILE_PATH = 'coccoc_crawler_{}.log'
FILE_PATH = 'coccoc_data_{}.json'

def get_data(x, y, next_x, next_y):
	url = URL.format(x, y, next_x, next_y)
	response = None
	while response == None:
		try:
			response = requests.get(url, verify=False)
			break
		except:
			print("Let me sleep for 5 seconds")
			time.sleep(5)
			continue
	json_response = json.loads(response.content)
	try:
		results = json_response['result']['poi']
	except KeyError:
		results = []
		logging.error('url: {}\njson_response: {}'.format(url, json_response))
	return results

def handle_data(results, result_dict):
	for res in results:
		one_res_dict = dict()
		gps = dict()
		gps['latitude'] = res['gps']['latitude']
		gps['longitude'] = res['gps']['longitude']
		one_res_dict['gps'] = gps
		try:
			one_res_dict['title'] = res['title'].replace(u'\xa0', u' ')
			one_res_dict['address'] = res['address'].replace(u'\xa0', u' ')
			one_res_dict['category'] = res['category'].replace(u'\xa0', u' ')
		except KeyError:
			break
		result_dict[res['hash']] = one_res_dict

def recur_crawl(x, y, top, right, linspace_x_size, linspace_y_size, result_dict):
	if (top - x) < EPSILON or (right - y) < EPSILON:
		results = get_data(x, y, top, right)
		if len(results) > 20:
			logging.info('bot: {}, top: {}, left: {}, right: {}'\
				.format(x, top, y, right))
		handle_data(results, result_dict)
	else:
		# print('x = {}, y = {}, next_x = {}, next_y = {}, linspace_x_size = {}, linspace_y_size = {}'\
		# 			.format(x, y, top, right, linspace_x_size, linspace_y_size))
		lin_x_list = np.linspace(x, top, num=linspace_x_size)
		lin_y_list = np.linspace(y, right, num=linspace_y_size)
		for i in range (len(lin_x_list)-1):
			for j in range (len(lin_y_list)-1):
				# print ('bot: {}, top: {}, left: {}, right: {}'\
				# 	.format(lin_x_list[i], lin_x_list[i+1], lin_y_list[j], lin_y_list[j+1]))
				results = get_data(lin_x_list[i], lin_y_list[j], lin_x_list[i+1], lin_y_list[j+1])
				# print('len(results) = ', len(results))
				time.sleep(rd.uniform(0.1,0.3))
				if len(results) > 20:
					recur_crawl(lin_x_list[i], lin_y_list[j], lin_x_list[i+1], lin_y_list[j+1], linspace_x_size, linspace_y_size, result_dict)
				else:
					handle_data(results, result_dict)

start_time = time.time()
for area in areas:
	logging.basicConfig(filename=LOG_FILE_PATH.format(area.name), level=logging.INFO)
	result_dict = dict()
	recur_crawl (area.bot, area.left, area.top, area.right, 3, 3, result_dict)
	with open(FILE_PATH.format(area.name), 'w+', encoding='utf-8') as f:
		json.dump(result_dict, f, ensure_ascii=False)
print("\nRunning time: %s seconds" % (time.time() - start_time))

# Noti for finishing
# import winsound
# frequency = 2500  # Set Frequency To 2500 Hertz
# duration = 300  # Set Duration To 1000 ms == 1 second
# winsound.Beep(frequency, duration)






    

