import json
import psycopg2
import requests
import paramiko

# Function to read parameters from JSON configuration file
def read_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

# Function to connect to the PostgreSQL database
def connect_to_postgres(host, port, user, password, dbname):
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=dbname,
        port=port
    )
    return conn


# Function to connect to the PostgreSQL database via SSH tunnel
def connect_to_postgres_by_ssh(host, port, user, password, dbname, enable_ssh, ssh_host, ssh_port, ssh_user, ssh_password=None, ssh_pem_key=None):
    # Establish SSH connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Use password authentication if ssh_password is provided
    if ssh_password:
        ssh_client.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
    elif ssh_pem_key:
        ssh_key = paramiko.RSAKey.from_private_key_file(ssh_pem_key)
        ssh_client.connect(ssh_host, port=ssh_port, username=ssh_user, pkey=ssh_key)
    else:
        raise ValueError("Either ssh_password or ssh_pem_key must be provided.")

    # Forward local port to remote PostgreSQL server
    local_port = 5433  # Choose any available local port
    ssh_transport = ssh_client.get_transport()
    ssh_transport.request_port_forward('', local_port)
    print('SSH tunnel connected successfully')
    # Connect to PostgreSQL via forwarded port
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=dbname,
        port=port)
    return conn

# Function to get a list of tables/views from the specified schema
def get_layers_name(conn, schema):
    layers_name = []
    cursor = conn.cursor()
    cursor.execute(f"SELECT table_name FROM information_schema.columns WHERE column_name ='geom' and table_schema ='{schema}'")
    layers_name.extend(cursor.fetchall())
    cursor.close()
    return layers_name

# Function to check if layer exists in GeoServer
def layer_exists(host, port, user, password, workspace, datastore, layer_name):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores/{datastore}/featuretypes/{layer_name}"
    response = requests.get(url, auth=(user, password))
    return response.status_code == 200

# Function to create layer in GeoServer
def create_layer(host, port, user, password, workspace, datastore, layer_name):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores/{datastore}/featuretypes"
    headers = {'Content-Type': 'application/json'}
    auth = (user, password)
    data = {
        "featureType": {
            "name": layer_name,
            "nativeName": layer_name,
            "title": layer_name,
            "enabled": True
        }
    }
    response = requests.post(url, json=data, headers=headers, auth=auth)
    return response.status_code == 201

# Function to check if workspace exists in GeoServer
def workspace_exists(host, port, user, password, workspace):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}"
    response = requests.get(url, auth=(user, password))
    return response.status_code == 200

# Function to create workspace in GeoServer
def create_workspace(host, port, user, password, workspace):
    url = f"http://{host}:{port}/geoserver/rest/workspaces"
    headers = {'Content-Type': 'application/xml'}
    data = f"<workspace><name>{workspace}</name></workspace>"
    response = requests.post(url, data=data, headers=headers, auth=(user, password))
    return response.status_code == 201

# Function to check if store exists in GeoServer
def store_exists(host, port, user, password, workspace, store_name):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores/{store_name}"
    response = requests.get(url, auth=(user, password))
    return response.status_code == 200

def create_store(host, port, user, password, workspace, store_name, dbhost, dbname, dbuser, dbpass, dbport):
    url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores"
    headers = {'Content-Type': 'application/json'}

    # Create dictionary representing the data
    data = {
                "dataStore": {
                "name": store_name,
                "type": "PostGIS",
                "enabled": True,
                "connectionParameters": {
                    "host": dbhost,
                    "port": dbport,
                    "database": dbname,
                    "user": dbuser,
                    "passwd": dbpass,
                    "dbtype": "postgis",
                    "schema": store_name,
                    "max connections": 10,
                    "min connections": 1,
                    "Evictor run periodicity": 300,
                    "Loose bbox": True,
                    "SSL mode": "DISABLE",
                    "Estimated extends": True,
                    "fetch size": 1000,
                    "preparedStatements": False,
                    "Batch insert size": 1,
                    "encode functions": True,
                    "Max open prepared statements": 50,
                    "Expose primary keys": True,
                    "validate connections": True,
                    "Support on the fly geometry simplification": True,
                    "Connection timeout": 20,
                    "Method used to simplify geometries": "FAST",
                    "Evictor tests per run": 3,
                    "Test while idle": True,
                    "Max connection idle time": 300
                }
            }
    }

    # Convert dictionary to JSON string
    json_data = json.dumps(data)

    # Send POST request with JSON data
    response = requests.post(url, data=json_data, headers=headers, auth=(user, password))
    
    if response.status_code != 201:
        print(response.content)
    else:
        return response.status_code == 201

# Function to publish layers to GeoServer
def publish_to_geoserver(host, port, user, password, workspace, datastore, table_name):
    if not layer_exists(host, port, user, password, workspace, datastore, table_name):
        url = f"http://{host}:{port}/geoserver/rest/workspaces/{workspace}/datastores/{datastore}/featuretypes"
        headers = {'Content-Type': 'application/json'}
        auth = (user, password)
        data = {
            "featureType": {
                "name": table_name,
                "nativeName": table_name,
                "title": table_name,
                "enabled": True
            }
        }
        response = requests.post(url, json=data, headers=headers, auth=auth)
        if response.status_code == 201:
            print(f"Layer '{table_name}' published successfully to GeoServer.")
        else:
            print(f"Failed to publish layer '{table_name}' to GeoServer. Error: {response.text}")
    else:
        print(f"Layer '{table_name}' already exists in GeoServer.")

# Main function
def main():
    # Read parameters from configuration file
    config = read_config('config.json')
    postgresql_config = config['postgresql']
    geoserver_config = config['geoserver']
    schemas = config['schemas']
    workspace = postgresql_config['dbname']  # Workspace name is set to dbname
    ssh_config = config['ssh']
    
    if ssh_config['enable_ssh']:
        conn = connect_to_postgres_by_ssh(**postgresql_config, **ssh_config)
    else:
        # Connect to PostgreSQL
        conn = connect_to_postgres(**postgresql_config)
    
    if conn:
        print("DB connected successfully")
    else:
        print("Can't connect to DB")
        return
    
    # Check if workspace exists, if not, create it
    if not workspace_exists(**geoserver_config, workspace=workspace):
        if create_workspace(**geoserver_config, workspace=workspace):
            print(f"Workspace '{workspace}' created successfully.")
        else:
            print(f"Failed to create workspace '{workspace}'.")
            return
    
    # Get tables/views from specified schema
    for schema in schemas:
        tables = get_layers_name(conn, schema)
    
        # Publish each table/view to GeoServer
        for table in tables:
            table_name = table[0]
            store_name = schema  # Store name is set to schema name
            # Check if store exists, if not, create it
            if not store_exists(**geoserver_config, workspace=workspace, store_name=store_name):
                if create_store(**geoserver_config, workspace=workspace, store_name=store_name,dbhost=postgresql_config['host'], dbname=postgresql_config['dbname'], dbuser=postgresql_config['user'] , dbpass=postgresql_config['password'], dbport=postgresql_config['port']):
                    print(f"Datastore '{store_name}' created successfully.")
                else:
                    print(f"Failed to create datastore '{store_name}'.")
                    continue
            
            # Publish layer to GeoServer
            publish_to_geoserver(**geoserver_config, workspace=workspace, datastore=store_name, table_name=table_name)
    
    # Close PostgreSQL connection
    conn.close()
    print("Script Finished")

if __name__ == "__main__":
    main()
