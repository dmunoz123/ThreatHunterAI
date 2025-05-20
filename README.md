# ThreatHunter-AI (Spring 2025)

Welcome to the **Cybersecurity Threat-Hunting AI** project! This repository contains the code and documentation for a machine learning and neural network-based threat-hunting system. This system proactively identifies cybersecurity threats within a network environment by analyzing network traffic, user behavior, and threat intelligence feeds. By combining traditional machine learning techniques with neural networks, the system aims to detect both known and novel threats in real time.

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Installation](#installation)
- [License](#license)

## Project Overview

Cyber threats are increasingly complex, and traditional cybersecurity measures alone often fall short. This project leverages a hybrid approach, combining machine learning (ML) and deep learning models, to enhance cybersecurity threat detection. The system can proactively hunt for threats by analyzing network traffic patterns and recognizing suspicious behaviors before they become critical. 

The project uses a layered, modular design for easy scalability and adaptability, and it includes data ingestion, anomaly detection, contextual analysis, and visualization components.

## System Architecture

The system is divided into three main components:

1. **Data Processing and Management**: Responsible for data collection, preprocessing, and storage. It aggregates data from sources such as network logs and threat intelligence feeds.
2. **Threat Analysis Engine**: Combines traditional ML models for anomaly detection with neural network models for context-based threat analysis. This engine detects anomalies and generates potential threat scenarios.
3. **User Interface Control**: Provides an interactive dashboard with real-time alerts, metrics, and data visualizations for cybersecurity analysts.

## Features

- **Real-Time Data Collection**: Ingests data from multiple sources and processes it for analysis.
- **Anomaly Detection**: Uses machine learning to detect deviations from normal network behavior.
- **Contextual Analysis**: Applies neural networks to evaluate anomalies within broader contexts.
- **Threat Hypothesis Generation**: Constructs potential threat scenarios with probability scoring.
- **Interactive Dashboard**: Displays real-time alerts and threat insights for analysts.

## Installation/Starting Up

- Open up your command prompt/terminal and make sure/navigate to the right location (the root directory of this project)


#### Backend Server
- First we need to setup our python virtual environment to locally install all of the necessary packages for this project!
``` 
   python -m venv .venv 
```

- Now that we have that setup we can begin installing our packages by running:
``` 
   pip install -r requirements.txt 
```

- Our backend is all setup for the code to recieve the correct packages, now we just navigate into our backend folder and boot up the server!
```
   cd backend
   python main.py 
```

#### Frontend Server
- For our frontend we do things a little different. First we navigate into our frontend folder as such:
``` 
   cd frontend 
```

- Now that we are at the correct location we can install all of our required packages for the frontend code:
```
   npm install
```

- And now that we have all of our frontend packages setup we can start the server and navigate over to the hosted location of the application, as directed in the command prompt (typically localhost:5173)
```
npm run frontend
```

## License

This project is licensed under the MIT License 

