import paramiko
import getpass

keyfile = "/home/bastien/.ssh/id_rsa_grid5k"
slice = "inria_school"
host = "faraday.inria.fr"
password =  getpass.getpass()

ssh_key = paramiko.RSAKey.from_private_key_file(keyfile, password=password);
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy());
ssh.connect(hostname=host, username=slice, pkey=ssh_key);
stdin, stdout, stderr = ssh.exec_command('ping -c1 google.fr');
print(stdout.read())
print(stderr.read())
