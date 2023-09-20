import os
import requests
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
import tiktoken
import pynecone as pc

llm = ChatOpenAI(temperature=0.9, model="gpt-3.5-turbo-16k", openai_api_key='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')

def truncate_text(text, max_tokens=3000):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
        return text
    return enc.decode(tokens[:max_tokens])

def read_template(file):
    f = open(file, mode="r")
    contents = f.read()
    f.close()
    contents = "".join(contents)
    return contents

guide = os.path.join(os.getcwd(), "template/kakaosync.txt")

system_template=f"""
당신은 카카오싱크에서 도움말을 주는 챗봇입니다.
챗봇 가이드라인은 다음과 같습니다.
{truncate_text(guide, max_tokens=4000)}
다음 규칙에 맞게 답변하세요.
- 5줄로 요약해서 답변하세요
"""
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template="{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
chain = LLMChain(llm=llm, prompt=chat_prompt)

# Web
class Data(pc.Model, table=True):
    """A table for questions and answers in the database."""

    title: str
    content: str
    url: str
    summary: str
    timestamp: datetime = datetime.now()


class State(pc.State):
    """The app state."""

    query: str = ""
    content: str = "답변을 기다리는 중..."

    is_working: bool = False

    async def handle_submit(self, form_data):
        self.is_working = True
        self.query = form_data['query']

        answer = chain.run(self.query)
        self.content = answer

        self.is_working = False

def index() -> pc.Component:
    return pc.center(
        pc.vstack(
            pc.form(
                pc.vstack(
                    pc.heading("카카오 싱크 챗봇", font_size="2em", font_family="Nanum Gothic"),
                    pc.input(placeholder="카카오 싱크에 대해 문의해 보세요", id="query", font_family="Nanum Gothic"),
                    pc.button("Submit", type_="submit"),

                ),
                on_submit=State.handle_submit,

                width="80%",
            ),
            pc.cond(State.is_working,
                    pc.spinner(
                        color="lightgreen",
                        thickness=5,
                        speed="1.5s",
                        size="xl",
                    ), ),
            pc.box(
                pc.markdown(State.content),
                border_radius="15px",
                border_color="gray",
                border_width="thin",
                padding = 5,
                font_family="Nanum Gothic"
            ),

            spacing="1em",
            font_size="1em",
            width="80%",

            padding_top="10%", )
    )

# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()
