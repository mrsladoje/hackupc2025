# 🕊️ Peaceful Protest Tracker: Headlines vs Reality

>
> 🏆 **2ND PRIZE WINNER** | [**HACKUPC 2025 - Grafana Challenge**](https://devpost.com/software/peaceful-protest-tracker-headlines-vs-reality) 🏅
> 
[![Built with](https://img.shields.io/badge/Built%20with-❤️%20%26%20Coffee-red)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-6DB33F?logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)](https://mongodb.com)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com)

---

## 🌟 About

Following the tragic Novi Sad railway canopy collapse in November 2024 that claimed 16 lives, widespread student-led protests erupted across Serbia demanding accountability and institutional reform. As conflicting narratives emerged from different media outlets, we were inspired to create a solution that brings transparency to media coverage through real-time data analysis.

**Our mission**: Embody the spirit of UN SDG 16 by promoting peaceful, inclusive societies through transparent information access.

## ✨ What It Does

Our dynamic dashboard presents a comprehensive view of how the protest situation unfolds, powered by near real-time data from both regime-controlled and independent media outlets.

### 🎯 Key Features

- **📍 Live Protest Map**: Semi-real-time visualization of reported protest locations across Serbia
- **💭 Sentiment Analysis**: Track how students and protesters are portrayed across different media
- **🔍 Keyword Analysis**: Compare usage of protest-related terms like "justice" vs. propaganda language
- **📊 Headlines vs Reality**: Direct visualization of narrative contrasts through comparative charts and statistics

## 🏗️ Architecture

Our solution employs an automated pipeline designed to gather, analyze, and visualize protest-related information:

 ![Workflow](https://d112y698adiu2z.cloudfront.net/photos/production/software_photos/003/405/832/datas/original.png)

## 😎 Preview (IT'S A YT LINK CLICK IT :)) )

[![Youtube Preview of Grafana Dashboard](https://img.youtube.com/vi/Eguzdn9z5Ac/maxresdefault.jpg)](https://www.youtube.com/watch?v=Eguzdn9z5Ac)

## 😗 Try it out

[**View the Dashboard**](https://protests.grafana.net/public-dashboards/b2a775b17b8b47b49a215a161b0c9a91)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Java 11+
- MongoDB Atlas account
- Grafana instance
- Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mrsladoje/hackupc2025.git
   cd hackupc2025
   ```

2. **Set up Python environment**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URLs
   ```

4. **Run the Spring Boot backend**
   ```bash
   ./mvnw spring-boot:run
   ```

5. **Access Grafana dashboard**
   - Import dashboard configuration from `grafana/dashboards/`
   - Configure data source to point to your backend API

## 💪 Challenges Overcome

The biggest challenge was designing a complex yet logical system architecture that seamlessly connects diverse technologies. Coordinating web scraping, AI analysis, backend processing, and real-time visualization required careful planning and robust error handling.

## 🏆 What We're Proud Of

- **🎯 Meaningful Impact**: Addressing media bias on a personally important topic
- **⚡ Rapid Development**: Bringing a complex idea to life in 36 hours
- **🚀 Technical Achievement**: Successfully integrating multiple cutting-edge technologies
- **📚 Learning Journey**: Mastering Grafana and web scraping from scratch

## 📚 What We've Learned

This project was a crash course in:
- **Data Visualization** with Grafana
- **Web Scraping** techniques and best practices  
- **AI Integration** for content analysis
- **System Architecture** for real-time data pipelines
- **Team Collaboration** under time pressure

*Turns out sleep deprivation and potato chips can fuel incredible innovation! 🥔*

## 🤝 Contributing

We welcome contributions! Whether it's bug fixes, feature additions, or documentation improvements, every contribution helps make information more accessible.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The brave students of Serbia fighting for transparency and justice

---

<div align="center">

**Built with ❤️ for transparency, accountability, and peaceful change**

[🌟 Star this repo](https://github.com/mrsladoje/hackupc2025) | [🐛 Report Bug](https://github.com/mrsladoje/hackupc2025/issues) | [💡 Request Feature](https://github.com/mrsladoje/hackupc2025/issues)

</div>
