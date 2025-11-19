# AI-Mavericks
# Product Trend Tracker

## Project Overview
The Product Trend Tracker is a real-time system that monitors trending products based on simulated user interactions such as views and purchases. It uses streaming infrastructure to process events, stores data for fast lookup, and serves trending product results through a performant API. The system is monitored with Prometheus and Grafana and deployed via a CI/CD pipeline.

## Architecture
The project architecture includes:
- **Producer:** Simulates product events and sends them to Kafka topics.
- **Kafka:** Handles messaging and streaming of events.
- **Consumer:** Validates events and writes to Redis for fast access and object storage for durable batch processing.
- **Model Registry:** Stores event weight models for scoring.
- **Recommender API:** Serves trending product queries.
- **Monitoring:** Uses Prometheus for metrics collection and Grafana for dashboard visualization.
- **CI/CD:** Automates builds, testing, and deployment using GitHub Actions.

An architecture diagram is included in the project documentation.

## Setup & Running

### Prerequisites
- Docker and Docker Compose installed
- Kafka and Redis instances available (Confluent Cloud Kafka or local cluster)
- Object storage access for batch snapshots (e.g., Cloudflare R2)

### Running Locally
1. Clone the repository
git clone <repo-url>
cd product-trend-tracker


2. Build and launch containers
docker-compose up --build


3. Access the API at `http://localhost:8000`

## Repo Structure
product-trend-tracker/
├── docker/
│ ├── api.Dockerfile
│ ├── consumer.Dockerfile
├── service/
│ └── app.py
├── stream/
│ ├── producer.py
│ └── consumer.py
├── model_registry/
│ └── v0.1/model.pkl
├── tests/
│ └── test_service.py
└── README.md


## Testing
- Unit tests live in the `tests/` folder
- Run tests with:


## Monitoring
- Prometheus metrics endpoint exposed
- Grafana dashboards visualize key performance metrics and health checks

## Contributing
- Use feature branches and submit pull requests for review
- Follow team guidelines on code reviews and testing

## License
MIT License

---

For questions or assistance, please contact the project lead.
