# 🚀 TEPIS - Trip and Event Planning Integration System

<div align="center">

![TEPIS Logo](https://img.shields.io/badge/TEPIS-🎯%20Event%20to%20Adventure-purple?style=for-the-badge)

**Transform Events Into Epic Adventures**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-brightgreen?style=flat-square&logo=mongodb)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=flat-square&logo=docker)](https://docker.com)
[![AI Powered](https://img.shields.io/badge/AI-Powered%20by%20Mistral%207B-orange?style=flat-square)](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
[![AWS](https://img.shields.io/badge/AWS-Cloud%20Deployed-yellow?style=flat-square&logo=amazon-aws)](https://aws.amazon.com)

[🌟 Live Demo](#) • [📖 Documentation](PROJECT_REPORT.md) • [🐛 Report Bug](#) • [💡 Request Feature](#)

</div>

---

## 🌟 What is TEPIS?

TEPIS is a revolutionary travel platform that bridges the gap between event discovery and comprehensive trip planning. Instead of just booking event tickets, users get AI-powered, personalized travel itineraries that transform a simple event into an unforgettable adventure.

### ✨ Key Features

🎯 **Smart Event Discovery**
- Curated global events across music, sports, culture, and more
- Advanced filtering by category, location, price, and preferences
- Real-time search with intelligent matching

🤖 **AI-Powered Trip Planning**
- **5 Specialized AI Agents** working together
- Personalized hotel recommendations
- Curated restaurant suggestions
- Day-by-day activity itineraries
- Real-time weather integration
- Comprehensive transportation guides

🌍 **Comprehensive Travel Experience**
- End-to-end trip planning from arrival to departure
- Local insights and cultural recommendations
- Budget-aware suggestions (Budget → Premium → Luxury)
- Mobile-responsive design for planning on the go

---

## 🚀 Live in Action

### 🏠 **Discover Events**
Browse thousands of curated events worldwide with intelligent filtering and search capabilities.

### 🎨 **Plan Your Adventure**
Select preferences and watch our AI agents create your perfect itinerary in real-time.

### 🗺️ **Complete Itinerary**
Get hotels, restaurants, activities, transportation, and weather - all tailored to your event and preferences.

---

## 🛠️ Technical Architecture

### 🏗️ **System Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Interface│    │   Flask Backend │    │   MongoDB Atlas │
│   (Responsive)  │◄──►│   (Python 3.9) │◄──►│   (Event Data)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │    AI Agent Hub     │
                    │  🏨 🍽️ 🗓️ 🌤️ 🚗    │
                    │   (Mistral 7B)     │
                    └─────────────────────┘
```

### 🤖 **AI Agent Ecosystem**

| Agent | Purpose | Technology | Cache |
|-------|---------|------------|--------|
| 🏨 **Hotel Agent** | Accommodation recommendations | Mistral 7B + LangChain | 24h |
| 🍽️ **Restaurant Agent** | Dining experiences | Mistral 7B + LangChain | 24h |
| 🗓️ **Itinerary Agent** | Activity planning | Mistral 7B + LangChain | 24h |
| 🌤️ **Weather Agent** | Real-time weather | Open-Meteo API | 1h |
| 🚗 **Transportation Agent** | Travel logistics | Mistral 7B + LangChain | 24h |

### 💻 **Technology Stack**

#### **Backend Powerhouse**
- **🐍 Python 3.9** - Core application logic
- **🌶️ Flask** - Lightweight web framework
- **🧠 LangChain** - AI agent orchestration
- **🤗 Hugging Face** - AI model inference
- **🔗 PyMongo** - MongoDB integration
- **☁️ Boto3** - AWS services integration

#### **Database & Storage**
- **🍃 MongoDB Atlas** - Scalable NoSQL database
- **📊 Event Collection** - Rich event metadata
- **⚡ Smart Indexing** - Optimized queries

#### **Frontend Experience**
- **📱 Responsive HTML5** - Mobile-first design
- **🎨 Modern CSS3** - Beautiful, accessible UI
- **⚡ JavaScript ES6+** - Interactive features
- **🔄 Jinja2 Templates** - Dynamic content

#### **Infrastructure & Deployment**
- **🐳 Docker** - Containerized deployment
- **☁️ AWS EC2** - Production hosting
- **🔄 CI/CD Pipeline** - Automated deployment
- **📈 Auto-scaling** - Handle traffic spikes

---

## 🚀 Quick Start

### 📋 **Prerequisites**
- Python 3.9+
- Docker & Docker Compose
- MongoDB Atlas account
- Hugging Face API token

### ⚡ **Fast Setup**

```bash
# 1️⃣ Clone the repository
git clone https://github.com/your-username/TEPIS_TEST.git
cd TEPIS_TEST

# 2️⃣ Environment setup
cp .env.example .env
# Add your API tokens to .env file

# 3️⃣ Docker deployment (Recommended)
docker-compose up -d

# 4️⃣ Access the application
open http://localhost:5000
```

### 🔧 **Manual Setup**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGINGFACEHUB_API_TOKEN="your_token_here"

# Run the application
python app/app.py
```

---

## 📊 **Event Data Structure**

TEPIS works with rich event data to provide comprehensive planning:

```json
{
  "_id": "unique_event_id",
  "event_title": "Amazing Music Festival 2025",
  "summary": "Three days of incredible music...",
  "event_type": "Festival",
  "ticket_price": "From $199",
  "start_date": "2025-08-15",
  "end_date": "2025-08-17",
  "city_name": "Austin",
  "state_name": "Texas",
  "country_name": "USA",
  "category": "music",
  "price_tier": "moderate",
  "duration": "3 days"
}
```

---

## 🌟 **Key Features Showcase**

### 🔍 **Smart Event Discovery**
- **Advanced Filtering**: Category, price range, location, dates
- **Intelligent Search**: Natural language event search
- **Pagination**: Efficient browsing of large event catalogs
- **Real-time Stats**: Live event counts and global coverage

### 🤖 **AI-Powered Planning**
- **Multi-Agent Coordination**: Specialized agents for each travel aspect
- **Personalized Recommendations**: Tailored to budget and preferences  
- **Real-time Generation**: Live itinerary creation (30-60 seconds)
- **Fallback Systems**: Reliable service even during high load

### 📱 **User Experience**
- **Responsive Design**: Perfect on mobile, tablet, and desktop
- **Loading States**: Clear feedback during AI processing
- **Error Handling**: Graceful degradation with helpful messages
- **Progressive Enhancement**: Core functionality works without JavaScript

---

## 🏗️ **Project Structure**

```
TEPIS_TEST/
├── 🐳 docker-compose.yaml     # Multi-service orchestration
├── 🐋 Dockerfile             # Container configuration
├── 📦 requirements.txt       # Python dependencies
├── 📄 PROJECT_REPORT.md      # Detailed technical documentation
│
├── app/                      # Main application
│   ├── 🌶️ app.py            # Flask application core
│   │
│   ├── agents/               # AI Agent ecosystem
│   │   ├── 🧠 coordinator.py      # Agent orchestrator
│   │   ├── 🏨 hotel_agent.py      # Hotel recommendations
│   │   ├── 🍽️ restaurant_agent.py # Dining suggestions
│   │   ├── 🗓️ itinerary_agent.py  # Activity planning
│   │   ├── 🌤️ weather_agent.py    # Weather integration
│   │   └── 🚗 transportation_agent.py # Travel logistics
│   │
│   ├── static/               # Frontend assets
│   │   ├── css/
│   │   │   └── 🎨 style.css  # Modern, responsive styling
│   │   ├── js/
│   │   │   └── ⚡ main.js    # Interactive functionality
│   │   └── images/           # Static images
│   │
│   └── templates/            # Jinja2 templates
│       ├── 🏠 home.html      # Landing page
│       ├── 🎯 events.html    # Event discovery
│       ├── 📋 event_detail.html # Event details & itinerary
│       └── 🗓️ trip_planner.html # Trip customization
```

---

## 🚢 **Deployment**

### 🐳 **Docker Deployment (Recommended)**

```yaml
# docker-compose.yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - HUGGINGFACEHUB_API_TOKEN=${HF_TOKEN}
      - MONGODB_URI=${MONGO_URI}
```

### ☁️ **AWS EC2 Production**

1. **Launch EC2 Instance** (t3.medium recommended)
2. **Install Docker & Docker Compose**
3. **Clone repository and configure environment**
4. **Deploy with Docker Compose**
5. **Configure security groups** (HTTP/HTTPS access)

### 🔄 **CI/CD Pipeline**

- **Version Control**: Git-based workflow
- **Automated Testing**: Unit and integration tests
- **Container Building**: Automated Docker builds
- **Deployment**: Zero-downtime deployments
- **Monitoring**: Health checks and alerts

---

## 🔧 **API & Integration**

### 🌐 **External APIs**
- **Hugging Face**: AI model inference
- **Open-Meteo**: Real-time weather data
- **MongoDB Atlas**: Event data storage

### 🔑 **Environment Variables**
```bash
HUGGINGFACEHUB_API_TOKEN=your_hugging_face_token
MONGODB_URI=your_mongodb_connection_string
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

---

## 📈 **Performance & Scaling**

### ⚡ **Optimization Features**
- **Smart Caching**: 24-hour AI response caching
- **Database Indexing**: Optimized MongoDB queries
- **Lazy Loading**: Agents loaded on-demand
- **Response Compression**: Reduced bandwidth usage

### 📊 **Monitoring**
- **Application Metrics**: Response times and error rates
- **AI Performance**: Model response times and success rates
- **Database Health**: Connection pooling and query performance
- **Infrastructure**: CPU, memory, and network monitoring

---

## 🛡️ **Security**

### 🔐 **Data Protection**
- **API Token Security**: Secure environment variable storage
- **Input Validation**: Comprehensive data sanitization
- **Database Security**: MongoDB Atlas security features
- **Container Security**: Docker best practices

### 🌐 **Infrastructure Security**
- **AWS Security Groups**: Network-level protection
- **SSL/TLS**: HTTPS encryption for data in transit
- **VPC Configuration**: Isolated network architecture
- **Access Control**: Principle of least privilege

---

## 🧪 **Testing**

### 🔬 **Test Coverage**
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow validation
- **AI Agent Tests**: Model response validation
- **Performance Tests**: Load and stress testing

### 🚀 **Quality Assurance**
- **Code Linting**: PEP 8 compliance
- **Security Scanning**: Vulnerability detection
- **Dependency Auditing**: Package security checks
- **Container Scanning**: Image security validation

---

## 📚 **Documentation**

- **📄 [Technical Report](PROJECT_REPORT.md)** - Comprehensive system analysis
- **🔧 API Documentation** - Endpoint specifications
- **🏗️ Architecture Guide** - System design deep-dive
- **📱 User Guide** - Feature walkthroughs

---

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

1. **🍴 Fork the repository**
2. **🌿 Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **💾 Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **📤 Push to branch** (`git push origin feature/amazing-feature`)
5. **🔄 Open a Pull Request**

### 📋 **Contribution Guidelines**
- Follow Python PEP 8 style guide
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure Docker builds pass
- Include AI agent testing for new agents

---

## 🐛 **Troubleshooting**

### Common Issues

**🤖 AI Agents Not Responding**
```bash
# Check Hugging Face API token
echo $HUGGINGFACEHUB_API_TOKEN

# Verify model availability
curl -H "Authorization: Bearer $HF_TOKEN" \
     https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2
```

**🔌 Database Connection Issues**
```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient('$MONGODB_URI').admin.command('ping'))"
```

**🐳 Docker Build Problems**
```bash
# Clear Docker cache
docker system prune -a
docker-compose build --no-cache
```

---

## 📊 **Project Stats**

<div align="center">

| Metric | Value |
|--------|-------|
| 🎯 **Events** | 1000+ Global Events |
| 🌍 **Countries** | 50+ Countries |
| 🤖 **AI Agents** | 5 Specialized Agents |
| ⚡ **Response Time** | < 60 seconds |
| 📱 **Mobile Support** | 100% Responsive |
| 🔄 **Uptime** | 99.9% Target |

</div>

---

## 🚀 **Future Roadmap**

### 🎯 **Phase 1: Enhanced Intelligence**
- [ ] GPT-4 integration for advanced planning
- [ ] Machine learning for personalization
- [ ] Multi-language support
- [ ] Voice-activated planning

### 🌍 **Phase 2: Global Expansion**
- [ ] International payment processing
- [ ] Local partner integrations
- [ ] Region-specific customizations
- [ ] Multi-currency support

### 📱 **Phase 3: Platform Evolution**
- [ ] Native mobile applications
- [ ] Social features and community
- [ ] Corporate travel solutions
- [ ] White-label platform offerings

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **🤗 Hugging Face** for providing world-class AI models
- **🍃 MongoDB** for scalable data storage
- **🌤️ Open-Meteo** for reliable weather data
- **☁️ AWS** for robust cloud infrastructure
- **🐳 Docker** for consistent deployment

---

## 📞 **Contact & Support**

<div align="center">

**Built with ❤️ for travelers who dream bigger**

[![Email](https://img.shields.io/badge/Email-hello%40tepis.com-blue?style=flat-square&logo=gmail)](mailto:hello@tepis.com)
[![GitHub](https://img.shields.io/badge/GitHub-TEPIS--Team-black?style=flat-square&logo=github)](https://github.com/krunalpatel355)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com)

**⭐ Star this repo if you find it useful!**

*Transform your events into epic adventures with TEPIS* 🚀

</div>
