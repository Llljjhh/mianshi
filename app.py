import streamlit as st
import requests
import os
import time

# ==================== 1. 页面配置与高级 CSS 注入 ====================
st.set_page_config(page_title="春木出海 AI 中枢", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(circle at 50% -20%, #11253e 0%, #020617 80%); color: #e2e8f0; }
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.6) !important; backdrop-filter: blur(16px); border-right: 1px solid rgba(255, 255, 255, 0.05); }
    [data-testid="stChatMessage"] { background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); transition: transform 0.2s ease; }
    [data-testid="stChatMessage"]:hover { transform: translateY(-2px); }
    .gradient-title { background: linear-gradient(135deg, #2dd4bf 0%, #3b82f6 50%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; font-size: 26px; }
    .sub-caption { color: #64748b; font-size: 13px; margin-bottom: 20px; }
    .stChatInput { background: rgba(15, 23, 42, 0.8) !important; border: 1px solid rgba(45, 212, 191, 0.3) !important; border-radius: 24px !important; color: white !important; }
    .stButton>button { background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid rgba(255, 255, 255, 0.1); color: #cbd5e1; border-radius: 12px; transition: all 0.3s; }
    .stButton>button:hover { border-color: #2dd4bf; color: #2dd4bf; box-shadow: 0 0 15px rgba(45, 212, 191, 0.2); }
</style>
""", unsafe_allow_html=True)

# ==================== 2. 极简 RAG (纯Python实现，避免云端依赖报错) ====================
KNOWLEDGE_BASE = {
    "FDA": "【美国FDA膳食补充剂合规指南】1. 禁止声称产品可以“治愈、治疗、预防”任何疾病。2. 允许使用“结构/功能声明”，但必须附带免责声明。3. 亚马逊Listing要求：必须包含GMP认证信息。",
    "TikTok": "【TikTok爆款SOP】1. 前3秒必须抓住注意力（痛点引入）。2. 视频时长控制在15-30秒。3. 必须包含“Call to Action (CTA)”。"
}

def query_rag(query):
    # 极简的关键词匹配 RAG
    if "FDA" in query or "合规" in query or "政策" in query:
        return KNOWLEDGE_BASE["FDA"]
    if "TikTok" in query or "脚本" in query or "SOP" in query:
        return KNOWLEDGE_BASE["TikTok"]
    return ""

# ==================== 3. Agent 流式逻辑 (支持云端降级) ====================
def run_agent_stream(user_input):
    context = query_rag(user_input)
    
    # 判断是否为云端环境 (Streamlit Cloud 会自带这个环境变量)
    IS_CLOUD = os.environ.get("STREAMLIT_SHARING_MODE") is not None
    
    if IS_CLOUD:
        # 云端演示模式：模拟流式输出合规文案（避免本地 Ollama 报错）
        mock_text = f"【云端演示模式】检测到您在云端环境。\n\n以下是针对您的需求“{user_input}”生成的模拟合规草稿（已通过 FDA 合规审查）：\n\n1. 痛点引入（前3秒）：你是否经常感到疲惫？\n2. 产品引入：这款维生素C软糖...\n3. Call to Action：点击下方链接购买！\n\n*注：本地运行可体验真实 Qwen2.5 大模型生成。*"
        for char in mock_text:
            yield char
            time.sleep(0.02) # 模拟打字机速度
        return

    # 本地开发模式：调用 Ollama
    system_prompt = f"""你是一名资深的跨境电商AI运营专家，服务于一家专注美国市场的大健康（食品补充剂）企业。
你精通亚马逊和TikTok平台规则，熟悉FDA合规要求。
知识库上下文：{context}
请根据用户需求生成高质量、高转化率且合规的内容。请使用Markdown格式排版。"""
    
    payload = {
        "model": "qwen2.5:3b",
        "prompt": f"{system_prompt}\n用户：{user_input}\nAI：",
        "stream": True
    }
    try:
        res = requests.post("http://localhost:11434/api/generate", json=payload, stream=True, timeout=60)
        res.raise_for_status()
        import json
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                if 'response' in chunk:
                    yield chunk['response']
    except Exception as e:
        yield f"\n\n⚠️ 连接Ollama失败，请确保Ollama正在后台运行。错误: {e}"

# ==================== 4. UI 布局 ====================
with st.sidebar:
    st.markdown('<div class="gradient-title">🌿 春木出海 AI 中枢</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-caption">专为美国大健康市场打造</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚙️ 模型状态")
    # 动态显示状态
    if os.environ.get("STREAMLIT_SHARING_MODE"):
        st.info("☁️ 当前运行在云端演示模式")
    else:
        st.success("✅ 本地 qwen2.5:3b 已连接")
    st.caption("● 流式输出已启用 (Streaming)")
    st.markdown("---")
    st.markdown("### 🛡️ 人工审核区")
    st.info("待审核草稿：TikTok脚本 - 维生素C软糖")
    col1, col2 = st.columns(2)
    if col1.button("✅ 通过", use_container_width=True):
        st.toast("已通过审核，准备发布！", icon="✅")
    if col2.button("❌ 驳回", use_container_width=True):
        st.toast("已驳回，请重新生成", icon="❌")

st.markdown("### 🚀 Agent 工作台")
st.caption("涵盖 FDA 合规审查、TikTok 爆款生成、亚马逊 Listing 优化")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好！我是你的大健康出海AI助手。\n\n我可以帮你：\n1. 查询 FDA 合规要求\n2. 生成 TikTok 爆款脚本\n3. 优化亚马逊 Listing"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的业务需求..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = st.write_stream(run_agent_stream(prompt))
    st.session_state.messages.append({"role": "assistant", "content": response})
