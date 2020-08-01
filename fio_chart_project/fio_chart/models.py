from django.db import models

class DriveBenchmark(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    drive_pn = models.CharField(max_length=100, default='NA')

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.drive_pn

class DrivePerformance(models.Model):
    drive = models.ForeignKey(DriveBenchmark, related_name='drive_performances', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class BlockPerformance(models.Model):
    drive_performance = models.ForeignKey(DrivePerformance, related_name='block_performances', null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    block_size = models.IntegerField()
    read_speed = models.BigIntegerField()
    write_speed = models.BigIntegerField()

    class Meta:
        ordering = ['block_size']

    def __str__(self):
        return str(self.block_size) + ': ' + str(self.read_speed) + ' ' + str(self.write_speed)