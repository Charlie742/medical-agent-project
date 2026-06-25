import streamlit
import streamlit as st
import time
import pandas as pd
import requests
import json


API_KEY = "在这里粘贴你的豆包API Key"
ENDPOINT_ID = "在这里粘贴推理接入点ID"


st.set_page_config(page_title="轻症导诊辅助智能体", page_icon="🏥", layout="wide")
st.title("🏥 门诊预问诊导诊智能体")
st.warning("重要提示：本智能体仅做症状收集、科室推荐与健康科普，不具备临床诊断资质，身体不适请及时线下就医！")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_info" not in st.session_state:
    st.session_state.user_info = {"name":"","age":"","gender":"","symptom":"","duration":""}


def get_department(symptom):
    symptom = symptom.lower()
    fever = ["发烧","发热","高烧","低热"]
    stomach = ["胃痛","腹痛","反酸","腹泻","恶心"]
    joint = ["关节痛","腿疼","腰痛","肩颈酸痛"]
    sleep = ["失眠","睡不着","多梦","熬夜心慌"]
    cough = ["咳嗽","咽痛","嗓子疼","流鼻涕"]
    heart = ["胸闷","心慌","心跳快"]

    if any(word in symptom for word in fever):
        return "发热门诊"
    elif any(word in symptom for word in stomach):
        return "消化内科"
    elif any(word in symptom for word in joint):
        return "骨科/疼痛科"
    elif any(word in symptom for word in sleep):
        return "神经内科/睡眠门诊"
    elif any(word in symptom for word in cough):
        return "呼吸内科"
    elif any(word in symptom for word in heart):
        return "心血管内科"
    else:
        return "全科门诊"


def llm_chat(user_msg, info, dept):
    name = info["name"]
    age = info["age"]
    symp = info["symptom"]
    time = info["duration"]
    reply = f"""您好{name}，{age}岁的朋友！
你描述的症状：{symp}，已经持续{time}。
系统根据你的症状匹配推荐就诊科室：{dept}
温馨健康提示：
1. 多喝温水、少辛辣，保证休息；
2. 本工具仅预问诊参考，不能代替医生诊断；
3. 若发烧超过38.5℃、呼吸困难请立刻前往急诊。"""
    return reply


with st.sidebar:
    st.header("📋 患者基础信息录入")
    st.session_state.user_info["name"] = st.text_input("姓名")
    st.session_state.user_info["age"] = st.text_input("年龄")
    st.session_state.user_info["gender"] = st.radio("性别", ["男","女","其他"])
    st.session_state.user_info["symptom"] = st.text_area("当前主要症状")
    st.session_state.user_info["duration"] = st.text_input("症状持续时间（例：2天、一周）")
    save_btn = st.button("保存患者信息")
    if save_btn:
        st.success("信息已保存，可开始问诊对话！")


st.subheader("💬 问诊对话区")
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

user_input = st.chat_input("请描述你的身体不适或提问...")
if user_input:
    st.session_state.chat_history.append({"role":"user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    dept = get_department(st.session_state.user_info["symptom"])
    with st.chat_message("assistant"):
        with st.spinner("智能体思考中..."):
            reply = llm_chat(user_input, st.session_state.user_info, dept)
            st.write(reply)
    st.session_state.chat_history.append({"role":"assistant", "content": reply})


st.divider()
st.subheader("📄 导出本次问诊记录")
if st.button("生成问诊报告"):
    info = st.session_state.user_info
    data = [
        ["患者姓名", info["name"]],
        ["年龄", info["age"]],
        ["性别", info["gender"]],
        ["主诉症状", info["symptom"]],
        ["持续时间", info["duration"]],
        ["推荐就诊科室", get_department(info["symptom"])]
    ]
    df = pd.DataFrame(data, columns=["项目","内容"])
    st.dataframe(df)
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("下载问诊记录CSV", csv, "问诊记录.csv", mime="text/csv")
