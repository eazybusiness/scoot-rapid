#!/usr/bin/env python3
"""
ScootRapid Diagram Generator
Creates professional diagrams for documentation
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configure matplotlib for professional look
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

class ScootRapidDiagramGenerator:
    def __init__(self, output_dir="../diagrams"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # ScootRapid Colors
        self.colors = {
            'primary': '#1a237e',
            'secondary': '#3949ab',
            'accent': '#5c6bc0',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'light': '#e8eaf6',
            'dark': '#283593'
        }
    
    def create_architecture_diagram(self):
        """Create system architecture diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_title('ScootRapid - System Architecture', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Define components
        components = {
            'Web Frontend': {'pos': (2, 8), 'size': (2, 1), 'color': self.colors['primary']},
            'REST API': {'pos': (2, 6), 'size': (2, 1), 'color': self.colors['secondary']},
            'Flask App': {'pos': (2, 4), 'size': (2, 1), 'color': self.colors['accent']},
            'MySQL DB': {'pos': (2, 2), 'size': (2, 1), 'color': self.colors['success']},
            'Railway Cloud': {'pos': (6, 5), 'size': (2, 2), 'color': self.colors['warning']},
            'Gunicorn': {'pos': (6, 3), 'size': (2, 1), 'color': self.colors['dark']},
        }
        
        # Draw components
        for name, comp in components.items():
            rect = plt.Rectangle(comp['pos'], comp['size'][0], comp['size'][1], 
                                facecolor=comp['color'], edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            ax.text(comp['pos'][0] + comp['size'][0]/2, comp['pos'][1] + comp['size'][1]/2, 
                    name, ha='center', va='center', fontweight='bold', color='white')
        
        # Draw arrows
        arrows = [
            ((3, 7.5), (3, 7)),  # Frontend to API
            ((3, 5.5), (3, 5)),  # API to Flask
            ((3, 3.5), (3, 3)),  # Flask to DB
            ((4, 6), (6, 6)),    # API to Railway
            ((7, 5), (7, 4)),    # Railway to Gunicorn
            ((8, 4), (4, 4)),    # Gunicorn to Flask
        ]
        
        for start, end in arrows:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['dark']))
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add legend
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, fc=self.colors['primary'], label='Frontend'),
            plt.Rectangle((0, 0), 1, 1, fc=self.colors['secondary'], label='API'),
            plt.Rectangle((0, 0), 1, 1, fc=self.colors['success'], label='Database'),
            plt.Rectangle((0, 0), 1, 1, fc=self.colors['warning'], label='Cloud'),
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scootrapid_architecture.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Architecture diagram created")
    
    def create_database_schema(self):
        """Create database ER diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_title('ScootRapid - Database Schema', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Define tables
        tables = {
            'users': {
                'pos': (2, 8), 'size': (3, 2),
                'fields': ['id (PK)', 'email (UNIQUE)', 'password_hash', 'first_name', 'last_name', 'role', 'created_at']
            },
            'scooters': {
                'pos': (7, 8), 'size': (3, 2.5),
                'fields': ['id (PK)', 'identifier (UNIQUE)', 'model', 'brand', 'status', 'battery_level', 'latitude', 'longitude', 'provider_id (FK)']
            },
            'rentals': {
                'pos': (2, 4), 'size': (3, 2.5),
                'fields': ['id (PK)', 'user_id (FK)', 'scooter_id (FK)', 'start_time', 'end_time', 'duration_minutes', 'total_cost', 'status']
            },
            'payments': {
                'pos': (7, 4), 'size': (3, 2),
                'fields': ['id (PK)', 'rental_id (FK)', 'amount', 'payment_method', 'status', 'transaction_id']
            }
        }
        
        # Draw tables
        for name, table in tables.items():
            # Table box
            rect = plt.Rectangle(table['pos'], table['size'][0], table['size'][1], 
                                facecolor=self.colors['light'], edgecolor=self.colors['primary'], linewidth=2)
            ax.add_patch(rect)
            
            # Table name
            ax.text(table['pos'][0] + table['size'][0]/2, table['pos'][1] + table['size'][1] - 0.2, 
                   name.upper(), ha='center', va='top', fontweight='bold', color=self.colors['primary'])
            
            # Fields
            for i, field in enumerate(table['fields']):
                y_pos = table['pos'][1] + table['size'][1] - 0.5 - (i * 0.25)
                ax.text(table['pos'][0] + 0.1, y_pos, field, ha='left', va='center', fontsize=8)
        
        # Draw relationships
        relationships = [
            ((3.5, 8), (3.5, 6.5)),  # users to rentals
            ((8.5, 8), (8.5, 6.5)),  # scooters to rentals
            ((3.5, 4), (7, 5)),      # rentals to payments
        ]
        
        for start, end in relationships:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['dark']))
        
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 11)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scootrapid_database_schema.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Database schema diagram created")
    
    def create_api_flow_diagram(self):
        """Create API flow diagram using Plotly"""
        fig = go.Figure()
        
        # Add nodes
        nodes = [
            ('Mobile App', 1, 5, '#1a237e'),
            ('Web Frontend', 1, 3, '#3949ab'),
            ('API Gateway', 3, 4, '#5c6bc0'),
            ('Auth Service', 5, 5, '#4caf50'),
            ('Scooter Service', 5, 3, '#ff9800'),
            ('Rental Service', 5, 1, '#f44336'),
            ('MySQL Database', 7, 3, '#283593'),
        ]
        
        for name, x, y, color in nodes:
            fig.add_shape(
                type="rect",
                x0=x-0.4, y0=y-0.3, x1=x+0.4, y1=y+0.3,
                fillcolor=color, line=dict(color="black", width=2)
            )
            fig.add_annotation(
                x=x, y=y, text=name,
                showarrow=False, font=dict(color="white", size=10)
            )
        
        # Add arrows
        arrows = [
            ((1.4, 5), (2.6, 4.5)),
            ((1.4, 3), (2.6, 3.5)),
            ((3.4, 4.5), (4.6, 5)),
            ((3.4, 3.5), (4.6, 3)),
            ((3.4, 2.5), (4.6, 1)),
            ((5.4, 5), (6.6, 3.5)),
            ((5.4, 3), (6.6, 3)),
            ((5.4, 1), (6.6, 2.5)),
        ]
        
        for start, end in arrows:
            fig.add_annotation(
                ax=end[0], ay=end[1], x=start[0], y=start[1],
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="black"
            )
        
        fig.update_layout(
            title="ScootRapid - API Flow Diagram",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
            plot_bgcolor='white'
        )
        
        fig.write_image(f"{self.output_dir}/scootrapid_api_flow.png", width=800, height=600, scale=2)
        print("✅ API flow diagram created")
    
    def create_performance_metrics(self):
        """Create performance metrics dashboard"""
        # Generate sample data
        time_periods = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
        api_calls = [45, 32, 156, 289, 198, 87]
        response_times = [120, 95, 145, 180, 165, 110]
        active_users = [12, 8, 67, 145, 98, 43]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('API Calls per Hour', 'Response Time (ms)', 'Active Users', 'System Load'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # API Calls
        fig.add_trace(
            go.Scatter(x=time_periods, y=api_calls, name='API Calls', 
                      line=dict(color=self.colors['primary'], width=3)),
            row=1, col=1
        )
        
        # Response Times
        fig.add_trace(
            go.Scatter(x=time_periods, y=response_times, name='Response Time', 
                      line=dict(color=self.colors['warning'], width=3)),
            row=1, col=2
        )
        
        # Active Users
        fig.add_trace(
            go.Bar(x=time_periods, y=active_users, name='Active Users', 
                  marker_color=self.colors['success']),
            row=2, col=1
        )
        
        # System Load
        cpu_usage = [25, 18, 45, 67, 52, 31]
        memory_usage = [35, 28, 58, 72, 61, 38]
        
        fig.add_trace(
            go.Scatter(x=time_periods, y=cpu_usage, name='CPU %', 
                      line=dict(color=self.colors['error'], width=3)),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=time_periods, y=memory_usage, name='Memory %', 
                      line=dict(color=self.colors['dark'], width=3)),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="ScootRapid - Performance Metrics Dashboard",
            showlegend=True,
            height=800
        )
        
        fig.write_image(f"{self.output_dir}/scootrapid_performance.png", width=1200, height=800, scale=2)
        print("✅ Performance metrics dashboard created")
    
    def create_deployment_diagram(self):
        """Create deployment architecture diagram"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_title('ScootRapid - Deployment Architecture', fontsize=16, fontweight='bold', color=self.colors['primary'])
        
        # Railway Cloud
        railway_rect = plt.Rectangle((1, 1), 10, 8, facecolor='#f0f4f8', edgecolor=self.colors['primary'], linewidth=3)
        ax.add_patch(railway_rect)
        ax.text(6, 8.5, 'Railway Cloud Platform', ha='center', fontsize=14, fontweight='bold', color=self.colors['primary'])
        
        # Components
        components = {
            'Load Balancer': {'pos': (2, 7), 'size': (2, 0.8), 'color': self.colors['secondary']},
            'Gunicorn WSGI': {'pos': (5, 7), 'size': (2, 0.8), 'color': self.colors['accent']},
            'Flask Application': {'pos': (8, 7), 'size': (2, 0.8), 'color': self.colors['primary']},
            'MySQL Database': {'pos': (3.5, 5), 'size': (2.5, 0.8), 'color': self.colors['success']},
            'Redis Cache': {'pos': (7.5, 5), 'size': (2, 0.8), 'color': self.colors['warning']},
            'Static Files': {'pos': (2, 3), 'size': (2, 0.8), 'color': self.colors['dark']},
            'SSL Certificate': {'pos': (5, 3), 'size': (2, 0.8), 'color': self.colors['error']},
            'Monitoring': {'pos': (8, 3), 'size': (2, 0.8), 'color': self.colors['secondary']},
        }
        
        for name, comp in components.items():
            rect = plt.Rectangle(comp['pos'], comp['size'][0], comp['size'][1], 
                                facecolor=comp['color'], edgecolor='black', linewidth=1, alpha=0.8)
            ax.add_patch(rect)
            ax.text(comp['pos'][0] + comp['size'][0]/2, comp['pos'][1] + comp['size'][1]/2, 
                    name, ha='center', va='center', fontweight='bold', color='white', fontsize=9)
        
        # Connections
        connections = [
            ((3, 7.4), (5, 7.4)),
            ((7, 7.4), (8, 7.4)),
            ((6, 6.8), (4.75, 5.8)),
            ((6, 6.8), (8.5, 5.8)),
            ((3, 6.8), (3, 3.8)),
            ((6, 6.8), (6, 3.8)),
            ((9, 6.8), (9, 3.8)),
        ]
        
        for start, end in connections:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['dark']))
        
        # External connections
        ax.annotate('Users', xy=(2, 8.5), xytext=(-0.5, 8.5),
                   arrowprops=dict(arrowstyle='->', lw=3, color=self.colors['success']),
                   fontsize=12, fontweight='bold')
        
        ax.set_xlim(-1, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scootrapid_deployment.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ Deployment diagram created")
    
    def generate_all_diagrams(self):
        """Generate all diagrams"""
        print("🎨 Generating ScootRapid diagrams...")
        self.create_architecture_diagram()
        self.create_database_schema()
        self.create_api_flow_diagram()
        self.create_performance_metrics()
        self.create_deployment_diagram()
        print(f"✅ All diagrams saved to {self.output_dir}/")

if __name__ == "__main__":
    generator = ScootRapidDiagramGenerator()
    generator.generate_all_diagrams()
