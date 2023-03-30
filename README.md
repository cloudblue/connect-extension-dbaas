# DBaaS Extension
On-demand provisioning of cloud-based database storages as a service.

## Configuration
1. Publicly visible MongoDB Cluster (!) shall be created with at least one DB and at least one User with read and write access to the created DB.
2. Extension with the environment, based on this repository, shall be created within the Connect platform.
3. Environment variables (keys with explanations can be seen in `dbaas.database.DBEnvVar`) shall be filled to provide access to the MongoDB storage.
4. Regions collection shall be filled with at least one region via Regions API, described in the API Specification section of the Extension environment (ApiKey can be obtained in the Integrations module of the Connect platform).

## License
**DBaaS Extension** is licensed under the *Apache Software License 2.0* license.
