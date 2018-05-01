import sys
import subprocess
from pipsi import IS_WIN


def test_create_env(tmpdir):
    subprocess.check_call([
        sys.executable, 'get-pipsi.py',
        '--home', str(tmpdir.join('venv')),
        '--bin-dir', str(tmpdir.join('test_bin')),
        '--src', '.',
        '--ignore-existing',
    ])
    if IS_WIN:
        subprocess.check_call([
            str(tmpdir.join('test_bin/pipsi.exe'))
        ])
    else:
        subprocess.check_call([
            str(tmpdir.join('test_bin/pipsi'))
        ])


def test_create_env_version(tmpdir):
    subprocess.check_call([
        sys.executable, 'get-pipsi.py',
        '--home', str(tmpdir.join('venv')),
        '--bin-dir', str(tmpdir.join('test_bin')),
        '--src', '.',
        '--ignore-existing',
        '--suffix-version',
    ])
    version = '.'.join(map(str, sys.version_info[:3]))
    if IS_WIN:
        subprocess.check_call([
            str(tmpdir.join('test_bin/pipsi-{}.exe'.format(version)))
        ])
    else:
        subprocess.check_call([
            str(tmpdir.join('test_bin/pipsi-{}'.format(version)))
        ])
