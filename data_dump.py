from life_log.lifelogger import utils as utils
from life_log.models import Event
from django.contrib.auth.models import User

raw1 =  utils.converter('/webapps/thor/thor_app/assets/lanahanj_data.csv')
raw2 =  utils.converter('/webapps/thor/thor_app/assets/lanahanj_data2.csv')

raws = raw1 + raw2

events = []
user = User.objects.get(username='thor')
for r in raws:
    events += [Event(user=user, raw=r)]
    events[-1].full_clean()
    events[-1].save()
