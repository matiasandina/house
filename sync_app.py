import dash
from dash import html
from dash import dcc, html, Input, Output
import pandas as pd
import datetime
import os
import glob
import paramiko
import datetime
from py_console import console
import pprint
import yaml

app = dash.Dash(__name__)

def read_secret_keys(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def convert_c_to_f(celsius):
    return (celsius * 9/5) + 32

def read_last_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return lines[-1]

def get_latest_data(base_path):
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    data = {}
    target_path = f"{base_path}/*/data/{today}"
    console.info(f"Searching target path {target_path}")
    for path in glob.glob(target_path):
        print(path)
        mac = path.split('/')[-5]
        temp_hum_path = os.path.join(path, "temp_hum.csv")
        lux_path = os.path.join(path, "lux.csv")
        temp_hum_last_line = read_last_line(temp_hum_path)
        lux_last_line = read_last_line(lux_path)
        _, temp, hum = temp_hum_last_line.strip().split(',')
        _, lux = lux_last_line.strip().split(',')
        data[mac] = {"temp": float(temp), "hum": float(hum), "lux": int(lux)}
    return data

def generate_table(data, box_mapping):
    entries_with_names = []
    for mac, details in data.items():
        box_name = next((name for name, address in box_mapping.items() if address == mac), 'Unknown Box')
        entries_with_names.append((box_name, mac, details))

    # Sort this list by box_name
    entries_with_names.sort(key=lambda x: x[0])

    # Then generate rows using the sorted list
    rows = []
    for index, (box_name, mac, details) in enumerate(entries_with_names):
        row_style = {'backgroundColor': '#FFFFFF'} if index % 2 == 0 else {'backgroundColor': '#F2F2F2'}
        temp_f = round(convert_c_to_f(details['temp']), 1)
        rows.append(html.Tr([
            html.Td(box_name),
            html.Td(details['timestamp'].replace(microsecond = 0).time()),
            html.Td(mac),
            html.Td(details['temp']),
            html.Td(temp_f),
            html.Td(details['hum']),
            html.Td(details['lux'])
        ], style=row_style))
    return html.Table([
        html.Thead(html.Tr([
    html.Th('Box Name', style={'textAlign': 'left', 'borderBottom': '1px solid black'}),
    html.Th("Last Update", style={'textAlign': 'left', 'borderBottom': '1px solid black'}),
    html.Th('MAC Address', style={'textAlign': 'left', 'borderBottom': '1px solid black'}),
    html.Th('Temperature (°C)', style={'textAlign': 'left', 'borderBottom': '1px solid black'}),
    html.Th('Temperature (°F)', style={'textAlign': 'left', 'borderBottom': '1px solid black'}),
    html.Th('Humidity (%)', style={'textAlign': 'left', 'borderBottom': '1px solid black'}),
    html.Th('Lux', style={'textAlign': 'left', 'borderBottom': '1px solid black'})
    ])),
        html.Tbody(rows),
    ], style={'fontSize': '25px', 'borderCollapse': 'collapse', 'width': '50%'},
       className='table-striped table-hover')



def fetch_nas_data(nas_ip, nas_port, username, password, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(nas_ip, port=nas_port, username=username, password=password)
    
    # Step 2: List folders in remote_path
    stdin, stdout, stderr = client.exec_command(f"ls {remote_path}")
    mac_folders = stdout.read().decode().splitlines()
    
    data = {}
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    
    # Step 3 & 4: For each folder, build path for today's data and request the tail of CSVs
    for mac in mac_folders:
        print(f"[{datetime.datetime.now()}] Fetching Data for mac {mac}")
        temp_hum_path = f"{remote_path}/{mac}/data/{today}/temp_hum.csv"
        lux_path = f"{remote_path}/{mac}/data/{today}/lux.csv"
        #print(temp_hum_path)
        #print(lux_path)
        # Fetch last line of temp_hum.csv
        # Fetch last line of temp_hum.csv
        stdin, stdout, stderr = client.exec_command(f"tail -n 1 {temp_hum_path}")
        temp_hum_last_line = stdout.read().decode().strip()  # Read once and store
        console.success(f"Fetched {temp_hum_path}")
        console.info(f"Got {temp_hum_last_line}")  # Use the stored result
        timestamp, temp, hum = temp_hum_last_line.split(",")  # Split the stored result
        # Fetch last line of lux.csv
        stdin, stdout, stderr = client.exec_command(f"tail -n 1 {lux_path}")
        lux_last_line = stdout.read().decode().strip()
        console.success(f"Fetched {lux_path}")
        console.info(f"Got {lux_last_line}")
        _, lux = lux_last_line.split(",") 
        data[mac] = {
            "timestamp": datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f'),
            "temp": round(float(temp), 1),
            "hum": round(float(hum), 1),
            "lux": round(float(lux), 1)
        }
    
    client.close()
    return data

@app.callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    # READING SECRET KEYS FOR CONFIGS
    # it might not be as efficient to read this every time, but it will work for now
    config = read_secret_keys('secret_db_keys.yaml')
    box_mapping = config['macs']
    nas_ip = config['nas']['ip']
    nas_port = config['nas']['port']
    nas_user = config['nas']['user']
    nas_password = config['nas']['password']
    remote_path = config['nas']['remote_path']
    data = fetch_nas_data(nas_ip=nas_ip, nas_port=nas_port, username=nas_user, password=nas_password, remote_path=remote_path)
    pprint.PrettyPrinter(depth=4).pprint(data)
    return [generate_table(data, box_mapping)]

app.layout = html.Div([
    html.H1('Sensor Data Dashboard'),
    html.Div(id='live-update-text'),
    dcc.Interval(
        id='interval-component',
        interval=1*60000,  # in milliseconds
        n_intervals=0
    )
])

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')