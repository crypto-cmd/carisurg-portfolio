# Custom Surgical Grasper with Integrated Sensing V0.0.1-alpha

Custom Surgical Grasper Research Project Portfolio as a scholar of the CariSurg program in partnership with the University of Leeds, STORM Lab, under the supervision of PhD Student Charles (Charlie) DeLorey.

## 🎯 Objective
To engineer a proof-of-concept snap-on sensor module integrating near-infrared (NIR) transillumination and tetrapolar bioimpedance for real-time vascular detection and tissue classification in robot-assisted minimally invasive surgery (RMIS).

## 📖 Overview
In robot-assisted minimally invasive surgery, surgeons lack tactile feedback (haptics) and sub-surface anatomical awareness. This project bridges that sensory gap.

Designed specifically for the da Vinci Cadiere Forceps (parallel-action), this repository houses the firmware, signal processing pipeline, and backend dashboard for a custom snap-on sensor end-effector. The system allows a surgeon to "see" hidden blood vessels and "feel" tissue composition (cancerous vs. normal) _without_ altering the instrument's 8mm trocar clearance or modifying the extremely expensive native surgical hardware.

## 👥 Who This Is For
* **Medical Roboticists & Biomedical Engineers:** Looking for open-source reference architectures for integrating multimodal flexible printed circuits (FPCs) into highly constrained kinematic mechanisms.
* **Engineering Students:** Looking for a guide on the journey of attempting to create sensor feedback in a highly constrained footprint.

## 🛠️ Tech Stack
* **Hardware:** Custom FPC design, 3D Printed SLA Resin
* **Firmware:** C++ (32-bit MCU)
* **Backend:** Python

## 📂 Repository Structure

* `/data` — All datasets used for any ML training.
* `/docs` — Written documentation and other artifacts produced during research, including the proposal and draft literature reviews.
* `/notebooks` — Jupyter notebooks containing code to test experimental ideas derived from literature reviews.
* `/hardware` — 3D-printable `.stl` files for the snap-on resin clips and Gerber files for the Y-shaped Polyimide Flexible Printed Circuit (FPC).
* `/firmware` — C++ code for the 32-bit MCU handling the optical transimpedance amplifiers, PWM LED intensity adaptation loop, and impedance sweeps.
* `/backend` — REST API code that processes incoming serial data streams, runs noise-rejection algorithms, and executes the tissue classification logic.
* `/dashboard` — A frontend application for live clinical data visualization.

## 🫱🏼‍🫲🏿 Contributing & Contact
This project is developed solely as a proof-of-concept for graduate-level research. If you are a researcher or engineer looking to collaborate on minimally invasive sensor integration, feel free to open an issue, submit a pull request, or message me directly.

* **Researcher:** Orville Daley
* **Contact:** [linkedin.com/in/orvilledaley](https://linkedin.com/in/orvilledaley)
* **Supervisor:** Charles (Charlie) DeLorey

> [!WARNING]
> Disclaimer: This repository contains experimental designs and code. It is not FDA-approved and is strictly for research and portfolio demonstration purposes. 
> Do NOT use in clinical settings.
