# Phase 2 Implementation Plan: Web UI Migration

## Overview
Phase 2 transitions the Chess Fairplay Analyzer from CLI-based to a modern web application with React frontend and Flask backend, improving usability and enabling real-time analysis.

## Timeline: Q3 2026 (July - September)
- **Month 1** (July): Architecture & Setup
- **Month 2** (August): Backend Development
- **Month 3** (September): Frontend Development & Integration

---

## Architecture Overview

### Current State (CLI)
```
chess_analyzer/ (core logic)
├── __init__.py
├── menu.py (CLI interface)
├── analyzer.py
├── move_tree_builder.py
├── d3_visualizer.py
└── ... other modules
```

### Target State (Web-Based)
```
chess-fairplay-web/
├── backend/
│   ├── app.py (Flask app)
│   ├── chess_analyzer/ (existing core logic - no changes)
│   ├── routes/ (API endpoints)
│   ├── services/ (business logic)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/ (React components)
│   │   ├── pages/ (page routes)
│   │   ├── hooks/ (custom hooks)
│   │   ├── utils/ (helpers)
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
└── docs/
```

---

## Week 1-2: Architecture & Setup (July 1-14)

### 1.1 Backend Architecture Design
- [ ] Design REST API endpoints
- [ ] Plan database schema (SQLAlchemy)
- [ ] Plan authentication/authorization
- [ ] Plan session management
- [ ] Create API specification (OpenAPI/Swagger)

**API Endpoints** (Preliminary):
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/players/{id}
GET    /api/games/{id}
POST   /api/analyze
POST   /api/upload
GET    /api/results/{id}
GET    /api/reports/{id}
```

**Output**: `docs/api_specification.md`

### 1.2 Frontend Architecture Design
- [ ] Design page structure/routing
- [ ] Plan component hierarchy
- [ ] Plan state management (Redux/Context)
- [ ] Plan styling strategy (Tailwind CSS)
- [ ] Create wireframes

**Pages**:
- Dashboard (main page)
- Player Search
- Game Upload
- Analysis Results
- Report View
- Settings

**Output**: `docs/frontend_architecture.md`, wireframes

### 1.3 Development Environment Setup
- [ ] Initialize Flask project
- [ ] Initialize React project (with TypeScript)
- [ ] Setup development databases
- [ ] Setup linting/formatting (ESLint, Prettier)
- [ ] Setup testing frameworks (pytest, Jest)
- [ ] Create Docker setup

**Output**: Project scaffolding, docker-compose.yml

---

## Week 3-4: Backend Foundation (July 15-28)

### 2.1 Flask App Setup
- [ ] Create `backend/app.py` with Flask configuration
- [ ] Setup blueprints for modular routes
- [ ] Setup CORS for frontend communication
- [ ] Setup error handling middleware
- [ ] Setup logging

```python
# backend/app.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints
from routes.auth import auth_bp
from routes.analysis import analysis_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
```

**Output**: `backend/app.py`, `backend/routes/` directory

### 2.2 Database Setup
- [ ] Create SQLAlchemy models
- [ ] Setup migrations (Alembic)
- [ ] Create database schema
- [ ] Add indexes for performance

**Models**:
- User
- Game
- AnalysisResult
- Report
- Session

```python
# backend/models.py
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    games = db.relationship('Game', backref='user', lazy=True)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pgn = db.Column(db.Text)
    analyzed = db.Column(db.Boolean, default=False)
    analysis_result = db.relationship('AnalysisResult')
```

**Output**: `backend/models.py`, migrations

### 2.3 Authentication Service
- [ ] Implement JWT-based authentication
- [ ] Create login endpoint
- [ ] Create registration endpoint
- [ ] Add password hashing (bcrypt)
- [ ] Add token refresh mechanism

```python
# backend/routes/auth.py
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        token = create_access_token(identity=user.id)
        return {'access_token': token}, 200
    return {'error': 'Invalid credentials'}, 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return {'message': 'User created'}, 201
```

**Output**: `backend/routes/auth.py`, authentication service

### 2.4 Core Analysis API
- [ ] Create analysis endpoint
- [ ] Integrate existing analyzer modules
- [ ] Add job queuing (Celery optional)
- [ ] Add progress tracking
- [ ] Add result caching

```python
# backend/routes/analysis.py
@analysis_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    data = request.json
    games = parse_pgn(data['pgn'])
    
    # Use existing analyzer
    analyzer = EnhancedAnalyzer(config)
    results = analyzer.analyze_games(games)
    
    # Store results
    analysis = AnalysisResult(
        user_id=current_user_id,
        games=json.dumps(results),
        accuracy=calculate_accuracy(results)
    )
    db.session.add(analysis)
    db.session.commit()
    
    return {'id': analysis.id, 'results': results}, 200
```

**Output**: `backend/routes/analysis.py`

---

## Week 5-6: Backend Services (August 1-12)

### 3.1 File Upload Service
- [ ] Create upload endpoint
- [ ] Validate PGN files
- [ ] Store files securely
- [ ] Handle multiple file formats
- [ ] Add virus scanning (ClamAV optional)

```python
# backend/services/file_service.py
class FileService:
    def upload_pgn(self, file, user_id):
        """Upload and validate PGN file"""
        # Validate file
        # Scan for viruses
        # Store in database
        # Return file ID
        pass
```

**Output**: `backend/services/file_service.py`

### 3.2 Report Generation Service
- [ ] Create report generation endpoints
- [ ] Generate HTML reports with charts
- [ ] Generate PDF reports
- [ ] Support custom report templates
- [ ] Add email report delivery

```python
# backend/services/report_service.py
class ReportService:
    def generate_html_report(self, analysis_id):
        """Generate interactive HTML report"""
        pass
    
    def generate_pdf_report(self, analysis_id):
        """Generate PDF export"""
        pass
    
    def send_report_email(self, analysis_id, email):
        """Email report to user"""
        pass
```

**Output**: `backend/services/report_service.py`

### 3.3 Visualization Service
- [ ] Create endpoints for D3 data
- [ ] Create endpoints for chart data
- [ ] Create endpoints for heatmap data
- [ ] Cache visualization data

```python
# backend/services/visualization_service.py
class VisualizationService:
    def get_tree_data(self, analysis_id):
        """Get D3 tree JSON"""
        # Use existing move_tree_builder
        pass
    
    def get_accuracy_chart_data(self, analysis_id):
        """Get data for accuracy chart"""
        pass
    
    def get_opening_heatmap(self, analysis_id):
        """Get opening frequency heatmap"""
        pass
```

**Output**: `backend/services/visualization_service.py`

### 3.4 API Testing
- [ ] Create comprehensive API tests
- [ ] Test authentication flow
- [ ] Test file upload
- [ ] Test analysis endpoints
- [ ] Test error handling

```python
# backend/tests/test_api.py
def test_login():
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_analyze():
    # Login first
    # Upload PGN
    # Call analyze
    # Check results
    pass
```

**Output**: `backend/tests/` directory with comprehensive tests

---

## Week 7-8: Frontend Development (August 13-26)

### 4.1 React Project Setup
- [ ] Initialize React app (TypeScript)
- [ ] Setup Tailwind CSS
- [ ] Setup routing (React Router v6)
- [ ] Setup state management (Redux Toolkit or Context API)
- [ ] Setup HTTP client (axios)

```typescript
// frontend/src/App.tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PlayerSearch from './pages/PlayerSearch';
import AnalysisResults from './pages/AnalysisResults';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<PlayerSearch />} />
        <Route path="/results/:id" element={<AnalysisResults />} />
      </Routes>
    </Router>
  );
}
```

**Output**: Project scaffolding with routing setup

### 4.2 Core Pages
- [ ] Dashboard page (main landing)
- [ ] Player search page
- [ ] Game upload page
- [ ] Analysis results page
- [ ] Settings/Profile page

**Dashboard Page**:
```typescript
// frontend/src/pages/Dashboard.tsx
export function Dashboard() {
  return (
    <div className="container mx-auto">
      <h1>Chess Fairplay Analyzer</h1>
      <button>Search Player</button>
      <button>Upload Games</button>
      <RecentAnalyses />
    </div>
  );
}
```

**Upload Page**:
- Drag-and-drop PGN upload
- File validation feedback
- Upload progress indicator
- Success/error messages

**Results Page**:
- Tabs: Summary, Games, Tree, Report
- Accuracy score display
- D3 tree visualization
- Detailed game analysis
- Export buttons

**Output**: `frontend/src/pages/` directory

### 4.3 Reusable Components
- [ ] Header/Navigation component
- [ ] Card component (for results)
- [ ] Chart components (accuracy, rating, openings)
- [ ] D3 Tree component
- [ ] Loading spinner
- [ ] Error boundary

```typescript
// frontend/src/components/D3Tree.tsx
interface D3TreeProps {
  data: TreeNode;
  onNodeClick: (node: TreeNode) => void;
}

export function D3Tree({ data, onNodeClick }: D3TreeProps) {
  useEffect(() => {
    // Initialize D3
    // Draw tree
  }, [data]);
  
  return <svg ref={svgRef} />;
}
```

**Output**: `frontend/src/components/` directory

### 4.4 State Management
- [ ] Setup Redux store
- [ ] Create slices: auth, analysis, ui
- [ ] Create selectors
- [ ] Setup middleware (thunks)

```typescript
// frontend/src/store/slices/authSlice.ts
const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, token: null },
  reducers: {
    loginSuccess: (state, action) => {
      state.token = action.payload.token;
      state.user = action.payload.user;
    },
  },
});

// frontend/src/store/slices/analysisSlice.ts
const analysisSlice = createSlice({
  name: 'analysis',
  initialState: { results: [], loading: false },
  reducers: {
    setResults: (state, action) => {
      state.results = action.payload;
    },
  },
});
```

**Output**: `frontend/src/store/` directory

### 4.5 Frontend Testing
- [ ] Setup Jest and React Testing Library
- [ ] Create component tests
- [ ] Create integration tests
- [ ] Create E2E tests (Cypress)

```typescript
// frontend/src/components/__tests__/Dashboard.test.tsx
describe('Dashboard', () => {
  it('renders main buttons', () => {
    render(<Dashboard />);
    expect(screen.getByText('Search Player')).toBeInTheDocument();
    expect(screen.getByText('Upload Games')).toBeInTheDocument();
  });
});
```

**Output**: `frontend/src/__tests__/` directory

---

## Week 9-10: Integration & Deployment (September 1-16)

### 5.1 Frontend-Backend Integration
- [ ] Connect login form to auth API
- [ ] Connect upload to file API
- [ ] Connect analysis to analysis API
- [ ] Connect results display to result API
- [ ] Add error handling and validation
- [ ] Add loading states

```typescript
// frontend/src/hooks/useAnalysis.ts
export function useAnalysis() {
  const dispatch = useDispatch();
  
  const uploadAndAnalyze = async (pgn: string) => {
    dispatch(setLoading(true));
    try {
      const response = await apiClient.post('/api/analysis/analyze', { pgn });
      dispatch(setResults(response.data));
      return response.data.id;
    } catch (error) {
      dispatch(setError(error.message));
    } finally {
      dispatch(setLoading(false));
    }
  };
  
  return { uploadAndAnalyze };
}
```

**Output**: Integrated frontend/backend

### 5.2 Docker Setup
- [ ] Create Dockerfile for backend
- [ ] Create Dockerfile for frontend
- [ ] Create docker-compose.yml
- [ ] Test local Docker deployment
- [ ] Document Docker setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/chess_analyzer
      - FLASK_ENV=production
    depends_on:
      - db
  
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  db:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: chess_analyzer
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Output**: `docker-compose.yml`, Dockerfiles

### 5.3 Deployment Setup
- [ ] Create deployment documentation
- [ ] Setup CI/CD (GitHub Actions)
- [ ] Setup environment configuration
- [ ] Setup monitoring/logging (optional)
- [ ] Create deployment checklist

**GitHub Actions Workflow**:
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: cd backend && pytest
      - name: Run frontend tests
        run: cd frontend && npm test
  
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker images
        run: docker-compose build
      - name: Push to registry
        run: docker push ...
```

**Output**: `docker-compose.yml`, CI/CD configuration

### 5.4 Documentation
- [ ] Create deployment guide
- [ ] Create API documentation (Swagger/OpenAPI)
- [ ] Create frontend development guide
- [ ] Create user manual for web interface

**Output**: `docs/DEPLOYMENT.md`, `docs/API.md`, `docs/FRONTEND_DEV.md`

### 5.5 Performance Optimization
- [ ] Implement caching strategy
- [ ] Optimize database queries
- [ ] Optimize frontend bundle size
- [ ] Setup CDN for static assets
- [ ] Add lazy loading for routes

---

## Week 11-12: QA & Launch (September 17-30)

### 6.1 Comprehensive Testing
- [ ] Integration testing (backend + frontend)
- [ ] Cross-browser testing
- [ ] Mobile responsiveness testing
- [ ] Performance testing (load testing)
- [ ] Security testing

### 6.2 Bug Fixes & Refinement
- [ ] Fix reported issues
- [ ] Optimize slow components
- [ ] Improve UI/UX based on feedback
- [ ] Add missing features

### 6.3 Launch Preparation
- [ ] Setup production database
- [ ] Create backup strategy
- [ ] Setup monitoring/alerting
- [ ] Create support documentation
- [ ] Prepare release notes

### 6.4 Launch
- [ ] Deploy to production
- [ ] Verify all features working
- [ ] Monitor for errors
- [ ] Communicate with users
- [ ] Setup feedback channel

---

## Deliverables Checklist

**Backend Code**:
- [ ] `backend/app.py` (Flask main app)
- [ ] `backend/models.py` (SQLAlchemy models)
- [ ] `backend/routes/` (API endpoints)
- [ ] `backend/services/` (business logic)
- [ ] `backend/tests/` (comprehensive tests)
- [ ] `backend/requirements.txt`

**Frontend Code**:
- [ ] `frontend/src/App.tsx`
- [ ] `frontend/src/pages/` (all pages)
- [ ] `frontend/src/components/` (reusable components)
- [ ] `frontend/src/store/` (Redux store)
- [ ] `frontend/src/hooks/` (custom hooks)
- [ ] `frontend/src/__tests__/` (tests)
- [ ] `frontend/package.json`
- [ ] `frontend/tailwind.config.js`

**Deployment**:
- [ ] `docker/Dockerfile.backend`
- [ ] `docker/Dockerfile.frontend`
- [ ] `docker-compose.yml`
- [ ] `.github/workflows/deploy.yml`
- [ ] Kubernetes manifests (optional)

**Documentation**:
- [ ] `docs/DEPLOYMENT.md`
- [ ] `docs/API.md` (Swagger/OpenAPI)
- [ ] `docs/FRONTEND_DEV.md`
- [ ] `docs/USER_MANUAL.md`
- [ ] Architecture diagrams

---

## Success Criteria

**Functionality**:
- ✅ All features accessible via web UI
- ✅ Analysis results identical to CLI version
- ✅ Reports display correctly
- ✅ D3 visualizations fully functional
- ✅ File upload working smoothly

**User Experience**:
- ✅ Responsive on mobile/tablet/desktop
- ✅ Page load time < 3 seconds
- ✅ Analysis results visible within reasonable time
- ✅ Clear error messages
- ✅ Intuitive navigation

**Performance**:
- ✅ Backend API response time < 500ms
- ✅ Frontend bundle size < 500KB (gzipped)
- ✅ Support 100+ concurrent users
- ✅ 99.9% uptime

**Quality**:
- ✅ Backend test coverage >= 80%
- ✅ Frontend test coverage >= 70%
- ✅ Zero critical security vulnerabilities
- ✅ All features documented
- ✅ No known bugs

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Over-scoping | Timeline miss | Focus on MVP first, phase 2 features |
| Database performance | Slow analysis | Proper indexing, caching, query optimization |
| Frontend complexity | Development delays | Use component libraries (shadcn/ui, MUI) |
| Frontend-backend mismatch | Integration issues | Regular integration testing, API contracts |
| User adoption | Low engagement | Create onboarding guide, collect feedback |

---

## Success Metrics

- **Users**: 1000+ registered users by Q4 2026
- **Performance**: API response time < 500ms (p95)
- **Quality**: 99.9% uptime, <0.1% error rate
- **Adoption**: 50%+ feature usage
- **Satisfaction**: >4.5/5 star rating

---

## Budget Estimate
- **Development Time**: 120 hours (~3 months, 1-2 developers)
- **Hosting Cost**: $50-200/month (depending on scale)
- **Third-party Services**: $0 (all open-source)

---

## Migration Strategy

### Phase 2 Coexistence (Initial)
- Keep CLI version available
- Provide data migration tools
- Support both interfaces

### Phase 2 Transition (Month 6)
- Encourage web UI adoption
- Sunset CLI version
- Archive legacy code

### Phase 2 Completion (Month 9)
- CLI fully deprecated
- 100% of users on web UI
- Legacy code removed

---

**Document Created**: January 30, 2026  
**Phase 2 Start Date**: July 1, 2026  
**Phase 2 Target Completion**: September 30, 2026  
**Version**: 1.0
