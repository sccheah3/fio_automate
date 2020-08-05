import xlsxwriter
import sys
import re
import subprocess
import json


# I hate regex. 

# provide logical mapping to disk pn
disk_dict = {}
disk_names = subprocess.Popen(['/bin/ls', '/dev'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
nvme_info, err = subprocess.Popen(['nvme', 'list', '-o', 'json'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()

# gets all sd* and saves them as /dev/sda, /dev/sdb
match = re.findall(r'sd[\w]+', disk_names.stdout.read().decode('utf-8'), re.IGNORECASE)
disk_names = [str('/dev/') + disk for disk in match]

# getting data with smartctl
for disk in disk_names:
	disk_info = subprocess.Popen(['/usr/sbin/smartctl', '-a', disk], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	match = re.findall(r'Device\s+Model:[\t\s]*([\w\d\s-]+)\n[\s\S]*firmware\s+version:[\t\s]*([\w\d\s-]+)\n', disk_info.stdout.read().decode('utf-8'), re.IGNORECASE)
	for m in match:
		disk_dict[disk] = {'part_number': m[0], 'firmware_version': m[1]}
		
# convert nvme disk info to json format
nvme_info = nvme_info.decode('unicode_escape')
nvme_info = json.loads(nvme_info)	

for device in nvme_info['Devices']:
	disk_dict[device['DevicePath']] = {'part_number': device['ModelNumber'], 'firmware_version': device['Firmware']}


# save disk info into separate file. can refactor this into a separate pkg
f = open("/root/disk_info.txt", "w+")
for device in disk_dict.keys():
	f.write("%s,%s,%s\n" % (device, disk_dict[device]['part_number'], disk_dict[device]['firmware_version']))
f.close()


class Drive:
	def __init__(self, device_name=""):
		# self.disk_name = ""
		self.device_name = device_name
		# self.device_driver = ""
		self.rw_speed = {}

	def __str__(self):
		return (self.device_name + ": " + str(self.rw_speed))


	def add_data(self, block_size, speed):
		if block_size in self.rw_speed:
			self.rw_speed[block_size].append(speed)
		else:
			self.rw_speed[block_size] = [speed]

def chart(text, output_filename="drive_performance.xlsx"):
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
	match = re.findall(r'seq_read_([\d]+.)_(.*): \(.*\n.*\(([\d\.]+[\w]+/\w)\)', text)
	for data in match:
		if data[1] in drives:
			drive = drives[data[1]]
			drive.add_data(convert_to_bytes(data[0]), convert_to_bytes(data[2]))
		else:
			drive = Drive(device_name=data[1])
			drive.add_data(convert_to_bytes(data[0]), convert_to_bytes(data[2]))
			drives[data[1]] = drive


	match = re.findall(r'seq_write_([\d]+.)_(.*): \(.*\n.*\(([\d\.]+[\w]+/\w)\)', text)
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


	workbook = xlsxwriter.Workbook(output_filename)
	worksheet = workbook.add_worksheet()

	row = 0
	col = 0
	c = 1
	for drive in drives.values():
		worksheet.write(row, col, "/dev/" + str(drive.device_name))
		row += 1
		worksheet.write(row, col, "PN: " + str(disk_dict['/dev/' + drive.device_name]['part_number']))
		row += 1
		worksheet.write(row, col, "FW: " + str(disk_dict['/dev/' + drive.device_name]['firmware_version']))
		row += 1
		worksheet.write(row, col, "Block Size")
		worksheet.write(row, col + 1, "Read (MB/s)")
		worksheet.write(row, col + 2, "Write (MB/s)")
		row += 1

		chart = workbook.add_chart({'type': 'line'})
		chart.set_title({'name': drive.device_name})
		chart.set_y_axis({'name': 'Speed (MB/s)', })

		row_line_chart = row

		for block_size in sorted(drive.rw_speed.keys()):

			worksheet.write(row, col, normalize(block_size))
			worksheet.write(row, col + 1, (drive.rw_speed[block_size][0]) / pow(1024, 2))
			worksheet.write(row, col + 2, (drive.rw_speed[block_size][1]) / pow(1024, 2))

			row += 1


		chart.add_series({'name': 'Read', 'categories': str('=Sheet1!$A$' + str(row_line_chart + 1) + ':$A$' + str(row)),
						'values': str('=Sheet1!$B$' + str(row_line_chart + 1) + ':$B$' + str(row))})
		chart.add_series({'name': 'Write', 'categories': str('=Sheet1!$A$' + str(row_line_chart + 1) + ':$A$' + str(row)),
						'values': str('=Sheet1!$C$' + str(row_line_chart + 1) + ':$C$' + str(row))})

		worksheet.insert_chart(str('C' + str(c)), chart, {'x_offset': 100, 'y_offset': row_line_chart * 18.65})

		c += 1
		row += 3

	workbook.close()

	return workbook

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Usage: python3 chart_fio.py [input filename] [output filename]")
		exit(1)

	input_filename = sys.argv[1]
	output_filename = sys.argv[2]

	if not output_filename.endswith(".xlsx"):
		output_filename = output_filename + '.xlsx'

	file = open(input_filename, 'r')
	text = file.read()

	chart(text, output_filename)