from plugins.dependencies.models import *
from plugins.dependencies.controllers import *


admin.add_view(WithIdView(Environment, db.session, category='Global'))
admin.add_view(WithIdView(Application, db.session, category='Software', name='Applications'))
