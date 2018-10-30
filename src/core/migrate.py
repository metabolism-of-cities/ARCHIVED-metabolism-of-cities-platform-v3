from .models import Video, Journal, Organization

list = Journal.object.all
for info in list:
    str(info.name)
