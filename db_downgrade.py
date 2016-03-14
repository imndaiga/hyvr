from app import app
from migrate.versioning import api

SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_MIGRATE_REPO=app.config['SQLALCHEMY_MIGRATE_REPO']

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))
