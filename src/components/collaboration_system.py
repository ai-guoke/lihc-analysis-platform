"""
Real-time Collaboration System
实时协作系统 - 支持多用户实时协作分析
"""

import json
import uuid
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio
import websockets
from threading import Lock
import sqlite3
from pathlib import Path
import hashlib

@dataclass
class User:
    """用户信息"""
    user_id: str
    username: str
    email: str
    avatar_url: str = ""
    role: str = "analyst"  # analyst, reviewer, admin
    last_active: str = ""
    current_workspace: str = ""
    cursor_position: Dict = None

@dataclass
class Workspace:
    """工作空间"""
    workspace_id: str
    name: str
    description: str
    owner_id: str
    members: List[str]
    created_at: str
    modified_at: str
    status: str = "active"  # active, archived
    permissions: Dict = None
    current_analysis: str = ""

@dataclass
class Comment:
    """评论"""
    comment_id: str
    workspace_id: str
    user_id: str
    username: str
    content: str
    target_type: str  # chart, table, analysis, general
    target_id: str
    position: Dict  # x, y coordinates for chart comments
    created_at: str
    replies: List = None
    resolved: bool = False

@dataclass
class AnalysisVersion:
    """分析版本"""
    version_id: str
    workspace_id: str
    analysis_type: str
    parameters: Dict
    results: Dict
    created_by: str
    created_at: str
    message: str
    parent_version: str = None

@dataclass
class LiveAction:
    """实时动作"""
    action_id: str
    user_id: str
    username: str
    action_type: str  # cursor_move, selection, annotation, analysis_start, etc.
    target: str
    data: Dict
    timestamp: str

class CollaborationDatabase:
    """协作数据库管理"""
    
    def __init__(self, db_path: str = "collaboration.db"):
        self.db_path = Path(db_path)
        self.lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        
        # 用户表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                avatar_url TEXT,
                role TEXT DEFAULT 'analyst',
                last_active TIMESTAMP,
                current_workspace TEXT,
                cursor_position TEXT
            )
        """)
        
        # 工作空间表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                workspace_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                owner_id TEXT,
                members TEXT,  -- JSON array
                created_at TIMESTAMP,
                modified_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                permissions TEXT,  -- JSON object
                current_analysis TEXT
            )
        """)
        
        # 评论表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id TEXT PRIMARY KEY,
                workspace_id TEXT,
                user_id TEXT,
                username TEXT,
                content TEXT,
                target_type TEXT,
                target_id TEXT,
                position TEXT,  -- JSON object
                created_at TIMESTAMP,
                replies TEXT,  -- JSON array
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 版本表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_versions (
                version_id TEXT PRIMARY KEY,
                workspace_id TEXT,
                analysis_type TEXT,
                parameters TEXT,  -- JSON object
                results TEXT,  -- JSON object
                created_by TEXT,
                created_at TIMESTAMP,
                message TEXT,
                parent_version TEXT
            )
        """)
        
        # 实时动作表（临时存储）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS live_actions (
                action_id TEXT PRIMARY KEY,
                user_id TEXT,
                username TEXT,
                action_type TEXT,
                target TEXT,
                data TEXT,  -- JSON object
                timestamp TIMESTAMP,
                workspace_id TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, user: User) -> bool:
        """创建用户"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("""
                    INSERT INTO users 
                    (user_id, username, email, avatar_url, role, last_active, current_workspace, cursor_position)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id, user.username, user.email, user.avatar_url,
                    user.role, user.last_active, user.current_workspace,
                    json.dumps(user.cursor_position) if user.cursor_position else None
                ))
                conn.commit()
                conn.close()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                user_id=row[0], username=row[1], email=row[2], avatar_url=row[3],
                role=row[4], last_active=row[5], current_workspace=row[6],
                cursor_position=json.loads(row[7]) if row[7] else None
            )
        return None
    
    def create_workspace(self, workspace: Workspace) -> bool:
        """创建工作空间"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO workspaces 
                (workspace_id, name, description, owner_id, members, created_at, modified_at, status, permissions, current_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workspace.workspace_id, workspace.name, workspace.description,
                workspace.owner_id, json.dumps(workspace.members),
                workspace.created_at, workspace.modified_at, workspace.status,
                json.dumps(workspace.permissions) if workspace.permissions else None,
                workspace.current_analysis
            ))
            conn.commit()
            conn.close()
            return True
    
    def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """获取用户的工作空间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT * FROM workspaces 
            WHERE owner_id = ? OR members LIKE ?
        """, (user_id, f'%"{user_id}"%'))
        
        workspaces = []
        for row in cursor.fetchall():
            workspace = Workspace(
                workspace_id=row[0], name=row[1], description=row[2],
                owner_id=row[3], members=json.loads(row[4]),
                created_at=row[5], modified_at=row[6], status=row[7],
                permissions=json.loads(row[8]) if row[8] else None,
                current_analysis=row[9]
            )
            workspaces.append(workspace)
        
        conn.close()
        return workspaces
    
    def add_comment(self, comment: Comment) -> bool:
        """添加评论"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO comments 
                (comment_id, workspace_id, user_id, username, content, target_type, target_id, position, created_at, replies, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comment.comment_id, comment.workspace_id, comment.user_id,
                comment.username, comment.content, comment.target_type,
                comment.target_id, json.dumps(comment.position) if comment.position else None,
                comment.created_at, json.dumps(comment.replies) if comment.replies else None,
                comment.resolved
            ))
            conn.commit()
            conn.close()
            return True
    
    def get_workspace_comments(self, workspace_id: str) -> List[Comment]:
        """获取工作空间评论"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT * FROM comments WHERE workspace_id = ? ORDER BY created_at DESC
        """, (workspace_id,))
        
        comments = []
        for row in cursor.fetchall():
            comment = Comment(
                comment_id=row[0], workspace_id=row[1], user_id=row[2],
                username=row[3], content=row[4], target_type=row[5],
                target_id=row[6], position=json.loads(row[7]) if row[7] else None,
                created_at=row[8], replies=json.loads(row[9]) if row[9] else None,
                resolved=bool(row[10])
            )
            comments.append(comment)
        
        conn.close()
        return comments

class RealtimeCollaborationManager:
    """实时协作管理器"""
    
    def __init__(self):
        self.db = CollaborationDatabase()
        self.active_connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.user_sessions: Dict[str, User] = {}
        self.workspace_cursors: Dict[str, Dict[str, Dict]] = {}  # workspace_id -> user_id -> cursor_data
        
    async def register_user(self, websocket, user_id: str, workspace_id: str):
        """注册用户连接"""
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = set()
        
        self.active_connections[workspace_id].add(websocket)
        
        # 更新用户状态
        user = self.db.get_user(user_id)
        if user:
            user.last_active = datetime.now().isoformat()
            user.current_workspace = workspace_id
            self.user_sessions[user_id] = user
            
            # 广播用户上线
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'user_joined',
                'user': asdict(user),
                'timestamp': datetime.now().isoformat()
            }, exclude=websocket)
    
    async def unregister_user(self, websocket, user_id: str, workspace_id: str):
        """注销用户连接"""
        if workspace_id in self.active_connections:
            self.active_connections[workspace_id].discard(websocket)
            
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]
        
        # 移除光标
        if workspace_id in self.workspace_cursors and user_id in self.workspace_cursors[workspace_id]:
            del self.workspace_cursors[workspace_id][user_id]
        
        # 广播用户离线
        if user_id in self.user_sessions:
            user = self.user_sessions[user_id]
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'user_left',
                'user': asdict(user),
                'timestamp': datetime.now().isoformat()
            }, exclude=websocket)
            
            del self.user_sessions[user_id]
    
    async def handle_message(self, websocket, message: Dict):
        """处理消息"""
        message_type = message.get('type')
        workspace_id = message.get('workspace_id')
        user_id = message.get('user_id')
        
        if message_type == 'cursor_move':
            await self.handle_cursor_move(workspace_id, user_id, message.get('data', {}))
        
        elif message_type == 'selection_change':
            await self.handle_selection_change(workspace_id, user_id, message.get('data', {}))
        
        elif message_type == 'comment_add':
            await self.handle_comment_add(workspace_id, user_id, message.get('data', {}))
        
        elif message_type == 'analysis_start':
            await self.handle_analysis_start(workspace_id, user_id, message.get('data', {}))
        
        elif message_type == 'chat_message':
            await self.handle_chat_message(workspace_id, user_id, message.get('data', {}))
    
    async def handle_cursor_move(self, workspace_id: str, user_id: str, data: Dict):
        """处理光标移动"""
        if workspace_id not in self.workspace_cursors:
            self.workspace_cursors[workspace_id] = {}
        
        # 更新光标位置
        self.workspace_cursors[workspace_id][user_id] = {
            'x': data.get('x', 0),
            'y': data.get('y', 0),
            'element': data.get('element', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # 广播光标位置
        user = self.user_sessions.get(user_id)
        if user:
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'cursor_update',
                'user_id': user_id,
                'username': user.username,
                'cursor': self.workspace_cursors[workspace_id][user_id]
            })
    
    async def handle_selection_change(self, workspace_id: str, user_id: str, data: Dict):
        """处理选择变化"""
        user = self.user_sessions.get(user_id)
        if user:
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'selection_update',
                'user_id': user_id,
                'username': user.username,
                'selection': data
            })
    
    async def handle_comment_add(self, workspace_id: str, user_id: str, data: Dict):
        """处理添加评论"""
        user = self.user_sessions.get(user_id)
        if user:
            comment = Comment(
                comment_id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                user_id=user_id,
                username=user.username,
                content=data.get('content', ''),
                target_type=data.get('target_type', 'general'),
                target_id=data.get('target_id', ''),
                position=data.get('position'),
                created_at=datetime.now().isoformat(),
                replies=[],
                resolved=False
            )
            
            # 保存到数据库
            self.db.add_comment(comment)
            
            # 广播新评论
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'comment_added',
                'comment': asdict(comment)
            })
    
    async def handle_analysis_start(self, workspace_id: str, user_id: str, data: Dict):
        """处理分析开始"""
        user = self.user_sessions.get(user_id)
        if user:
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'analysis_started',
                'user_id': user_id,
                'username': user.username,
                'analysis_type': data.get('analysis_type', ''),
                'timestamp': datetime.now().isoformat()
            })
    
    async def handle_chat_message(self, workspace_id: str, user_id: str, data: Dict):
        """处理聊天消息"""
        user = self.user_sessions.get(user_id)
        if user:
            await self.broadcast_to_workspace(workspace_id, {
                'type': 'chat_message',
                'user_id': user_id,
                'username': user.username,
                'avatar_url': user.avatar_url,
                'message': data.get('message', ''),
                'timestamp': datetime.now().isoformat()
            })
    
    async def broadcast_to_workspace(self, workspace_id: str, message: Dict, exclude=None):
        """向工作空间广播消息"""
        if workspace_id not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for websocket in self.active_connections[workspace_id]:
            if websocket == exclude:
                continue
                
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            self.active_connections[workspace_id].discard(websocket)
    
    def get_workspace_presence(self, workspace_id: str) -> Dict:
        """获取工作空间在线状态"""
        online_users = []
        cursors = {}
        
        for user_id, user in self.user_sessions.items():
            if user.current_workspace == workspace_id:
                online_users.append(asdict(user))
                
                if workspace_id in self.workspace_cursors and user_id in self.workspace_cursors[workspace_id]:
                    cursors[user_id] = self.workspace_cursors[workspace_id][user_id]
        
        return {
            'online_users': online_users,
            'cursors': cursors,
            'total_online': len(online_users)
        }

class CollaborationUI:
    """协作界面组件"""
    
    def __init__(self, collaboration_manager: RealtimeCollaborationManager):
        self.manager = collaboration_manager
    
    def create_workspace_panel(self, user_id: str) -> html.Div:
        """创建工作空间面板"""
        workspaces = self.manager.db.get_user_workspaces(user_id)
        
        return html.Div([
            # 头部
            html.Div([
                html.H4([
                    html.I(className="fas fa-users", style={'marginRight': '10px'}),
                    "协作工作空间"
                ]),
                html.Button([
                    html.I(className="fas fa-plus"),
                    " 新建工作空间"
                ], id="create-workspace", className="btn btn-primary")
            ], style={'display': 'flex', 'justifyContent': 'space-between', 
                     'alignItems': 'center', 'marginBottom': '20px'}),
            
            # 工作空间列表
            html.Div([
                self._create_workspace_card(ws) for ws in workspaces
            ], id="workspace-list"),
            
            # 创建工作空间模态框
            self._create_workspace_modal()
        ])
    
    def _create_workspace_card(self, workspace: Workspace) -> html.Div:
        """创建工作空间卡片"""
        return html.Div([
            html.Div([
                # 工作空间信息
                html.Div([
                    html.H5(workspace.name, style={'margin': '0 0 5px 0'}),
                    html.P(workspace.description, style={'margin': '0', 'color': '#666'}),
                    html.Small(f"创建于 {workspace.created_at[:10]}", style={'color': '#999'})
                ], style={'flex': '1'}),
                
                # 成员和操作
                html.Div([
                    html.Div([
                        html.I(className="fas fa-users", style={'marginRight': '5px'}),
                        f"{len(workspace.members)} 成员"
                    ], style={'marginBottom': '10px', 'fontSize': '0.9rem'}),
                    
                    html.Button([
                        html.I(className="fas fa-arrow-right"),
                        " 进入"
                    ], id=f"enter-workspace-{workspace.workspace_id}",
                       className="btn btn-outline-primary btn-sm")
                ])
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], className="workspace-card", style={
            'border': '1px solid #ddd',
            'borderRadius': '8px',
            'padding': '15px',
            'marginBottom': '10px',
            'backgroundColor': '#f8f9fa'
        })
    
    def _create_workspace_modal(self) -> html.Div:
        """创建工作空间模态框"""
        return html.Div([
            html.Div([
                html.Div([
                    # 头部
                    html.Div([
                        html.H4("创建新工作空间"),
                        html.Button("×", id="close-workspace-modal",
                                  style={'background': 'none', 'border': 'none',
                                        'fontSize': '24px', 'cursor': 'pointer'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between',
                             'alignItems': 'center', 'padding': '20px',
                             'borderBottom': '1px solid #dee2e6'}),
                    
                    # 内容
                    html.Div([
                        html.Div([
                            html.Label("工作空间名称"),
                            dcc.Input(
                                id="workspace-name",
                                type="text",
                                placeholder="输入工作空间名称...",
                                className="form-control"
                            )
                        ], style={'marginBottom': '15px'}),
                        
                        html.Div([
                            html.Label("描述"),
                            dcc.Textarea(
                                id="workspace-description",
                                placeholder="描述这个工作空间的用途...",
                                style={'width': '100%', 'height': '80px'},
                                className="form-control"
                            )
                        ], style={'marginBottom': '15px'}),
                        
                        html.Div([
                            html.Label("邀请成员 (邮箱)"),
                            dcc.Input(
                                id="workspace-members",
                                type="email",
                                placeholder="user@example.com",
                                className="form-control"
                            )
                        ])
                    ], style={'padding': '20px'}),
                    
                    # 底部
                    html.Div([
                        html.Button("取消", id="cancel-workspace",
                                  className="btn btn-secondary",
                                  style={'marginRight': '10px'}),
                        html.Button("创建", id="create-workspace-confirm",
                                  className="btn btn-primary")
                    ], style={'padding': '20px', 'textAlign': 'right',
                             'borderTop': '1px solid #dee2e6'})
                ])
            ], style={'backgroundColor': 'white', 'borderRadius': '8px',
                     'maxWidth': '500px', 'margin': '50px auto'})
        ], id="workspace-modal", style={
            'position': 'fixed', 'top': '0', 'left': '0', 'right': '0', 'bottom': '0',
            'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': '1050', 'display': 'none'
        })
    
    def create_collaboration_sidebar(self, workspace_id: str) -> html.Div:
        """创建协作侧边栏"""
        return html.Div([
            # 在线用户
            html.Div([
                html.H6([
                    html.I(className="fas fa-circle", 
                          style={'color': '#28a745', 'marginRight': '5px'}),
                    "在线成员"
                ]),
                html.Div(id="online-users-list")
            ], style={'marginBottom': '20px'}),
            
            # 实时聊天
            html.Div([
                html.H6([
                    html.I(className="fas fa-comments", style={'marginRight': '5px'}),
                    "团队聊天"
                ]),
                html.Div(
                    id="chat-messages",
                    style={'height': '200px', 'overflowY': 'auto',
                          'border': '1px solid #ddd', 'padding': '10px',
                          'marginBottom': '10px', 'borderRadius': '4px'}
                ),
                html.Div([
                    dcc.Input(
                        id="chat-input",
                        type="text",
                        placeholder="输入消息...",
                        style={'width': '100%'},
                        className="form-control"
                    ),
                    html.Button([
                        html.I(className="fas fa-paper-plane")
                    ], id="send-chat", className="btn btn-primary btn-sm",
                       style={'marginTop': '5px', 'width': '100%'})
                ])
            ], style={'marginBottom': '20px'}),
            
            # 评论列表
            html.Div([
                html.H6([
                    html.I(className="fas fa-comment-dots", style={'marginRight': '5px'}),
                    "评论"
                ]),
                html.Div(id="comments-list")
            ])
        ], style={
            'position': 'fixed', 'right': '0', 'top': '0', 'bottom': '0',
            'width': '300px', 'backgroundColor': '#f8f9fa',
            'borderLeft': '1px solid #ddd', 'padding': '20px',
            'overflowY': 'auto', 'zIndex': '1000'
        })
    
    def create_presence_indicators(self) -> html.Div:
        """创建在线状态指示器"""
        return html.Div([
            # 光标显示
            html.Div(id="user-cursors"),
            
            # 选择高亮
            html.Div(id="user-selections")
        ])

# 全局实例
collaboration_manager = RealtimeCollaborationManager()
collaboration_ui = CollaborationUI(collaboration_manager)