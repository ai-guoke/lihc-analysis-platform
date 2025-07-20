"""
User Management Interface for LIHC Platform
Provides administrative and user management functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import time

from src.database.models import User, Dataset, Analysis, SystemLog
from src.utils.logging_system import LIHCLogger
from src.api.dependencies import get_password_hash, verify_password


class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    RESEARCHER = "researcher" 
    VIEWER = "viewer"
    GUEST = "guest"


@dataclass
class UserProfile:
    """User profile data class"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    datasets_count: int = 0
    analyses_count: int = 0
    storage_used: float = 0.0  # in MB


class UserManagementInterface:
    """User management interface for administrators"""
    
    def __init__(self):
        self.logger = LIHCLogger(name="UserManagement")
        
        # Initialize session state
        if 'users_data' not in st.session_state:
            st.session_state.users_data = self._load_sample_users()
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = {}
    
    def _load_sample_users(self) -> List[UserProfile]:
        """Load sample user data for demonstration"""
        return [
            UserProfile(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@lihc.ai", 
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.now() - timedelta(days=30),
                last_login=datetime.now() - timedelta(hours=2),
                datasets_count=5,
                analyses_count=15,
                storage_used=1250.5
            ),
            UserProfile(
                id=str(uuid.uuid4()),
                username="researcher1",
                email="researcher1@institution.edu",
                full_name="Dr. Sarah Chen",
                role=UserRole.RESEARCHER,
                is_active=True,
                created_at=datetime.now() - timedelta(days=15),
                last_login=datetime.now() - timedelta(hours=6),
                datasets_count=8,
                analyses_count=23,
                storage_used=2100.3
            ),
            UserProfile(
                id=str(uuid.uuid4()),
                username="researcher2", 
                email="researcher2@biotech.com",
                full_name="Dr. Michael Rodriguez",
                role=UserRole.RESEARCHER,
                is_active=True,
                created_at=datetime.now() - timedelta(days=20),
                last_login=datetime.now() - timedelta(days=1),
                datasets_count=3,
                analyses_count=7,
                storage_used=750.2
            ),
            UserProfile(
                id=str(uuid.uuid4()),
                username="viewer1",
                email="viewer@hospital.org",
                full_name="Dr. Emily Watson",
                role=UserRole.VIEWER,
                is_active=True,
                created_at=datetime.now() - timedelta(days=5),
                last_login=datetime.now() - timedelta(hours=12),
                datasets_count=0,
                analyses_count=2,
                storage_used=0.0
            ),
            UserProfile(
                id=str(uuid.uuid4()),
                username="inactive_user",
                email="inactive@old.com",
                full_name="Inactive User",
                role=UserRole.RESEARCHER,
                is_active=False,
                created_at=datetime.now() - timedelta(days=100),
                last_login=datetime.now() - timedelta(days=45),
                datasets_count=2,
                analyses_count=1,
                storage_used=150.0
            )
        ]
    
    def render_login_interface(self):
        """Render login interface"""
        st.title("🔐 LIHC Platform Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if self._authenticate_user(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    self._log_failed_login(username)
    
    def _authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials"""
        # Simple authentication for demo (in production, use proper password hashing)
        valid_credentials = {
            "admin": "admin123",
            "researcher1": "research123", 
            "viewer1": "view123"
        }
        
        if username in valid_credentials and valid_credentials[username] == password:
            # Find user profile
            for user in st.session_state.users_data:
                if user.username == username and user.is_active:
                    st.session_state.current_user = user
                    user.last_login = datetime.now()
                    return True
        return False
    
    def _log_failed_login(self, username: str):
        """Log failed login attempt"""
        current_time = time.time()
        if username not in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = []
        
        st.session_state.login_attempts[username].append(current_time)
        
        # Keep only last 5 attempts
        st.session_state.login_attempts[username] = \
            st.session_state.login_attempts[username][-5:]
    
    def render_user_management_dashboard(self):
        """Render main user management dashboard"""
        if not st.session_state.current_user:
            self.render_login_interface()
            return
        
        current_user = st.session_state.current_user
        
        # Header with user info
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.title(f"👋 Welcome, {current_user.full_name}")
        with col2:
            st.metric("Your Role", current_user.role.value.title())
        with col3:
            if st.button("Logout"):
                st.session_state.current_user = None
                st.rerun()
        
        # Check permissions
        if current_user.role not in [UserRole.ADMIN]:
            st.warning("You don't have permission to access user management.")
            self.render_user_dashboard()
            return
        
        # Sidebar navigation
        st.sidebar.title("User Management")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["Overview", "User List", "Add User", "System Logs", "Analytics"]
        )
        
        if page == "Overview":
            self.render_overview()
        elif page == "User List":
            self.render_user_list()
        elif page == "Add User":
            self.render_add_user()
        elif page == "System Logs":
            self.render_system_logs()
        elif page == "Analytics":
            self.render_analytics()
    
    def render_overview(self):
        """Render overview dashboard"""
        st.header("📊 System Overview")
        
        users_data = st.session_state.users_data
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = len(users_data)
            st.metric("Total Users", total_users)
        
        with col2:
            active_users = len([u for u in users_data if u.is_active])
            st.metric("Active Users", active_users, f"{active_users/total_users*100:.1f}%")
        
        with col3:
            total_datasets = sum(u.datasets_count for u in users_data)
            st.metric("Total Datasets", total_datasets)
        
        with col4:
            total_analyses = sum(u.analyses_count for u in users_data)
            st.metric("Total Analyses", total_analyses)
        
        # User activity chart
        st.subheader("User Activity (Last 30 Days)")
        
        # Create sample activity data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        activity_data = []
        
        for date in dates:
            daily_active = max(0, int(active_users * (0.6 + 0.4 * hash(str(date)) % 100 / 100)))
            activity_data.append({
                'Date': date,
                'Active Users': daily_active,
                'New Analyses': max(0, int(daily_active * 0.3 + hash(str(date)) % 5)),
                'Data Uploads': max(0, int(daily_active * 0.1 + hash(str(date)) % 3))
            })
        
        activity_df = pd.DataFrame(activity_data)
        
        fig = px.line(activity_df, x='Date', y=['Active Users', 'New Analyses', 'Data Uploads'],
                     title="Daily Platform Activity")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Storage usage
        st.subheader("Storage Usage by User")
        storage_data = [(u.username, u.storage_used) for u in users_data if u.storage_used > 0]
        storage_df = pd.DataFrame(storage_data, columns=['User', 'Storage (MB)'])
        
        fig = px.bar(storage_df, x='User', y='Storage (MB)', 
                    title="Storage Usage by User")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_user_list(self):
        """Render user list with management options"""
        st.header("👥 User Management")
        
        users_data = st.session_state.users_data
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            role_filter = st.selectbox("Filter by Role", 
                                     ["All"] + [role.value for role in UserRole])
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        with col3:
            search_term = st.text_input("Search by name/email")
        
        # Apply filters
        filtered_users = users_data
        if role_filter != "All":
            filtered_users = [u for u in filtered_users if u.role.value == role_filter]
        if status_filter == "Active":
            filtered_users = [u for u in filtered_users if u.is_active]
        elif status_filter == "Inactive":
            filtered_users = [u for u in filtered_users if not u.is_active]
        if search_term:
            filtered_users = [u for u in filtered_users 
                            if search_term.lower() in u.full_name.lower() or 
                               search_term.lower() in u.email.lower()]
        
        # User table
        st.subheader(f"Users ({len(filtered_users)} of {len(users_data)})")
        
        if filtered_users:
            for user in filtered_users:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                    
                    with col1:
                        status_icon = "🟢" if user.is_active else "🔴"
                        st.write(f"{status_icon} **{user.full_name}**")
                        st.write(f"@{user.username}")
                    
                    with col2:
                        st.write(user.email)
                        st.write(f"Role: {user.role.value.title()}")
                    
                    with col3:
                        st.metric("Datasets", user.datasets_count)
                    
                    with col4:
                        st.metric("Analyses", user.analyses_count)
                    
                    with col5:
                        if st.button(f"Edit {user.username}", key=f"edit_{user.id}"):
                            st.session_state[f"editing_{user.id}"] = True
                        
                        if user.is_active:
                            if st.button(f"Deactivate", key=f"deactivate_{user.id}"):
                                user.is_active = False
                                st.success(f"Deactivated {user.username}")
                                st.rerun()
                        else:
                            if st.button(f"Activate", key=f"activate_{user.id}"):
                                user.is_active = True
                                st.success(f"Activated {user.username}")
                                st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f"editing_{user.id}", False):
                        with st.expander(f"Edit {user.full_name}", expanded=True):
                            with st.form(f"edit_user_{user.id}"):
                                new_full_name = st.text_input("Full Name", value=user.full_name)
                                new_email = st.text_input("Email", value=user.email)
                                new_role = st.selectbox("Role", 
                                                       [role.value for role in UserRole],
                                                       index=[role.value for role in UserRole].index(user.role.value))
                                
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.form_submit_button("Save Changes"):
                                        user.full_name = new_full_name
                                        user.email = new_email
                                        user.role = UserRole(new_role)
                                        st.session_state[f"editing_{user.id}"] = False
                                        st.success("User updated successfully!")
                                        st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("Cancel"):
                                        st.session_state[f"editing_{user.id}"] = False
                                        st.rerun()
                    
                    st.divider()
        else:
            st.info("No users found matching the filters.")
    
    def render_add_user(self):
        """Render add user interface"""
        st.header("➕ Add New User")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*")
                full_name = st.text_input("Full Name*")
                role = st.selectbox("Role*", [role.value for role in UserRole])
            
            with col2:
                email = st.text_input("Email*")
                password = st.text_input("Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            send_welcome_email = st.checkbox("Send welcome email", value=True)
            
            submit_button = st.form_submit_button("Create User")
            
            if submit_button:
                # Validation
                errors = []
                if not username or not full_name or not email or not password:
                    errors.append("All required fields must be filled")
                if password != confirm_password:
                    errors.append("Passwords do not match")
                if len(password) < 8:
                    errors.append("Password must be at least 8 characters")
                if any(u.username == username for u in st.session_state.users_data):
                    errors.append("Username already exists")
                if any(u.email == email for u in st.session_state.users_data):
                    errors.append("Email already exists")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Create new user
                    new_user = UserProfile(
                        id=str(uuid.uuid4()),
                        username=username,
                        email=email,
                        full_name=full_name,
                        role=UserRole(role),
                        is_active=True,
                        created_at=datetime.now(),
                        last_login=None
                    )
                    
                    st.session_state.users_data.append(new_user)
                    st.success(f"User {username} created successfully!")
                    
                    if send_welcome_email:
                        st.info(f"Welcome email sent to {email}")
                    
                    # Clear form
                    st.rerun()
    
    def render_system_logs(self):
        """Render system logs interface"""
        st.header("📋 System Logs")
        
        # Generate sample log data
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        log_modules = ["Authentication", "DataUpload", "Analysis", "UserManagement", "System"]
        
        logs_data = []
        for i in range(100):
            timestamp = datetime.now() - timedelta(minutes=i*5)
            level = log_levels[i % len(log_levels)]
            module = log_modules[i % len(log_modules)]
            
            messages = {
                "INFO": [f"User login successful", f"Analysis completed", f"Dataset uploaded"],
                "WARNING": [f"High memory usage detected", f"Slow query detected", f"User session timeout"],
                "ERROR": [f"Authentication failed", f"Analysis failed", f"Database connection error"],
                "DEBUG": [f"Function called", f"Variable value", f"Processing step"]
            }
            
            message = messages[level][i % len(messages[level])]
            
            logs_data.append({
                "Timestamp": timestamp,
                "Level": level,
                "Module": module,
                "Message": f"{message} (ID: {i+1})",
                "User": f"user_{(i % 5) + 1}" if level in ["INFO", "WARNING"] else None
            })
        
        logs_df = pd.DataFrame(logs_data)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            level_filter = st.multiselect("Log Level", 
                                        log_levels, 
                                        default=log_levels)
        with col2:
            module_filter = st.multiselect("Module", 
                                         log_modules, 
                                         default=log_modules)
        with col3:
            hours_back = st.selectbox("Time Range", 
                                    [1, 6, 12, 24, 48, 72], 
                                    index=3)
        
        # Apply filters
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        filtered_logs = logs_df[
            (logs_df['Level'].isin(level_filter)) &
            (logs_df['Module'].isin(module_filter)) &
            (logs_df['Timestamp'] >= cutoff_time)
        ]
        
        # Log level distribution
        st.subheader("Log Level Distribution")
        level_counts = filtered_logs['Level'].value_counts()
        fig = px.pie(values=level_counts.values, names=level_counts.index,
                    title="Distribution of Log Levels")
        st.plotly_chart(fig, use_container_width=True)
        
        # Logs table
        st.subheader(f"Recent Logs ({len(filtered_logs)} entries)")
        
        # Color code by level
        def style_level(val):
            colors = {
                "ERROR": "background-color: #ffebee",
                "WARNING": "background-color: #fff3e0", 
                "INFO": "background-color: #e8f5e8",
                "DEBUG": "background-color: #f3f3f3"
            }
            return colors.get(val, "")
        
        styled_logs = filtered_logs.style.applymap(style_level, subset=['Level'])
        st.dataframe(styled_logs, use_container_width=True, height=400)
        
        # Export logs
        if st.button("Export Logs to CSV"):
            csv = filtered_logs.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def render_analytics(self):
        """Render analytics dashboard"""
        st.header("📈 Platform Analytics")
        
        users_data = st.session_state.users_data
        
        # User registration over time
        st.subheader("User Registration Trend")
        
        # Create registration timeline
        registration_data = []
        for user in users_data:
            registration_data.append({
                'Date': user.created_at.date(),
                'User': user.username,
                'Role': user.role.value
            })
        
        reg_df = pd.DataFrame(registration_data)
        reg_timeline = reg_df.groupby(['Date', 'Role']).size().reset_index(name='Count')
        
        fig = px.bar(reg_timeline, x='Date', y='Count', color='Role',
                    title="User Registrations Over Time")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Role distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Role Distribution")
            role_counts = {}
            for user in users_data:
                role_counts[user.role.value] = role_counts.get(user.role.value, 0) + 1
            
            fig = px.pie(values=list(role_counts.values()), 
                        names=list(role_counts.keys()),
                        title="Distribution by Role")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Activity Metrics")
            active_users = [u for u in users_data if u.is_active]
            
            # Calculate activity metrics
            total_datasets = sum(u.datasets_count for u in active_users)
            total_analyses = sum(u.analyses_count for u in active_users)
            avg_datasets = total_datasets / len(active_users) if active_users else 0
            avg_analyses = total_analyses / len(active_users) if active_users else 0
            
            st.metric("Average Datasets per User", f"{avg_datasets:.1f}")
            st.metric("Average Analyses per User", f"{avg_analyses:.1f}")
            st.metric("Total Storage Used", f"{sum(u.storage_used for u in users_data):.1f} MB")
        
        # User activity heatmap
        st.subheader("User Activity Analysis")
        
        activity_matrix = []
        for user in users_data:
            activity_matrix.append({
                'User': user.username,
                'Datasets': user.datasets_count,
                'Analyses': user.analyses_count,
                'Storage_MB': user.storage_used,
                'Days_Since_Login': (datetime.now() - (user.last_login or user.created_at)).days,
                'Account_Age_Days': (datetime.now() - user.created_at).days
            })
        
        activity_df = pd.DataFrame(activity_matrix)
        
        # Correlation heatmap
        numeric_cols = ['Datasets', 'Analyses', 'Storage_MB', 'Days_Since_Login', 'Account_Age_Days']
        correlation_matrix = activity_df[numeric_cols].corr()
        
        fig = px.imshow(correlation_matrix, 
                       title="User Activity Correlation Matrix",
                       color_continuous_scale="RdBu_r")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_user_dashboard(self):
        """Render regular user dashboard"""
        current_user = st.session_state.current_user
        
        st.header(f"👤 {current_user.full_name}'s Dashboard")
        
        # User stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Your Datasets", current_user.datasets_count)
        with col2:
            st.metric("Your Analyses", current_user.analyses_count)
        with col3:
            st.metric("Storage Used", f"{current_user.storage_used:.1f} MB")
        with col4:
            days_since_login = (datetime.now() - (current_user.last_login or current_user.created_at)).days
            st.metric("Days Since Login", days_since_login)
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 Upload Dataset"):
                st.info("Dataset upload functionality would be here")
        
        with col2:
            if st.button("🔬 Start Analysis"):
                st.info("Analysis start functionality would be here")
        
        with col3:
            if st.button("📊 View Results"):
                st.info("Results viewing functionality would be here")
        
        # Recent activity (placeholder)
        st.subheader("Recent Activity")
        st.info("Your recent analyses and uploads would appear here")


def main():
    """Main function to run the user management interface"""
    st.set_page_config(
        page_title="LIHC Platform - User Management",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    interface = UserManagementInterface()
    interface.render_user_management_dashboard()


if __name__ == "__main__":
    main()