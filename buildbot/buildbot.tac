import os

from buildbot.master import BuildMaster
from twisted.application import service
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import LogFile

workdir = '.'
basedir = os.path.dirname(os.path.realpath(__file__))
rotateLength = 10000000
maxRotatedFiles = 10
configfile = os.environ.get('BB_CONF', os.path.join(basedir, 'conf/dev.py'))

# Default umask for server
umask = None

# note: this line is matched against to check that this is a buildmaster
# directory; do not edit it.
application = service.Application('buildmaster')
logfile = LogFile.fromFullPath(
    os.path.join(workdir, "twistd.log"),
    rotateLength=rotateLength,
    maxRotatedFiles=maxRotatedFiles)
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)

m = BuildMaster(workdir, configfile, umask)
m.setServiceParent(application)
m.log_rotation.rotateLength = rotateLength
m.log_rotation.maxRotatedFiles = maxRotatedFiles
