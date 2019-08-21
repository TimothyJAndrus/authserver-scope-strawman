
"""PostgreSQL Docker Container.
This class enables users to programmatically stand up and manipulate a PostgreSQL
Docker container for application testing.
"""

import os
import docker


class PostgreSQLContainer(object):
    """ PostgreSQL Container manager.
    This class is responsible for managing the creation and destruction of a PostgreSQL Docker container.
    Attributes:
        docker_client (obj): Reference to the Docker client running on the local system.
        container (obj): Pointer to the Docker container created by the class.
        configuration_type (str): The environment type that the configuration is reqeusted for from ConfigurationFactory
        configuration (obj): Application configuration object based on the configuration_type
        db_environment (list): Environment variables to pass to the PostgreSQL container on creation.
        db_ports (dict): Container port mappings to pass to the PostgreSQL container on creation.
    """

    def __init__(self, config: dict):
        self.postgres_image = config['postgres_image']
        self.container_name = config['container_name']
        self.docker_client = docker.from_env()
        self.container = None
        self.db_environment = [
            'POSTGRES_USER={}'.format(config['postgres_user']),
            'POSTGRES_PASSWORD={}'.format(config['postgres_password']),
            'POSTGRES_DB={}'.format(config['postgres_database'])
        ]
        self.db_ports = {'5432/tcp': config['postgres_port']}

    def start_container(self):
        """Start the application container."""
        self.container = self.docker_client.containers.run(
            self.postgres_image,
            detach=True, auto_remove=True, name=self.container_name, environment=self.db_environment, ports=self.db_ports)

    def stop_container(self):
        """Stop the PostgreSQL container."""
        try:
            if self.container is None:
                self.container = self.docker_client.containers.get(
                    self.container_name)
            self.container.stop()
        except Exception:
            pass
