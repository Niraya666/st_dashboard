import streamlit as st
import pandas as pd
import os

DATA_FILE = "llm_services.csv"

# 初始化数据存储
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "模型名称",
        "服务器名称", 
        "最大Token数",
        "Temperature",
        "端口号",
        "GPU编号",
        "启动时间",
        "是否支持tool-using",
        "是否支持多模态",
        "是否支持推理模式",
        "vllm版本",
        "运行状态"
    ])
    df.to_csv(DATA_FILE, index=False)
else:
    df = pd.read_csv(DATA_FILE)

# 侧边栏表单
with st.sidebar:
    st.header("添加新服务")
    with st.form("service_form"):
        model_name = st.text_input("模型名称*", help="例如: chatglm3-6b")
        server_name = st.text_input("服务器名称*", help="例如: gpu01")
        max_tokens = st.number_input("最大Token数", min_value=1, value=4096)
        temperature = st.slider("Temperature", 0.0, 2.0, 0.8)
        port = st.number_input("端口号*", min_value=1024, max_value=65535, value=8000)
        gpu_ids = st.multiselect(
            "GPU编号",
            options=[str(i) for i in range(16)],
            default=["0"],
            help="选择使用的GPU编号"
        )
        tool_using = st.checkbox("支持tool-using")
        multimodal = st.checkbox("支持多模态")
        inference = st.checkbox("支持推理模式")
        vllm_version = st.text_input("vllm版本", help="例如: 0.2.0")
        is_running = st.checkbox("是否运行中", value=True)
        
        if st.form_submit_button("提交"):
            if not model_name or not server_name or not port:
                st.error("请填写必填字段（带*号）")
            else:
                new_entry = {
                    "模型名称": model_name,
                    "服务器名称": server_name,
                    "最大Token数": max_tokens,
                    "Temperature": temperature,
                    "端口号": port,
                    "GPU编号": ", ".join(gpu_ids),
                    "启动时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "是否支持tool-using": "是" if tool_using else "否",
                    "是否支持多模态": "是" if multimodal else "否", 
                    "是否支持推理模式": "是" if inference else "否",
                    "vllm版本": vllm_version,
                    "运行状态": "运行中" if is_running else "已停止"
                }
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                updated_df.to_csv(DATA_FILE, index=False)
                st.success("服务添加成功！")
                df = updated_df  # 更新内存中的数据

# 主界面
st.title("LLM服务监控仪表盘")
st.header("运行中服务列表")

# 显示数据表格
if not df.empty:
    # 添加删除功能
    selected_indices = st.multiselect("选择要删除的服务", df.index)
    
    if st.button("删除选中服务"):
        df = df.drop(selected_indices).reset_index(drop=True)
        df.to_csv(DATA_FILE, index=False)
        st.experimental_rerun()
    
    # 显示带样式的表格
    st.dataframe(
        df.style.applymap(
            lambda x: "color: #4CAF50" if isinstance(x, str) and x in ["是", "运行中"] else (
                "color: #f44336" if isinstance(x, str) and x in ["否", "已停止"] else ""
            )
        ),
        use_container_width=True
    )
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总服务数", len(df))
    with col2:
        st.metric("使用中的GPU总数", sum(len(g.split(",")) for g in df["GPU编号"]))
    with col3:
        running_services = len(df[df["运行状态"] == "运行中"])
        st.metric("运行中服务数", running_services)
    with col4:
        st.metric("最新服务", df.iloc[-1]["模型名称"] if len(df) > 0 else "无")
else:
    st.warning("当前没有运行中的服务")
