import os

from buildbot.changes.gitpoller import GitPoller
from buildbot.config import BuilderConfig
from buildbot.plugins import worker
from buildbot.process.factory import BuildFactory
from buildbot.schedulers.basic import AnyBranchScheduler
from buildbot.steps.shell import ShellCommand
from buildbot.www.auth import UserPasswordAuth


def env(key, default):
    return os.environ.get(key, default)


def make_test_factory():
    """A simple factory that echoes 'Hello world!'."""
    f = BuildFactory()
    f.addStep(ShellCommand(command=["echo", "Hello world!"]))
    return f


PORT = int(env('BB_PORT', '8010'))

BuildmasterConfig = {
    "title": "Dolphin Emulator ⋅ DEVELOPMENT",
    "titleURL": "/",
    "buildbotURL": "http://localhost:{}/".format(PORT),

    "protocols": {
        "pb": {"port": 9989},
    },

    "change_source": [
        GitPoller(repourl=env('BB_REPOURL',
                              'https://github.com/dolphin-emu/dolphin.git'),
                  pollInterval=5),
    ],

    "workers": [
        worker.LocalWorker("test-worker"),
    ],

    "builders": [
        BuilderConfig(name="test-builder", workernames=["test-worker"],
                      factory=make_test_factory()),
        # TODO: add relevant builders from prod conf
    ],

    "schedulers": [
        AnyBranchScheduler(name="test-scheduler",
                           builderNames=["test-builder"]),
    ],

    "www": {
        "port": PORT,
        "auth": UserPasswordAuth(
            {env('BB_USER', 'dolphin'): env('BB_PSWD', 'dolphin')}),
        "plugins": {
            "waterfall_view": {"num_builds": 50},
            "console_view": {},
        },
    },

    "services": [],

    "db": {
        "db_url": "sqlite:///state.sqlite",
    },

    "collapseRequests": False,
    "buildbotNetUsageData": None,
}
