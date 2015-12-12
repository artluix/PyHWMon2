import subprocess
import time

def main():
	start_time = time.time()
	s = subprocess.check_output(['lshw', '-C', 'processor'])
	lshw_time = time.time() - start_time
	start_time = time.time()
	t = subprocess.check_output(['dmidecode', '-t', 'processor'])
	dmidecode_time = time.time() - start_time
	start_time = time.time()
	e = subprocess.check_output('decode-dimms')
	decode_dimms_time = time.time() - start_time	
	start_time = time.time()
	f = subprocess.check_output(['hwinfo', '--cpu'])
	hwinfo_time = time.time() - start_time

	print('lshw:' + str(lshw_time))
	print('dmidecode:' + str(dmidecode_time))
	print('decode-dimms:' + str(decode_dimms_time))
	print('hwinfo:' + str(hwinfo_time))


if __name__ == '__main__':
	main()