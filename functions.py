from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import os
import base64



#######################
### 연습 모드 관련 함수 ###
#######################
def get_initial_prompt(level):
    return f"""
        당신은 대한민국 상위 0.1%의 실력을 가진 영어 회화 교사입니다. 당신은 한국 학생들을 대상으로 영어 회화를 진행합니다.
        당신은 먼저 대화를 이끌어나주어야 합니다. 학생들이 먼저 질문하는 경우에는 답변을 해주셔도 좋지만, 답변 이후에는 다시 재질문을 이어서 해주셔야 합니다.

        예를 들어, 학생이 How are you? 라고 먼저 묻는다면 당신은 Quite Nice.하고 새로운 질문으로 대화를 이어가주시면 됩니다.

        현재 학생의 수준은 '{level}'입니다. 학생의 수준에 따라 질문, 대답의 길이 및 난이도를 적절하게 바꿔주셔야 합니다.

        학생들의 수준이 "상"이라면, 많은 단어와 다양한 문법을 알고 있는 "대학생" 수준이라 생각하여 다양한 품사와 고급 단어들을 사용해서 수준급 회화를 진행해주시면 됩닌다.
        학생들의 수준이 "중"이라면, 기본적인 문법을 이해하고 있고 어느정도의 단어들을 아는 "고등학생" 수준이라고 생각하여 회화를 진행해주시면 됩니다.
        학생들의 수준이 "하"라면, 아주 짧은 정도의 문장을 말하고 대답할 수 있는 "중학생" 수준이라고 생각하여 회화를 진행해주시면 됩니다. 

        단, 이용자는 모두 나이가 20대 이상의 성인들입니다. 상,중,하 난이도가 영향을 미치는 것은 단어, 문법, 문장의 길이 등을 말하는 것이고 내용의 수준은 변하면 안됩니다.
        예를 들어, 학생들의 수준이 "하"라고 하더라도 Do you like apple? 이런 초등학생 수준의 질문을 해서는 안됩니다.
        """

def practice_chat_init(level):
    return [SystemMessage(content=get_initial_prompt(level))]

def correct(llm,chat_history):
    prompt = f"""
    Your primary goal is to help the user practice responding to questions in English.
    Analyze the user's response provided below. First, determine if the response is in English or Korean. Then, follow the specific instructions for that language. Your output MUST be in the specified Markdown format.
    ---
    ### **If the User Responds in Korean:**

    Provide your response using this exact structure:

    #### **Natural English Version**
    Translate the user's Korean response into a natural, conversational English sentence. This shouldn't be a literal translation, but rather how a native speaker would express the same idea.

    #### **Key Expressions for This Topic**
    Suggest 3-4 useful English phrases or vocabulary words related to the topic. Provide a short explanation for each.
    *   **Expression 1:** [Explanation]
    *   **Expression 2:** [Explanation]
    *   **Expression 3:** [Explanation]

    ---

    ### **If the User Responds in English:**

    Provide your response using this exact structure:

    #### **Polished Version**
    Correct any grammatical mistakes or awkward phrasing in the user's response to make it sound more natural, while keeping the original meaning intact.

    #### **Changes Explained**
    Briefly explain the main corrections you made. (e.g., "Used 'at' instead of 'in' because it's the correct preposition for a specific time.")

    #### **Key Expressions for This Topic**
    Suggest 3-4 useful English phrases or vocabulary words related to the topic.
    *   **Expression 1:** [Explanation]
    *   **Expression 2:** [Explanation]
    *   **Expression 3:** [Explanation]

    #### **Expanded Answer Example**
    Show the user how they could have answered more richly. Write a more detailed sample answer based on their original intent, using more descriptive vocabulary and varied sentence structures.
    ---
    Question : {chat_history[-2]}
    User's Response : {chat_history[-1]}
    """

    result = llm.invoke(prompt)
    return result.content

def answer_guide(llm, question):
    result = llm.invoke(f"""{question}에 대해 영어로 답변하기 위한 가이드를 간단히 200자 이내로 정리해주시고, 영어 문장 예시를 1,2가지 알려주세요.
                        답변 형식은 다음과 같습니다. 
                        
                        답변 형식 : 
                        이렇게 답변해보세요! \n
                        (답변을 위한 가이드) \n
                        (예시 문장 1)\n
                        (예시 문장 2)
                        """)
    return result.content
#######################
### 실전 모드 관련 함수 ###
#######################
def real_chat_init(level):
    return [SystemMessage(content=get_initial_prompt(level))]

###############
### 공통 함수 ###
###############
def start_question(llm, topic):
    result = llm.invoke(f"""당신은 지금 영어 회화 RolePlaying을 하고 있습니다. 
                        상대방의 수준은 {st.session_state.level}입니다. 
                        해당 수준은 1이라면 짧은 1-2문장 대화 가능, 2라면 문단 단위 대화 가능, 3이라면 FreeTalking 대화 가능입니다.
                        '{topic}' 주제를 바탕으로 첫 영어 대화를 시작해주세요. 
                        다른 말은 하지말고 바로 질문을 통해 대화를 시작해주세요.""")
    return result.content

def continuation_question(llm,chat_history):
    revised_chat_history = []
    for i,message in enumerate(chat_history):
        if i == 0 : 
            revised_chat_history.append(f"참고하세요 : {message.content}")
        if isinstance(message,HumanMessage):
            revised_chat_history.append(f"답변 : {message.content}")
        elif isinstance(message,AIMessage):
            revised_chat_history.append(f"질문 : {message.content}")
        else : 
            pass
    prompt = f"""
    지금까지 학생과 대화한 내용을 기반으로 영어 대화를 이어나가 주세요. 
    학생이 바로 이전에 답변한 내용이 이해가 잘 안가더라도 최대한 의도를 물어보면서 영어로 대화를 이어나가주세요.

    대화 내용 : {revised_chat_history}
    """
    result = llm.invoke(prompt)
    return result.content

def final_feedback(llm,chat_history):
    revised_chat_history = []
    for i,message in enumerate(chat_history):
        if i == 0 : 
            continue # Remove System Prompt 
        if isinstance(message,HumanMessage):
            revised_chat_history.append(f"답변 : {message.content}")
        elif isinstance(message,AIMessage):
            revised_chat_history.append(f"질문 : {message.content}")
        else : 
            pass
    prompt ="""
            Your task is to provide a comprehensive evaluation of the student's English based on the QA conversation script provided below.

            Your response MUST be structured using Markdown and follow this exact format. Do not add any conversational text outside of this structure.
            ---

            ## English Proficiency Evaluation

            ### **Overall Score: [Provide a score out of 100]**
            Give a score that reflects the student's overall performance in the conversation, considering all factors below.

            ### **General Feedback**
            Write a concise, positive, and encouraging summary (2-4 sentences). Start by highlighting a key strength, then mention the main area for improvement. Conclude with an encouraging remark.

            ### **Detailed Analysis**

            #### **Grammar (문법)**
            - **Strengths:** Point out 1-2 specific examples of correct grammar usage (e.g., "Excellent use of the present perfect tense in the sentence '...'").
            - **Areas for Improvement:** List up specific grammatical errors. For each error, show the original sentence and the corrected version. Briefly explain the mistake.
            - **Error 1:**
                - **Original:** "[Student's sentence with an error]"
                - **Correction:** "[Corrected sentence]"
                - **Reason:** "[Brief explanation of the grammar rule]"

            #### **Vocabulary (어휘)**
            - **Level:** [Choose one: **High**, **Medium**, or **Low**]
            - **Comments:** Briefly describe the student's vocabulary usage. Mention if the vocabulary was varied or repetitive. If repetitive, list the overused words and suggest 2-3 synonyms for each.
            - *Example: The word "good" was used frequently. You could also try: "excellent," "fantastic," or "beneficial."*

            #### **Expression Suggestions (표현 제안)**
            Create a table to suggest more natural or sophisticated ways to phrase things the student reply. Provide at least 3 examples.

            | Student's Original Phrase | Suggested Improvement | Why it's better |
            | :--- | :--- | :--- |
            | [Quote the student's phrase] | [Offer a more natural phrase] | [Explain the nuance, e.g., "More formal," "More common among native speakers"] |
            | [Quote the student's phrase] | [Offer a more natural phrase] | [Explain the nuance] |
            | [Quote the student's phrase] | [Offer a more natural phrase] | [Explain the nuance] |


            ### **Next Steps & Encouragement**
            Provide one clear, actionable tip for what the student should focus on next (e.g., "For your next conversation, try to use at least three new adjectives you learned today!"). End with a final encouraging sentence.

            ---
            예시는 영어였지만, 당신의 답장은 한국어로 작성해주셔야 합니다.
            """
    result = llm.invoke(f"{prompt}\n\n대화 내용: {chat_history}")
    return result.content

def translator(llm,query):
    result = llm.invoke('다음 문장을 한국어로 번역해주세요.'+query)
    return result.content

def display_log_content(log_data):
    """지정된 로그 파일의 내용을 읽어 Streamlit Expander에 표시합니다."""
    # 파일명에서 날짜와 시간 정보 추출
    try:
        timestamp_str = log_data.get("timestamp")
        log_time = datetime.fromisoformat(timestamp_str).strftime('%Y년 %m월 %d일 %H:%M:%S')
        expander_title = f"대화 기록 ({log_time})"
    except (ValueError, TypeError):
        expander_title = "이전 대화 기록"

    with st.expander(expander_title, expanded=True):
        st.subheader("💬 대화 내용")
        for i,message in enumerate(log_data.get("chat_history", [])):

            if i == 0 : continue
            msg_type = message.get("type")
            content = message.get("content")
            if msg_type == "human":
                st.chat_message("user").markdown(content)
            elif msg_type == "ai":
                st.chat_message("assistant").markdown(content)
            elif msg_type in ["system", "info"]:
                st.info(content, icon="💡")
        
        st.subheader("📝 최종 피드백")
        st.write(log_data.get("final_feedback", "저장된 피드백이 없습니다."))

def speech_to_text(api_key,audio_file_path):
    
    client = OpenAI(api_key=api_key)
    audio_file= open(audio_file_path, "rb")

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        prompt="Your goal is to write down what you say on the sound source in text. The sound source includes English and Korean randomly. So when you write it, write it in English if it sounds in English, and write it in Korean if it sounds in Korean. An audio file is recorded in only one language.",
    )

    return transcription.text

def text_to_speech(api_key, text):
    """Generates speech from text and returns it as a base64 encoded string."""
    client = OpenAI(api_key=api_key)
    try:
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="coral",
            input=text,
        ) as response:
            audio_bytes = response.read()
            return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        st.error(f"음성(TTS) 생성 중 오류가 발생했습니다: {e}")
        return None

def display_chat_history(chat_history):
    # 채팅 컨테이너
    chat_container = st.container(height=800, border=True)
    with chat_container:
        for i,message in enumerate(chat_history):
            if i == 0 : 
                continue # Remove System Prompt 
            if isinstance(message,HumanMessage):
                st.chat_message("user").markdown(message.content)
            elif isinstance(message,AIMessage):
                st.chat_message("assistant").markdown(message.content)
            else : 
                with st.expander("AI Feedback", expanded=False):
                    st.info(message.content,icon="💡")
    
