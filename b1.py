import paramiko
import getpass
import socket
import sys
import time
from contextlib import closing

keyfile = "/home/bastien/.ssh/id_rsa_grid5k"
slice = "inria_school"
gateway = "faraday.inria.fr"
nodes = ['fit01', 'fit19']
password =  getpass.getpass()

def find_free_port():
 with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
  s.bind(('localhost', 0))
  return s.getsockname()[1]

def ssh_init():
 ssh_key = paramiko.RSAKey.from_private_key_file(keyfile, password=password);

 ssh_gateway = paramiko.SSHClient()
 ssh_gateway.set_missing_host_key_policy(paramiko.AutoAddPolicy());
 ssh_gateway.connect(hostname=gateway, username=slice, pkey=ssh_key);

 sshs = []
 ssh_via = paramiko.SSHClient()
 ssh_via.set_missing_host_key_policy(paramiko.AutoAddPolicy());
 ssh_via.connect(hostname=gateway, username=slice, pkey=ssh_key);

 for node in nodes:

  transport = ssh_via.get_transport()
  port = find_free_port()
  channel = transport.open_channel('direct-tcpip', (node, 22), ('127.0.0.1', port))

  ssh = paramiko.SSHClient();
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
  ssh.connect(hostname='127.0.0.1', port=port, username='root', password='', sock=channel)

  sshs.append(ssh)

 return ssh_gateway, ssh_via, sshs

def lease_check(ssh_gw):
 stdin, stdout, stderr = ssh_gw.exec_command('rhubarbe leases --check');
 print(stdout.read())
 status = stdout.channel.recv_exit_status()
 if status != 0:
  print('rhubarbe exited with status %d' % (status))
 return status


def turn_on_wireless(ssh, driver, ifname, netname, freq, addr, cidr):
 commands = [
  'source /etc/profile.d/nodes.sh',
  'git-pull-r2lab',
  'turn-off-wireless',
  'modprobe %s' % (driver),
  'sleep 1',
  'ip addr flush dev %s' % (ifname),
  'ip link set down dev %s' % (ifname),
  'iw dev %s set type ibss' % (ifname),
  'ip link set up dev %s' % (ifname),
  'iw dev %s ibss join %s %d' % (ifname, netname, freq),
  'ip addr add %s/%d dev %s' % (addr,cidr,ifname)
 ]
 for c in commands:
  stdin, stdout, stderr = ssh.exec_command(c)
  status = stdout.channel.recv_exit_status()
  if status != 0:
   print('%s exited with status %d' % (c, status))

def main():
 ssh_gw, ssh_via, ssh = ssh_init()
 if 0 != lease_check(ssh_gw):
  sys.exit(1)

 turn_on_wireless(ssh[0], 'ath9k', 'atheros', 'mynetworkname', 2412, '10.0.0.1', 24);
 turn_on_wireless(ssh[1], 'ath9k', 'atheros', 'mynetworkname', 2412, '10.0.0.2', 24);

 time.sleep(10)
 stdin, stdout, stderr = ssh[0].exec_command('ping -c20 -I atheros 10.0.0.2')
 print(stdout.read())

 for n in ssh:
  n.close()
 ssh_via.close()
 ssh_gw.close()

if '__main__' == __name__:
 main()

