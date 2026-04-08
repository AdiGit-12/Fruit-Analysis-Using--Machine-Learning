# 🍎 Fruit Analysis Using Machine Learning

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-orange.svg)
![Keras](https://img.shields.io/badge/Keras-2.0+-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-06B6D4.svg)

> **High-tech computer vision meets the tactile world of nature.**  
> *Identify fruits, assess ripeness, and unlock deep nutritional insights with a single image.*

🔗 **GitHub Repository**: [AdiGit-12/Fruit-Analysis-Using-Machine-Learning](https://github.com/AdiGit-12/Fruit-Analysis-Using--Machine-Learning.git)

---

## 📌 Project Overview

This project develops an **automated system** that analyzes fruit quality using **machine learning**. It classifies fruit types, detects freshness (fresh/rotten/optimal), and provides storage recommendations — all from a single image. The goal is to reduce food waste and improve supply chain efficiency through intelligent computer vision.

### 🎯 Objectives
- Classify fruit species with high confidence
- Detect freshness levels (Fresh / Optimal / Rotten)
- Provide nutritional insights and storage guidelines
- Reduce post-harvest food waste
- Improve supply chain decision-making

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🍏 **Fruit Classification** | Identifies fruit species (Apple, Banana, Orange, etc.) with confidence score |
| 🟢 **Freshness Detection** | Classifies as Fresh, Optimal, or Rotten |
| 📊 **Confidence Metric** | Displays model prediction confidence (up to 100%) |
| 🧠 **Nutritional Insights** | Provides calorie estimates and freshness curves |
| 📦 **Storage Recommendations** | Suggests optimal storage conditions and freshness span |
| 👨‍💻 **Admin Dashboard** | Manage users, view predictions, and monitor contacts |
| 📧 **Contact System** | Users can send messages for API access and support |
| 🔐 **User Authentication** | Secure login for admin access |

---

## 🧠 Machine Learning Model

### Model Architecture
- **Type**: Convolutional Neural Network (CNN)
- **Framework**: TensorFlow 2.0+ with Keras API
- **Dataset**: 100,000+ augmented images of 50+ fruit variants
- **Accuracy**: 95%+ confidence in fruit classification & freshness detection

### Training Details
```python
# Model architecture summary
- Conv2D layers with ReLU activation
- MaxPooling2D for dimensionality reduction
- Dropout layers to prevent overfitting
- Dense layers for final classification
- Softmax output layer for multi-class prediction
