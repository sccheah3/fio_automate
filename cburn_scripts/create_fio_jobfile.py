# ex: sudo python3 create_fio_jobfile.py /dev/sda /dev/sdb /dev/sdc

# CHANGE RUNTIME AND RAMPTIME  BACK TO 10, 120

import os
import sys

SEQ_JOBFILE = "/root/fio_jobfile/seq.fio"
RAND_JOBFILE = "/root/fio_jobfile/rand.fio"

BLOCK_SIZES = ["1k", "2k", "4k", "8k", "16k", "32k", "64k", "128k", "256k", "512k", "1M", "2M"]


os.makedirs(os.path.dirname(SEQ_JOBFILE), exist_ok=True)

with open(SEQ_JOBFILE, 'w+') as s_jobfile:
	# global block
	s_jobfile.write("[global]\n")
	s_jobfile.write("direct=1\n")
	s_jobfile.write("buffered=0\n")
	s_jobfile.write("ioengine=libaio\n")
	s_jobfile.write("ramp_time=0\n")
	s_jobfile.write("runtime=15\n")
	s_jobfile.write("group_reporting\n")
	s_jobfile.write("iodepth=128\n")
	s_jobfile.write("numjobs=8\n")
	s_jobfile.write("numa_cpu_nodes=0\n")
	s_jobfile.write("numa_mem_policy=bind:0\n")
	s_jobfile.write("\n")


	# seq read
	for x in sys.argv[1:]:
		dev_full_name = str(x)
		dev_name = x.split('/')[2]

		for bs in BLOCK_SIZES:
			s_jobfile.write("[seq_read_%s_%s]\n" %(bs, dev_name))
			s_jobfile.write("stonewall\n")
			s_jobfile.write("rw=read\n")
			s_jobfile.write("bs=%s\n" %(bs))
			s_jobfile.write("filename=%s\n" %(dev_full_name))
			s_jobfile.write("\n")

	# seq write
	for x in sys.argv[1:]:
		dev_full_name = str(x)
		dev_name = x.split('/')[2]

		for bs in BLOCK_SIZES:
			s_jobfile.write("[seq_write_%s_%s]\n" %(bs, dev_name))
			s_jobfile.write("stonewall\n")
			s_jobfile.write("rw=read\n")
			s_jobfile.write("bs=%s\n" %(bs))
			s_jobfile.write("filename=%s\n" %(dev_full_name))
			s_jobfile.write("\n")

	s_jobfile.close()



with open(RAND_JOBFILE, 'w+') as s_jobfile:
	# global block
	s_jobfile.write("[global]\n")
	s_jobfile.write("direct=1\n")
	s_jobfile.write("buffered=0\n")
	s_jobfile.write("ioengine=libaio\n")
	s_jobfile.write("ramp_time=0\n")
	s_jobfile.write("runtime=2\n")
	s_jobfile.write("group_reporting\n")
	s_jobfile.write("iodepth=32\n")
	s_jobfile.write("numjobs=8\n")
	s_jobfile.write("numa_cpu_nodes=0\n")
	s_jobfile.write("numa_mem_policy=bind:0\n")
	s_jobfile.write("\n")

	# rand read @ 4k
	for x in sys.argv[1:]:
		dev_full_name = str(x)
		dev_name = x.split('/')[2]

		s_jobfile.write("[rand_read_4k_%s]\n" %(dev_name))
		s_jobfile.write("stonewall\n")
		s_jobfile.write("rw=randread\n")
		s_jobfile.write("bs=4k\n")
		s_jobfile.write("filename=%s\n" %(dev_full_name))
		s_jobfile.write("\n")

	# rand write @ 4k
	for x in sys.argv[1:]:
		dev_full_name = str(x)
		dev_name = x.split('/')[2]

		s_jobfile.write("[rand_write_4k_%s]\n" %(dev_name))
		s_jobfile.write("stonewall\n")
		s_jobfile.write("rw=randwrite\n")
		s_jobfile.write("bs=4k\n")
		s_jobfile.write("filename=%s\n" %(dev_full_name))
		s_jobfile.write("\n")

	s_jobfile.close()