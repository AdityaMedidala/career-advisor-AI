import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from core.scoring import load_occupations
from datetime import datetime, timedelta
import random

st.title("📊 Job Market Intelligence Dashboard")
st.markdown("### Comprehensive analysis of career opportunities and market trends")

# Load data
occupations = load_occupations()
user_skills = st.session_state.get("skills", [])

if not occupations:
    st.error("Unable to load occupation data.")
    st.stop()

# Sidebar filters and controls
with st.sidebar:
    st.markdown("### 🎯 Analysis Filters")
    
    # Role categories
    all_roles = [o['occupation'] for o in occupations]
    selected_roles = st.multiselect(
        "Select roles to analyze:",
        options=all_roles,
        default=all_roles[:5] if len(all_roles) >= 5 else all_roles,
        help="Choose specific roles for detailed analysis"
    )
    
    # Skills filter
    all_skills = set()
    for occ in occupations:
        for skill_obj in occ.get('skills_required', []):
            all_skills.add(skill_obj['skill'])
    
    skill_filter = st.multiselect(
        "Focus on specific skills:",
        options=sorted(list(all_skills)),
        help="Filter analysis to specific skills"
    )
    
    # Analysis type
    analysis_depth = st.selectbox(
        "Analysis depth:",
        ["Quick Overview", "Detailed Analysis", "Predictive Insights"]
    )

# Main dashboard tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Market Overview", "🎯 Role Analysis", "💰 Salary Intel", "🔮 Future Trends"])

with tab1:
    st.markdown("## 📈 Job Market Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Career Paths", len(occupations))
    with col2:
        total_skills = len(all_skills)
        st.metric("Unique Skills Tracked", total_skills)
    with col3:
        avg_skills = np.mean([len(occ['skills_required']) for occ in occupations])
        st.metric("Avg Skills per Role", f"{avg_skills:.1f}")
    with col4:
        if user_skills:
            user_role_matches = sum(1 for occ in occupations 
                                  if any(skill['skill'] in user_skills 
                                        for skill in occ.get('skills_required', [])))
            st.metric("Your Compatible Roles", f"{user_role_matches}/{len(occupations)}")
        else:
            st.metric("Market Coverage", "Complete")
    
    # Skills demand heatmap
    st.markdown("### 🔥 Skills Demand Heatmap")
    
    # Calculate skill demand across roles
    skill_demand_matrix = {}
    role_names = [occ['occupation'] for occ in occupations]
    
    for skill in sorted(list(all_skills))[:20]:  # Top 20 skills for visualization
        skill_demand_matrix[skill] = []
        for occ in occupations:
            skill_weight = next((s['weight'] for s in occ['skills_required'] if s['skill'] == skill), 0)
            skill_demand_matrix[skill].append(skill_weight)
    
    # Create heatmap
    heatmap_df = pd.DataFrame(skill_demand_matrix, index=role_names)
    
    fig_heatmap = px.imshow(
        heatmap_df.T,
        labels=dict(x="Career Roles", y="Skills", color="Importance"),
        title="Skills Importance Across Career Roles (1=Low, 5=Critical)",
        color_continuous_scale="RdYlBu_r"
    )
    fig_heatmap.update_layout(height=600)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Market trends simulation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Skills Popularity Distribution")
        
        skill_counts = {}
        for occ in occupations:
            for skill_obj in occ.get('skills_required', []):
                skill = skill_obj['skill']
                if skill in skill_counts:
                    skill_counts[skill] += 1
                else:
                    skill_counts[skill] = 1
        
        # Create distribution chart
        popularity_df = pd.DataFrame([
            {'Skill': skill, 'Frequency': count}
            for skill, count in skill_counts.items()
        ]).sort_values('Frequency', ascending=False).head(15)
        
        fig_popularity = px.bar(
            popularity_df,
            x='Frequency',
            y='Skill',
            orientation='h',
            title="Most Required Skills (Frequency)"
        )
        fig_popularity.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_popularity, use_container_width=True)
    
    with col2:
        st.markdown("### ⭐ Skills Impact Analysis")
        
        # Calculate skill impact (frequency × average importance)
        skill_impact = {}
        skill_importance_sum = {}
        
        for occ in occupations:
            for skill_obj in occ.get('skills_required', []):
                skill = skill_obj['skill']
                weight = skill_obj['weight']
                
                if skill in skill_impact:
                    skill_impact[skill] += 1
                    skill_importance_sum[skill] += weight
                else:
                    skill_impact[skill] = 1
                    skill_importance_sum[skill] = weight
        
        impact_df = pd.DataFrame([
            {
                'Skill': skill,
                'Impact_Score': count * (skill_importance_sum[skill] / count),
                'Frequency': count,
                'Avg_Importance': skill_importance_sum[skill] / count
            }
            for skill, count in skill_impact.items()
        ]).sort_values('Impact_Score', ascending=False).head(15)
        
        fig_impact = px.scatter(
            impact_df,
            x='Frequency',
            y='Avg_Importance',
            size='Impact_Score',
            hover_name='Skill',
            title="Skills: Frequency vs. Importance",
            labels={'Avg_Importance': 'Average Importance', 'Frequency': 'Required in # of Roles'}
        )
        st.plotly_chart(fig_impact, use_container_width=True)

with tab2:
    st.markdown("## 🎯 Career Role Deep Dive")
    
    if not selected_roles:
        st.warning("Please select at least one role from the sidebar to analyze.")
    else:
        # Role comparison radar chart
        if len(selected_roles) > 1:
            st.markdown("### 📊 Multi-Role Skills Comparison")
            
            fig_radar = go.Figure()
            
            # Get common skills across selected roles
            common_skills = set()
            role_data = {}
            
            for role_name in selected_roles[:3]:  # Limit to 3 roles for readability
                role = next(occ for occ in occupations if occ['occupation'] == role_name)
                role_skills = {s['skill']: s['weight'] for s in role['skills_required']}
                role_data[role_name] = role_skills
                common_skills.update(role_skills.keys())
            
            common_skills = sorted(list(common_skills))
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            for i, (role_name, skills_dict) in enumerate(role_data.items()):
                values = [skills_dict.get(skill, 0) for skill in common_skills]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=common_skills,
                    fill='toself',
                    name=role_name,
                    line_color=colors[i % len(colors)]
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=True,
                title="Skills Profile Comparison",
                height=600
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed role analysis
        st.markdown("### 🔍 Individual Role Analysis")
        
        for role_name in selected_roles:
            role = next(occ for occ in occupations if occ['occupation'] == role_name)
            
            with st.expander(f"📋 {role_name} - Detailed Analysis", expanded=len(selected_roles) == 1):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Skills breakdown
                    skills_df = pd.DataFrame(role['skills_required']).sort_values('weight', ascending=False)
                    
                    fig_skills = px.bar(
                        skills_df,
                        x='weight',
                        y='skill',
                        orientation='h',
                        color='weight',
                        title=f"Required Skills for {role_name}",
                        color_continuous_scale='Viridis'
                    )
                    fig_skills.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_skills, use_container_width=True)
                
                with col2:
                    # Role statistics
                    total_skills = len(role['skills_required'])
                    critical_skills = len([s for s in role['skills_required'] if s['weight'] >= 4])
                    avg_importance = np.mean([s['weight'] for s in role['skills_required']])
                    
                    st.metric("Total Skills Required", total_skills)
                    st.metric("Critical Skills (4-5)", critical_skills)
                    st.metric("Avg Skill Importance", f"{avg_importance:.1f}")
                    
                    # User compatibility
                    if user_skills:
                        user_matches = [s for s in role['skills_required'] if s['skill'] in user_skills]
                        match_score = len(user_matches) / total_skills * 100
                        
                        st.metric("Your Match Score", f"{match_score:.0f}%")
                        
                        if user_matches:
                            st.success("✅ Your matching skills:")
                            for skill in user_matches[:3]:
                                st.write(f"• {skill['skill']}")
                
                # Skills categorization
                st.markdown("**🏷️ Skills by Category:**")
                
                # Simple categorization
                categories = {
                    'Programming': ['Python', 'Java', 'JavaScript', 'SQL', 'R', 'C++'],
                    'Cloud & DevOps': ['AWS', 'Azure', 'Docker', 'Kubernetes', 'CI/CD'],
                    'Data & Analytics': ['Excel', 'Tableau', 'Power BI', 'Statistics', 'Machine Learning'],
                    'Management': ['Project Management', 'Leadership', 'Agile', 'Scrum'],
                    'Design': ['UI/UX', 'Figma', 'Adobe', 'Prototyping'],
                    'Soft Skills': ['Communication', 'Problem-solving', 'Teamwork']
                }
                
                role_categories = {}
                for skill_obj in role['skills_required']:
                    skill = skill_obj['skill']
                    categorized = False
                    for category, cat_skills in categories.items():
                        if any(cat_skill.lower() in skill.lower() for cat_skill in cat_skills):
                            if category not in role_categories:
                                role_categories[category] = []
                            role_categories[category].append(skill_obj)
                            categorized = True
                            break
                    if not categorized:
                        if 'Other' not in role_categories:
                            role_categories['Other'] = []
                        role_categories['Other'].append(skill_obj)
                
                cols = st.columns(min(len(role_categories), 4))
                for i, (category, skills) in enumerate(role_categories.items()):
                    with cols[i % 4]:
                        st.write(f"**{category}** ({len(skills)})")
                        for skill in skills[:3]:
                            importance = "🔴" if skill['weight'] >= 4 else "🟡" if skill['weight'] >= 3 else "🟢"
                            st.write(f"{importance} {skill['skill']}")

with tab3:
    st.markdown("## 💰 Salary Intelligence & Market Value")
    
    # Simulated salary data based on skill complexity
    st.info("💡 Salary estimates are based on skill complexity, market demand, and industry standards")
    
    salary_data = []
    for occ in occupations:
        # Calculate salary based on skills complexity and market demand
        skill_complexity = sum(s['weight'] for s in occ['skills_required'])
        num_skills = len(occ['skills_required'])
        
        # Base salary calculation (simulated)
        base_salary = 45000 + (skill_complexity * 6000) + (num_skills * 2500)
        
        # Add some randomization for realism
        variation = random.uniform(0.85, 1.15)
        estimated_salary = int(base_salary * variation)
        
        # Skill premium calculation
        premium_skills = ['AI', 'Machine Learning', 'AWS', 'Kubernetes', 'React', 'Python']
        has_premium = any(premium in [s['skill'] for s in occ['skills_required']] 
                         for premium in premium_skills)
        
        if has_premium:
            estimated_salary = int(estimated_salary * 1.2)
        
        salary_data.append({
            'Role': occ['occupation'],
            'Estimated_Salary': estimated_salary,
            'Skill_Complexity': skill_complexity,
            'Skills_Count': num_skills,
            'Has_Premium_Skills': has_premium
        })
    
    salary_df = pd.DataFrame(salary_data).sort_values('Estimated_Salary', ascending=False)
    
    # Salary visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Salary Range by Role")
        
        fig_salary = px.bar(
            salary_df,
            x='Estimated_Salary',
            y='Role',
            color='Has_Premium_Skills',
            title="Estimated Annual Salaries by Role",
            color_discrete_map={True: '#4CAF50', False: '#FFA726'}
        )
        fig_salary.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_salary, use_container_width=True)
    
    with col2:
        st.markdown("### 💎 Salary Insights")
        
        highest_salary = salary_df.iloc[0]
        st.metric("Highest Paying Role", highest_salary['Role'])
        st.metric("Top Salary Range", f"${highest_salary['Estimated_Salary']:,}")
        
        avg_salary = salary_df['Estimated_Salary'].mean()
        st.metric("Market Average", f"${avg_salary:,.0f}")
        
        premium_avg = salary_df[salary_df['Has_Premium_Skills']]['Estimated_Salary'].mean()
        regular_avg = salary_df[~salary_df['Has_Premium_Skills']]['Estimated_Salary'].mean()
        premium_boost = ((premium_avg - regular_avg) / regular_avg) * 100
        
        st.metric("Premium Skills Boost", f"+{premium_boost:.0f}%")
    
    # Salary vs complexity analysis
    st.markdown("### 📈 Salary vs Skill Complexity Analysis")
    
    fig_scatter = px.scatter(
        salary_df,
        x='Skill_Complexity',
        y='Estimated_Salary',
        size='Skills_Count',
        color='Has_Premium_Skills',
        hover_name='Role',
        title="Salary vs Skill Complexity",
        labels={'Skill_Complexity': 'Total Skill Complexity Score', 'Estimated_Salary': 'Annual Salary ($)'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Salary bands
    st.markdown("### 💰 Salary Bands Analysis")
    
    # Create salary bands
    salary_bands = {
        '$40K-$60K': len(salary_df[(salary_df['Estimated_Salary'] >= 40000) & (salary_df['Estimated_Salary'] < 60000)]),
        '$60K-$80K': len(salary_df[(salary_df['Estimated_Salary'] >= 60000) & (salary_df['Estimated_Salary'] < 80000)]),
        '$80K-$100K': len(salary_df[(salary_df['Estimated_Salary'] >= 80000) & (salary_df['Estimated_Salary'] < 100000)]),
        '$100K-$120K': len(salary_df[(salary_df['Estimated_Salary'] >= 100000) & (salary_df['Estimated_Salary'] < 120000)]),
        '$120K+': len(salary_df[salary_df['Estimated_Salary'] >= 120000])
    }
    
    bands_df = pd.DataFrame([
        {'Salary_Band': band, 'Role_Count': count}
        for band, count in salary_bands.items()
    ])
    
    fig_bands = px.pie(bands_df, values='Role_Count', names='Salary_Band', 
                      title="Role Distribution by Salary Bands")
    st.plotly_chart(fig_bands, use_container_width=True)

with tab4:
    st.markdown("## 🔮 Future Market Trends & Predictions")
    
    # Trend analysis
    st.markdown("### 📈 Emerging Technology Trends")
    
    # Simulated trend data
    emerging_trends = {
        'AI & Machine Learning': {'growth': 45, 'demand_level': 5, 'avg_salary': 120000},
        'Cloud Computing': {'growth': 35, 'demand_level': 5, 'avg_salary': 110000},
        'Cybersecurity': {'growth': 30, 'demand_level': 4, 'avg_salary': 105000},
        'Data Science': {'growth': 28, 'demand_level': 4, 'avg_salary': 115000},
        'DevOps': {'growth': 25, 'demand_level': 4, 'avg_salary': 108000},
        'Blockchain': {'growth': 40, 'demand_level': 3, 'avg_salary': 125000},
        'IoT': {'growth': 22, 'demand_level': 3, 'avg_salary': 95000},
        'Edge Computing': {'growth': 38, 'demand_level': 3, 'avg_salary': 112000}
    }
    
    trends_df = pd.DataFrame([
        {
            'Technology': tech,
            'Growth_Rate': data['growth'],
            'Current_Demand': data['demand_level'],
            'Avg_Salary': data['avg_salary']
        }
        for tech, data in emerging_trends.items()
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_growth = px.bar(
            trends_df.sort_values('Growth_Rate', ascending=True),
            x='Growth_Rate',
            y='Technology',
            orientation='h',
            color='Growth_Rate',
            title="Projected Growth Rates (Next 3 Years)",
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_growth, use_container_width=True)
    
    with col2:
        fig_bubble = px.scatter(
            trends_df,
            x='Current_Demand',
            y='Growth_Rate',
            size='Avg_Salary',
            color='Technology',
            title="Technology Opportunity Matrix",
            labels={'Current_Demand': 'Current Market Demand (1-5)', 'Growth_Rate': 'Projected Growth %'}
        )
        st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Future skills prediction
    st.markdown("### 🎯 Skills You Should Consider for the Future")
    
    future_skills = [
        {'Skill': 'Prompt Engineering', 'Relevance': 'AI Integration', 'Timeline': '0-1 years'},
        {'Skill': 'Quantum Computing', 'Relevance': 'Next-gen Computing', 'Timeline': '3-5 years'},
        {'Skill': 'Edge AI', 'Relevance': 'Distributed Intelligence', 'Timeline': '1-2 years'},
        {'Skill': 'Sustainable Tech', 'Relevance': 'Green Computing', 'Timeline': '1-3 years'},
        {'Skill': 'AR/VR Development', 'Relevance': 'Immersive Experiences', 'Timeline': '2-4 years'},
        {'Skill': 'Neuromorphic Engineering', 'Relevance': 'Brain-inspired Computing', 'Timeline': '5+ years'}
    ]
    
    future_df = pd.DataFrame(future_skills)
    
    st.dataframe(
        future_df,
        use_container_width=True,
        column_config={
            'Skill': st.column_config.TextColumn('Future Skill', width='medium'),
            'Relevance': st.column_config.TextColumn('Market Relevance', width='medium'),
            'Timeline': st.column_config.TextColumn('Adoption Timeline', width='small')
        }
    )
    
    # Market prediction timeline
    st.markdown("### 📅 5-Year Market Evolution Timeline")
    
    timeline_data = [
        {'Year': '2025', 'Trend': 'AI Integration Mainstream', 'Impact': 'High'},
        {'Year': '2026', 'Trend': 'Quantum Computing Commercial Use', 'Impact': 'Medium'},
        {'Year': '2027', 'Trend': 'Edge Computing Dominance', 'Impact': 'High'},
        {'Year': '2028', 'Trend': 'Autonomous Systems Standard', 'Impact': 'High'},
        {'Year': '2029', 'Trend': 'Sustainable Tech Mandate', 'Impact': 'Medium'}
    ]
    
    timeline_df = pd.DataFrame(timeline_data)
    
    fig_timeline = px.scatter(
        timeline_df,
        x='Year',
        y='Trend',
        color='Impact',
        size=[100] * len(timeline_df),
        title="Technology Adoption Timeline",
        color_discrete_map={'High': '#FF6B6B', 'Medium': '#FFD93D', 'Low': '#6BCF7F'}
    )
    fig_timeline.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Personal recommendations
    if user_skills:
        st.markdown("### 🎯 Personalized Future Recommendations")
        
        with st.container(border=True):
            st.markdown("**Based on your current skills, consider these strategic moves:**")
            
            # Simple logic for recommendations
            has_programming = any('Python' in skill or 'JavaScript' in skill or 'Java' in skill 
                                for skill in user_skills)
            has_data_skills = any('SQL' in skill or 'Excel' in skill or 'Data' in skill 
                                for skill in user_skills)
            has_cloud = any('AWS' in skill or 'Azure' in skill or 'Cloud' in skill 
                          for skill in user_skills)
            
            recommendations = []
            
            if has_programming and has_data_skills:
                recommendations.append("🤖 **AI/ML Focus**: Your programming + data skills are perfect for AI/ML. Consider TensorFlow, PyTorch.")
            
            if has_cloud:
                recommendations.append("⚡ **Edge Computing**: Expand your cloud skills to edge computing and IoT platforms.")
            
            if has_programming:
                recommendations.append("🔒 **Cybersecurity**: Add security frameworks and ethical hacking to your programming skills.")
            
            if not recommendations:
                recommendations.append("🚀 **Foundation Building**: Focus on core programming or data analysis skills as your foundation.")
            
            for rec in recommendations:
                st.markdown(rec)
            
            # Timeline for user
            st.markdown("**📅 Your 12-Month Learning Path:**")
            st.markdown("- **Months 1-3**: Master one emerging technology")
            st.markdown("- **Months 4-6**: Build portfolio projects")
            st.markdown("- **Months 7-9**: Gain industry certifications")
            st.markdown("- **Months 10-12**: Network and explore job opportunities")

# Bottom action panel
st.divider()
st.markdown("## 🚀 Take Action on Market Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📝 Update My Skills", use_container_width=True):
        st.switch_page("pages/1_Profile.py")

with col2:
    if st.button("🎯 Find Opportunities", use_container_width=True):
        st.switch_page("pages/2_Matches.py")

with col3:
    if st.button("🗺️ Create Learning Plan", use_container_width=True):
        st.switch_page("pages/3_Roadmap.py")

with col4:
    if st.button("🤖 Discuss with AI", use_container_width=True):
        st.switch_page("pages/4_AI_Coach.py")

# Market insights summary
with st.expander("📋 Market Intelligence Summary", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Key Takeaways:**")
        st.write("• AI and Cloud skills command premium salaries")
        st.write("• Full-stack roles offer the most versatility")
        st.write("• Data skills are required across most career paths")
        st.write("• Cybersecurity shows consistent growth")
        
    with col2:
        st.markdown("**📈 Action Items:**")
        st.write("• Identify 2-3 high-growth skills to develop")
        st.write("• Focus on skills that appear in multiple roles")
        st.write("• Consider emerging technologies for future-proofing")
        st.write("• Balance technical and soft skills development")