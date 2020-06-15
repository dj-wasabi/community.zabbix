import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_zabbiserver_running_and_enabled(host):
    # if host.system_info.distribution == 'centos':
    zabbix = host.service("zabbix-server")
    assert zabbix.is_enabled
    assert zabbix.is_running


@pytest.mark.parametrize("server", [("zabbix-server-pgsql"), ("zabbix-server-mysql")])
def test_zabbix_package(host, server):
    ansible_data = host.ansible.get_variables()
    zabbixhost = ansible_data['inventory_hostname']

    zabbixhost = zabbixhost.replace("-centos", "")
    zabbixhost = zabbixhost.replace("-debian", "")
    zabbixhost = zabbixhost.replace("-ubuntu", "")

    if zabbixhost == server:
        if host.system_info.distribution in ['debian', 'ubuntu']:
            zabbix_server = host.package(server)
            assert zabbix_server.version.startswith("1:4.4")
        elif host.system_info.distribution == 'centos':
            zabbix_server = host.package(server)
            assert zabbix_server.version.startswith("4.4")
        assert zabbix_server.is_installed


def test_zabbix_server_dot_conf(host):
    zabbix_server_conf = host.file("/etc/zabbix/zabbix_server.conf")
    assert zabbix_server_conf.user == "zabbix"
    assert zabbix_server_conf.group == "zabbix"
    assert zabbix_server_conf.mode == 0o640

    assert zabbix_server_conf.contains("ListenPort=10051")
    assert zabbix_server_conf.contains("DBHost=localhost")
    assert zabbix_server_conf.contains("DebugLevel=3")


def test_zabbix_include_dir(host):
    zabbix_include_dir = host.file("/etc/zabbix/zabbix_server.conf.d")
    assert zabbix_include_dir.is_directory
    assert zabbix_include_dir.user == "zabbix"
    assert zabbix_include_dir.group == "zabbix"
    # assert zabbix_include_dir.mode == 0o644
