import os
import paramiko
import yaml

class DataSyncer:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.nas_ip = self.config['nas']['ip']
        self.nas_port = self.config['nas']['port']
        self.nas_user = self.config['nas']['user']
        self.remote_path = self.config['nas']['remote_path']
        self.local_path = "data"
        
        # Function to get MAC address, assuming it's defined elsewhere in your code
        self.mac_address = self.get_mac().replace(":", "")

    def sync(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Assuming you've set up SSH keys for passwordless access
        client.connect(self.nas_ip, port=self.nas_port, username=self.nas_user)
        
        # Determine the remote directory path, creating it if necessary
        remote_dir = os.path.join(self.remote_path, self.mac_address, "data")
        stdin, stdout, stderr = client.exec_command(f'mkdir -p {remote_dir}')
        stderr.read()  # Wait for the directory creation command to complete
        
        # Use rsync to sync the data directory
        rsync_command = f"rsync -avz -e 'ssh -p {self.nas_port}' {self.local_path}/ {self.nas_user}@{self.nas_ip}:{remote_dir}"
        os.system(rsync_command)

        client.close()

    def get_mac(self, interface='wlan0'):
        try:
            with open(f'/sys/class/net/{interface}/address') as f:
                mac = f.readline().strip()
        except FileNotFoundError:
            mac = "00:00:00:00:00:00"
        return mac

if __name__ == "__main__":
    import time
    config_path = "db_keys.yaml"  # Path to your YAML configuration file
    data_syncer = DataSyncer(config_path)
    
    while True:
        data_syncer.sync()
        time.sleep(300)  # Sleep for 5 minutes (300 seconds) before the next sync