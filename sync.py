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
        self.local_path = "data" # no slash here since this data dir will not be sent
        
        # Function to get MAC address, assuming it's defined elsewhere in your code
        self.mac_address = self.get_mac().replace(":", "")

    def sync(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Assuming you've set up SSH keys for passwordless access
            print(f"Connecting to {self.nas_user}@{self.nas_ip} at port {self.nas_port}")
            client.connect(self.nas_ip, port=self.nas_port, username=self.nas_user, timeout=10)
            # Determine the remote directory path, creating it if necessary
            remote_dir = os.path.join(self.remote_path, self.mac_address, "data")
            if not os.path.isdir(remote_dir):
                print(f"Creating remote directory {remote_dir}")
                stdin, stdout, stderr = client.exec_command(f'mkdir -p {remote_dir}')
                stderr.read()  # Wait for the directory creation command to complete
                print(f"Created {remote_dir}")
            # Use rsync to sync the data directory
            print("Trying to send data via rsync")
            rsync_command = f"rsync -avz {self.local_path}/ {self.nas_user}@{self.nas_ip}:{remote_dir}"
            os.system(rsync_command)
            #scp_command = f"scp -r -P {self.nas_port} {self.local_path}/ {self.nas_user}@{self.nas_ip}:{remote_dir}"
            #print(f"Trying to send data via scp")
            #print(scp_command)
            #os.system(scp_command)
            client.close()
        except Exception as e:
            print(f"An error occurred during data synchronization: {e}")

    def get_mac(self, interface='wlan0'):
        try:
            with open(f'/sys/class/net/{interface}/address') as f:
                mac = f.readline().strip()
        except FileNotFoundError:
            mac = "00:00:00:00:00:00"
        return mac

if __name__ == "__main__":
    import time
    config_path = "secret_db_keys.yaml"  # Path to your YAML configuration file
    data_syncer = DataSyncer(config_path)
    
    while True:
        data_syncer.sync()
        time.sleep(300)  # Sleep for 5 minutes (300 seconds) before the next sync
