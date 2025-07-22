# これらすべて(Dockerfile,docker-compose, app scripts)を統括し、config.yaml に基づいてシミュレーション環境を構築・実行する
import yaml
import subprocess
import argparse
import os

def load_config(config_path):
    """Loads the simulation configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_docker_compose(config):
    """Generates the docker-compose.yaml content based on the config."""
    services = {}
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Add Zenoh router services
    for router_config in config.get('zenoh_routers', []):
        router_name = router_config.get('name', 'zenoh-router')
        service = {
            'image': 'eclipse/zenoh-router:latest',
            'container_name': router_name,
            'networks': [config['simulation']['network_name']],
            'volumes': [],
            'command': ''
        }
        # Mount config file if specified　ルータコンテナに設定ファイル (`zenoh-router-config.json5`) をマウントする機能
        if 'config_file' in router_config:
            local_config_path = os.path.join(project_root, router_config['config_file'])
            container_config_path = '/etc/zenoh/zenohd.json5'
            service['volumes'].append(f"{local_config_path}:{container_config_path}:ro")
            service['command'] = f"--config {container_config_path}"
        
        # Add storage volume for caching　プロデューサーコンテナにストリーミング対象のファイル (`SampleJPGImage_5mbmb.jpg` など) をマウントする機能
        if 'storage_path' in router_config:
             local_storage_path = os.path.join(project_root, router_config['storage_path'])
             container_storage_path = '/data/zenoh-storage'
             service['volumes'].append(f"{local_storage_path}:{container_storage_path}")

        services[router_name] = service


    # Add node services
    for node in config.get('nodes', []):
        node_service = {
            'build': {
                'context': '.',
                'dockerfile': 'docker/Dockerfile',
                'args': {
                    'APP_NAME': node['app']
                }
            },
            'container_name': node['name'],
            'environment': {
                'ZENOH_CONNECT': node.get('connect')
            },
            'networks': [config['simulation']['network_name']],
            'depends_on': node.get('depends_on', []),
            'volumes': []
        }

        # Construct command with arguments
        command_parts = [f"python apps/{node['app']}/main.py"]
        if 'args' in node:
            for arg, value in node['args'].items():
                command_parts.append(f"--{arg} {value}")
        node_service['command'] = " ".join(command_parts)

        # Mount volumes for producer's source file and client's output directory
        if 'volumes' in node:
            for volume in node['volumes']:
                local_path = os.path.join(project_root, volume['local'])
                # Ensure local directory exists for output
                if 'output' in volume['container'] and not os.path.exists(local_path):
                    os.makedirs(local_path)
                node_service['volumes'].append(f"{local_path}:{volume['container']}")

        services[node['name']] = node_service

    docker_compose_config = {
        'version': '3.8',
        'networks': {
            config['simulation']['network_name']: {
                'driver': 'bridge',
                'ipam': {
                    'config': [{'subnet': config['simulation']['subnet']}]
                }
            }
        },
        'services': services
    }
    
    return yaml.dump(docker_compose_config)

def run_simulation(config_path):
    """Generates docker-compose.yaml and starts the simulation."""
    config = load_config(config_path)
    docker_compose_content = generate_docker_compose(config)

    compose_file_path = '/home/otogr/icn_ws/zenoh_docker_simulator/docker-compose.yaml'
    with open(compose_file_path, 'w') as f:
        f.write(docker_compose_content)
    
    print("Generated docker-compose.yaml. Starting simulation...")
    
    # Using subprocess.run to execute docker-compose
    try:
        subprocess.run(['docker-compose', '-f', compose_file_path, 'up', '--build'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running docker-compose: {e}")
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        cleanup_simulation(compose_file_path)

def cleanup_simulation(compose_file_path):
    """Stops and removes the simulation containers."""
    print("Cleaning up Docker resources...")
    subprocess.run(['docker-compose', '-f', compose_file_path, 'down', '--volumes'], check=True)
    # os.remove(compose_file_path) # Optionally remove the generated file
    print("Cleanup complete.")


def main():
    parser = argparse.ArgumentParser(description="Zenoh Docker Simulator")
    parser.add_argument(
        '--config', 
        type=str, 
        default='/home/otogr/icn_ws/zenoh_docker_simulator/config.yaml',
        help='Path to the configuration file.'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Stop and clean up the simulation environment.'
    )
    args = parser.parse_args()

    compose_file_path = '/home/otogr/icn_ws/zenoh_docker_simulator/docker-compose.yaml'

    if args.cleanup:
        if os.path.exists(compose_file_path):
            cleanup_simulation(compose_file_path)
        else:
            print("docker-compose.yaml not found. Nothing to clean up.")
    else:
        if not os.path.exists(args.config):
            print(f"Error: Config file not found at {args.config}")
            print("Please create a config.yaml file (you can copy config.yaml.example).")
            return
        run_simulation(args.config)

if __name__ == "__main__":
    main()
