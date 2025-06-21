from django.db import models
import uuid

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    device_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='active')
    os = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

class SecurityEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20)
    source_ip = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    is_threat = models.BooleanField(default=False)
