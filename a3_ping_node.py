import paramiko
import getpass
import socket
from contextlib import closing

def find_free_port():
 with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
  s.bind(('localhost', 0))
  return s.getsockname()[1]

keyfile = "/home/bastien/.ssh/id_rsa_grid5k"
slice = "inria_school"
gateway = "faraday.inria.fr"
node = 'fit01'
password =  getpass.getpass()

ssh_key = paramiko.RSAKey.from_private_key_file(keyfile, password=password);
ssh_gateway = paramiko.SSHClient()
ssh_gateway.set_missing_host_key_policy(paramiko.AutoAddPolicy());
ssh_gateway.connect(hostname=gateway, username=slice, pkey=ssh_key);

transport = ssh_gateway.get_transport()
port = find_free_port()
channel = transport.open_channel('direct-tcpip', (node, 22), ('127.0.0.1', port))

ssh = paramiko.SSHClient();
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
ssh.connect(hostname='127.0.0.1', port=port, username='root', password='', sock=channel)
stdin, stdout, stderr = ssh.exec_command('ping -c1 google.fr');

print(stdout.read())
print(stderr.read())
