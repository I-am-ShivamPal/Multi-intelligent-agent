import pandas as pd
import matplotlib.pyplot as plt

# Read student scores dataset
student_df = pd.read_csv('dataset/student_scores.csv')

# Read patient health dataset  
patient_df = pd.read_csv('dataset/patient_health.csv')

# Create plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Student Scores - Marks vs Work Hours Studied
# Calculate average marks across all subjects
marks_cols = ['math_score', 'history_score', 'physics_score', 'chemistry_score', 
              'biology_score', 'english_score', 'geography_score']
student_df['average_marks'] = student_df[marks_cols].mean(axis=1)

ax1.scatter(student_df['weekly_self_study_hours'], student_df['average_marks'], alpha=0.6)
ax1.set_xlabel('Weekly Self Study Hours')
ax1.set_ylabel('Average Marks')
ax1.set_title('Student Scores: Average Marks vs Work Hours Studied')
ax1.grid(True, alpha=0.3)

# Plot 2: Patient Health - Risk Category vs Timestamp
# Convert timestamp to datetime
patient_df['Timestamp'] = pd.to_datetime(patient_df['Timestamp'])

# Count risk categories over time
risk_counts = patient_df.groupby(['Timestamp', 'Risk Category']).size().unstack(fill_value=0)

# Plot stacked area chart
ax2.stackplot(risk_counts.index, risk_counts['High Risk'], risk_counts['Low Risk'], 
              labels=['High Risk', 'Low Risk'], alpha=0.7)
ax2.set_xlabel('Timestamp')
ax2.set_ylabel('Count')
ax2.set_title('Patient Health: Risk Category vs Timestamp')
ax2.legend()
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()