from pwnedapi import create_app, db
from common.models import Scan
from rq import get_current_job
import os
import subprocess
import sys
import traceback

def execute_tool(cmd):
    app = create_app(os.environ.get('CONFIG', 'Production'))
    with app.app_context():
        try:
            output = ''
            env = os.environ.copy()
            env['PATH'] = os.pathsep.join(('/usr/bin', env['PATH']))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            out, err = p.communicate()
            output = (out + err).decode()
        except:
            app.logger.error('Unhandled exception', exc_info=sys.exc_info())
            output = traceback.format_exc()
        finally:
            job = get_current_job()
            scan = Scan.query.get(job.get_id())
            scan.complete = True
            scan.results = output
            db.session.commit()
