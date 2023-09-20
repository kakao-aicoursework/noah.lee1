import tiktoken

def read_template(file):
    f = open(file, mode="r")
    contents = f.read()
    f.close()
    contents = "".join(contents)
    return contents

def truncate_text(text, max_tokens=3000):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
        return text
    return enc.decode(tokens[:max_tokens])