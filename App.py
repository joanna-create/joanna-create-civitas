import json
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Civitas Dashboard", layout="wide", page_icon="🏗")
st.title("🏗 Welcome to Civitas Construction Dashboard!")
st.markdown("### Your all-in-one tool for managing construction projects 🚀")
st.markdown("---")

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'username' not in st.session_state:
    st.session_state.username = None


# Custom serializer for datetime objects


def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# Save projects to JSON


def save_projects():
    try:
        with open("projects.json", "w") as file:
            json.dump(st.session_state.projects, file, indent=4, default=custom_serializer)
    except Exception as e:
        st.error(f"Error saving projects: {e}")


# Load projects from JSON


def load_projects():
    try:
        with open("projects.json", "r") as file:
            st.session_state.projects = json.load(file)
    except FileNotFoundError:
        st.session_state.projects = []


# Login/Register System


def login_register():
    with st.sidebar:
        st.header("🔑 Login/Register")
        action_choice = st.radio("Choose an action", ["Login", "Register"])

        if action_choice == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if username == "admin" and password == "admin":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Admin"
                    st.session_state.username = username
                    st.success(f"Welcome back, Admin!")
                elif username == "user" and password == "user":
                    st.session_state.logged_in = True
                    st.session_state.user_role = "User"
                    st.session_state.username = username
                    st.success(f"Welcome back, {username}!")
                else:
                    st.error("Invalid credentials. Try again.")
                    st.warning("Make sure you enter 'admin' as the username and password to test the login!")

        elif action_choice == "Register":
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if new_username and new_password == confirm_password:
                    st.success(f"Account created successfully for {new_username}!")
                else:
                    st.error("Passwords do not match or fields are empty.")


# Display Login/Register if not logged in


if not st.session_state.logged_in:
    login_register()
else:
    st.sidebar.header(f"👋 Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    # Tabs for Dashboard
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📂 Project Overview", "📊 Progress Tracking", "💰 Financials",
                                                  "✅ Task Management", "📄 Documents", "💼 Interim Claims"])

    # Tab 1: Project Overview
    with tab1:
        st.header("📂 Project Overview")
        st.markdown("View and manage all your projects here.")
        project_action = st.radio("Choose an action", ["Register New Project", "View Existing Projects"])

        if project_action == "Register New Project":
            with st.form(key="project_form"):
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.text_input("Project Name")
                    project_id = st.text_input("Project ID")
                    client_name = st.text_input("Client Name")
                with col2:
                    start_date = st.date_input("Start Date")
                    end_date = st.date_input("End Date", min_value=start_date)
                    budget = st.number_input("Budget ($)", min_value=0, value=100000)

                submit = st.form_submit_button("Register Project")
                if submit:
                    if not project_name or not project_id or not client_name:
                        st.error("All fields are required!")
                    else:
                        new_project = {
                            "name": project_name,
                            "id": project_id,
                            "client": client_name,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                            "budget": budget,
                            "progress": 0,
                            "tasks": [],
                            "documents": [],
                            "interim_claims": []  # Ensure interim_claims is initialized as an empty list
                        }

                        st.session_state.projects.append(new_project)
                        save_projects()
                        st.success(f"Project {project_name} registered successfully!")

        elif project_action == "View Existing Projects":
            load_projects()

            if st.session_state.projects:
                project_names = [proj["name"] for proj in st.session_state.projects]
                selected_project = st.selectbox("Select a Project to Track", project_names,
                                                key="existing_project_select")
                project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)
                st.write("**Project Details:**")
                st.json(project_data)

                # Option to delete project
                if st.button("Delete Project", key=f"delete_{selected_project}"):
                    st.session_state.projects = [proj for proj in st.session_state.projects if
                                                 proj["name"] != selected_project]
                    save_projects()
                    st.success(f"Project {selected_project} deleted successfully!")
            else:
                st.info("No projects available. Please register a new project.")

    # Tab 2: Progress Tracking
    with tab2:
        st.header("📊 Progress Tracking")
        st.write("Monitor project progress with interactive visuals.")
        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project to Track", project_names, key="progress_tracking_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            if "progress" not in project_data:
                project_data["progress"] = 0  # Initialize progress if not present

            progress = st.slider("Update Progress (%)", 0, 100, project_data["progress"],
                                 key=f"progress_slider_{selected_project}")
            project_data["progress"] = progress
            save_projects()
            st.success(f"Updated progress for {project_data['name']} to {progress}%!")

            # Display progress using a gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=progress,
                title={"text": "Project Progress"},
                gauge={"axis": {"range": [0, 100]}}))
            st.plotly_chart(fig)

            # Display overall progress graph
            st.subheader("Project Progress - Milestone Overview")
            milestone_data = {
                'Milestone': ['Planning', 'Design', 'Construction', 'Completion'],
                'Progress': [20, 40, 60, progress]
            }
            progress_fig = px.bar(milestone_data, x='Milestone', y='Progress', title="Project Milestones")
            st.plotly_chart(progress_fig)

    # Tab 3: Financials
    with tab3:
        st.header("💰 Financial Overview")
        st.write("Track budgets and spending dynamically.")
        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project for Financials", project_names, key="financials_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            spent = st.number_input("Spent Amount ($)", min_value=0, value=0, key=f"spent_input_{selected_project}")
            remaining = project_data["budget"] - spent
            st.write(f"Remaining Budget: ${remaining}")

            # Display financial breakdown
            financial_data = {
                "Spent": spent,
                "Remaining": remaining,
                "Total Budget": project_data["budget"]
            }
            financial_fig = px.pie(names=list(financial_data.keys()), values=list(financial_data.values()),
                                   title="Budget Breakdown")
            st.plotly_chart(financial_fig)

    # Tab 4: Task Management
    with tab4:
        st.header("📅 Task Management & Scheduling")
        st.write("Manage and schedule tasks efficiently for each project.")

        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project", project_names, key="task_management_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            # Display existing tasks
            st.subheader("Current Tasks")
            if project_data["tasks"]:
                for task in project_data["tasks"]:
                    st.write(f"**Task:** {task['task_name']}")
                    st.write(f"**Assigned To:** {task['assigned_to']}")
                    st.write(f"**Priority:** {task['priority']}")
                    st.write(f"**Deadline:** {task['deadline']}")
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Description:** {task['description']}")

                    # Task status update
                    status_update = st.selectbox(f"Update Status for {task['task_name']}",
                                                 ["Pending", "In Progress", "Completed"],
                                                 key=f"status_update_{task['task_name']}")
                    if st.button(f"Update Status for {task['task_name']}", key=f"update_button_{task['task_name']}"):
                        task["status"] = status_update
                        save_projects()
                        st.success(f"Status of {task['task_name']} updated to {status_update}.")

                    # Task comments
                    st.subheader(f"Comments on {task['task_name']}")
                    task_comments = st.text_area(f"Add a comment for {task['task_name']}",
                                                 key=f"comment_{task['task_name']}")
                    if st.button(f"Save Comment for {task['task_name']}", key=f"comment_button_{task['task_name']}"):
                        if 'comments' not in task:
                            task['comments'] = []
                        task['comments'].append(task_comments)
                        save_projects()
                        st.success(f"Comment added for {task['task_name']}.")

            else:
                st.info("No tasks available. Please add new tasks.")

            # Adding a new task
            st.subheader("Add a New Task")
            task_name = st.text_input("Task Name")
            assigned_to = st.text_input("Assign to")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            deadline = st.date_input("Deadline")
            description = st.text_area("Task Description")

            if st.button("Add Task"):
                if task_name and assigned_to and description:
                    new_task = {
                        "task_name": task_name,
                        "assigned_to": assigned_to,
                        "priority": priority,
                        "deadline": deadline,
                        "status": "Pending",  # Default status
                        "description": description,
                        "comments": []  # Comments section for the task
                    }
                    project_data["tasks"].append(new_task)
                    save_projects()
                    st.success(f"New task '{task_name}' added successfully!")
                else:
                    st.error("Please fill in all the required fields.")

            # Task Search & Filter
            st.subheader("Search and Filter Tasks")
            search_query = st.text_input("Search for a task")
            filtered_tasks = [task for task in project_data["tasks"] if
                              search_query.lower() in task["task_name"].lower()]

            if filtered_tasks:
                for task in filtered_tasks:
                    st.write(f"**Task Name:** {task['task_name']}")
                    st.write(f"Assigned to: {task['assigned_to']}")
                    st.write(f"Priority: {task['priority']}")
                    st.write(f"Deadline: {task['deadline']}")
                    st.write(f"Status: {task['status']}")
            else:
                st.info("No tasks found matching the search query.")

            # Gantt Chart Representation (Optional)
            st.subheader("Task Timeline (Gantt Chart)")
            # You can implement this using a package like Plotly or Altair for interactive Gantt charts
            # Example placeholder for Gantt chart integration
            # Gantt chart would be shown here for visualizing task timelines.

            # Task Scheduling - Gantt chart integration can also be added here
            st.write("Gantt Chart could be integrated here to visualize tasks' timelines.")

    # Tab 5: Documents
    with tab5:
        st.header("📄 Document Management")
        st.write("Upload and manage project documents.")

        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project for Documents", project_names,
                                            key="document_management_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            # Show uploaded documents
            st.subheader("Uploaded Documents")
            if project_data["documents"]:
                for idx, doc in enumerate(project_data["documents"]):
                    st.write(f"**Document {idx + 1}:**")
                    st.text(f"Filename: {doc.name}")
                    st.text(f"Type: {doc.type}")
                    st.download_button(label="Download", data=doc, file_name=doc.name)
                    if st.button(f"Delete Document {idx + 1}", key=f"delete_doc_{idx}"):
                        project_data["documents"].remove(doc)
                        save_projects()
                        st.success(f"Document {doc.name} deleted successfully!")
            else:
                st.info("No documents uploaded yet. Please upload a new document.")

            # Upload multiple documents
            uploaded_files = st.file_uploader("Upload Documents", type=["pdf", "docx", "png", "jpg", "jpeg"],
                                              accept_multiple_files=True)
            if uploaded_files:
                for uploaded_file in uploaded_files:  # Renaming 'file' to 'uploaded_file'
                    project_data["documents"].append(uploaded_file)
                save_projects()
                st.success("Documents uploaded successfully!")

            # Document categorization (example: project-specific tags)
            categories = ["Contracts", "Plans", "Invoices", "Reports"]
            doc_category = st.selectbox("Select Document Category", categories)
            st.text(f"Selected category: {doc_category}")

            # Option to add metadata for documents
            st.subheader("Add Document Metadata")
            doc_title = st.text_input("Document Title")
            doc_description = st.text_area("Document Description")
            if st.button("Save Metadata"):
                if doc_title and doc_description:
                    metadata = {"Title": doc_title, "Description": doc_description}
                    st.session_state.document_metadata = metadata
                    st.success("Metadata saved!")
                else:
                    st.error("Please fill in both the title and description fields.")

    # Tab 6: Interim Claims
    with tab6:
        st.header("💼 Interim Claims")
        st.write("Manage interim claims and track payments.")

        if st.session_state.projects:
            project_names = [proj["name"] for proj in st.session_state.projects]
            selected_project = st.selectbox("Select a Project for Interim Claims", project_names,
                                            key="interim_claims_select")
            project_data = next(proj for proj in st.session_state.projects if proj["name"] == selected_project)

            # Ensure interim_claims is initialized
            if "interim_claims" not in project_data:
                project_data["interim_claims"] = []

            interim_claim_action = st.radio("Interim Claims Action",
                                            ["View Claims", "Add New Claim", "Update Claim Status"])

            if interim_claim_action == "Add New Claim":
                # Add New Claim Form
                claim_amount = st.number_input("Claim Amount ($)", min_value=0)
                claim_status = st.selectbox("Claim Status", ["Pending", "Approved", "Rejected"])
                payment_schedule = st.date_input("Payment Schedule")
                notes = st.text_area("Claim Notes", placeholder="Add any notes or comments")

                if st.button("Add Claim"):
                    project_data["interim_claims"].append({
                        "amount": claim_amount,
                        "status": claim_status,
                        "payment_schedule": payment_schedule.isoformat(),
                        "notes": notes
                    })
                    save_projects()
                    st.success(f"Claim of ${claim_amount} added successfully!")

            elif interim_claim_action == "View Claims":
                # View Claims in Table Form with Search and Filter
                if project_data["interim_claims"]:
                    # Convert claims data to DataFrame
                    claims_df = pd.DataFrame(project_data["interim_claims"])
                    claims_df.index += 1  # Start indexing from 1
                    claims_df = claims_df.rename(columns={
                        "amount": "Claim Amount ($)",
                        "status": "Claim Status",
                        "payment_schedule": "Payment Schedule",
                        "notes": "Claim Notes"
                    })

                    # Filter by status, amount, or date
                    filter_status = st.selectbox("Filter by Claim Status", ["All", "Pending", "Approved", "Rejected"],
                                                 index=0)
                    if filter_status != "All":
                        claims_df = claims_df[claims_df["Claim Status"] == filter_status]

                    # Search bar for amount or notes
                    search_term = st.text_input("Search Claims", "")
                    if search_term:
                        claims_df = claims_df[
                            claims_df.apply(lambda row: row.astype(str).str.contains(search_term).any(), axis=1)]

                    # Sorting options
                    sort_by = st.selectbox("Sort Claims By", ["Claim Amount ($)", "Payment Schedule", "Claim Status"],
                                           index=0)
                    claims_df = claims_df.sort_values(by=sort_by, ascending=True)

                    # Display the claims table
                    st.dataframe(claims_df)

                    # Export Claims to CSV
                    if st.button("Export Claims to CSV"):
                        csv = claims_df.to_csv(index=False)
                        st.download_button("Download CSV", csv, "claims_data.csv", "text/csv")

                else:
                    st.info("No interim claims found for this project.")

            elif interim_claim_action == "Update Claim Status":
                # Update Existing Claim Status
                if project_data["interim_claims"]:
                    claim_options = [f"Claim #{idx + 1}" for idx in range(len(project_data["interim_claims"]))]
                    selected_claim = st.selectbox("Select a Claim to Update", claim_options)

                    # Get the selected claim's index
                    claim_idx = claim_options.index(selected_claim)
                    selected_claim_data = project_data["interim_claims"][claim_idx]

                    # Allow user to update the status of the selected claim
                    new_status = st.selectbox("Update Claim Status", ["Pending", "Approved", "Rejected"],
                                              index=["Pending", "Approved", "Rejected"].index(
                                                  selected_claim_data["status"]))

                    if st.button(f"Update Status for {selected_claim}"):
                        # Update the claim's status
                        project_data["interim_claims"][claim_idx]["status"] = new_status
                        save_projects()
                        st.success(f"The status for {selected_claim} has been updated to {new_status}.")
                else:
                    st.info("No interim claims found for this project.")

            # Claim History or Audit Trail
            if project_data["interim_claims"]:
                st.subheader("Claim History / Audit Trail")
                # Updated for handling missing 'notes'
                audit_data = []
                for claim in project_data["interim_claims"]:
                    audit_data.append({
                        "Claim Amount": claim["amount"],
                        "Status": claim["status"],
                        "Payment Schedule": claim["payment_schedule"],
                        "Notes": claim.get("notes", "No notes provided")
                        # Using get to avoid errors if 'notes' is missing
                    })

                if audit_data:
                    audit_df = pd.DataFrame(audit_data)
                    st.write(audit_df)
