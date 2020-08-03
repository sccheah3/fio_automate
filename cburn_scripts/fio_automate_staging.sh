#! /bin/bash

HOSTSERV="172.16.118.50"

source /root/stage2.conf


yum install -y https://repo.ius.io/ius-release-el7.rpm
yum install -y python3
pip3 install xlsxwriter


wget "http://${HOSTSERV}/create_fio_jobfile.py" -O /root/create_fio_jobfile.py &> /dev/null
if [ $? -ne 0 ]; then
	echo "Error acquiring fio job building tool" | tee -a /dev/tty0 ${SYS_DIR}/fio_status.log
	return 1
fi

wget "http://${HOSTSERV}/cburn_chart_fio.py" -O /root/cburn_chart_fio.py &> /dev/null
if [ $? -ne 0 ]; then
	echo "Error acquiring fio charting tool" | tee -a /dev/tty0 ${SYS_DIR}/fio_status.log
	return 2
fi

# get drive arrays
diskname_sd=$( ls /dev/ | grep -iE sd.+ )
diskname_nvme=$( ls /dev/ | grep -iE nvme.+n1$ )

DRIVES=()

for disk in $diskname_sd ; do
	DRIVES+=( "/dev/$disk" )
done

for disk in $diskname_nvme ; do
	DRIVES+=( "/dev/$disk" )
done


# create jobfiles
echo "Creating jobfiles..." > /dev/tty0
python3 /root/create_fio_jobfile.py "${DRIVES[@]}"
cp -r /root/fio_jobfile ${SYS_DIR}
mkdir /root/fio_results

# run fio
echo "Running FIO..." > /dev/tty0
fio /root/fio_jobfile/seq.fio --output=/root/fio_results/seq.log
fio /root/fio_jobfile/rand.fio --output=/root/fio_results/rand.log


# copy the logs to DIR
echo "Copying log files to ${SYS_DIR}..." > /dev/tty0
cp -r /root/fio_results/ ${SYS_DIR}

echo "Charting the results..." > /dev/tty0
python3 /root/cburn_chart_fio.py /root/fio_results/seq.log /root/drive_chart_performance.xlsx
echo "Copying chart xlsx file to ${SYS_DIR}..." > /dev/tty0
cp -r /root/drive_chart_performance.xlsx ${SYS_DIR}

echo "Uploading results to server..."
curl -X POST -F 'drive_info_file=@/root/disk_info.txt' -F 'fio_log_file=@/root/fio_results/seq.log' "http://${HOSTSERV}/drive_benchmark/upload_performance_data/"


return 0