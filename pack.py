import os
import shutil
import pathlib
import glob
from collections import defaultdict


stdpkg = [
    # Repos
    'cython',
    'cython2',
    'freeglut',
    'glu',
    'libjpeg-turbo',
    'libxtst',
    'mesa',
    'git',
    'libnotify',
    'python-boto3',
    'python-future',
    'python-jinja',
    'python-numpy',
    'python-scipy',
    'python-scikit-learn',
    'python-setuptools',
    'python-matplotlib',
    'python-mysqlclient',
    'python-networkx',
    'python-psutil',
    'python-requests',
    'python-six',
    'webkit2gtk',
   'jdk-openjdk', 
   'jdk11-openjdk',

    # Fragile AUR
    'wxgtk3-dev',
    'python-mahotas',
]


if __name__ == '__main__':

    root_fdn = pathlib.Path('/home/fabio/programs/aur')
    pkg_folders = os.listdir(root_fdn)

    deps = defaultdict(list)

    def find_deps(deps, pkg_fdn):
        if pkg_fdn in deps:
            return
        if not (root_fdn / pkg_fdn).exists():
            print(f'Package folder not found: {pkg_fdn}')
            deps[pkg_fdn] = None
            return

        with open(root_fdn / pkg_fdn / 'PKGBUILD') as f:
            in_deplist = False
            for line in f:
                if line.startswith('depends') or ('makedepends' in line):
                    in_deplist = True
                if in_deplist:
                    if ')' in line:
                        in_deplist = False

                        if '(' not in line:
                            continue

                    line = line.rstrip('\n')
                    if '(' in line:
                        line = line[line.find('(') + 1:].strip()

                    if ')' in line:
                        line = line[:line.find(')')].strip()

                    if line == '':
                        continue

                    if ' ' in line:
                        fields = line.split()
                    else:
                        fields = [line]

                    for field in fields:
                        field = field.strip(' \'"')

                        if '=' in field:
                            field = field.split('=')[0]
                            field = field.split('>')[0]
                            field = field.split('<')[0]

                        # A few exceptions
                        if field == 'python-wxpython':
                            field += '4.1.0'

                        # Skip a bunch of standard packages
                        if 'python2' in field:
                            continue
                        if field in stdpkg:
                            continue

                        deps[pkg_fdn].append(field)

        # Tail recursion
        for dep in deps[pkg_fdn]:
            find_deps(deps, dep)

    find_deps(deps, 'cellprofiler')

    deplist = []
    for depis in deps.values():
        if depis is not None:
            deplist.extend(depis)
    deplist = sorted(set(deplist))

    cwd = pathlib.Path(os.path.abspath('.'))
    for dep in deplist:
        os.makedirs(cwd / 'pkgbuilds' / dep, exist_ok=True)
        shutil.copy(
            root_fdn / dep / 'PKGBUILD',
            cwd / 'pkgbuilds' / dep / 'PKGBUILD',
        )
