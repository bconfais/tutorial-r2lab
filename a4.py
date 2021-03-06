import paramiko
import getpass
import socket
import sys
from contextlib import closing

keyfile = "/home/bastien/.ssh/id_rsa_grid5k"
slice = "inria_school"
gateway = "faraday.inria.fr"
node = 'fit01'
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

 ssh_via = paramiko.SSHClient()
 ssh_via.set_missing_host_key_policy(paramiko.AutoAddPolicy());
 ssh_via.connect(hostname=gateway, username=slice, pkey=ssh_key);

 transport = ssh_via.get_transport()
 port = find_free_port()
 channel = transport.open_channel('direct-tcpip', (node, 22), ('127.0.0.1', port))

 ssh = paramiko.SSHClient();
 ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
 ssh.connect(hostname='127.0.0.1', port=port, username='root', password='', sock=channel)
 return ssh_gateway, ssh_via, ssh

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

 stdin, stdout, stderr = ssh.exec_command('ping -c1 google.fr');
 print(stdout.read())


 ssh.close()
 ssh_via.close()
 ssh_gw.close()

if '__main__' == __name__:
 main()

