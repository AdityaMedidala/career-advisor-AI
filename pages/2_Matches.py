import streamlit as st
from core.scoring import load_occupations, rank_roles
from core import jobs
from core import llm
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.title("2. 🎯 Your Perfect Job Matches")
st.markdown("### Discover roles that align with your unique skill profile")

skills = st.session_state.get("skills", [])
if not skills:
    st.warning("⚠️ Please create your profile first to find job matches.")
    if st.button("📝 Create Profile Now"):
        st.switch_page("pages/1_Profile.py")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filter & Refine")
    
    # Skills refinement
    st.markdown("**Your Skills:**")
    edited_skills = st.multiselect(
        "Modify your skills for better matches:",
        options=sorted(list(set(skills + ["Python", "SQL", "JavaScript", "AWS", "Docker", "Git", 
                                        "Excel", "Tableau", "React", "Node.js", "Linux", "Agile"]))),
        default=skills,
        key="skills_filter"
    )
    
    # Match filters
    st.markdown("**Match Criteria:**")
    min_score = st.slider("Minimum Match Score %", 0, 100, 20, 5)
    show_count = st.selectbox("Number of matches to show", [3, 5, 8, 10], index=1)
    
    # Career preferences integration
    if st.session_state.get("user_profile"):
        profile = st.session_state.user_profile
        st.markdown("**Your Preferences:**")
        
        if profile.get("risk_tolerance"):
            st.write(f"Risk Tolerance: {profile['risk_tolerance']}")
        if profile.get("work_style"):
            st.write(f"Work Style: {profile['work_style']}")
        if profile.get("time_commitment"):
            st.write(f"Learning Time: {profile['time_commitment']}h/week")

# Update session skills
st.session_state.skills = edited_skills

# Main content area
if not edited_skills:
    st.error("Please select at least one skill to find matches.")
    st.stop()

# Load and rank occupations
occs = load_occupations()
all_matches = rank_roles(edited_skills, occs, top_k=len(occs))
filtered_matches = [m for m in all_matches if (m['score'] * 100) >= min_score][:show_count]

st.session_state.matches = filtered_matches

# Overview metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Your Skills", len(edited_skills))
with col2:
    best_match = max([m['score'] * 100 for m in filtered_matches]) if filtered_matches else 0
    st.metric("Best Match", f"{best_match:.0f}%")
with col3:
    avg_gaps = sum(len(m['gaps']) for m in filtered_matches) / len(filtered_matches) if filtered_matches else 0
    st.metric("Avg Skill Gaps", f"{avg_gaps:.1f}")
with col4:
    total_careers = len([m for m in all_matches if m['score'] > 0])
    st.metric("Compatible Careers", total_careers)

st.divider()

# Match results
if not filtered_matches:
    st.warning(f"No matches found with {min_score}% minimum score. Try lowering the threshold or adding more skills.")
    st.info("💡 **Suggestion:** Add more skills to your profile or lower the minimum match score in the sidebar.")
else:
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🎯 Top Matches", "📊 Skills Analysis", "🔍 Detailed Comparison"])
    
    with tab1:
        st.markdown(f"### Your Top {len(filtered_matches)} Career Matches")
        
        for i, m in enumerate(filtered_matches):
            score_percentage = int(m['score'] * 100)
            
            with st.container(border=True):
                # Header with role and score
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {i+1}. {m['occupation']}")
                with col2:
                    color = "green" if score_percentage >= 70 else "orange" if score_percentage >= 50 else "red"
                    st.markdown(f"<h3 style='color: {color}; text-align: right;'>{score_percentage}%</h3>", 
                              unsafe_allow_html=True)
                
                # Progress bar
                st.progress(score_percentage / 100, text=f"{score_percentage}% Skill Alignment")
                
                # Skills breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    # Matching skills
                    required_skills = {s['skill']: s['weight'] for s in m["skills_required"]}
                    matching_skills = [skill for skill in edited_skills if skill in required_skills]
                    
                    if matching_skills:
                        st.markdown("**✅ Your Matching Skills:**")
                        for skill in matching_skills:
                            importance = required_skills[skill]
                            stars = "⭐" * importance
                            st.write(f"• **{skill}** {stars}")
                    
                with col2:
                    # Skill gaps
                    if m["gaps"]:
                        st.markdown("**📚 Skills to Develop:**")
                        gap_importance = {gap: next(s['weight'] for s in m["skills_required"] if s['skill'] == gap) 
                                        for gap in m["gaps"]}
                        sorted_gaps = sorted(m["gaps"], key=lambda x: gap_importance[x], reverse=True)
                        
                        for gap in sorted_gaps:
                            importance = gap_importance[gap]
                            urgency = "🔴 Critical" if importance >= 4 else "🟡 Important" if importance >= 3 else "🟢 Nice to have"
                            st.write(f"• **{gap}** - {urgency}")
                    else:
                        st.success("🎉 Perfect skill alignment!")
                
                # Action buttons
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Smart job search
                    user_skills_set = set(edited_skills)
                    required_skills_set = set(s['skill'] for s in m["skills_required"])
                    matching_user_skills = list(user_skills_set.intersection(required_skills_set))
                    smart_link = jobs.refined_google_jobs(m["occupation"], matching_user_skills)
                    st.link_button("🔍 Smart Job Search", smart_link, use_container_width=True)
                
                with col2:
                    if st.button(f"📈 Skill Analysis", key=f"analyze_{i}"):
                        st.session_state[f"analyze_{m['occupation']}"] = True
                
                with col3:
                    if st.button(f"🎯 Build Roadmap", key=f"roadmap_{i}"):
                        st.session_state.selected_role = m
                        st.switch_page("pages/3_Roadmap.py")
                
                # Expandable detailed analysis
                if st.session_state.get(f"analyze_{m['occupation']}", False):
                    with st.expander("📊 Detailed Role Analysis", expanded=True):
                        
                        # Skill importance radar chart
                        skills_for_chart = [s['skill'] for s in m["skills_required"]]
                        weights_for_chart = [s['weight'] for s in m["skills_required"]]
                        user_has_skill = [1 if skill in edited_skills else 0 for skill in skills_for_chart]
                        
                        fig = go.Figure()
                        
                        # Required skills
                        fig.add_trace(go.Scatterpolar(
                            r=weights_for_chart,
                            theta=skills_for_chart,
                            fill='toself',
                            name='Required Level',
                            line_color='lightblue'
                        ))
                        
                        # User's skills
                        user_weights = [weights_for_chart[i] if user_has_skill[i] else 0 
                                       for i in range(len(skills_for_chart))]
                        fig.add_trace(go.Scatterpolar(
                            r=user_weights,
                            theta=skills_for_chart,
                            fill='toself',
                            name='Your Level',
                            line_color='green'
                        ))
                        
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                            showlegend=True,
                            title=f"Skills Profile: {m['occupation']}",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Gap analysis
                        if m["gaps"]:
                            st.markdown("**🎯 Learning Priority Matrix:**")
                            gap_df = pd.DataFrame([
                                {
                                    'Skill': gap,
                                    'Importance': next(s['weight'] for s in m["skills_required"] if s['skill'] == gap),
                                    'Priority': 'High' if next(s['weight'] for s in m["skills_required"] if s['skill'] == gap) >= 4 else 'Medium' if next(s['weight'] for s in m["skills_required"] if s['skill'] == gap) >= 3 else 'Low'
                                }
                                for gap in m["gaps"]
                            ])
                            
                            fig_priority = px.bar(
                                gap_df.sort_values('Importance', ascending=True),
                                x='Importance',
                                y='Skill',
                                color='Priority',
                                orientation='h',
                                title="Skill Gap Priorities",
                                color_discrete_map={'High': '#FF6B6B', 'Medium': '#FFE66D', 'Low': '#4ECDC4'}
                            )
                            st.plotly_chart(fig_priority, use_container_width=True)
    
    with tab2:
        st.markdown("### 📊 Skills Analysis Across All Matches")
        
        if filtered_matches:
            # Skills demand analysis
            all_required_skills = {}
            for match in filtered_matches:
                for skill_obj in match["skills_required"]:
                    skill = skill_obj['skill']
                    weight = skill_obj['weight']
                    if skill in all_required_skills:
                        all_required_skills[skill] += weight
                    else:
                        all_required_skills[skill] = weight
            
            # Create skills demand chart
            skills_demand_df = pd.DataFrame([
                {
                    'Skill': skill,
                    'Total_Demand': demand,
                    'You_Have': skill in edited_skills
                }
                for skill, demand in all_required_skills.items()
            ]).sort_values('Total_Demand', ascending=False)
            
            fig_demand = px.bar(
                skills_demand_df.head(15),
                x='Skill',
                y='Total_Demand',
                color='You_Have',
                title="Most In-Demand Skills Across Your Matches",
                color_discrete_map={True: '#4CAF50', False: '#FF5722'}
            )
            fig_demand.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_demand, use_container_width=True)
            
            # Skills gap summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔴 Most Critical Missing Skills:**")
                missing_skills = skills_demand_df[~skills_demand_df['You_Have']].head(5)
                for _, row in missing_skills.iterrows():
                    roles_requiring = sum(1 for m in filtered_matches 
                                        if row['Skill'] in [s['skill'] for s in m['skills_required']])
                    st.write(f"• **{row['Skill']}** - Required in {roles_requiring}/{len(filtered_matches)} matches")
            
            with col2:
                st.markdown("**✅ Your Strongest Assets:**")
                your_skills = skills_demand_df[skills_demand_df['You_Have']].head(5)
                for _, row in your_skills.iterrows():
                    roles_requiring = sum(1 for m in filtered_matches 
                                        if row['Skill'] in [s['skill'] for s in m['skills_required']])
                    st.write(f"• **{row['Skill']}** - Valued in {roles_requiring}/{len(filtered_matches)} matches")
    
    with tab3:
        st.markdown("### 🔍 Side-by-Side Role Comparison")
        
        if len(filtered_matches) >= 2:
            # Role selection for comparison
            comparison_roles = st.multiselect(
                "Select up to 3 roles to compare:",
                options=[m['occupation'] for m in filtered_matches],
                default=[m['occupation'] for m in filtered_matches[:min(3, len(filtered_matches))]]
            )
            
            if len(comparison_roles) >= 2:
                selected_matches = [m for m in filtered_matches if m['occupation'] in comparison_roles]
                
                # Comparison table
                comparison_data = []
                all_skills = set()
                for match in selected_matches:
                    for skill_obj in match['skills_required']:
                        all_skills.add(skill_obj['skill'])
                
                for skill in sorted(all_skills):
                    row = {'Skill': skill}
                    for match in selected_matches:
                        skill_weight = next((s['weight'] for s in match['skills_required'] if s['skill'] == skill), 0)
                        if skill in edited_skills and skill_weight > 0:
                            row[match['occupation']] = f"✅ {skill_weight}/5"
                        elif skill_weight > 0:
                            row[match['occupation']] = f"❌ {skill_weight}/5"
                        else:
                            row[match['occupation']] = "—"
                    comparison_data.append(row)
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Summary comparison
                st.markdown("**📈 Quick Comparison:**")
                cols = st.columns(len(selected_matches))
                
                for i, match in enumerate(selected_matches):
                    with cols[i]:
                        st.markdown(f"**{match['occupation']}**")
                        st.metric("Match Score", f"{int(match['score'] * 100)}%")
                        st.metric("Skill Gaps", len(match['gaps']))
                        st.metric("Total Skills Required", len(match['skills_required']))
        else:
            st.info("Add more skills or lower the minimum match score to see more roles for comparison.")

# Action buttons at bottom
st.divider()
st.markdown("### 🚀 Next Steps")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📝 Update Profile", use_container_width=True):
        st.switch_page("pages/1_Profile.py")

with col2:
    if st.button("🗺️ Create Roadmap", use_container_width=True):
        if filtered_matches:
            st.session_state.selected_role = filtered_matches[0]
        st.switch_page("pages/3_Roadmap.py")

with col3:
    if st.button("🤖 AI Career Coach", use_container_width=True):
        st.switch_page("pages/4_AI_Coach.py")

with col4:
    if st.button("📊 Market Analysis", use_container_width=True):
        st.switch_page("pages/5_Market_Insights.py")

# Skill improvement suggestions
if filtered_matches:
    with st.expander("💡 Quick Skill Boost Recommendations"):
        st.markdown("**Add these high-impact skills to improve your match scores:**")
        
        # Find skills that appear in multiple matches but user doesn't have
        skill_impact = {}
        for match in filtered_matches:
            for skill_obj in match['skills_required']:
                skill = skill_obj['skill']
                if skill not in edited_skills:
                    if skill in skill_impact:
                        skill_impact[skill] += skill_obj['weight']
                    else:
                        skill_impact[skill] = skill_obj['weight']
        
        top_impact_skills = sorted(skill_impact.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for skill, impact in top_impact_skills:
            roles_count = sum(1 for m in filtered_matches 
                            if skill in [s['skill'] for s in m['skills_required']])
            st.write(f"• **{skill}** - Would improve {roles_count} matches (Impact: {impact})")
            
            # Quick add button
            if st.button(f"Add {skill}", key=f"quick_add_{skill}"):
                current_skills = set(st.session_state.skills)
                current_skills.add(skill)
                st.session_state.skills = sorted(list(current_skills))
                st.rerun()