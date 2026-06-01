"""
test_mdu_registry.py — Unit Tests for MDU Registry FastAPI Router

Verifies live health polling, failure simulations, dataset catalog listings,
ingestion lineage mappings, administrative lifecycle actions, state reconciliation,
and schema mismatch (TANTRA) validations.

Run with: pytest backend/tests/test_mdu_registry.py -v
"""

import pytest
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

# Add parent directory to path to ensure proper module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.routers.mdu_registry import router as mdu_router
from app.core.database import get_db

@pytest.fixture(scope="module")
def mock_db():
    # Create a simple mock session for DB query isolation
    session = MagicMock(spec=Session)
    
    # Mock profile and database query return values for reconciliation tests
    mock_query = MagicMock()
    mock_query.count.return_value = 5
    mock_query.all.return_value = []
    
    session.query.return_value = mock_query
    return session

@pytest.fixture(scope="module")
def client(mock_db):
    # Use isolated FastAPI app for ultra-fast, dependency-free router unit testing
    app = FastAPI()
    
    # Dependency override for database session
    app.dependency_overrides[get_db] = lambda: mock_db
    
    app.include_router(mdu_router, prefix="/api/v1")
    yield TestClient(app)

class TestMduRegistryRouter:
    """Test Suite for MDU Registry Router API"""

    def test_get_mdu_health(self, client):
        """Test health diagnostics and components response"""
        response = client.get("/api/v1/mdu/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Healthy"
        assert "sqlite_relational_database" in data["components"]
        assert "chromadb_vector_store" in data["components"]
        assert data["diagnostics"]["sqlite_write_locks_active"] == 0

    def test_simulate_failure_states(self, client):
        """Test failure simulation toggling and graceful rejections"""
        # Enable failure simulation
        response = client.post("/api/v1/mdu/simulate-failure?enable=true")
        assert response.status_code == 200
        assert response.json()["simulated_failure_active"] is True

        # Health endpoint should now return 500 error
        response = client.get("/api/v1/mdu/health")
        assert response.status_code == 500
        assert "SIMULATED FAILURE" in response.json()["detail"]

        # Restore health endpoint
        response = client.post("/api/v1/mdu/simulate-failure?enable=false")
        assert response.status_code == 200
        assert response.json()["simulated_failure_active"] is False

        # Health should be 200 OK again
        response = client.get("/api/v1/mdu/health")
        assert response.status_code == 200

    def test_get_datasets_list(self, client):
        """Test ingested curriculum catalog listing and queries"""
        response = client.get("/api/v1/mdu/datasets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        # Verify specific datasets exist in the catalog
        codes = [d["textbook_code"] for d in data]
        assert "NCERT-S10-EN" in codes
        assert "MSB-S10-MR" in codes

    def test_get_datasets_search_filter(self, client):
        """Test dataset search querying"""
        response = client.get("/api/v1/mdu/datasets", params={"search": "Balbharati"})
        assert response.status_code == 200
        data = response.json()
        for d in data:
            assert "balbharati" in d["canonical_name"].lower()

    def test_get_dataset_lineage(self, client):
        """Test horizontal lineage map retrieval"""
        response = client.get("/api/v1/mdu/lineage/NCERT-S10-EN")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "links" in data
        assert data["nodes"][0]["id"] == "src"
        assert "NCERT" in data["nodes"][0]["label"]

    def test_get_dataset_lineage_not_found(self, client):
        """Test non-existent lineage error handling"""
        response = client.get("/api/v1/mdu/lineage/NONEXISTENT-DATASET")
        assert response.status_code == 404
        assert "could not be located" in response.json()["detail"]

    def test_lifecycle_administrative_actions(self, client):
        """Test schema transition rules and provenance updates"""
        payload = {
            "dataset_id": "MSB-S9-EN",
            "action": "ACTIVATE",
            "operator": "Soham Kotkar (Lead)"
        }
        response = client.post("/api/v1/mdu/lifecycle/action", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["updated_state"] == "ACTIVE"

        # Verify dataset state updated in catalog
        response = client.get("/api/v1/mdu/datasets")
        for d in response.json():
            if d["id"] == "MSB-S9-EN":
                assert d["status"] == "ACTIVE"

    def test_lifecycle_action_validation_fails(self, client):
        """Test invalid lifecycle action error handling"""
        payload = {
            "dataset_id": "MSB-S9-EN",
            "action": "INVALID_ACTION",
            "operator": "Soham"
        }
        response = client.post("/api/v1/mdu/lifecycle/action", json=payload)
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"]

    def test_get_provenance_logs(self, client):
        """Test cryptographic provenance logs listing"""
        response = client.get("/api/v1/mdu/provenance")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "hash" in data[0]
        assert "operator" in data[0]

    def test_mdu_state_reconciliation(self, client):
        """Test profile storage and registry reconciliation pathway"""
        response = client.post("/api/v1/mdu/reconcile")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "RECONCILED"
        assert len(data["reconciliation_trace"]) > 0
        assert "profiles" in data["reconciliation_trace"][0]["description"]

    def test_schema_mismatch_422(self, client):
        """Test schema payload validator blocking (422)"""
        # Payload lacks required keys 'user_id' and 'sequence'
        payload = {
            "registry": "prana.event.contracts",
            "event_type": "task_submit",
            "version": "1.0.0",
            "payload": {
                "title": "Bad payload missing user and sequence fields"
            }
        }
        response = client.post("/api/v1/mdu/schema-mismatch", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["reason"] == "payload_schema_invalid"
        assert "user_id" in [item["field"] for item in data["detail"]["details"]]

    def test_schema_version_409(self, client):
        """Test schema version verification check rejection (409)"""
        payload = {
            "registry": "prana.event.contracts",
            "event_type": "integrity_probe",
            "version": "2.0.0", # Version mismatch - only 1.0.0 is registered
            "payload": {
                "sequence": 1,
                "route": "test",
                "user_id": "user-1"
            }
        }
        response = client.post("/api/v1/mdu/schema-mismatch", json=payload)
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["reason"] == "version_mismatch"
        assert "1.0.0" in data["detail"]["expected_versions"]
