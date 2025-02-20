import streamlit as st
import pandas as pd
import os

DATA_FILE = "llm_services.csv"

# Initialize data storage
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "Model Name",
        "Server Name", 
        "Max Tokens",
        "Port",
        "GPU IDs",
        "Start Time",
        "Tool Using Support",
        "Multimodal Support", 
        "Inference Support",
        "VLLM Version",
        "Status"
    ])
    df.to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)

# Sidebar form
with st.sidebar:
    st.header("Add New Service")
    with st.form("service_form"):
        model_name = st.text_input("Model Name*", help="e.g.: chatglm3-6b")
        server_name = st.selectbox(
            "Server Name*",
            options=["hgcnbdptps01", "hgcnbdpips01"]
        )
        max_tokens = st.number_input("Max Tokens", min_value=1, value=4096)
        port = st.number_input("Port*", min_value=1024, max_value=65535, value=8000)
        gpu_ids = st.multiselect(
            "GPU IDs",
            options=[str(i) for i in range(16)],
            default=["0"],
            help="Select GPU IDs to use"
        )
        tool_using = st.checkbox("Tool Using Support")
        multimodal = st.checkbox("Multimodal Support")
        inference = st.checkbox("Inference Support")
        vllm_version = st.text_input("VLLM Version", help="e.g.: 0.2.0")
        is_running = st.checkbox("Running Status", value=True)
        
        if st.form_submit_button("Submit"):
            if not model_name or not server_name or not port:
                st.error("Please fill in required fields (with *)")
            else:
                new_entry = {
                    "Model Name": model_name,
                    "Status": "Running" if is_running else "Stopped",
                    "Server Name": server_name,
                    "Max Tokens": max_tokens,
                    "Port": port,
                    "GPU IDs": ", ".join(gpu_ids),
                    "Start Time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Tool Using Support": "Yes" if tool_using else "No",
                    "Multimodal Support": "Yes" if multimodal else "No",
                    "Inference Support": "Yes" if inference else "No",
                    "VLLM Version": vllm_version
                    
                }
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                updated_df.to_csv(DATA_FILE, index=False)
                st.success("Service added successfully!")
                df = updated_df

# Main interface
st.title("LLM Service Monitoring Dashboard")
st.header("Running Services List")

# Display data table
if not df.empty:
    # Add delete functionality
    selected_indices = st.multiselect("Select services to delete", df.index)
    
    # Add status update functionality
    status_update_idx = st.selectbox("Select service to update status", df.index)
    new_status = st.radio("Select new status", ["Running", "Stopped"])
    
    if st.button("Update Status"):
        df.loc[status_update_idx, "Status"] = new_status
        df.to_csv(DATA_FILE, index=False)
        st.experimental_rerun()
    
    if st.button("Delete Selected Services"):
        df = df.drop(selected_indices).reset_index(drop=True)
        df.to_csv(DATA_FILE, index=False)
        st.experimental_rerun()
    
    # Display styled table
    st.dataframe(
        df.style.applymap(
            lambda x: "color: #4CAF50" if isinstance(x, str) and x in ["Yes", "Running"] else (
                "color: #f44336" if isinstance(x, str) and x in ["No", "Stopped"] else ""
            )
        ),
        use_container_width=True
    )
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Services", len(df))
    with col2:
        st.metric("Total GPUs in Use", sum(len(g.split(",")) for g in df["GPU IDs"]))
    with col3:
        running_services = len(df[df["Status"] == "Running"])
        st.metric("Running Services", running_services)
    with col4:
        st.metric("Latest Service", df.iloc[-1]["Model Name"] if len(df) > 0 else "None")
else:
    st.warning("No running services currently")
