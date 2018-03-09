from fabric.api import run, local, hosts, cd, execute
from fabric.colors import green


@hosts('root@www.cheungchan.cc')
def hostname():
    h = run('hostname')
    print(green(h))


@hosts('root@47.94.23.48')
def pull():
    with cd('/root/py_project/qingdian_jian'):
        run('git pull')


@hosts('root@47.94.23.48')
def restart():
    with cd('/root/py_project/qingdian_jian'):
        run('sh restart.sh')


@hosts('root@47.94.23.48')
def pull_and_restart():
    execute(hostname)
    execute(restart)


def ls(path='.'):
    local(f'ls {path}')
