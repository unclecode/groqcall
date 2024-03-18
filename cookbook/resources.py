from phi.docker.app.postgres import PgVectorDb
from phi.docker.resources import DockerResources

# -*- PgVector2 running on port 5432:5432
vector_db = PgVectorDb(
    name="knowledge-db",
    pg_user="ai",
    pg_password="ai",
    pg_database="ai",
    host_port=5532,
)

# -*- DockerResources
dev_docker_resources = DockerResources(apps=[vector_db])
