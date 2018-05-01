#!/usr/bin/env python
import argparse
import os
import shutil
import sys
from subprocess import Popen
import textwrap


try:
    WindowsError
except NameError:
    IS_WIN = False
    PIP = '/bin/pip'
    PIPSI = '/bin/pipsi'
else:
    IS_WIN = True
    PIP = '/Scripts/pip.exe'
    PIPSI = '/Scripts/pipsi.exe'

try:
    import virtualenv
    venv_pkg = 'virtualenv'
    del virtualenv
except ImportError:
    try:
        import venv
        venv_pkg = 'venv'
        del venv
    except ImportError:
        venv_pkg = None

DEFAULT_PIPSI_HOME = os.path.expanduser('~/.local/venvs')
DEFAULT_PIPSI_BIN_DIR = os.path.expanduser('~/.local/bin')
DEFAULT_PIPSI_SUFFIX_VERSION = '0'


def echo(msg=''):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def fail(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()
    sys.exit(1)


def succeed(msg):
    echo(msg)
    sys.exit(0)


def command_exists(cmd):
    with open(os.devnull, 'w') as null:
        try:
            return Popen(
                [cmd, '--version'],
                stdout=null, stderr=null).wait() == 0
        except OSError:
            return False


def publish_script(venv, bin_dir, suffix):
    if IS_WIN:
        for name in os.listdir(venv + '/Scripts'):
            if 'pipsi' in name.lower():
                shutil.copy(venv + '/Scripts/' + name,
                            os.path.join(bin_dir, append_suffix(name, suffix)))
    else:
        os.symlink(venv + '/bin/pipsi',
                   os.path.join(bin_dir, append_suffix('pipsi', suffix)))
    echo('Installed {} binary in {}'.format(append_suffix('pipsi', suffix),
                                            bin_dir))


def install_files(venv, bin_dir, install, suffix):
    try:
        os.makedirs(bin_dir)
    except OSError:
        pass

    def _cleanup():
        try:
            shutil.rmtree(venv)
        except (OSError, IOError):
            pass

    if Popen([sys.executable, '-m', venv_pkg, venv]).wait() != 0:
        _cleanup()
        fail('Could not create virtualenv for pipsi :(')

    # pass env to overcome issue described here:
    # https://github.com/pypa/virtualenv/issues/845
    env = dict(os.environ)
    env.pop('__PYVENV_LAUNCHER__', None)
    if Popen([venv + PIP, 'install', install], env=env).wait() != 0:
        _cleanup()
        fail('Could not install pipsi :(')

    publish_script(venv, bin_dir, suffix)


def parse_options(argv):
    bin_dir = os.environ.get('PIPSI_BIN_DIR', DEFAULT_PIPSI_BIN_DIR)
    home_dir = os.environ.get('PIPSI_HOME', DEFAULT_PIPSI_HOME)
    suffix_version = os.environ.get('PIPSI_SUFFIX_VERSION',
                                    DEFAULT_PIPSI_SUFFIX_VERSION) == '1'

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bin-dir',
        default=bin_dir,
        help=(
            'Executables will be installed into this folder. '
            'Default: %(default)s'
        ),
    )
    parser.add_argument(
        '--home',
        dest='home_dir',
        default=home_dir,
        help='Virtualenvs are created in this folder. Default: %(default)s',
    )
    parser.add_argument(
        '--src',
        default='pipsi',
        help=(
            'The specific version of pipsi to install. This value is passed '
            'to "pip install <value>". For example, to install from master '
            'use "git+https://github.com/mitsuhiko/pipsi.git#egg=pipsi". '
            'Default: %(default)s'
        ),
    )
    parser.add_argument(
        '--ignore-existing',
        action='store_true',
        help=(
            "ignore versions of pipsi already installed. "
            "Use this to ignore a package manager based install or for testing"
        ),
    )
    parser.add_argument(
        '--suffix-version',
        action='store_true',
        default=suffix_version,
        help='Suffix executables with Python version (including pipsi)',
    )
    return parser.parse_args(argv)


def append_suffix(name, suffix):
    if suffix:
        if '.' in name:
            ext = name[name.rindex('.'):]
            return name[:name.rindex('.')] + '-' + suffix + ext
        return name + '-' + suffix
    return name


def main(argv=sys.argv[1:]):
    args = parse_options(argv)
    if args.suffix_version:
        suffix = '.'.join(map(str, sys.version_info[:3]))
    else:
        suffix = ''

    cmd = append_suffix('pipsi', suffix)
    if command_exists(cmd) and not args.ignore_existing:
        succeed('You already have {} installed'.format(cmd))
    else:
        echo('Installing ' + cmd)

    if venv_pkg is None:
        fail('You need to have virtualenv installed to bootstrap pipsi.')

    venv = os.path.join(args.home_dir, append_suffix('pipsi', suffix))
    install_files(venv, args.bin_dir, args.src, suffix)

    if not command_exists(cmd):
        echo(textwrap.dedent(
            '''
            %(sep)s

            Warning:
              It looks like %(bin_dir)s is not on your PATH so pipsi will not
              work out of the box. To fix this problem make sure to add this to
              your .bashrc / .profile file:

              export PATH=%(bin_dir)s:$PATH

            %(sep)s
            ''' % dict(sep='=' * 60, bin_dir=args.bin_dir)
        ))

    succeed(cmd + ' is now installed.')


if __name__ == '__main__':
    main()
