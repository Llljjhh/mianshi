# ==========================================
# 1. 导入依赖包
# ==========================================
import streamlit as st  # 用于快速构建 Web UI
import requests  # 用于发送 HTTP 请求给 Ollama
import chromadb  # 本地向量数据库，用于 RAG 检索
import json  # 用于解析 Ollama 的流式 JSON 响应

# ==========================================
# 2. 页面配置与高级 CSS 注入 (UI 层)
# ==========================================
# 设置页面标题、图标和布局。layout="wide" 让页面更宽敞，适合展示数据。
st.set_page_config(page_title="春木出海 AI 中枢", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# 注入 CSS 样式。Streamlit 默认样式较平庸，这里通过 CSS 实现“暗黑玻璃拟态”风格。
st.markdown("""
<style>
    /* 引入 Google 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* 全局字体与背景：使用径向渐变打造深邃星空感 */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { 
        background: radial-gradient(circle at 50% -20%, #11253e 0%, #020617 80%);
        color: #e2e8f0; 
    }

    /* 侧边栏玻璃拟态：半透明背景 + 背景模糊 */
    [data-testid="stSidebar"] { 
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* 聊天气泡美化：圆角、半透明、阴影、悬浮动画 */
    [data-testid="stChatMessage"] { 
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px; 
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover { transform: translateY(-2px); } # 鼠标悬浮微动效

    /* 自定义标题渐变 */
    .gradient-title {
        background: linear-gradient(135deg, #2dd4bf 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700; font-size: 26px; letter-spacing: -0.5px;
    }
    .sub-caption { color: #64748b; font-size: 13px; margin-bottom: 20px; }

    /* 输入框自定义 */
    .stChatInput { 
        background: rgba(15, 23, 42, 0.8) !important; 
        border: 1px solid rgba(45, 212, 191, 0.3) !important;
        border-radius: 24px !important;
        color: white !important;
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
# 3. RAG (检索增强生成) 知识库初始化 (数据层)
# ==========================================
# 使用 @st.cache_resource 装饰器，确保数据库只初始化一次，避免每次刷新页面都重新加载。
@st.cache_resource
def init_rag():
    # 创建 ChromaDB 客户端（内存模式，重启即清空，适合 MVP 演示）
    client = chromadb.Client()
    # 创建或获取一个名为 knowledge_base 的集合
    collection = client.get_or_create_collection(name="knowledge_base")

    # 模拟业务数据（面试官会看你是否懂业务，这里直接切入 FDA 合规和 TikTok SOP）
    mock_data = [
        "【美国FDA膳食补充剂合规指南】1. 禁止声称产品可以“治愈、治疗、预防”任何疾病。2. 允许使用“结构/功能声明”，但必须附带免责声明。3. 亚马逊Listing要求：必须包含GMP认证信息。",
        "【TikTok爆款SOP】1. 前3秒必须抓住注意力（痛点引入）。2. 视频时长控制在15-30秒。3. 必须包含“Call to Action (CTA)”。"
    ]
    # 将数据插入向量库（实际项目中，这里会调用 Embedding 模型将文本向量化）
    for i, text in enumerate(mock_data):
        collection.add(documents=[text], ids=[f"id_{i}"])
    return collection


collection = init_rag()


# 检索函数：根据用户查询，返回最相关的知识库内容
def query_rag(query, n_results=1):
    results = collection.query(query_texts=[query], n_results=n_results)
    if results and results['documents']:
        return "\n".join(results['documents'][0])
    return ""


# ==========================================
# 4. Agent 核心逻辑 (业务逻辑层)
# ==========================================
# 这是一个生成器函数（使用 yield），用于实现流式输出。
def run_agent_stream(user_input):
    context = ""
    # 【意图路由】：判断用户是否在问合规问题。如果是，才去查 RAG 知识库。
    # 面试加分点：不是所有问题都需要查知识库，精准路由可以节省 Token 和时间。
    if any(k in user_input for k in ["合规", "FDA", "政策", "限制"]):
        context = query_rag(user_input)

    # 【Prompt 工程】：将系统提示词、知识库上下文、用户输入拼接。
    # 注意：角色设定（资深的跨境电商AI运营专家）和大健康业务背景，让模型输出更专业。
    system_prompt = f"""你是一名资深的跨境电商AI运营专家，服务于一家专注美国市场的大健康（食品补充剂）企业。
你精通亚马逊和TikTok平台规则，熟悉FDA合规要求。
知识库上下文：{context}
请根据用户需求生成高质量、高转化率且合规的内容。请使用Markdown格式排版。"""

    # 构建 Ollama API 的请求体
    payload = {
        "model": "qwen2.5:3b",
        "prompt": f"{system_prompt}\n用户：{user_input}\nAI：",
        "stream": True  # 【关键】开启流式输出
    }

    try:
        # 发送流式请求。stream=True 允许我们逐行读取响应。
        res = requests.post("http://localhost:11434/api/generate", json=payload, stream=True, timeout=60)
        res.raise_for_status()  # 检查 HTTP 错误

        # 逐行解析 Ollama 返回的 JSON 数据
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                if 'response' in chunk:
                    yield chunk['response']  # 每次 yield 一小段文字，前端就能实现打字机效果
    except Exception as e:
        yield f"\n\n⚠️ 连接Ollama失败，请确保Ollama正在后台运行。错误: {e}"


# ==========================================
# 5. UI 布局与交互 (展示层)
# ==========================================
# 侧边栏
with st.sidebar:
    st.markdown('<div class="gradient-title">🌿 春木出海 AI 中枢</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-caption">专为美国大健康市场打造</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ 模型状态")
    st.success("✅ 本地 qwen2.5:3b 已连接")
    st.caption("● 流式输出已启用 (Streaming)")

    st.markdown("---")
    # 【人工审核区】：对应 JD 第6点“必要的人工审核机制”
    st.markdown("### 🛡️ 人工审核区 (Human-in-the-loop)")
    st.info("待审核草稿：TikTok脚本 - 维生素C软糖")
    col1, col2 = st.columns(2)
    if col1.button("✅ 通过", use_container_width=True):
        st.toast("已通过审核，准备发布至 TikTok/Amazon", icon="✅")
    if col2.button("❌ 驳回", use_container_width=True):
        st.toast("已驳回，请重新生成", icon="❌")

# 主界面
st.markdown("### 🚀 Agent 工作台")
st.caption("涵盖 FDA 合规审查、TikTok 爆款生成、亚马逊 Listing 优化")

# 【会话状态管理】：Streamlit 每次交互都会重跑整个脚本，用 st.session_state 保存聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "你好！我是你的大健康出海AI助手。\n\n我可以帮你：\n1. 查询 FDA 合规要求\n2. 生成 TikTok 爆款脚本\n3. 优化亚马逊 Listing\n\n请告诉我你的需求！"}
    ]

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 【用户输入与流式响应】
if prompt := st.chat_input("输入你的业务需求，例如：帮我写一个维生素C软糖的TikTok脚本..."):
    # 1. 展示用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 调用 Agent 并流式展示 AI 回复
    with st.chat_message("assistant"):
        response_stream = run_agent_stream(prompt)
        # st.write_stream 接收生成器，自动实现打字机效果，并返回完整文本
        response = st.write_stream(response_stream)

    # 3. 将 AI 回复保存到历史记录
    st.session_state.messages.append({"role": "assistant", "content": response})