import json
import re

def main():
	data = []
	with open('lshw_all.json', 'r') as f:
		data = f.read()

	sf = json.loads(data)
	parse(sf, 0)
	

def parse(d, i):
	if type(d) is dict:
		for k in d:
			if type(d[k]) in (list, dict):
				print(' ' * (i * 4) + str(k))
				if type(d[k]) is list and len(d[k]) == 1:
					parse(d[k], i)
				else:
					parse(d[k], i + 1)
			else:
				print(' ' * (i * 4) + str(k) + ' : ' + str(d[k]))
	else:
		for item in d:
			if type(item) in (list, dict):
				if re.match('bank:[0-9]', item['id']):
					print('-------------------------I CATCH HIM--------------------------------------')
				else:
					parse(item, i + 1)
			else: 
				print(' ' * (i * 4) + str(item))

if __name__ == '__main__':
	main()