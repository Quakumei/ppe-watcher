from system_of_analysis.app.infrastructure.db.database import engine
from system_of_analysis.app.infrastructure.db import models

def init_db():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    init_db()
