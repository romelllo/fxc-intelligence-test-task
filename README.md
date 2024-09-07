# Transaction Synchronizer

## Description

This project is a data processing application that integrates PostgreSQL, RabbitMQ, and KeyDB to manage and process financial transactions. The application performs the following tasks:

1. **Database Initialization**: Connects to a PostgreSQL database and initializes necessary data.
2. **Message Handling**: Publishes and consumes messages from RabbitMQ queues.
3. **Data Synchronization**: Updates and synchronizes data in KeyDB based on transactions and initial data from the PostgreSQL database.

## Services

- **PostgreSQL**: A relational database system used for storing initial and historical transaction data.
- **RabbitMQ**: A message broker used for handling transactional messages.
- **KeyDB**: A high-performance key-value store used for caching and quick access to aggregated transaction data.

## Requirements

1. **Python 3.10+**: Ensure Python is installed on your system.
2. **Docker**: Required for containerizing and running the services.

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/romelllo/fxc-intelligence-test-task.git
   cd fxc-intelligence-test-task
   ```

2. **Create and Configure the `.env` File**

   Copy the example environment file and fill in the required values:

   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to include the actual environment variables.  

3. **Build and Run the Services**

   Use Docker Compose to build and start the services:

   ```bash
   docker-compose up --build
   ```

4. **Stopping the Services**

   To stop the services, press `Ctrl+C` in the terminal where Docker Compose is running. This will gracefully shut down all running containers.

5. **Accessing the Services**

   - **PostgreSQL**: Available at `localhost:5432`
   - **RabbitMQ**: Management interface available at `localhost:15672`
   - **KeyDB**: Available at `localhost:6379`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
