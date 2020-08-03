import sys
import re
from .models import DriveBenchmark, DrivePerformance, BlockPerformance
from django.utils import timezone

class Drive:
	def __init__(self, device_name=""):
		self.device_name = device_name
		self.pn = ""
		self.fw = ""
		self.rw_speed = {}

	def __str__(self):
		return (self.device_name + ": " + str(self.rw_speed))


	def add_data(self, block_size, speed):
		if block_size in self.rw_speed:
			self.rw_speed[block_size].append(speed)
		else:
			self.rw_speed[block_size] = [speed]

def parse_fio_log(text):
	# convert to bytes. eg 1k -> 1024
	def convert_to_bytes(s):
		val = int(re.search(r'\d+', s).group())

		if s.lower().endswith('k') or s.endswith('KB/s'):
			return val * 1024
		elif s.lower().endswith('m') or s.endswith('MB/s'):
			return val * pow(1024, 2)
		elif s.lower().endswith('g') or s.endswith('GB/s'):
			return val * pow(1024, 3)
		else:	# should be in bytes: B/s
			return val

		return -1


	# convert from raw byte to readable values aka 2M
	def normalize(num):
		# 2**10 = 1024
		power = 2**10
		n = 0
		power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
		while num >= power:
			num /= power
			n += 1
		return str(int(num)) + power_labels[n]

	drives = {}

	# ('1M', 'nvme0n1', '3231MB/s') - will have a tuple of these
	match = re.findall(r'seq_read_([\d]+.)_(.*): \(.*\n.*\(([\d]+[\w]+/\w)\)', text)
	for data in match:
		if data[1] in drives:
			drive = drives[data[1]]
			drive.add_data(convert_to_bytes(data[0]), convert_to_bytes(data[2]))
		else:
			drive = Drive(device_name=data[1])
			drive.add_data(convert_to_bytes(data[0]), convert_to_bytes(data[2]))
			drives[data[1]] = drive


	match = re.findall(r'seq_write_([\d]+.)_(.*): \(.*\n.*\(([\d]+[\w]+/\w)\)', text)
	for data in match:
		if data[1] in drives:
			drive = drives[data[1]]

			if convert_to_bytes(data[0]) in drive.rw_speed:
				drive.add_data(convert_to_bytes(data[0]), convert_to_bytes(data[2]))
			else:
				drive.rw_speed[convert_to_bytes(data[0])] = ["NA", convert_to_bytes(data[2])]
		else:
			drive = Drive(device_name=data[1])
			drive.rw_speed[convert_to_bytes(data[0])] = ["NA", convert_to_bytes(data[2])]
			drives[data[1]] = drive

	# case where there is a read value but no write
	for drive in drives.values():
		for block_size in drive.rw_speed:
			if len(drive.rw_speed[block_size]) < 2:
				drive.rw_speed[block_size].append("NA")

	return drives
	



def parse_and_save(drive_info, fio_log):
	dev_dict = {}

	for chunk in drive_info.readlines():
		chunk = str(chunk, 'utf-8')
		dev, pn, fw = chunk.strip('\n').split(',')
		dev_dict[dev] = (pn, fw)
	
	drives = parse_fio_log(fio_log.read().decode())
	for drive in drives.values():
		key = drive.device_name = str('/dev/') + drive.device_name
		drive.pn, drive.fw = dev_dict[key]

		drive_bench, created = DriveBenchmark.objects.get_or_create(drive_pn=drive.pn, drive_fw=drive.fw)
		if created:
			drive_bench = created

		drive_bench.modified = timezone.now()
		drive_bench.save()
		
		drive_perf = DrivePerformance(drive=drive_bench)
		drive_perf.save()

		for block_size in sorted(drive.rw_speed.keys()):
			r_speed = (drive.rw_speed[block_size][0]) / pow(1024, 2)
			w_speed = (drive.rw_speed[block_size][1]) / pow(1024, 2)
			block_perf = BlockPerformance(drive_performance=drive_perf, block_size=block_size, read_speed=r_speed, write_speed=w_speed)
			block_perf.save()

