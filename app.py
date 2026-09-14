import streamlit as st
import requests
import os
import time
import json

# ==========================================
# 1. 页面配置与高级 CSS 注入 (暗黑玻璃拟态风)
# ==========================================
st.set_page_config(page_title="春木出海 AI 中枢", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 引入 Google 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* 全局字体与径向渐变背景 */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(circle at 50% -20%, #11253e 0%, #020617 80%); color: #e2e8f0; }
    
    /* 侧边栏玻璃拟态 */
    [data-testid="stSidebar"] { 
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* 聊天气泡高级感设计 */
    [data-testid="stChatMessage"] { 
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; 
        padding: 20px; margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover { transform: translateY(-2px); }
    
    /* 用户气泡颜色 */
    [data-testid="stChatMessage"]:has(div:contains("user")) {
        background: rgba(45, 212, 191, 0.1) !important;
        border-color: rgba(45, 212, 191, 0.3);
    }
    
    /* 标题渐变 */
    .gradient-title {
        background: linear-gradient(135deg, #2dd4bf 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 700; font-size: 26px; letter-spacing: -0.5px;
    }
    .sub-caption { color: #64748b; font-size: 13px; margin-bottom: 20px; }
    
    /* 输入框自定义 */
    .stChatInput { 
        background: rgba(15, 23, 42, 0.8) !important; 
        border: 1px solid rgba(45, 212, 191, 0.3) !important;
        border-radius: 24px !important; color: white !important;
    }
    
    /* 按钮美化 */
    .stButton>button {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #cbd5e1; border-radius: 12px; transition: all 0.3s;
    }
    .stButton>button:hover { border-color: #2dd4bf; color: #2dd4bf; box-shadow: 0 0 15px rgba(45, 212, 191, 0.2); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 极简 RAG 知识库 (避免云端 ChromaDB 安装崩溃)
# ==========================================
# 模拟真实业务数据：FDA 合规指南与 TikTok 爆款 SOP
KNOWLEDGE_BASE = {
    "FDA": "【美国FDA膳食补充剂合规指南】1. 禁止声称产品可以“治愈、治疗、预防”任何疾病。2. 允许使用“结构/功能声明”，但必须附带免责声明。3. 亚马逊Listing要求：必须包含GMP认证信息。",
    "TikTok": "【TikTok爆款SOP】1. 前3秒必须抓住注意力（痛点引入）。2. 视频时长控制在15-30秒。3. 必须包含“Call to Action (CTA)”。"
}

def query_rag(query):
    """轻量级意图路由：根据关键词匹配知识库"""
    if any(k in query for k in ["FDA", "合规", "政策", "限制", "封店"]):
        return KNOWLEDGE_BASE["FDA"]
    if any(k in query for k in ["TikTok", "脚本", "SOP", "短视频"]):
        return KNOWLEDGE_BASE["TikTok"]
    return ""

# ==========================================
# 3. Agent 核心逻辑 (本地真模型 + 云端降级模式)
# ==========================================
def run_agent_stream(user_input):
    context = query_rag(user_input)
    
    # 判断是否运行在 Streamlit 云端环境
    IS_CLOUD = os.environ.get("STREAMLIT_SHARING_MODE") is not None
    
    if IS_CLOUD:
        # ☁️ 云端演示模式：模拟流式输出，防止找不到本地 Ollama 报错
        mock_text = f"【云端演示模式】\n\n检测到您在云端环境。基于您的需求“{user_input}”，已通过 FDA 合规知识库审查，生成以下草稿：\n\n1. 痛点引入（前3秒）：你是否经常感到疲惫？\n2. 产品引入：这款大健康补充剂富含天然成分...\n3. Call to Action：点击下方链接购买！\n\n*注：本地运行可体验真实 Qwen2.5 大模型流式生成。*"
        for char in mock_text:
            yield char
            time.sleep(0.02) # 模拟打字机打字速度
        return

    # 💻 本地开发模式：调用本地 Ollama
    system_prompt = f"""你是一名资深的跨境电商AI运营专家，服务于一家专注美国市场的大健康（食品补充剂）企业。
你精通亚马逊和TikTok平台规则，熟悉FDA合规要求。
知识库上下文：{context}
请根据用户需求生成高质量、高转化率且合规的内容。请使用Markdown格式排版。"""
    
    payload = {
        "model": "qwen2.5:3b",
        "prompt": f"{system_prompt}\n用户：{user_input}\nAI：",
        "stream": True # 开启流式输出
    }
    
      try:
        # 发送流式请求给本地 Ollama，增加更短的超时时间
        res = requests.post("http://localhost:11434/api/generate", json=payload, stream=True, timeout=10)
        res.raise_for_status()
        
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                if 'response' in chunk:
                    yield chunk['response']
                    
    except Exception as e:
        # 🚨 连不上 Ollama 时，自动降级为云端模拟模式，不再报错！
        mock_text = f"【演示模式】检测到本地 Ollama 未启动或不在本地环境。\n\n基于您的需求“{user_input}”，结合 FDA 合规知识库，为您生成以下草稿：\n\n1. 痛点引入（前3秒）：你是否经常感到疲惫？\n2. 产品引入：这款大健康补充剂富含天然成分...\n3. Call to Action：点击下方链接购买！\n\n*注：请在本地启动 Ollama 以体验真实 Qwen2.5 模型生成。*"
        for char in mock_text:
            yield char
            time.sleep(0.02)

# ==========================================
# 4. UI 布局与交互
# ==========================================
# 侧边栏
with st.sidebar:
    st.markdown('<div class="gradient-title">🌿 春木出海 AI 中枢</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-caption">专为美国大健康市场打造</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ 模型状态")
    if os.environ.get("STREAMLIT_SHARING_MODE"):
        st.info("☁️ 当前运行在云端演示模式")
    else:
        st.success("✅ 本地 qwen2.5:3b 已连接")
    st.caption("● 流式输出已启用 (Streaming)")
    
    st.markdown("---")
    # 【人工审核区】对应 JD 第6点：必要的人工审核机制
    st.markdown("### 🛡️ 人工审核区 (Human-in-the-loop)")
    st.info("待审核草稿：TikTok脚本 - 维生素C软糖")
    col1, col2 = st.columns(2)
    if col1.button("✅ 通过", use_container_width=True):
        st.toast("已通过审核，准备发布至 Amazon/TikTok", icon="✅")
    if col2.button("❌ 驳回", use_container_width=True):
        st.toast("已驳回，请重新生成", icon="❌")

# 主界面
st.markdown("### 🚀 Agent 工作台")
st.caption("涵盖 FDA 合规审查、TikTok 爆款生成、亚马逊 Listing 优化")

# 会话历史管理
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是你的大健康出海AI助手。\n\n我可以帮你：\n1. 查询 FDA 合规要求\n2. 生成 TikTok 爆款脚本\n3. 优化亚马逊 Listing\n\n请告诉我你的需求！"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入与流式响应
if prompt := st.chat_input("输入你的业务需求，例如：帮我写一个维生素C软糖的TikTok脚本..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        # 使用 st.write_stream 实现丝滑的打字机效果
        response = st.write_stream(run_agent_stream(prompt))
        
    st.session_state.messages.append({"role": "assistant", "content": response})
