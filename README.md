# ThreatHunter-AI (Spring 2025)

### Work in Progress
- Moving over to a browser extension as it feels more sensible for users to start/stop a chrome extension that checks their network traffic, saves it to their local computer for their own analysis if wanted, and if prompted to, will run my ML model on this network traffic file
- Also gives me a chance to remove zombie/useless code!
- docker run command: ```docker run --network=host --privileged backend-test1```

Welcome to the **Cybersecurity Threat-Hunting AI** project! This repository contains the code for a network threat-hunting system. This system proactively identifies cybersecurity threats within your Local-Access-Network (LAN) by analyzing network traffic and predicting safety of the data being transfered in those packets through the usage of my pre-trained model (using AutoGluon). Training data is almost an even split between safe data captured using WireShark on my LAN and network anomalous data where I utilized hping3 to simulate ICMP flood attacks targeting a Windows machine from a Kali Linux machine.

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Installation](#Installation)
- [License](#license)

## Project Overview

This project leverages a pre-trained model to enhance cybersecurity threat detection. The system can proactively hunt for threats by analyzing network traffic patterns and recognizing suspicious behaviors before they become critical. 

The project has a simple design structure for easy scalability and adaptability, and it includes data ingestion, anomaly detection, and visualization components.

## System Architecture

The system is divided into three main components:

1. **Data Processing and Management**: Responsible for data collection, preprocessing, and storage. It aggregates data from sources such as network logs actively scraped through WireShark.
2. **Threat Analysis Engine**: This engine detects anomalies and generates potential threat reports, urging the user to then further investigate due to suspicious activity.
3. **User Interface Control**: Provides a dashboard displaying anomalous/safe packets with real-time metrics.

## Features

- **Real-Time Data Collection**: Ingests data from multiple sources and processes it for analysis.
- **Anomaly Detection**: Uses a pre-trained model to detect deviations from normal network behavior.
- **Threat Hypothesis Generation**: Constructs threat probability scoring.
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

