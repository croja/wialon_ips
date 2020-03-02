#!/usr/bin/env python3

import appdirs
import json
import os
import re
import requests
import socket
import sys
import time

from PyInquirer import prompt

PRESETS_DIR = appdirs.user_data_dir("wialon_ips", "Sergey Shevchik")
if not os.path.exists(PRESETS_DIR):
	os.makedirs(PRESETS_DIR)

PRESETS_PATH = os.path.join(PRESETS_DIR, 'wialon_ips_presets.conf')

if len(sys.argv) > 1 and sys.argv[1] == 'clear':
	try:
		os.remove(PRESETS_PATH)
	except:
		pass
	sys.exit()



def endpoint_filter(endpoint):
	return endpoint.split()[0]

DEFAULT_TRACK_URL = 'http://89.223.93.46:8000/wialon_ips/sample_track.txt'

ENDPOINTS = {
	'Wialon Hosting NL': '193.193.165.165',
	'Wialon Hosting MSK': '185.213.0.24',
	'Wialon Hosting USA': '64.120.108.24',
	'Wialon Hosting TRACE': '193.193.165.166',
	'Wialon Hosting TIG': '185.213.1.24',
	'Wialon Hosting OLD': '77.74.50.78',
	'Specify custom': 'Custom'
}

LAST_PRESETS = None
LAST_CUSTOM_ENDPOINT = None
LAST_UID = None
LAST_SRC_URL = None
LAST_SRC_PATH = None

PRESET = None

try:
	with open(PRESETS_PATH, 'r') as cf:
		conf = json.load(cf)
		if 'last_uid' in conf:
			LAST_UID = conf['last_uid']
		if 'last_src_url' in conf:
			LAST_SRC_URL = conf['last_src_url']
		if 'last_src_path' in conf:
			LAST_SRC_PATH = conf['last_src_path']
		if 'last_custom_endpoint' in conf:
			LAST_CUSTOM_ENDPOINT = conf['last_custom_endpoint']

		if 'presets' in conf and type(conf['presets']) is dict:
			LAST_PRESETS = conf['presets']
			if len(LAST_PRESETS):
				load_preset = prompt(dict(message=f'Load from preset', type='list', choices=['no', 'yes'], name='load_preset'))['load_preset']
				if load_preset == 'yes':
					choosen_preset = prompt(dict(message='Choose preset', type='list', choices=LAST_PRESETS, name='choosen_preset'))['choosen_preset']
					if len(choosen_preset):
						PRESET = LAST_PRESETS[choosen_preset]
except:
	pass

SETTINGS = {}
if PRESET:
	SETTINGS = PRESET
else:
	# ASKING PROTOCOL
	SETTINGS['protocol'] = prompt(dict(message='Protocol', type='list', choices=['TCP', 'UDP'], name='protocol'))['protocol']

	# ASKING ENDPOINT
	endpoint = prompt(dict(message='Choose endpoint', type='list', choices=[ENDPOINTS[ep] + ' (' + ep + ')' for ep in ENDPOINTS], \
		name='ep', filter=endpoint_filter))['ep']
	if endpoint == 'Custom':
		ep_q = dict(message='Enter endpoint', type='input', name='ep')
		if LAST_CUSTOM_ENDPOINT:
			ep_q['default'] = LAST_CUSTOM_ENDPOINT
		SETTINGS['endpoint'] = prompt(ep_q)['ep']
		if len(SETTINGS['endpoint']):
			LAST_CUSTOM_ENDPOINT = SETTINGS['endpoint']
	else:
		SETTINGS['endpoint'] = endpoint
	
	# ASKING PORT
	SETTINGS['port'] = int(prompt(dict(message='Port', type='input', default='20332', name='port'))['port'])

	# ASKING INTERVAL
	SETTINGS['interval'] = prompt(dict(message='Interval(seconds)', type='input', default='5', name='ival'))['ival']

	# ASKING UID
	uid_q = dict(message='IMEI', type='input', name='uid')
	if LAST_UID:
		uid_q['default'] = LAST_UID
	SETTINGS['uid'] = prompt(uid_q)['uid']
	if len(SETTINGS['uid']):
		LAST_UID = SETTINGS['uid']
	
	# ASKING SRC
	SETTINGS['track_src_type'] = prompt(dict(message='Track source type', type='list', choices=['URL', 'File'], name='track_src_type'))['track_src_type']
	src_q = dict(name='src', type='input')
	if SETTINGS['track_src_type'] == 'File':
		src_q['message'] = 'File path'
		if LAST_SRC_PATH:
			src_q['default'] = LAST_SRC_PATH
		SETTINGS['track_src'] = prompt(src_q)['src']
		if len(SETTINGS['track_src']):
			LAST_SRC_PATH = SETTINGS['track_src']
	else:
		src_q['message'] = 'Track URL'
		if LAST_SRC_URL:
			src_q['default'] = LAST_SRC_URL
		else:
			src_q['default'] = DEFAULT_TRACK_URL
		SETTINGS['track_src'] = prompt(src_q)['src']
		if len(SETTINGS['track_src']):
			LAST_SRC_URL = SETTINGS['track_src']

try:
	PROTOCOL = SETTINGS['protocol']
	ENDPOINT = SETTINGS['endpoint']
	PORT = SETTINGS['port']
	UID = SETTINGS['uid']
	INTERVAL = SETTINGS['interval']
	TRACK_SRC_TYPE = SETTINGS['track_src_type']
	TRACK_SRC = SETTINGS['track_src']
except Exception as e:
	print(f'Settings are invalid: {e}')
	sys.exit()

TRACK_DATA = None
if TRACK_SRC_TYPE == 'File':
	try:
		with open(TRACK_SRC) as f:
			TRACK_DATA = f.readlines()
	except Exception as e:
		print(f'Failed to get track data from specified source {TRACK_SRC} ({TRACK_SRC_TYPE}): {e}')
elif TRACK_SRC_TYPE == 'URL':
	try:
		r = requests.get(TRACK_SRC)
		TRACK_DATA = r.text.split()
	except Exception as e:
		print(f'Failed to get track data from specified source {TRACK_SRC} ({TRACK_SRC_TYPE}): {e}')

if not TRACK_DATA:
	sys.exit()

try:
	with open(PRESETS_PATH, 'w') as cf:
		new_config = dict()
		if LAST_UID:
			new_config['last_uid'] = LAST_UID
		if LAST_CUSTOM_ENDPOINT:
			new_config['last_custom_endpoint'] = LAST_CUSTOM_ENDPOINT
		if LAST_SRC_PATH:
			new_config['last_src_path'] = LAST_SRC_PATH
		if LAST_SRC_URL:
			new_config['last_src_url'] = LAST_SRC_URL
		
		new_presets = None
		if LAST_PRESETS:
			new_presets = LAST_PRESETS
		if not PRESET:
			save_to_preset = prompt(dict(message='Save as preset', type='list', choices=['no', 'yes'], name='answer'))['answer']
			if save_to_preset == 'yes':
				preset_name = prompt(dict(message='New preset name', type='input', name='preset_name'))['preset_name']
				if len(preset_name):
					new_presets = new_presets or dict()
					new_presets[preset_name] = SETTINGS
		
		if new_presets:
			new_config["presets"] = new_presets

		json.dump(new_config, cf)
except Exception as e:
	print(f'Failed to save update config: {e}')

def parse_line(input_line):
	res = re.search(r'(\d+.\d+),(?!A)(\D),(\d+.\d+),(\D)', input_line)
	lat1 = res.group(1)
	lat2 = res.group(2)
	lon1 = res.group(3)
	lon2 = res.group(4)
	return (lat1, lat2, lon1, lon2)

msgs = [parse_line(line) for line in TRACK_DATA]

if PROTOCOL == 'TCP':
	LOGIN_MESSAGE = b'#L#'
	LOGIN_MESSAGE = b''.join([LOGIN_MESSAGE, bytearray(UID, 'utf-8')])
	LOGIN_MESSAGE = b''.join([LOGIN_MESSAGE, b';NA\r\n'])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ENDPOINT, PORT))

	print(f'Connected to {s.getpeername()}')

	print(f'Sending login message')
	sent = s.send(LOGIN_MESSAGE)
	data = s.recv(1024)
	if data.decode('utf-8').startswith('#AL#1'):
		print('Login Success. Sending messages...')
	else:
		print('Login Failed: ' + data.decode('utf-8'))
		sys.exit()

	while True:
		for msg in msgs:
			request = '#SD#NA;NA;{};{};{};{};140;0;100;6'.format(msg[0], msg[1], msg[2], msg[3]).encode('utf-8') + b'\r\n'

			bytes_sent = s.send(request)
			print(request)
			readen_data = s.recv(1024)
			print(readen_data)

			time.sleep(float(INTERVAL))

	s.close()
elif PROTOCOL == 'UDP':
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while True:
		for msg in msgs:
			request = '{}#SD#NA;NA;{};{};{};{};140;0;100;6'.format(UID, msg[0], msg[1], msg[2], msg[3])
			r = b''.join([bytearray(request, 'utf-8'), b'\r\n'])
			print(r)
			sock.sendto(r, (ENDPOINT, PORT))
			# data = sock.recv(400)
			# print(data)
			time.sleep(float(INTERVAL))

