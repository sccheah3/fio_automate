from django.db import models

class DriveBenchmark(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    drive_pn = models.CharField(max_length=100, default='NA')
    drive_fw = models.CharField(max_length=100, default='NA')

    class Meta:
        ordering = ['modified']

    def __str__(self):
        return self.drive_pn

    @property
    def get_avg(self):
        avg = {1024: [], 2048: [], 4096: [], 8192: [], 16384: [], 32768: [], \
               65536: [], 131072: [], 262144: [], 524288: [], 1048576: [], 2097152: []}

        for drive_performance in self.drive_performances.all():
            for block_performance in drive_performance.block_performances.all():
                avg[block_performance.block_size].append((block_performance.read_speed, block_performance.write_speed))

        l = []

        # store tuples of each run (read, write) -> then convert to avg
        for key in avg:
            N = len(avg[key])
            avg_read = 0
            avg_write = 0

            for read, write in avg[key]:
                avg_read += read
                avg_write += write

            avg_read = avg_read // N
            avg_write = avg_write // N

            l.append([avg_read, avg_write])

        return l

class DrivePerformance(models.Model):
    drive = models.ForeignKey(DriveBenchmark, related_name='drive_performances', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ("pk=%s; Date=%s" %(self.pk, self.created))


class BlockPerformance(models.Model):
    drive_performance = models.ForeignKey(DrivePerformance, related_name='block_performances', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    block_size = models.IntegerField()
    read_speed = models.IntegerField()
    write_speed = models.IntegerField()

    class Meta:
        ordering = ['block_size']

    def __str__(self):
        return str(self.block_size) + ': ' + str(self.read_speed) + ' ' + str(self.write_speed)