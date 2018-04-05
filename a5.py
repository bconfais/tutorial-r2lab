import paramiko
import getpass
import socket
import sys
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
  print('rhubarbe exit with status %d' % (status))
 return status


def main():
 ssh_gw, ssh_via, ssh = ssh_init()
 if 0 != lease_check(ssh_gw):
  sys.exit(1)

 for n in ssh:
  stdin, stdout, stderr = n.exec_command('turn-on-data')
 stdin, stdout, stderr = ssh[0].exec_command('ping -c1 -I data data02')
 print(stdout.read())

 for n in ssh:
  n.close()
 ssh_via.close()
 ssh_gw.close()

if '__main__' == __name__:
 main()

